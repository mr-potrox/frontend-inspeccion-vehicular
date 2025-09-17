# Inspector Vehicular - Backend

Sistema de inspección vehicular con IA desarrol### Verificación

Para verificar que todo está configurado correctamente:

```bash
source venv/bin/activate
python scripts/verify_setup.py
```a TFM. Utiliza YOLOv8 para detectar partes de vehículos y daños.

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)
```bash
./start_backend.sh
```

### Opción 2: Manual
```bash
# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias mínimas
pip install pydantic pydantic-settings python-dotenv fastapi uvicorn

# Verificar configuración
python scripts/verify_setup.py

# Iniciar servidor
uvicorn app.main:app --reload --port 8000
```

## 📊 Modelos de IA Configurados

- **Modelo de Daños**: `models/damage_best.pt` (6.0 MB)
  - Detecta: scratches, dents, broken_glass
  - Entrenado por 54 épocas
  
- **Modelo de Partes**: `models/parts_best.pt` (6.0 MB)
  - Detecta: Bonet, Bumper, Door, Headlight, Mirror, Tailight, Windshield
  - 15 clases de partes vehiculares

## ⚙️ Configuración

El sistema está configurado con las funcionalidades esenciales habilitadas:

✅ **Habilitado:**
- Detección de daños (YOLOv8)
- Detección de partes (YOLOv8)
- Procesamiento de imágenes
- API REST con FastAPI
- Base de datos MongoDB

❌ **Deshabilitado:**
- Segmentación de carrocería
- Clasificador de fondo
- Análisis de severidad de scratches
- Detección de alteraciones
- OCR para placas/VIN

## 🗄️ Base de Datos

- **MongoDB**: `mongodb://localhost:27017`
- **Base de datos**: `vehicular_tfm`
- **Seeding**: Ejecutar `python -m scripts.seed_all` para datos de prueba

## 📁 Estructura de Archivos

```
backend/
├── app/
│   ├── main.py           # FastAPI app principal
│   ├── config.py         # Configuración
│   └── yolo_model.py     # Carga de modelos YOLO
├── models/
│   ├── damage_best.pt    # Modelo de daños
│   └── parts_best.pt     # Modelo de partes
├── scripts/
│   ├── seed_all.py            # Script de seeding
│   ├── verify_setup.py        # Verificación de configuración
│   └── reorganize_repository.sh # Reorganización del repositorio
├── .env                       # Variables de entorno
├── requirements.txt           # Dependencias Python
└── start_backend.sh           # Script de inicio automático
```

## 🔧 Verificación

Para verificar que todo está configurado correctamente:

```bash
source venv/bin/activate
python scripts/verify_setup.py
```

## 📚 API Endpoints

Una vez iniciado el servidor:

- **Documentación interactiva**: http://localhost:8000/docs
- **API Schema**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## 🎯 Resultados del Entrenamiento

**Modelo de Partes (Epoch 54):**
- Precision: 0.518
- Recall: 0.651
- mAP@0.5: 0.586
- mAP@0.5:0.95: 0.361

**Análisis de Dataset:**
- Coeficiente de Variación: 0.438
- Clase dominante: "rueda" (2.58x sobrerrepresentada)
- Degradación observada durante entrenamiento (académicamente relevante)

## 🚨 Requisitos

- Python 3.8+
- MongoDB (para persistencia)
- ~200MB espacio en disco (modelos + dependencias)

## 🔍 Troubleshooting

1. **Error de Python**: Usar `python3` en lugar de `python`
2. **Dependencias**: El script de inicio maneja automáticamente las dependencias básicas
3. **Modelos faltantes**: Verificar que existan `models/damage_best.pt` y `models/parts_best.pt`
4. **MongoDB**: Asegurar que MongoDB esté ejecutándose en puerto 27017

## 📝 Notas de Desarrollo

Este backend forma parte de un trabajo de investigación académica (TFM) que estudia la efectividad de YOLO para inspección vehicular. Los modelos muestran degradación de rendimiento que aporta valor académico al analizar las limitaciones de los datasets balanceados.
