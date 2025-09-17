#!/bin/bash

# Script para reorganizar archivos del repositorio Inspector Vehicular
# Mueve archivos de investigación fuera del repositorio git

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/../.."  # Ir al directorio raíz del proyecto

echo "🚗 REORGANIZACIÓN DEL REPOSITORIO INSPECTOR VEHICULAR"
echo "===================================================="

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Este script debe ejecutarse desde la carpeta inspector-vehicular/"
    exit 1
fi

# Crear estructura de investigación
RESEARCH_DIR="../proyecto_tfm_research"
echo "📁 Creando estructura de investigación en: $RESEARCH_DIR"

mkdir -p "$RESEARCH_DIR"/{datasets,models,notebooks,analysis_scripts,results,configs}

echo "✅ Estructura creada:"
echo "   📊 $RESEARCH_DIR/datasets/"
echo "   🤖 $RESEARCH_DIR/models/"
echo "   📓 $RESEARCH_DIR/notebooks/"
echo "   🔧 $RESEARCH_DIR/analysis_scripts/"
echo "   📈 $RESEARCH_DIR/results/"
echo "   ⚙️  $RESEARCH_DIR/configs/"

# Función para mover archivo/carpeta si existe
move_if_exists() {
    local source="$1"
    local dest="$2"
    
    if [ -e "$source" ]; then
        echo "📦 Moviendo: $source → $dest"
        mv "$source" "$dest"
    else
        echo "⚠️  No encontrado: $source (saltando)"
    fi
}

echo ""
echo "🔄 Moviendo archivos de investigación..."

# Mover datasets
echo ""
echo "📊 DATASETS:"
move_if_exists "dataset_maestro_danos.zip" "$RESEARCH_DIR/datasets/"
move_if_exists "car_parts_dataset.zip" "$RESEARCH_DIR/datasets/"

# Mover modelos antiguos (preservar backend/models/)
echo ""
echo "🤖 MODELOS:"
if [ -d "modelos" ]; then
    echo "📦 Moviendo: modelos/ → $RESEARCH_DIR/models/old_models/"
    mkdir -p "$RESEARCH_DIR/models/old_models"
    mv modelos/* "$RESEARCH_DIR/models/old_models/" 2>/dev/null || true
    rmdir modelos 2>/dev/null || true
fi

# Mover notebooks
echo ""
echo "📓 NOTEBOOKS:"
move_if_exists "training_notebooks" "$RESEARCH_DIR/notebooks/"

# Mover scripts de análisis
echo ""
echo "🔧 SCRIPTS DE ANÁLISIS:"
move_if_exists "analyze_confusion.py" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "balance_dataset.py" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "clean_multiclass_dataset.py" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "consolidate_datasets.py" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "evaluate_model_readiness.py" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "verify_balance.py" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "create-structure.sh" "$RESEARCH_DIR/analysis_scripts/"
move_if_exists "setup-configs.sh" "$RESEARCH_DIR/analysis_scripts/"

# Mover resultados
echo ""
echo "📈 RESULTADOS:"
move_if_exists "cleaning_results" "$RESEARCH_DIR/results/"
move_if_exists "confusion_prediction_results_run_1" "$RESEARCH_DIR/results/"
move_if_exists "confusion_env" "$RESEARCH_DIR/results/"

# Mover configuraciones
echo ""
echo "⚙️  CONFIGURACIONES:"
move_if_exists "hyp_tuned_train_parts_detector.yaml" "$RESEARCH_DIR/configs/"

# Crear README en la carpeta de investigación
echo ""
echo "📝 Creando documentación de investigación..."

cat > "$RESEARCH_DIR/README.md" << 'EOF'
# TFM - Archivos de Investigación

Esta carpeta contiene todos los archivos relacionados con la investigación y desarrollo del TFM Inspector Vehicular que no forman parte del código de la aplicación.

## 📁 Estructura

### 📊 `datasets/`
- Datasets originales y procesados
- Archivos .zip con imágenes de entrenamiento
- Datos de validación y testing

### 🤖 `models/`
- Modelos pre-entrenados y experimentales
- Checkpoints de entrenamiento
- Modelos ONNX y otros formatos

### 📓 `notebooks/`
- Jupyter notebooks de entrenamiento
- Análisis exploratorio de datos
- Experimentos y pruebas

### 🔧 `analysis_scripts/`
- Scripts de procesamiento de datasets
- Herramientas de análisis de balance
- Scripts de consolidación y limpieza

### 📈 `results/`
- Resultados de experimentos
- Análisis de confusión
- Métricas de rendimiento
- Visualizaciones

### ⚙️ `configs/`
- Configuraciones de hiperparámetros
- Archivos YAML de entrenamiento
- Configuraciones experimentales

## 🔄 Relación con el Repositorio Principal

El repositorio `inspector-vehicular/` contiene únicamente:
- Código del backend (FastAPI)
- Código del frontend (React)
- Modelos finales para producción
- Documentación de usuario
- Scripts de despliegue

Esta separación permite:
- ✅ Repositorio limpio y enfocado en la aplicación
- ✅ Clones rápidos sin archivos grandes
- ✅ Mejor colaboración en el desarrollo
- ✅ Organización clara entre investigación y producción

## 📝 Notas

- Los modelos finales están en `inspector-vehicular/backend/models/`
- Los scripts de análisis se ejecutan desde esta carpeta
- Los datasets no se incluyen en el repositorio por su tamaño
EOF

# Limpiar archivos temporales
echo ""
echo "🧹 Limpiando archivos temporales..."

# Remover .DS_Store
find . -name ".DS_Store" -delete 2>/dev/null || true

# Verificar estado del repositorio
echo ""
echo "✅ REORGANIZACIÓN COMPLETADA"
echo "=============================="

echo ""
echo "📂 ESTRUCTURA DEL REPOSITORIO (limpia):"
echo "inspector-vehicular/"
ls -la | grep -E '^d' | grep -v '.git' | while read -r line; do
    echo "  $(echo "$line" | awk '{print $NF}')"
done

echo ""
echo "📂 ARCHIVOS DE INVESTIGACIÓN MOVIDOS A:"
echo "$RESEARCH_DIR"
ls -la "$RESEARCH_DIR" 2>/dev/null | grep -E '^d' | while read -r line; do
    echo "  $(echo "$line" | awk '{print $NF}')"
done

echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo "1. Revisar que el sistema siga funcionando:"
echo "   ./start_system.sh"
echo ""
echo "2. Hacer commit de los cambios:"
echo "   git add ."
echo "   git commit -m 'Reorganizar repositorio: mover archivos de investigación'"
echo ""
echo "3. Los archivos de investigación están en:"
echo "   $RESEARCH_DIR"

echo ""
echo "✅ ¡Repositorio reorganizado exitosamente!"
