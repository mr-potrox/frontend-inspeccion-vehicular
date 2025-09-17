# 📁 ARCHIVOS Y CARPETAS PARA EXCLUIR DEL REPOSITORIO GIT

## 🎯 **Objetivo**
Identificar archivos y carpetas que NO están relacionados con el código del backend/frontend y deberían ser movidos fuera del repositorio para mantenerlo limpio y enfocado en el código de la aplicación.

---

## ❌ **CARPETAS PARA MOVER FUERA DEL REPOSITORIO**

### 📊 **Datasets y Datos de Entrenamiento**
```
❌ dataset_maestro_danos.zip           # Dataset comprimido (grande)
❌ car_parts_dataset.zip               # Dataset de partes (grande)
❌ confusion_env/                      # Entorno de análisis de confusión
❌ confusion_prediction_results_run_1/ # Resultados de predicción
❌ cleaning_results/                   # Resultados de limpieza de dataset
```

### 🤖 **Modelos de IA Pre-entrenados**
```
❌ modelos/                           # Carpeta con modelos .pt (grandes)
   ├── damage_yolo.pt                 # Modelo de daños (MB)
   ├── parts_yolo.pt                  # Modelo de partes (MB)
   ├── parts_detector/                # Subcarpeta de modelos
   └── content/                       # Contenido adicional
```

### 📓 **Notebooks de Entrenamiento**
```
❌ training_notebooks/                # Notebooks Jupyter de entrenamiento
   ├── Train_Damage_Detector.ipynb
   ├── Train_Damage_Detector_V2.ipynb
   ├── Train_Parts_Detector_V3.ipynb
   ├── Train_Parts_Detector_V4.ipynb
   └── Train_Parts_Detector_V4-1.ipynb
```

### 🔧 **Scripts de Análisis y Dataset**
```
❌ analyze_confusion.py               # Script de análisis de confusión
❌ balance_dataset.py                 # Script de balance de dataset
❌ clean_multiclass_dataset.py        # Script de limpieza multiclase
❌ consolidate_datasets.py            # Script de consolidación
❌ evaluate_model_readiness.py        # Script de evaluación
❌ verify_balance.py                  # Script de verificación de balance
❌ create-structure.sh                # Script de creación de estructura
❌ setup-configs.sh                   # Script de configuración
```

### 📄 **Archivos de Configuración de Entrenamiento**
```
❌ hyp_tuned_train_parts_detector.yaml # Configuración de hiperparámetros
```

---

## ✅ **CARPETAS QUE SÍ DEBEN QUEDARSE EN EL REPOSITORIO**

### 🔧 **Backend (Código de la aplicación)**
```
✅ backend/                           # API FastAPI
   ├── app/                           # Código de la aplicación
   ├── scripts/                       # Scripts de utilidad
   ├── models/                        # Modelos finales (damage_best.pt, parts_best.pt)
   ├── requirements.txt               # Dependencias
   ├── .env.example                   # Ejemplo de configuración
   ├── start_backend.sh               # Script de inicio
   ├── verify_setup.py                # Verificación
   └── README.md                      # Documentación
```

### 🎨 **Frontend (Código de la interfaz)**
```
✅ frontend/                          # Interfaz React
   ├── src/                           # Código fuente
   ├── public/                        # Archivos estáticos
   ├── package.json                   # Dependencias
   ├── .env.example                   # Ejemplo de configuración
   ├── start_frontend.sh              # Script de inicio
   └── README.md                      # Documentación
```

### 📚 **Documentación del Sistema**
```
✅ README.md                          # Documentación principal
✅ CONFIGURACION_COMPLETA.md          # Guía de configuración
✅ start_system.sh                    # Script de inicio del sistema
✅ .gitignore                         # Configuración git
```

---

## 🚀 **COMANDOS PARA REORGANIZAR**

### 1. Crear estructura fuera del repositorio
```bash
# Crear carpeta para archivos de investigación
mkdir -p ../proyecto_tfm_research
mkdir -p ../proyecto_tfm_research/datasets
mkdir -p ../proyecto_tfm_research/models
mkdir -p ../proyecto_tfm_research/notebooks
mkdir -p ../proyecto_tfm_research/analysis_scripts
mkdir -p ../proyecto_tfm_research/results
```

### 2. Mover datasets y archivos grandes
```bash
# Mover datasets
mv dataset_maestro_danos.zip ../proyecto_tfm_research/datasets/
mv car_parts_dataset.zip ../proyecto_tfm_research/datasets/

# Mover modelos antiguos (mantener solo los finales en backend/models/)
mv modelos/ ../proyecto_tfm_research/models/
```

### 3. Mover notebooks de entrenamiento
```bash
# Mover notebooks
mv training_notebooks/ ../proyecto_tfm_research/notebooks/
```

### 4. Mover scripts de análisis
```bash
# Mover scripts de análisis
mv analyze_confusion.py ../proyecto_tfm_research/analysis_scripts/
mv balance_dataset.py ../proyecto_tfm_research/analysis_scripts/
mv clean_multiclass_dataset.py ../proyecto_tfm_research/analysis_scripts/
mv consolidate_datasets.py ../proyecto_tfm_research/analysis_scripts/
mv evaluate_model_readiness.py ../proyecto_tfm_research/analysis_scripts/
mv verify_balance.py ../proyecto_tfm_research/analysis_scripts/
mv create-structure.sh ../proyecto_tfm_research/analysis_scripts/
mv setup-configs.sh ../proyecto_tfm_research/analysis_scripts/
```

### 5. Mover resultados de análisis
```bash
# Mover resultados
mv cleaning_results/ ../proyecto_tfm_research/results/
mv confusion_prediction_results_run_1/ ../proyecto_tfm_research/results/
mv confusion_env/ ../proyecto_tfm_research/results/
```

### 6. Mover configuraciones de entrenamiento
```bash
# Mover configuraciones
mv hyp_tuned_train_parts_detector.yaml ../proyecto_tfm_research/notebooks/
```

---

## 📝 **ACTUALIZAR .gitignore**

Añadir estas líneas al .gitignore:

```gitignore
# === ARCHIVOS DE INVESTIGACIÓN Y DESARROLLO ===

# Datasets (grandes)
*.zip
datasets/
data/

# Modelos de IA (grandes) - excepto los finales en backend/models/
*.pt
*.onnx
*.pkl
!backend/models/*.pt

# Notebooks de entrenamiento
*.ipynb
training_notebooks/

# Resultados de análisis
cleaning_results/
confusion_*/
analysis_results/
results/

# Scripts de preprocessing/análisis
analyze_*.py
balance_*.py
clean_*.py
consolidate_*.py
evaluate_*.py
verify_*.py
*-structure.sh
*-configs.sh

# Configuraciones de entrenamiento
*.yaml
!docker-compose.yml

# Archivos temporales
*.log
*.tmp
*.cache

# Entornos virtuales adicionales
*_env/
confusion_env/

# OS específicos
.DS_Store
Thumbs.db
```

---

## 🎯 **ESTRUCTURA FINAL LIMPIA**

Después de la reorganización, el repositorio quedará así:

```
inspector-vehicular/                   # 🔥 REPOSITORIO LIMPIO
├── backend/                           # ✅ Backend FastAPI
├── frontend/                          # ✅ Frontend React
├── README.md                          # ✅ Documentación principal
├── CONFIGURACION_COMPLETA.md          # ✅ Guía de setup
├── start_system.sh                    # ✅ Script de inicio
├── .gitignore                         # ✅ Configuración git mejorada
└── .git/                              # ✅ Control de versiones

../proyecto_tfm_research/              # 📚 ARCHIVOS DE INVESTIGACIÓN
├── datasets/                          # Datasets y archivos grandes
├── models/                            # Modelos pre-entrenados
├── notebooks/                         # Notebooks de entrenamiento
├── analysis_scripts/                  # Scripts de análisis
└── results/                           # Resultados de experimentos
```

---

## ✅ **BENEFICIOS DE ESTA REORGANIZACIÓN**

1. **📦 Repositorio Limpio**: Solo código de la aplicación
2. **⚡ Clones Rápidos**: Sin archivos grandes innecesarios
3. **🔍 Foco en el Código**: Mejor navegación y desarrollo
4. **📊 Investigación Organizada**: Archivos de research separados
5. **🚀 Deploy Simplificado**: Solo lo necesario para producción
6. **👥 Colaboración Mejorada**: Otros desarrolladores no necesitan datasets

---

## 🚨 **IMPORTANTE ANTES DE MOVER**

1. **Hacer backup completo** del proyecto
2. **Verificar que el sistema funcione** después de los cambios
3. **Actualizar rutas** en scripts si es necesario
4. **Documentar la nueva estructura** para el equipo
