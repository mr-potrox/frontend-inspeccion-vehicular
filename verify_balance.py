import os
import yaml
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
from pathlib import Path


def select_dataset_folder():
    """Selector manual de carpeta del dataset (sin tkinter)"""
    print("📁 SELECTOR DE DATASET")
    print("="*50)
    
    # Mostrar directorio actual
    current_dir = os.getcwd()
    print(f"📍 Directorio actual: {current_dir}")
    
    # Buscar datasets automáticamente
    print("\n🔍 Buscando datasets en ubicaciones comunes...")
    
    search_paths = [
        "./datasets",
        "../datasets",
        "./dataset_damage",
        "./dataset_parts",
        "./dataset_balanced",
        os.path.expanduser("~/Documents/proyecto_tfm/inspector-vehicular/datasets"),
        os.path.expanduser("~/Downloads")
    ]
    
    found_datasets = []
    
    for search_path in search_paths:
        if os.path.exists(search_path):
            try:
                for item in os.listdir(search_path):
                    item_path = os.path.join(search_path, item)
                    if os.path.isdir(item_path):
                        # Buscar data.yaml
                        data_yaml = os.path.join(item_path, 'data.yaml')
                        if os.path.exists(data_yaml):
                            found_datasets.append({
                                'name': item,
                                'path': os.path.abspath(item_path)
                            })
            except PermissionError:
                continue
    
    # Mostrar datasets encontrados
    if found_datasets:
        print(f"\n📋 Datasets encontrados automáticamente:")
        for i, dataset in enumerate(found_datasets, 1):
            print(f"  {i}. {dataset['name']}")
            print(f"     📁 {dataset['path']}")
        
        print(f"  {len(found_datasets)+1}. Ingresar ruta manualmente")
        print("  0. Salir")
        
        while True:
            try:
                choice = input(f"\n➤ Seleccione dataset (0-{len(found_datasets)+1}): ").strip()
                
                if choice == "0":
                    print("👋 Saliendo...")
                    return None
                elif choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(found_datasets):
                        selected = found_datasets[choice_num-1]
                        print(f"✅ Dataset seleccionado: {selected['name']}")
                        return selected['path']
                    elif choice_num == len(found_datasets)+1:
                        break  # Ir a entrada manual
                
                print("❌ Opción inválida. Intente de nuevo.")
                
            except (ValueError, KeyboardInterrupt):
                print("\n👋 Cancelado")
                return None
    else:
        print("❌ No se encontraron datasets automáticamente")
    
    # Entrada manual
    print(f"\n✏️ ENTRADA MANUAL DE RUTA:")
    print(f"💡 Ejemplos de rutas válidas:")
    print(f"   ./datasets/mi_dataset")
    print(f"   /Users/jhonattandiazuribe/Documents/proyecto_tfm/mi_dataset")
    print(f"   ~/Downloads/dataset_damage")
    
    while True:
        try:
            dataset_path = input("\n📁 Ingrese la ruta del dataset (o 'q' para salir): ").strip()
            
            if dataset_path.lower() in ['q', 'quit', 'exit']:
                print("👋 Saliendo...")
                return None
            
            if not dataset_path:
                print("❌ Debe ingresar una ruta")
                continue
            
            # Expandir ruta
            dataset_path = os.path.expanduser(dataset_path)
            dataset_path = os.path.abspath(dataset_path)
            
            if os.path.exists(dataset_path):
                # Verificar estructura básica
                data_yaml = os.path.join(dataset_path, 'data.yaml')
                if os.path.exists(data_yaml):
                    print(f"✅ Dataset válido encontrado: {dataset_path}")
                    return dataset_path
                else:
                    print(f"⚠️ No se encontró 'data.yaml' en: {dataset_path}")
                    print("📁 Contenido del directorio:")
                    try:
                        items = os.listdir(dataset_path)[:10]  # Mostrar solo primeros 10
                        for item in items:
                            print(f"   - {item}")
                        if len(os.listdir(dataset_path)) > 10:
                            print(f"   ... y {len(os.listdir(dataset_path)) - 10} más")
                    except:
                        pass
                    
                    continue_anyway = input("¿Continuar de todas formas? (y/n): ").lower()
                    if continue_anyway in ['y', 'yes', 'sí', 's']:
                        return dataset_path
            else:
                print(f"❌ Ruta no encontrada: {dataset_path}")
                
        except KeyboardInterrupt:
            print("\n👋 Cancelado")
            return None

def load_dataset_config(data_yaml_path):
    """Cargar configuración del dataset desde data.yaml"""
    with open(data_yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def count_class_instances(labels_dir, class_names):
    """Contar instancias de cada clase en un directorio de etiquetas"""
    class_counts = Counter()
    total_instances = 0
    
    if not os.path.exists(labels_dir):
        print(f"⚠️ Directorio no encontrado: {labels_dir}")
        return class_counts, total_instances
    
    # Contar instancias en archivos .txt
    for label_file in os.listdir(labels_dir):
        if label_file.endswith('.txt'):
            label_path = os.path.join(labels_dir, label_file)
            with open(label_path, 'r') as f:
                for line in f:
                    try:
                        parts = line.strip().split()
                        if len(parts) >= 5:  # Formato YOLO: class x y w h
                            class_id = int(parts[0])
                            if 0 <= class_id < len(class_names):
                                class_counts[class_id] += 1
                                total_instances += 1
                    except (ValueError, IndexError):
                        continue
    
    return class_counts, total_instances

def analyze_dataset_balance(dataset_path):
    """Análisis completo del balance del dataset"""
    
    # Buscar data.yaml
    data_yaml_path = None
    for root, dirs, files in os.walk(dataset_path):
        if 'data.yaml' in files:
            data_yaml_path = os.path.join(root, 'data.yaml')
            break
    
    if not data_yaml_path:
        raise FileNotFoundError(f"No se encontró data.yaml en {dataset_path}")
    
    print(f"📋 Archivo data.yaml encontrado: {data_yaml_path}")
    
    # Cargar configuración
    config = load_dataset_config(data_yaml_path)
    class_names = config.get('names', [])
    num_classes = len(class_names)
    
    print(f"🎯 Dataset: {num_classes} clases")
    print(f"📝 Clases: {class_names}")
    
    # Analizar cada split
    splits_data = {}
    dataset_root = os.path.dirname(data_yaml_path)
    
    for split in ['train', 'val', 'test']:
        if split in config:
            # Obtener directorio de etiquetas
            images_dir = config[split]
            if not os.path.isabs(images_dir):
                images_dir = os.path.join(dataset_root, images_dir)
            
            labels_dir = images_dir.replace('images', 'labels')
            
            print(f"\n📁 Analizando split: {split}")
            print(f"   Imágenes: {images_dir}")
            print(f"   Etiquetas: {labels_dir}")
            
            # Contar instancias
            class_counts, total_instances = count_class_instances(labels_dir, class_names)
            
            # Guardar datos
            splits_data[split] = {
                'class_counts': class_counts,
                'total_instances': total_instances,
                'images_dir': images_dir,
                'labels_dir': labels_dir
            }
            
            print(f"   Total instancias: {total_instances}")
    
    return splits_data, class_names, config

def calculate_balance_metrics(splits_data, class_names):
    """Calcular métricas de balance"""
    train_data = splits_data.get('train', {})
    train_counts = train_data.get('class_counts', Counter())
    
    if not train_counts:
        print("❌ No se encontraron datos de entrenamiento")
        return None
    
    # Crear lista de conteos por clase
    counts = [train_counts.get(i, 0) for i in range(len(class_names))]
    
    if sum(counts) == 0:
        print("❌ No se encontraron instancias en el dataset")
        return None
    
    # Calcular métricas
    metrics = {
        'total_instances': sum(counts),
        'mean': np.mean(counts),
        'median': np.median(counts),
        'std': np.std(counts),
        'min': np.min(counts),
        'max': np.max(counts),
        'cv': np.std(counts) / np.mean(counts) if np.mean(counts) > 0 else 0,
        'counts': counts
    }
    
    return metrics

def create_balance_visualization(splits_data, class_names, output_dir='.'):
    """Crear visualizaciones del balance del dataset"""
    
    # Preparar datos para visualización
    viz_data = []
    for split, data in splits_data.items():
        class_counts = data['class_counts']
        for i, class_name in enumerate(class_names):
            count = class_counts.get(i, 0)
            percentage = (count / data['total_instances'] * 100) if data['total_instances'] > 0 else 0
            viz_data.append({
                'Split': split,
                'Clase': class_name,
                'Clase_ID': i,
                'Cantidad': count,
                'Porcentaje': percentage
            })
    
    df = pd.DataFrame(viz_data)
    
    # Crear figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Distribución por clase en train
    train_df = df[df['Split'] == 'train']
    if not train_df.empty:
        axes[0,0].bar(train_df['Clase'], train_df['Cantidad'], color='skyblue')
        axes[0,0].set_title('Distribución de Clases - Train Set', fontsize=14, fontweight='bold')
        axes[0,0].set_xlabel('Clases')
        axes[0,0].set_ylabel('Cantidad de Instancias')
        axes[0,0].tick_params(axis='x', rotation=45)
    
    # 2. Comparación entre splits
    if not df.empty:
        pivot_df = df.pivot(index='Clase', columns='Split', values='Cantidad').fillna(0)
        pivot_df.plot(kind='bar', ax=axes[0,1], color=['#ff7f0e', '#2ca02c', '#d62728'])
        axes[0,1].set_title('Comparación entre Splits', fontsize=14, fontweight='bold')
        axes[0,1].set_xlabel('Clases')
        axes[0,1].set_ylabel('Cantidad de Instancias')
        axes[0,1].tick_params(axis='x', rotation=45)
        axes[0,1].legend(title='Split')
    
    # 3. Histograma de balance
    train_counts = train_df['Cantidad'].values
    if len(train_counts) > 0:
        axes[1,0].hist(train_counts, bins=max(5, len(train_counts)//2), 
                      alpha=0.7, color='lightcoral', edgecolor='black')
        axes[1,0].axvline(np.mean(train_counts), color='red', linestyle='--', 
                         linewidth=2, label=f'Media: {np.mean(train_counts):.0f}')
        axes[1,0].set_title('Histograma de Balance - Train Set', fontsize=14, fontweight='bold')
        axes[1,0].set_xlabel('Cantidad de Instancias por Clase')
        axes[1,0].set_ylabel('Número de Clases')
        axes[1,0].legend()
    
    # 4. Estadísticas de balance
    if len(train_counts) > 0:
        metrics = calculate_balance_metrics(splits_data, class_names)
        if metrics:
            stats_text = f"""Estadísticas de Balance:
            
Total Instancias: {metrics['total_instances']:,}
Media: {metrics['mean']:.1f}
Mediana: {metrics['median']:.1f}
Desv. Estándar: {metrics['std']:.1f}
Mínimo: {metrics['min']:.0f}
Máximo: {metrics['max']:.0f}
Coef. Variación: {metrics['cv']:.3f}

Evaluación del Balance:"""
            
            # Evaluación del balance
            cv = metrics['cv']
            if cv <= 0.3:
                balance_status = "✅ EXCELENTE\n(CV ≤ 0.3)"
                color = 'lightgreen'
            elif cv <= 0.5:
                balance_status = "🟡 BUENO\n(0.3 < CV ≤ 0.5)"
                color = 'lightyellow'
            elif cv <= 0.8:
                balance_status = "🟠 REGULAR\n(0.5 < CV ≤ 0.8)"
                color = 'orange'
            else:
                balance_status = "🔴 DESBALANCEADO\n(CV > 0.8)"
                color = 'lightcoral'
            
            stats_text += f"\n{balance_status}"
            
            axes[1,1].text(0.05, 0.95, stats_text, transform=axes[1,1].transAxes, 
                          fontsize=11, verticalalignment='top',
                          bbox=dict(boxstyle="round,pad=0.5", facecolor=color, alpha=0.8))
            axes[1,1].set_title('Métricas de Balance', fontsize=14, fontweight='bold')
            axes[1,1].axis('off')
    
    plt.tight_layout()
    
    # Guardar visualización
    output_path = os.path.join(output_dir, 'dataset_balance_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"📊 Visualización guardada en: {output_path}")
    plt.show()
    
    return df

def generate_balance_report(splits_data, class_names, output_dir='.'):
    """Generar reporte detallado del balance"""
    
    metrics = calculate_balance_metrics(splits_data, class_names)
    if not metrics:
        return
    
    report = f"""
# REPORTE DE BALANCE DEL DATASET
=====================================

## Información General
- Total de clases: {len(class_names)}
- Total de instancias (train): {metrics['total_instances']:,}

## Clases del Dataset
{', '.join(class_names)}

## Métricas de Balance (Train Set)
- Media de instancias por clase: {metrics['mean']:.1f}
- Mediana: {metrics['median']:.1f}
- Desviación estándar: {metrics['std']:.1f}
- Rango: {metrics['min']:.0f} - {metrics['max']:.0f}
- Coeficiente de Variación: {metrics['cv']:.3f}

## Distribución por Clase (Train Set)
"""
    
    # Agregar conteo por clase
    for i, class_name in enumerate(class_names):
        count = metrics['counts'][i]
        percentage = (count / metrics['total_instances'] * 100) if metrics['total_instances'] > 0 else 0
        report += f"- {class_name}: {count:,} instancias ({percentage:.1f}%)\n"
    
    # Evaluación del balance
    cv = metrics['cv']
    report += f"\n## Evaluación del Balance\n"
    
    if cv <= 0.3:
        report += "✅ **EXCELENTE BALANCE** (CV ≤ 0.3)\n"
        report += "- Dataset bien balanceado, adecuado para entrenamiento.\n"
    elif cv <= 0.5:
        report += "🟡 **BUEN BALANCE** (0.3 < CV ≤ 0.5)\n"
        report += "- Balance aceptable, puede proceder con el entrenamiento.\n"
    elif cv <= 0.8:
        report += "🟠 **BALANCE REGULAR** (0.5 < CV ≤ 0.8)\n"
        report += "- Se recomienda aplicar técnicas de balanceo.\n"
    else:
        report += "🔴 **DATASET DESBALANCEADO** (CV > 0.8)\n"
        report += "- Es necesario balancear el dataset antes del entrenamiento.\n"
        report += "- Considere oversampling, undersampling o augmentación dirigida.\n"
    
    # Recomendaciones
    report += f"\n## Recomendaciones\n"
    
    # Identificar clases con pocas instancias
    low_count_classes = [(i, class_names[i], metrics['counts'][i]) 
                        for i in range(len(class_names)) 
                        if metrics['counts'][i] < metrics['mean'] * 0.5]
    
    if low_count_classes:
        report += f"### Clases con pocas instancias (< 50% de la media):\n"
        for _, class_name, count in low_count_classes:
            report += f"- {class_name}: {count} instancias\n"
        report += f"→ Considere aumentar datos para estas clases.\n\n"
    
    # Identificar clases dominantes
    high_count_classes = [(i, class_names[i], metrics['counts'][i]) 
                         for i in range(len(class_names)) 
                         if metrics['counts'][i] > metrics['mean'] * 2]
    
    if high_count_classes:
        report += f"### Clases dominantes (> 200% de la media):\n"
        for _, class_name, count in high_count_classes:
            report += f"- {class_name}: {count} instancias\n"
        report += f"→ Considere submuestreo para estas clases.\n\n"
    
    # Guardar reporte
    report_path = os.path.join(output_dir, 'balance_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte guardado en: {report_path}")
    print("\n" + "="*50)
    print(report)
    
    return metrics

def main():
    """Función principal para verificar balance del dataset"""
    
    print("🔍 VERIFICADOR DE BALANCE DE DATASET")
    print("="*50)
    
    # Selector de dataset
    DATASET_PATH = select_dataset_folder()
    
    if not DATASET_PATH:
        print("👋 Saliendo...")
        return
    
    print(f"\n🔍 Verificando balance del dataset en: {DATASET_PATH}")
    
    try:
        # Análisis del dataset
        splits_data, class_names, config = analyze_dataset_balance(DATASET_PATH)
        
        # Crear visualizaciones
        df = create_balance_visualization(splits_data, class_names, DATASET_PATH)
        
        # Generar reporte
        metrics = generate_balance_report(splits_data, class_names, DATASET_PATH)
        
        # Resumen final
        if metrics:
            cv = metrics['cv']
            print(f"\n🎯 RESUMEN FINAL:")
            print(f"   Coeficiente de Variación: {cv:.3f}")
            
            if cv <= 0.3:
                print(f"   ✅ Dataset EXCELENTE para entrenamiento")
            elif cv <= 0.5:
                print(f"   🟡 Dataset BUENO para entrenamiento")
            elif cv <= 0.8:
                print(f"   🟠 Dataset REGULAR - se recomienda balanceo")
            else:
                print(f"   🔴 Dataset DESBALANCEADO - requiere balanceo")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()