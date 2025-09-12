import os
import yaml
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from collections import defaultdict, Counter
import json

def load_dataset_config(dataset_path):
    """Cargar configuración del dataset"""
    data_yaml_path = None
    for root, dirs, files in os.walk(dataset_path):
        if 'data.yaml' in files:
            data_yaml_path = os.path.join(root, 'data.yaml')
            break
    
    if not data_yaml_path:
        raise FileNotFoundError(f"No se encontró data.yaml en {dataset_path}")
    
    with open(data_yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config, data_yaml_path

def manual_confusion_analysis(dataset_path):
    """Análisis manual de confusión basado en estructura del dataset"""
    
    print("🔍 ANÁLISIS DE CONFUSIÓN MANUAL")
    print("="*50)
    
    # Cargar configuración
    config, data_yaml_path = load_dataset_config(dataset_path)
    class_names = config.get('names', [])
    
    print(f"🎯 Clases detectadas: {class_names}")
    
    # Mapeo de clases
    class_mapping = {i: name for i, name in enumerate(class_names)}
    
    # Analizar distribución por clase
    dataset_root = os.path.dirname(data_yaml_path)
    
    confusion_patterns = {
        'scratch_broken_glass': [],  # Archivos que pueden confundirse
        'dent_broken_glass': [],
        'ambiguous_cases': []
    }
    
    # Buscar patrones en nombres de archivos
    for split in ['train', 'val', 'test']:
        if split in config:
            labels_dir = config[split].replace('images', 'labels')
            if not os.path.isabs(labels_dir):
                labels_dir = os.path.join(dataset_root, labels_dir)
            
            if os.path.exists(labels_dir):
                print(f"\n📁 Analizando {split}: {labels_dir}")
                
                for label_file in os.listdir(labels_dir):
                    if label_file.endswith('.txt'):
                        label_path = os.path.join(labels_dir, label_file)
                        
                        # Leer clases en el archivo
                        classes_in_file = []
                        with open(label_path, 'r') as f:
                            for line in f:
                                try:
                                    class_id = int(line.strip().split()[0])
                                    classes_in_file.append(class_id)
                                except:
                                    continue
                        
                        # Detectar patrones problemáticos
                        unique_classes = set(classes_in_file)
                        
                        # Casos con múltiples tipos de daño
                        if len(unique_classes) > 1:
                            confusion_patterns['ambiguous_cases'].append({
                                'file': label_file,
                                'classes': [class_mapping.get(c, f'class_{c}') for c in unique_classes],
                                'split': split
                            })
                        
                        # Buscar patrones en nombres de archivos
                        filename_lower = label_file.lower()
                        if any(word in filename_lower for word in ['scratch', 'scrape']) and \
                           any(word in filename_lower for word in ['glass', 'window', 'windshield']):
                            confusion_patterns['scratch_broken_glass'].append({
                                'file': label_file,
                                'classes': [class_mapping.get(c, f'class_{c}') for c in unique_classes],
                                'split': split
                            })
                        
                        if any(word in filename_lower for word in ['dent', 'dented']) and \
                           any(word in filename_lower for word in ['glass', 'window']):
                            confusion_patterns['dent_broken_glass'].append({
                                'file': label_file,
                                'classes': [class_mapping.get(c, f'class_{c}') for c in unique_classes],
                                'split': split
                            })
    
    return confusion_patterns, class_mapping

def analyze_class_cooccurrence(dataset_path):
    """Analizar co-ocurrencia de clases en las mismas imágenes"""
    
    config, data_yaml_path = load_dataset_config(dataset_path)
    class_names = config.get('names', [])
    dataset_root = os.path.dirname(data_yaml_path)
    
    # Matriz de co-ocurrencia
    cooccurrence_matrix = np.zeros((len(class_names), len(class_names)))
    
    # Contar co-ocurrencias
    for split in ['train', 'val']:
        if split in config:
            labels_dir = config[split].replace('images', 'labels')
            if not os.path.isabs(labels_dir):
                labels_dir = os.path.join(dataset_root, labels_dir)
            
            if os.path.exists(labels_dir):
                for label_file in os.listdir(labels_dir):
                    if label_file.endswith('.txt'):
                        label_path = os.path.join(labels_dir, label_file)
                        
                        classes_in_file = []
                        with open(label_path, 'r') as f:
                            for line in f:
                                try:
                                    class_id = int(line.strip().split()[0])
                                    if 0 <= class_id < len(class_names):
                                        classes_in_file.append(class_id)
                                except:
                                    continue
                        
                        # Actualizar matriz de co-ocurrencia
                        unique_classes = list(set(classes_in_file))
                        for i in unique_classes:
                            for j in unique_classes:
                                cooccurrence_matrix[i][j] += 1
    
    return cooccurrence_matrix

def create_confusion_prediction_analysis(dataset_path, output_dir='confusion_analysis_manual'):
    """Crear análisis predictivo de confusiones"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Análisis manual
    confusion_patterns, class_mapping = manual_confusion_analysis(dataset_path)
    
    # Análisis de co-ocurrencia
    cooccurrence_matrix = analyze_class_cooccurrence(dataset_path)
    class_names = list(class_mapping.values())
    
    # Crear visualizaciones
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Matriz de co-ocurrencia
    sns.heatmap(cooccurrence_matrix, 
                annot=True, 
                fmt='g',
                xticklabels=class_names,
                yticklabels=class_names,
                cmap='Blues',
                ax=axes[0,0])
    axes[0,0].set_title('Matriz de Co-ocurrencia de Clases', fontweight='bold')
    axes[0,0].set_xlabel('Clase')
    axes[0,0].set_ylabel('Clase')
    
    # 2. Casos ambiguos por split
    ambiguous_by_split = defaultdict(int)
    for case in confusion_patterns['ambiguous_cases']:
        ambiguous_by_split[case['split']] += 1
    
    splits = list(ambiguous_by_split.keys())
    counts = list(ambiguous_by_split.values())
    
    axes[0,1].bar(splits, counts, color=['orange', 'green', 'red'])
    axes[0,1].set_title('Casos Ambiguos por Split', fontweight='bold')
    axes[0,1].set_ylabel('Número de Casos')
    
    # 3. Patrones de confusión identificados
    pattern_names = ['Scratch + Glass', 'Dent + Glass', 'Casos Ambiguos']
    pattern_counts = [
        len(confusion_patterns['scratch_broken_glass']),
        len(confusion_patterns['dent_broken_glass']),
        len(confusion_patterns['ambiguous_cases'])
    ]
    
    colors = ['lightcoral', 'lightblue', 'lightyellow']
    bars = axes[1,0].bar(pattern_names, pattern_counts, color=colors)
    axes[1,0].set_title('Patrones de Confusión Identificados', fontweight='bold')
    axes[1,0].set_ylabel('Número de Casos')
    
    # Agregar etiquetas en las barras
    for bar, count in zip(bars, pattern_counts):
        axes[1,0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                      str(count), ha='center', va='bottom', fontweight='bold')
    
    # 4. Distribución de clases múltiples
    multi_class_distribution = defaultdict(int)
    for case in confusion_patterns['ambiguous_cases']:
        num_classes = len(case['classes'])
        multi_class_distribution[num_classes] += 1
    
    if multi_class_distribution:
        nums = list(multi_class_distribution.keys())
        counts = list(multi_class_distribution.values())
        axes[1,1].pie(counts, labels=[f'{n} clases' for n in nums], autopct='%1.1f%%')
        axes[1,1].set_title('Distribución de Imágenes Multi-clase', fontweight='bold')
    else:
        axes[1,1].text(0.5, 0.5, 'No se encontraron\ncasos multi-clase', 
                      ha='center', va='center', transform=axes[1,1].transAxes)
        axes[1,1].set_title('Distribución de Imágenes Multi-clase', fontweight='bold')
    
    plt.tight_layout()
    
    # Guardar visualización
    viz_path = os.path.join(output_dir, 'confusion_prediction_analysis.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Análisis guardado en: {viz_path}")
    
    return confusion_patterns, cooccurrence_matrix

def generate_prediction_report(confusion_patterns, class_mapping, output_dir='confusion_analysis_manual'):
    """Generar reporte predictivo de confusiones"""
    
    report = f"""
# ANÁLISIS PREDICTIVO DE CONFUSIONES
===================================

## Resumen del Análisis
Este análisis identifica patrones potenciales de confusión basándose en:
- Co-ocurrencia de clases en las mismas imágenes
- Patrones en nombres de archivos
- Casos con múltiples tipos de daño

## Clases Analizadas
{', '.join(class_mapping.values())}

## Patrones de Confusión Identificados

### 1. Scratch + Broken Glass
**Casos detectados**: {len(confusion_patterns['scratch_broken_glass'])}
**Problema potencial**: Rayones en vidrio pueden confundirse con vidrio roto
**Archivos problemáticos**:
"""
    
    for case in confusion_patterns['scratch_broken_glass'][:5]:
        report += f"- {case['file']} ({case['split']}) - Clases: {', '.join(case['classes'])}\n"
    
    report += f"""

### 2. Dent + Broken Glass  
**Casos detectados**: {len(confusion_patterns['dent_broken_glass'])}
**Problema potencial**: Abolladuras cerca de ventanas pueden confundirse
**Archivos problemáticos**:
"""
    
    for case in confusion_patterns['dent_broken_glass'][:5]:
        report += f"- {case['file']} ({case['split']}) - Clases: {', '.join(case['classes'])}\n"
    
    report += f"""

### 3. Casos Ambiguos (Multi-clase)
**Casos detectados**: {len(confusion_patterns['ambiguous_cases'])}
**Problema potencial**: Imágenes con múltiples tipos de daño
**Distribución por split**:
"""
    
    # Contar por split
    split_counts = defaultdict(int)
    for case in confusion_patterns['ambiguous_cases']:
        split_counts[case['split']] += 1
    
    for split, count in split_counts.items():
        report += f"- {split}: {count} casos\n"
    
    report += f"""

## Recomendaciones Específicas

### Problemas Críticos Identificados:
"""
    
    if len(confusion_patterns['scratch_broken_glass']) > 0:
        report += f"""
1. **Rayones en Vidrio vs Vidrio Roto** ({len(confusion_patterns['scratch_broken_glass'])} casos)
   - Crear subcategorías más específicas
   - Mejorar guidelines de etiquetado para distinguir:
     * Rayones superficiales en vidrio (scratch_on_glass)
     * Fracturas estructurales (broken_glass)
   - Revisar manualmente los casos identificados
"""
    
    if len(confusion_patterns['dent_broken_glass']) > 0:
        report += f"""
2. **Abolladuras cerca de Ventanas** ({len(confusion_patterns['dent_broken_glass'])} casos)
   - Separar claramente daños en carrocería vs vidrio
   - Establecer prioridad: si hay vidrio roto, etiquetar como broken_glass
   - Considerar etiquetado múltiple para casos complejos
"""
    
    if len(confusion_patterns['ambiguous_cases']) > 5:
        report += f"""
3. **Casos Multi-daño** ({len(confusion_patterns['ambiguous_cases'])} casos)
   - Revisar estrategia de etiquetado múltiple
   - Considerar jerarquía de daños por severidad
   - Posible división en imágenes separadas
"""
    
    report += f"""

### Acciones Inmediatas:
1. **Auditoría Manual**: Revisar los {sum([len(p) for p in confusion_patterns.values()])} casos identificados
2. **Re-etiquetado**: Aplicar guidelines más estrictos
3. **Augmentación Dirigida**: Generar más ejemplos claros de cada clase
4. **Validación Cruzada**: Doble verificación de casos ambiguos

### Métricas de Seguimiento:
- Casos ambiguos objetivo: <5% del dataset
- Claridad de etiquetado: >95%
- Consistencia inter-anotador: >90%
"""
    
    # Guardar reporte
    report_path = os.path.join(output_dir, 'confusion_prediction_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte predictivo guardado: {report_path}")
    print("\n" + "="*60)
    print(report)
    
    return report

def main():
    """Función principal para análisis predictivo de confusión"""
    
    print("🔍 ANÁLISIS PREDICTIVO DE CONFUSIÓN (Sin modelo)")
    print("="*60)
    
    # Solicitar dataset
    dataset_path = input("📁 Ruta del dataset: ").strip()
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset no encontrado: {dataset_path}")
        return
    
    # Crear directorio de salida
    output_dir = 'confusion_prediction_results'
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Análisis predictivo
        confusion_patterns, cooccurrence_matrix = create_confusion_prediction_analysis(
            dataset_path, output_dir
        )
        
        # Cargar configuración para obtener class_mapping
        config, _ = load_dataset_config(dataset_path)
        class_mapping = {i: name for i, name in enumerate(config.get('names', []))}
        
        # Generar reporte
        report = generate_prediction_report(confusion_patterns, class_mapping, output_dir)
        
        print(f"\n✅ Análisis predictivo completado!")
        print(f"📁 Resultados guardados en: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()