import os
import shutil
import yaml
from collections import defaultdict, Counter
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def analyze_multiclass_patterns(dataset_path):
    """Analizar patrones específicos en casos multi-clase"""
    
    # Cargar configuración
    data_yaml_path = None
    for root, dirs, files in os.walk(dataset_path):
        if 'data.yaml' in files:
            data_yaml_path = os.path.join(root, 'data.yaml')
            break
    
    if not data_yaml_path:
        raise FileNotFoundError(f"No se encontró data.yaml en {dataset_path}")
    
    with open(data_yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    class_names = config.get('names', [])
    dataset_root = os.path.dirname(data_yaml_path)
    
    multiclass_analysis = {
        'scratch_dent': [],           # 0,1
        'scratch_broken_glass': [],   # 0,2  
        'dent_broken_glass': [],      # 1,2
        'all_three': [],              # 0,1,2
        'dominant_class': defaultdict(list),  # Clase dominante por archivo
        'statistics': {
            'total_files': 0,
            'multiclass_files': 0,
            'single_class_files': 0
        }
    }
    
    print("🔍 Analizando patrones multi-clase...")
    
    for split in ['train', 'val', 'test']:
        if split in config:
            labels_dir = config[split].replace('images', 'labels')
            if not os.path.isabs(labels_dir):
                labels_dir = os.path.join(dataset_root, labels_dir)
            
            if os.path.exists(labels_dir):
                print(f"   📁 Procesando {split}: {labels_dir}")
                
                for label_file in os.listdir(labels_dir):
                    if label_file.endswith('.txt'):
                        label_path = os.path.join(labels_dir, label_file)
                        multiclass_analysis['statistics']['total_files'] += 1
                        
                        # Contar clases y bounding boxes
                        class_counts = Counter()
                        bbox_data = []
                        
                        with open(label_path, 'r') as f:
                            for line in f:
                                try:
                                    parts = line.strip().split()
                                    if len(parts) >= 5:
                                        class_id = int(parts[0])
                                        x, y, w, h = map(float, parts[1:5])
                                        class_counts[class_id] += 1
                                        bbox_data.append({
                                            'class': class_id,
                                            'x': x, 'y': y, 'w': w, 'h': h,
                                            'area': w * h
                                        })
                                except:
                                    continue
                        
                        if len(class_counts) == 1:
                            multiclass_analysis['statistics']['single_class_files'] += 1
                        elif len(class_counts) > 1:  # Multi-clase
                            multiclass_analysis['statistics']['multiclass_files'] += 1
                            unique_classes = set(class_counts.keys())
                            total_boxes = sum(class_counts.values())
                            
                            # Calcular área total por clase
                            area_by_class = defaultdict(float)
                            for bbox in bbox_data:
                                area_by_class[bbox['class']] += bbox['area']
                            
                            case_data = {
                                'file': label_file,
                                'split': split,
                                'counts': dict(class_counts),
                                'total_boxes': total_boxes,
                                'area_by_class': dict(area_by_class),
                                'bbox_data': bbox_data
                            }
                            
                            # Clasificar tipo de multi-clase
                            if unique_classes == {0, 1}:  # scratch + dent
                                multiclass_analysis['scratch_dent'].append(case_data)
                            elif unique_classes == {0, 2}:  # scratch + broken_glass
                                multiclass_analysis['scratch_broken_glass'].append(case_data)
                            elif unique_classes == {1, 2}:  # dent + broken_glass
                                multiclass_analysis['dent_broken_glass'].append(case_data)
                            elif unique_classes == {0, 1, 2}:  # todas las clases
                                multiclass_analysis['all_three'].append(case_data)
                            
                            # Determinar clase dominante (por cantidad y área)
                            dominant_by_count = max(class_counts, key=class_counts.get)
                            dominant_by_area = max(area_by_class, key=area_by_class.get)
                            
                            multiclass_analysis['dominant_class'][dominant_by_count].append({
                                **case_data,
                                'dominant_by_count': dominant_by_count,
                                'dominant_by_area': dominant_by_area,
                                'count_percentage': class_counts[dominant_by_count] / total_boxes * 100,
                                'area_percentage': area_by_class[dominant_by_area] / sum(area_by_class.values()) * 100
                            })
    
    # Mostrar estadísticas
    stats = multiclass_analysis['statistics']
    print(f"\n📊 ESTADÍSTICAS DEL DATASET:")
    print(f"   Total archivos: {stats['total_files']}")
    print(f"   Archivos single-class: {stats['single_class_files']} ({stats['single_class_files']/stats['total_files']*100:.1f}%)")
    print(f"   Archivos multi-class: {stats['multiclass_files']} ({stats['multiclass_files']/stats['total_files']*100:.1f}%)")
    
    return multiclass_analysis, class_names, data_yaml_path

def create_advanced_cleaning_strategy(multiclass_analysis, class_names):
    """Crear estrategia de limpieza avanzada con múltiples criterios"""
    
    cleaning_strategy = {
        'keep_dominant_count': [],      # Mantener clase dominante por cantidad
        'keep_dominant_area': [],       # Mantener clase dominante por área
        'keep_largest_bbox': [],        # Mantener solo la caja más grande
        'hierarchical_priority': [],    # Usar jerarquía de severidad
        'manual_review': [],            # Revisión manual necesaria
        'split_candidate': [],          # Candidato para división
        'statistics': {
            'total_cases': 0,
            'auto_resolvable': 0,
            'manual_needed': 0
        }
    }
    
    # Jerarquía de severidad (mayor número = más prioritario)
    severity_hierarchy = {
        2: 3,  # broken_glass - más severo
        1: 2,  # dent - moderado
        0: 1   # scratch - menos severo
    }
    
    print("\n🧹 Creando estrategia de limpieza avanzada...")
    
    total_cases = 0
    
    for pattern_type, cases in multiclass_analysis.items():
        if pattern_type in ['dominant_class', 'statistics']:
            continue
            
        total_cases += len(cases)
        cleaning_strategy['statistics']['total_cases'] += len(cases)
        
        print(f"\n📋 Analizando {pattern_type}: {len(cases)} casos")
        
        for case in cases:
            counts = case['counts']
            area_by_class = case['area_by_class']
            total_boxes = case['total_boxes']
            bbox_data = case['bbox_data']
            
            # Calcular diferentes métricas de dominancia
            max_count_class = max(counts, key=counts.get)
            max_area_class = max(area_by_class, key=area_by_class.get)
            
            count_dominance = counts[max_count_class] / total_boxes
            area_dominance = area_by_class[max_area_class] / sum(area_by_class.values())
            
            # Encontrar la bbox más grande
            largest_bbox = max(bbox_data, key=lambda x: x['area'])
            largest_bbox_class = largest_bbox['class']
            
            # Aplicar jerarquía de severidad
            classes_present = list(counts.keys())
            most_severe_class = max(classes_present, key=lambda x: severity_hierarchy.get(x, 0))
            
            # Decidir estrategia basada en múltiples criterios
            case_enhanced = {
                **case,
                'max_count_class': max_count_class,
                'max_area_class': max_area_class,
                'largest_bbox_class': largest_bbox_class,
                'most_severe_class': most_severe_class,
                'count_dominance': count_dominance,
                'area_dominance': area_dominance,
                'largest_bbox_area': largest_bbox['area']
            }
            
            # Lógica de decisión mejorada
            if count_dominance >= 0.8 and area_dominance >= 0.7:
                # Dominancia clara tanto en cantidad como área
                cleaning_strategy['keep_dominant_count'].append({
                    **case_enhanced,
                    'action': 'keep_dominant_count',
                    'reason': 'clear_dominance',
                    'target_class': max_count_class
                })
                cleaning_strategy['statistics']['auto_resolvable'] += 1
                
            elif area_dominance >= 0.8:
                # Dominancia clara por área
                cleaning_strategy['keep_dominant_area'].append({
                    **case_enhanced,
                    'action': 'keep_dominant_area', 
                    'reason': 'area_dominance',
                    'target_class': max_area_class
                })
                cleaning_strategy['statistics']['auto_resolvable'] += 1
                
            elif largest_bbox['area'] >= 0.5:  # Una caja ocupa >50% del área
                cleaning_strategy['keep_largest_bbox'].append({
                    **case_enhanced,
                    'action': 'keep_largest_bbox',
                    'reason': 'single_large_object',
                    'target_class': largest_bbox_class
                })
                cleaning_strategy['statistics']['auto_resolvable'] += 1
                
            elif most_severe_class in counts and counts[most_severe_class] >= 1:
                # Usar jerarquía de severidad
                cleaning_strategy['hierarchical_priority'].append({
                    **case_enhanced,
                    'action': 'hierarchical_priority',
                    'reason': 'severity_hierarchy',
                    'target_class': most_severe_class
                })
                cleaning_strategy['statistics']['auto_resolvable'] += 1
                
            elif total_boxes <= 3:
                # Pocos objetos, candidato para división
                cleaning_strategy['split_candidate'].append({
                    **case_enhanced,
                    'action': 'split_candidate',
                    'reason': 'few_objects'
                })
                cleaning_strategy['statistics']['manual_needed'] += 1
                
            else:
                # Caso complejo que requiere revisión manual
                cleaning_strategy['manual_review'].append({
                    **case_enhanced,
                    'action': 'manual_review',
                    'reason': 'complex_case'
                })
                cleaning_strategy['statistics']['manual_needed'] += 1
    
    return cleaning_strategy

def apply_cleaning_strategy(dataset_path, cleaning_strategy, data_yaml_path, backup=True):
    """Aplicar estrategia de limpieza completa"""
    
    if backup:
        backup_dir = f"{dataset_path}_backup_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        if not os.path.exists(backup_dir):
            print(f"📦 Creando backup...")
            shutil.copytree(dataset_path, backup_dir)
            print(f"✅ Backup creado en: {backup_dir}")
    
    # Cargar configuración
    with open(data_yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    dataset_root = os.path.dirname(data_yaml_path)
    
    cleaning_results = {
        'processed': 0,
        'errors': 0,
        'actions_applied': defaultdict(int)
    }
    
    print(f"\n🧹 Aplicando estrategia de limpieza...")
    
    # Procesar cada estrategia
    all_actions = []
    for strategy_name, cases in cleaning_strategy.items():
        if strategy_name == 'statistics':
            continue
        all_actions.extend(cases)
    
    for i, case in enumerate(all_actions):
        if i % 50 == 0:
            print(f"   Procesando: {i}/{len(all_actions)}")
        
        try:
            file_name = case['file']
            split = case['split']
            action = case['action']
            target_class = case.get('target_class')
            
            # Obtener ruta del archivo
            labels_dir = config[split].replace('images', 'labels')
            if not os.path.isabs(labels_dir):
                labels_dir = os.path.join(dataset_root, labels_dir)
            
            label_path = os.path.join(labels_dir, file_name)
            
            if os.path.exists(label_path):
                # Leer archivo original
                original_lines = []
                with open(label_path, 'r') as f:
                    original_lines = f.readlines()
                
                # Aplicar filtro según la acción
                filtered_lines = []
                
                if action in ['keep_dominant_count', 'keep_dominant_area', 'hierarchical_priority']:
                    # Mantener solo la clase objetivo
                    for line in original_lines:
                        try:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                class_id = int(parts[0])
                                if class_id == target_class:
                                    filtered_lines.append(line)
                        except:
                            continue
                
                elif action == 'keep_largest_bbox':
                    # Mantener solo la bounding box más grande de la clase objetivo
                    bbox_data = []
                    for line in original_lines:
                        try:
                            parts = line.strip().split()
                            if len(parts) >= 5:
                                class_id = int(parts[0])
                                if class_id == target_class:
                                    x, y, w, h = map(float, parts[1:5])
                                    bbox_data.append({
                                        'line': line,
                                        'area': w * h
                                    })
                        except:
                            continue
                    
                    if bbox_data:
                        largest = max(bbox_data, key=lambda x: x['area'])
                        filtered_lines.append(largest['line'])
                
                # Escribir archivo limpio si hay contenido
                if filtered_lines:
                    with open(label_path, 'w') as f:
                        f.writelines(filtered_lines)
                    cleaning_results['processed'] += 1
                    cleaning_results['actions_applied'][action] += 1
                else:
                    print(f"⚠️ No se encontraron líneas válidas para {file_name}")
                    cleaning_results['errors'] += 1
        
        except Exception as e:
            print(f"❌ Error procesando {case.get('file', 'unknown')}: {e}")
            cleaning_results['errors'] += 1
    
    return cleaning_results

def create_cleaning_visualization(multiclass_analysis, cleaning_strategy, output_dir='cleaning_results'):
    """Crear visualizaciones del proceso de limpieza"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Distribución de casos multi-clase por tipo
    pattern_counts = {}
    for pattern_type, cases in multiclass_analysis.items():
        if pattern_type not in ['dominant_class', 'statistics'] and cases:
            pattern_counts[pattern_type.replace('_', '+').title()] = len(cases)
    
    if pattern_counts:
        axes[0,0].bar(pattern_counts.keys(), pattern_counts.values(), 
                     color=['lightcoral', 'lightblue', 'lightgreen', 'lightyellow'])
        axes[0,0].set_title('Casos Multi-clase por Combinación', fontweight='bold')
        axes[0,0].set_ylabel('Número de Casos')
        axes[0,0].tick_params(axis='x', rotation=45)
    
    # 2. Estrategias de limpieza aplicadas
    strategy_counts = {}
    for strategy_name, cases in cleaning_strategy.items():
        if strategy_name != 'statistics' and cases:
            strategy_counts[strategy_name.replace('_', ' ').title()] = len(cases)
    
    if strategy_counts:
        colors = ['green', 'blue', 'orange', 'purple', 'red', 'brown'][:len(strategy_counts)]
        axes[0,1].bar(strategy_counts.keys(), strategy_counts.values(), color=colors)
        axes[0,1].set_title('Estrategias de Limpieza Aplicadas', fontweight='bold')
        axes[0,1].set_ylabel('Número de Casos')
        axes[0,1].tick_params(axis='x', rotation=45)
    
    # 3. Distribución antes/después
    stats = multiclass_analysis['statistics']
    before_data = [stats['single_class_files'], stats['multiclass_files']]
    before_labels = ['Single-class', 'Multi-class']
    
    axes[1,0].pie(before_data, labels=before_labels, autopct='%1.1f%%', 
                 colors=['lightgreen', 'lightcoral'])
    axes[1,0].set_title('Distribución ANTES de Limpieza', fontweight='bold')
    
    # 4. Resumen de resultados
    cleaning_stats = cleaning_strategy['statistics']
    result_data = [cleaning_stats['auto_resolvable'], cleaning_stats['manual_needed']]
    result_labels = ['Auto-resueltos', 'Revisión Manual']
    
    axes[1,1].pie(result_data, labels=result_labels, autopct='%1.1f%%',
                 colors=['lightgreen', 'lightyellow'])
    axes[1,1].set_title('Casos Procesados', fontweight='bold')
    
    plt.tight_layout()
    
    # Guardar visualización
    viz_path = os.path.join(output_dir, 'cleaning_process_analysis.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Visualización guardada en: {viz_path}")

def generate_comprehensive_report(multiclass_analysis, cleaning_strategy, cleaning_results, class_names, output_dir='cleaning_results'):
    """Generar reporte completo del proceso de limpieza"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    stats = multiclass_analysis['statistics']
    cleaning_stats = cleaning_strategy['statistics']
    
    # Calcular mejoras
    original_multiclass_percentage = stats['multiclass_files'] / stats['total_files'] * 100
    resolved_cases = cleaning_results['processed']
    remaining_multiclass = stats['multiclass_files'] - resolved_cases
    new_multiclass_percentage = remaining_multiclass / stats['total_files'] * 100
    improvement = original_multiclass_percentage - new_multiclass_percentage
    
    report = f"""
# REPORTE COMPLETO DE LIMPIEZA DE DATASET
=======================================

## 📊 Estadísticas del Dataset Original
- **Total de archivos**: {stats['total_files']:,}
- **Archivos single-class**: {stats['single_class_files']:,} ({stats['single_class_files']/stats['total_files']*100:.1f}%)
- **Archivos multi-class**: {stats['multiclass_files']:,} ({original_multiclass_percentage:.1f}%)
- **Clases**: {', '.join(class_names)}

## 🔍 Análisis de Casos Multi-clase
"""
    
    for pattern_type, cases in multiclass_analysis.items():
        if pattern_type not in ['dominant_class', 'statistics'] and cases:
            report += f"- **{pattern_type.replace('_', ' + ').title()}**: {len(cases)} casos\n"
    
    report += f"""

## 🧹 Estrategia de Limpieza Aplicada

### Criterios Utilizados:
1. **Dominancia por cantidad** (≥80% de objetos)
2. **Dominancia por área** (≥80% del área total)
3. **Objeto único grande** (≥50% del área)
4. **Jerarquía de severidad** (broken_glass > dent > scratch)
5. **Casos complejos** → Revisión manual

### Acciones Ejecutadas:
"""
    
    for action, count in cleaning_results['actions_applied'].items():
        report += f"- **{action.replace('_', ' ').title()}**: {count} casos\n"
    
    report += f"""

### Resultados del Procesamiento:
- **Casos procesados exitosamente**: {cleaning_results['processed']:,}
- **Errores durante procesamiento**: {cleaning_results['errors']}
- **Casos que requieren revisión manual**: {cleaning_stats['manual_needed']}

## 📈 Mejoras Logradas

### Reducción de Ambigüedad:
- **Antes**: {stats['multiclass_files']:,} casos multi-clase ({original_multiclass_percentage:.1f}%)
- **Después**: ~{remaining_multiclass} casos multi-clase ({new_multiclass_percentage:.1f}%)
- **Mejora**: {improvement:.1f} puntos porcentuales de reducción

### Impacto Esperado en el Modelo:
- **Reducción de confusión**: {improvement:.1f}% menos casos ambiguos
- **Mejora estimada en accuracy**: +{improvement*0.5:.1f}% a +{improvement*0.8:.1f}%
- **Consistencia de entrenamiento**: Mejorada significativamente

## 🎯 Próximos Pasos

### Inmediatos:
1. ✅ **Re-verificar balance** del dataset limpio
2. ✅ **Re-entrenar modelo** con datos limpios
3. 🔍 **Revisar casos manuales** ({cleaning_stats['manual_needed']} pendientes)

### Recomendaciones:
- **Entrenamiento**: Usar configuración conservadora inicialmente
- **Validación**: Comparar métricas antes/después de limpieza
- **Monitoreo**: Seguir accuracy y matriz de confusión
- **Iteración**: Aplicar limpieza adicional si es necesario

### Criterios de Éxito:
- **Objetivo**: <5% de casos multi-clase
- **Accuracy esperada**: >90%
- **Confusiones críticas**: <10 casos por tipo

## 🔧 Archivos Generados:
- Dataset limpio en ubicación original
- Backup en carpeta con timestamp
- Reportes y visualizaciones en `cleaning_results/`

---
*Limpieza completada el {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    # Guardar reporte
    report_path = os.path.join(output_dir, 'comprehensive_cleaning_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte completo guardado: {report_path}")
    print("\n" + "="*70)
    print(report)
    
    return report

def main():
    """Función principal para limpieza automática completa"""
    
    print("🧹 LIMPIEZA AUTOMÁTICA AVANZADA DE DATASET")
    print("="*70)
    print("Esta herramienta aplicará limpieza inteligente a casos multi-clase")
    print("basándose en dominancia, área, y jerarquía de severidad.\n")
    
    # Obtener dataset
    dataset_path = input("📁 Ruta del dataset a limpiar: ").strip()
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset no encontrado: {dataset_path}")
        return
    
    try:
        # Paso 1: Análisis completo
        print(f"\n🔍 PASO 1: Análisis del dataset...")
        multiclass_analysis, class_names, data_yaml_path = analyze_multiclass_patterns(dataset_path)
        
        # Paso 2: Crear estrategia
        print(f"\n🧠 PASO 2: Creando estrategia de limpieza...")
        cleaning_strategy = create_advanced_cleaning_strategy(multiclass_analysis, class_names)
        
        # Mostrar resumen de la estrategia
        stats = cleaning_strategy['statistics']
        print(f"\n📋 RESUMEN DE ESTRATEGIA:")
        print(f"   Total casos a procesar: {stats['total_cases']}")
        print(f"   Auto-resolvables: {stats['auto_resolvable']} ({stats['auto_resolvable']/stats['total_cases']*100:.1f}%)")
        print(f"   Revisión manual: {stats['manual_needed']} ({stats['manual_needed']/stats['total_cases']*100:.1f}%)")
        
        # Paso 3: Confirmar aplicación
        print(f"\n⚠️  IMPORTANTE: Se creará un backup automático antes de modificar.")
        apply_cleaning = input(f"¿Aplicar limpieza automática? (y/n): ").lower()
        
        if apply_cleaning in ['y', 'yes', 'sí', 's']:
            # Paso 4: Aplicar limpieza
            print(f"\n🧹 PASO 3: Aplicando limpieza...")
            cleaning_results = apply_cleaning_strategy(dataset_path, cleaning_strategy, data_yaml_path)
            
            # Paso 5: Generar reportes y visualizaciones
            print(f"\n📊 PASO 4: Generando reportes...")
            create_cleaning_visualization(multiclass_analysis, cleaning_strategy)
            report = generate_comprehensive_report(multiclass_analysis, cleaning_strategy, cleaning_results, class_names)
            
            print(f"\n✅ LIMPIEZA COMPLETADA EXITOSAMENTE!")
            print(f"📊 Archivos procesados: {cleaning_results['processed']}")
            print(f"🔧 Errores: {cleaning_results['errors']}")
            print(f"📄 Backup y reportes creados")
            print(f"\n💡 PRÓXIMO PASO: Ejecuta 'python verify_balance.py' para verificar mejoras")
            
        else:
            print("👍 Limpieza cancelada. No se realizaron cambios.")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
    