# 🚗 Inspector Vehicular - Sistema Completo

Sistema inteligente de inspección vehicular desarrollado como TFM (Trabajo de Fin de Máster) que utiliza modelos YOLO para la detección automática de daños y partes de vehículos.

## 🎯 Descripción del Proyecto

Este proyecto implementa un sistema end-to-end para la inspección vehicular automatizada que combina:

- **Inteligencia Artificial**: Modelos YOLOv8 para detección de daños y partes
- **Backend Robusto**: API REST con FastAPI y MongoDB
- **Frontend Moderno**: Interfaz React con análisis en tiempo real
- **Análisis Académico**: Metodología de investigación documentada

## 🚀 Inicio Rápido - Sistema Completo

### Opción 1: Un Solo Comando (Recomendado)
```bash
./start_system.sh
```

### Opción 2: Servicios Independientes
```bash
# Terminal 1 - Backend
cd backend
./start_backend.sh

# Terminal 2 - Frontend  
cd frontend
./start_frontend.sh
```

### URLs del Sistema
- **🎨 Frontend**: http://localhost:5173
- **🔧 Backend API**: http://localhost:8000
- **📚 Documentación**: http://localhost:8000/docs

## 📊 Capacidades del Sistema

### 🤖 Inteligencia Artificial

| Funcionalidad | Estado | Descripción |
|---------------|--------|-------------|
| **Detección de Daños** | ✅ Operativo | Scratches, dents, vidrios rotos |
| **Detección de Partes** | ✅ Operativo | 15 clases de partes vehiculares |
| **Segmentación** | ✅ Operativo | Máscara de carrocería vehicular |
| **OCR** | ✅ Operativo | Lectura de placas y VIN |
| **Clasificación de Fondo** | ✅ Operativo | Indoor/outdoor/garage/parking |
| **Análisis de Severidad** | ✅ Operativo | Minor/moderate/severe scratches |
| **Detección de Alteraciones** | ✅ Operativo | ELA + CNN tamper detection |

### 📱 Interfaz de Usuario

- **Captura Multi-imagen**: Fotos desde múltiples ángulos
- **Análisis en Tiempo Real**: Resultados instantáneos
- **Validación de Calidad**: Blur, iluminación, composición
- **Geolocalización**: Validación de ubicación de inspección
- **Reportes Detallados**: Exportación de resultados completos

### 🔧 Arquitectura Técnica

- **Backend**: FastAPI + MongoDB + YOLOv8
- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **IA**: Ultralytics YOLOv8, OpenCV, EasyOCR
- **Base de Datos**: MongoDB con seeding automático

## 📁 Estructura del Proyecto

```
inspector-vehicular/
├── backend/                    # API FastAPI
│   ├── app/                   # Código de la aplicación
│   ├── models/                # Modelos de IA (.pt files)
│   ├── scripts/               # Scripts de utilidad
│   ├── requirements.txt       # Dependencias Python
│   ├── start_backend.sh       # Inicio automático
│   └── README.md             # Documentación backend
├── frontend/                   # Interfaz React
│   ├── src/                   # Código fuente
│   ├── public/                # Archivos estáticos
│   ├── package.json           # Dependencias Node.js
│   ├── start_frontend.sh      # Inicio automático
│   └── README.md             # Documentación frontend
├── start_system.sh            # Inicio del sistema completo
└── README.md                 # Este archivo
```

## 🔬 Resultados de Investigación

### Modelos Entrenados

**Detector de Partes (54 épocas)**:
- **Precision**: 0.518
- **Recall**: 0.651
- **mAP@0.5**: 0.586
- **mAP@0.5:0.95**: 0.361

**Análisis de Dataset**:
- **Coeficiente de Variación**: 0.438
- **Clase Dominante**: "rueda" (2.58x sobrerrepresentada)
- **Contribución Académica**: Análisis de degradación durante entrenamiento

### Metodología Desarrollada

1. **Consolidación de Datasets**: Unificación de múltiples fuentes
2. **Análisis de Balance**: Herramientas de CV y distribución
3. **Entrenamiento Progresivo**: Fases con diferentes hiperparámetros
4. **Evaluación Integral**: Métricas de rendimiento y análisis de sesgo

## 🛠️ Instalación y Configuración

### Requisitos del Sistema

- **Python 3.8+** (para backend)
- **Node.js 16+** (para frontend)  
- **MongoDB** (base de datos)
- **~2GB RAM** (para inferencia)
- **~500MB disco** (modelos + dependencias)

### Instalación Automática

```bash
# Clonar proyecto (si aplica)
git clone [repo-url]
cd inspector-vehicular

# Dar permisos de ejecución
chmod +x start_system.sh
chmod +x backend/start_backend.sh
chmod +x frontend/start_frontend.sh

# Iniciar sistema completo
./start_system.sh
```

### Verificación de Instalación

```bash
# Verificar backend
curl http://localhost:8000/health

# Verificar frontend
curl http://localhost:5173

# Poblar base de datos (opcional)
cd backend
source venv/bin/activate
python -m scripts.seed_all
```

## 📚 Documentación Detallada

### Para Desarrolladores
- [Backend README](backend/README.md) - API, modelos, configuración
- [Frontend README](frontend/README.md) - UI, componentes, hooks

### Para Investigadores
- [TFM 3.md](TFM%203.md) - Análisis académico completo
- [Resultados de Entrenamiento](TFM_Proyecto_Modelos/) - Métricas y artefactos

### Para Usuarios
- **Documentación Interactiva**: http://localhost:8000/docs
- **Scripts de Verificación**: `backend/scripts/verify_setup.py`

## 🎯 Casos de Uso

### 1. Inspección Vehicular Básica
```bash
# 1. Iniciar sistema
./start_system.sh

# 2. Abrir http://localhost:5173
# 3. Seguir wizard de inspección
# 4. Capturar imágenes desde múltiples ángulos
# 5. Revisar detecciones automáticas
# 6. Generar reporte final
```

### 2. Desarrollo y Testing
```bash
# Backend solo
cd backend && ./start_backend.sh

# Frontend solo
cd frontend && ./start_frontend.sh

# Ejecutar tests
cd frontend && npm test
```

### 3. Investigación y Análisis
```bash
# Verificar modelos
cd backend && python scripts/verify_setup.py

# Consultar métricas
curl http://localhost:8000/health
```

## 🔍 Monitoreo y Logs

### Logs del Sistema
```bash
# Ver logs en tiempo real
tail -f backend.log    # Backend
tail -f frontend.log   # Frontend

# Logs de desarrollo
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
cd frontend && npm run dev
```

### Métricas de Performance
- **Tiempo de análisis**: 3-8 segundos por imagen
- **Precisión de detección**: 51.8% (académicamente relevante)
- **Throughput**: ~10-15 imágenes/minuto
- **Memoria utilizada**: ~1.5GB durante inferencia

## ⚠️ Troubleshooting

### Problemas Comunes

1. **Puerto ocupado**:
   ```bash
   # Verificar puertos
   lsof -i :8000   # Backend
   lsof -i :5173   # Frontend
   ```

2. **Modelos faltantes**:
   ```bash
   cd backend && python scripts/verify_setup.py
   ```

3. **Base de datos**:
   ```bash
   # Verificar MongoDB
   mongosh mongodb://localhost:27017
   ```

4. **Dependencias**:
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend  
   cd frontend && npm install
   ```

### Logs de Debugging
- **Backend**: `backend.log` o terminal directo
- **Frontend**: `frontend.log` + DevTools del navegador
- **Sistema**: Salida de `start_system.sh`

## 🚀 Deploy y Producción

### Configuración de Producción

```bash
# Backend
cd backend
pip install gunicorn
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000

# Frontend
cd frontend
npm run build
npx serve -s dist -l 5173
```

### Variables de Entorno

```bash
# Backend (.env)
MONGO_URI=mongodb://localhost:27017
MONGO_DB=vehicular_tfm
API_ORIGINS=http://production-domain.com

# Frontend (.env)
VITE_API_BASE_URL=http://api.production-domain.com
```

## 🎓 Contribución Académica

Este proyecto aporta:

1. **Metodología de Análisis**: Framework para evaluar degradación de modelos
2. **Dataset Unificado**: Consolidación de múltiples fuentes de daños vehiculares  
3. **Métricas de Balance**: Herramientas para CV y análisis de sesgo
4. **Sistema End-to-End**: Implementación completa desde captura hasta reporte

### Publicaciones y Referencias
- TFM Completo: Ver `TFM 3.md`
- Resultados de Entrenamiento: `TFM_Proyecto_Modelos/`
- Análisis de Balance: `balance_results/`

## 📞 Soporte

### Para Issues Técnicos
1. Verificar logs: `backend.log`, `frontend.log`
2. Ejecutar diagnósticos: `backend/scripts/verify_setup.py`
3. Revisar documentación: `README.md` de cada módulo

### Para Consultas Académicas
- Revisar análisis completo en `TFM 3.md`
- Consultar métricas en `resultados_finales/`
- Verificar metodología en documentación del proyecto

---

## 🎉 Estado del Proyecto

✅ **Sistema Operativo**: Backend + Frontend + IA integrados  
✅ **Modelos Entrenados**: YOLOv8 para daños y partes  
✅ **Documentación Completa**: Técnica y académica  
✅ **Scripts Automáticos**: Inicio y configuración sin intervención  
✅ **Análisis Académico**: Metodología y resultados documentados  

**El sistema está listo para uso, demostración e investigación académica.** 🚗🤖
