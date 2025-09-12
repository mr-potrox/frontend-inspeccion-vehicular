import pandas as pd
import matplotlib.pyplot as plt
import os
import json
import numpy as np

def analyze_training_results(results_dir):
    """Analizar resultados de entrenamiento sin dependencias complejas"""
    
    print("📊 ANÁLISIS DIRECTO DE RESULTADOS")
    print("="*50)
    
    # Buscar archivos relevantes
    results_csv = None
    model_files = []
    
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file == 'results.csv':
                results_csv = file_path
                print(f"✅ Encontrado: results.csv")
            elif file.endswith('.pt'):
                model_files.append(file_path)
                print(f"✅ Encontrado: {file}")
            elif file.endswith(('.png', '.jpg')) and any(word in file.lower() for word in ['confusion', 'results', 'matrix']):
                print(f"✅ Encontrado: {file}")
    
    if not results_csv:
        print("❌ No se encontró results.csv")
        print("💡 Busca manualmente el archivo y proporciona la ruta")
        return None
    
    # Cargar y analizar CSV
    try:
        df = pd.read_csv(results_csv)
        print(f"✅ CSV cargado: {len(df)} épocas")
        
        # Extraer métricas clave
        metrics = extract_key_metrics(df)
        
        # Evaluación para TFM
        evaluation = evaluate_for_tfm(metrics)
        
        # Crear visualización
        create_quick_visualization(df, results_dir)
        
        # Generar reporte
        generate_evaluation_report(metrics, evaluation, results_dir)
        
        return metrics, evaluation
        
    except Exception as e:
        print(f"❌ Error procesando CSV: {e}")
        return None

def extract_key_metrics(df):
    """Extraer métricas clave del DataFrame"""
    
    # Columnas esperadas en results.csv de YOLO
    metric_columns = {
        'map50': ['metrics/mAP50(B)', 'mAP50', 'map50'],
        'map50_95': ['metrics/mAP50-95(B)', 'mAP50-95', 'map50_95'],
        'precision': ['metrics/precision(B)', 'precision'],
        'recall': ['metrics/recall(B)', 'recall'],
        'val_loss': ['val/box_loss', 'val_loss'],
        'train_loss': ['train/box_loss', 'train_loss']
    }
    
    metrics = {}
    
    for metric_name, possible_cols in metric_columns.items():
        for col in possible_cols:
            if col in df.columns:
                if 'loss' in metric_name:
                    metrics[metric_name] = df[col].iloc[-1]  # Último valor para loss
                else:
                    metrics[metric_name] = df[col].max()  # Mejor valor para métricas
                break
    
    # Información adicional
    metrics.update({
        'total_epochs': len(df),
        'converged': check_convergence(df),
        'overfitting': check_overfitting(df)
    })
    
    return metrics

def check_convergence(df):
    """Verificar si el modelo convergió"""
    if 'val/box_loss' in df.columns:
        last_10_epochs = df['val/box_loss'].tail(10)
        std_last_epochs = last_10_epochs.std()
        return std_last_epochs < 0.01  # Convergió si la desviación es pequeña
    return None

def check_overfitting(df):
    """Detectar signos de overfitting"""
    if 'train/box_loss' in df.columns and 'val/box_loss' in df.columns:
        final_train_loss = df['train/box_loss'].iloc[-1]
        final_val_loss = df['val/box_loss'].iloc[-1]
        gap = final_val_loss - final_train_loss
        return gap > 0.05  # Overfitting si la diferencia es grande
    return None

def evaluate_for_tfm(metrics):
    """Evaluación específica para TFM"""
    
    print(f"\n📊 MÉTRICAS EXTRAÍDAS:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Criterios de evaluación
    evaluation = {
        'overall_score': 0,
        'recommendations': [],
        'status': 'UNKNOWN'
    }
    
    # Evaluar mAP@0.5
    map50 = metrics.get('map50', 0)
    if map50 >= 0.85:
        evaluation['map50_status'] = 'EXCELENTE'
        evaluation['overall_score'] += 3
    elif map50 >= 0.75:
        evaluation['map50_status'] = 'BUENO'
        evaluation['overall_score'] += 2
    elif map50 >= 0.65:
        evaluation['map50_status'] = 'ACCEPTABLE'
        evaluation['overall_score'] += 1
    else:
        evaluation['map50_status'] = 'INSUFICIENTE'
        evaluation['overall_score'] += 0
    
    # Evaluar precisión
    precision = metrics.get('precision', 0)
    if precision >= 0.85:
        evaluation['precision_status'] = 'EXCELENTE'
        evaluation['overall_score'] += 2
    elif precision >= 0.75:
        evaluation['precision_status'] = 'BUENO'
        evaluation['overall_score'] += 1
    else:
        evaluation['precision_status'] = 'NECESITA MEJORA'
        evaluation['overall_score'] += 0
    
    # Evaluar recall
    recall = metrics.get('recall', 0)
    if recall >= 0.80:
        evaluation['recall_status'] = 'EXCELENTE'
        evaluation['overall_score'] += 2
    elif recall >= 0.70:
        evaluation['recall_status'] = 'BUENO'
        evaluation['overall_score'] += 1
    else:
        evaluation['recall_status'] = 'NECESITA MEJORA'
        evaluation['overall_score'] += 0
    
    # Evaluación final
    max_score = 7  # 3 + 2 + 2
    score_percentage = evaluation['overall_score'] / max_score
    
    if score_percentage >= 0.8:
        evaluation['status'] = 'LISTO_PARA_TFM'
        evaluation['recommendations'].append("✅ Modelo excelente para TFM")
        evaluation['recommendations'].append("🚀 Proceder con desarrollo de aplicación")
    elif score_percentage >= 0.6:
        evaluation['status'] = 'ACCEPTABLE_PARA_TFM'
        evaluation['recommendations'].append("⚠️ Modelo acceptable para TFM")
        evaluation['recommendations'].append("💡 Mejoras opcionales si tienes tiempo")
    else:
        evaluation['status'] = 'NECESITA_MEJORA'
        evaluation['recommendations'].append("🔴 Modelo necesita mejora")
        evaluation['recommendations'].append("🛠️ Re-entrenamiento recomendado")
    
    # Recomendaciones específicas
    if metrics.get('overfitting', False):
        evaluation['recommendations'].append("⚠️ Detectado overfitting - Reducir complejidad")
    
    if not metrics.get('converged', True):
        evaluation['recommendations'].append("📈 Modelo no convergió - Aumentar épocas")
    
    if map50 < 0.8:
        evaluation['recommendations'].append("📊 Aumentar dataset o mejorar calidad de etiquetas")
    
    return evaluation

def create_quick_visualization(df, output_dir):
    """Crear visualización rápida de métricas"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('ANÁLISIS DE ENTRENAMIENTO - INSPECTOR VEHICULAR', fontsize=14, fontweight='bold')
    
    epochs = range(1, len(df) + 1)
    
    # 1. mAP Evolution
    if 'metrics/mAP50(B)' in df.columns:
        axes[0,0].plot(epochs, df['metrics/mAP50(B)'], 'b-', linewidth=2, label='mAP@0.5')
        if 'metrics/mAP50-95(B)' in df.columns:
            axes[0,0].plot(epochs, df['metrics/mAP50-95(B)'], 'r-', linewidth=2, label='mAP@0.5-0.95')
        axes[0,0].set_title('Evolución del mAP', fontweight='bold')
        axes[0,0].set_xlabel('Época')
        axes[0,0].set_ylabel('mAP')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
    
    # 2. Precision/Recall
    if 'metrics/precision(B)' in df.columns and 'metrics/recall(B)' in df.columns:
        axes[0,1].plot(epochs, df['metrics/precision(B)'], 'g-', linewidth=2, label='Precision')
        axes[0,1].plot(epochs, df['metrics/recall(B)'], 'orange', linewidth=2, label='Recall')
        axes[0,1].set_title('Precision vs Recall', fontweight='bold')
        axes[0,1].set_xlabel('Época')
        axes[0,1].set_ylabel('Score')
        axes[0,1].legend()
        axes[0,1].grid(True, alpha=0.3)
    
    # 3. Losses
    if 'train/box_loss' in df.columns and 'val/box_loss' in df.columns:
        axes[1,0].plot(epochs, df['train/box_loss'], 'purple', linewidth=2, label='Train Loss')
        axes[1,0].plot(epochs, df['val/box_loss'], 'red', linewidth=2, label='Val Loss')
        axes[1,0].set_title('Evolución de Pérdidas', fontweight='bold')
        axes[1,0].set_xlabel('Época')
        axes[1,0].set_ylabel('Loss')
        axes[1,0].legend()
        axes[1,0].grid(True, alpha=0.3)
    
    # 4. Métricas finales
    final_metrics = {}
    if 'metrics/mAP50(B)' in df.columns:
        final_metrics['mAP@0.5'] = df['metrics/mAP50(B)'].max()
    if 'metrics/precision(B)' in df.columns:
        final_metrics['Precision'] = df['metrics/precision(B)'].max()
    if 'metrics/recall(B)' in df.columns:
        final_metrics['Recall'] = df['metrics/recall(B)'].max()
    
    if final_metrics:
        metrics_names = list(final_metrics.keys())
        metrics_values = list(final_metrics.values())
        
        colors = ['skyblue', 'lightgreen', 'lightcoral']
        bars = axes[1,1].bar(metrics_names, metrics_values, color=colors[:len(metrics_names)])
        axes[1,1].set_title('Mejores Métricas Obtenidas', fontweight='bold')
        axes[1,1].set_ylabel('Score')
        axes[1,1].set_ylim(0, 1)
        
        # Agregar valores en barras
        for bar, value in zip(bars, metrics_values):
            axes[1,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                          f'{value:.3f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Guardar
    viz_path = os.path.join(output_dir, 'training_analysis.png')
    plt.savefig(viz_path, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Visualización guardada: {viz_path}")

def generate_evaluation_report(metrics, evaluation, output_dir):
    """Generar reporte de evaluación"""
    
    report = f"""
# EVALUACIÓN DEL MODELO PARA TFM
==============================

## 📊 Métricas Obtenidas

### Performance Principal:
- **mAP@0.5**: {metrics.get('map50', 'N/A'):.3f} - {evaluation.get('map50_status', 'N/A')}
- **Precision**: {metrics.get('precision', 'N/A'):.3f} - {evaluation.get('precision_status', 'N/A')}
- **Recall**: {metrics.get('recall', 'N/A'):.3f} - {evaluation.get('recall_status', 'N/A')}

### Información de Entrenamiento:
- **Épocas totales**: {metrics.get('total_epochs', 'N/A')}
- **Convergencia**: {'✅ Sí' if metrics.get('converged') else '❌ No' if metrics.get('converged') is not None else '❓ Desconocido'}
- **Overfitting**: {'⚠️ Detectado' if metrics.get('overfitting') else '✅ No detectado' if metrics.get('overfitting') is not None else '❓ Desconocido'}

## 🎯 Evaluación para TFM

### Veredicto: **{evaluation['status'].replace('_', ' ')}**

### Score General: {evaluation['overall_score']}/7 ({evaluation['overall_score']/7*100:.1f}%)

## 💡 Recomendaciones:
"""
    
    for rec in evaluation['recommendations']:
        report += f"- {rec}\n"
    
    if evaluation['status'] == 'LISTO_PARA_TFM':
        report += f"""

## ✅ PRÓXIMOS PASOS:
1. **Documentar resultados** para memoria del TFM
2. **Desarrollar aplicación web** de detección de daños
3. **Preparar datasets de prueba** para demostración
4. **Crear interfaz de usuario** intuitiva

## 🎯 ENFOQUE PARA TFM:
- Presenta este como un **"Sistema Especializado en Detección de Daños"**
- Argumenta que es un **módulo crítico** de un sistema más amplio
- Demuestra **valor práctico** en peritaje vehicular
- Destaca la **alta precisión** lograda ({metrics.get('map50', 0):.1%})
"""
    
    elif evaluation['status'] == 'ACCEPTABLE_PARA_TFM':
        report += f"""

## ⚠️ DECISIÓN REQUERIDA:
1. **Usar modelo actual** - Justificar limitaciones en TFM
2. **Mejorar modelo** - 1-2 semanas adicionales de trabajo

## 🛠️ MEJORAS RÁPIDAS (Si decides optimizar):
- Entrenar 50 épocas adicionales con LR=0.0001
- Augmentación más agresiva
- Validación cruzada
"""
    
    else:
        report += f"""

## 🔴 MEJORAS OBLIGATORIAS:
1. **Re-entrenamiento** con parámetros optimizados
2. **Aumentar dataset** (mínimo +30% por clase)  
3. **Revisar calidad** de etiquetas
4. **Considerar modelo más grande** (YOLOv8m)

## ⏱️ Tiempo estimado: 2-3 semanas
"""
    
    # Guardar reporte
    report_path = os.path.join(output_dir, 'evaluation_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 Reporte guardado: {report_path}")
    print("\n" + "="*60)
    print(report)

def main():
    """Función principal"""
    
    print("📊 ANALIZADOR DE RESULTADOS SIN DEPENDENCIAS")
    print("="*60)
    
    results_dir = input("📁 Ruta del directorio con resultados: ").strip()
    
    if not os.path.exists(results_dir):
        print(f"❌ Directorio no encontrado: {results_dir}")
        return
    
    result = analyze_training_results(results_dir)
    
    if result:
        metrics, evaluation = result
        print(f"\n🎯 VEREDICTO FINAL: {evaluation['status'].replace('_', ' ')}")
        
        if evaluation['status'] == 'LISTO_PARA_TFM':
            print("✅ ¡Modelo listo para TFM! Procede con la aplicación web.")
        elif evaluation['status'] == 'ACCEPTABLE_PARA_TFM':
            print("⚠️ Modelo acceptable. Decide si mejorar o continuar.")
        else:
            print("🔴 Modelo necesita mejora antes de continuar.")

if __name__ == "__main__":
    main()