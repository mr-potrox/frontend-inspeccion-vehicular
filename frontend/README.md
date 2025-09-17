# Inspector Vehicular - Frontend

Interfaz de usuario React para el sistema de inspección vehicular con IA. Desarrollado con React 18, TypeScript, Tailwind CSS y Vite.

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)
```bash
./start_frontend.sh
```

### Opción 2: Manual
```bash
# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### Opción 3: Sistema Completo
```bash
# Desde la carpeta principal inspector-vehicular/
./start_system.sh
```

## 🛠️ Tecnologías

- **React 18** - Framework de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool y dev server
- **Tailwind CSS** - Framework de CSS
- **Framer Motion** - Animaciones
- **Lucide React** - Iconos
- **React Dropzone** - Upload de archivos

## ⚙️ Configuración

### Variables de Entorno (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Scripts Disponibles
```bash
npm run dev      # Servidor de desarrollo
npm run build    # Build de producción
npm run preview  # Preview del build
npm run lint     # Linter ESLint
npm run test     # Tests con Vitest
```

### Scripts de Verificación
```bash
python3 verify_frontend.py  # Verificación completa del sistema
./start_frontend.sh          # Inicio automático con verificaciones
```

## 🎯 Funcionalidades

### ✅ Características Implementadas

**Sistema de Inspección:**
- 📸 Captura múltiple de imágenes por vehículo
- 🤖 Detección automática de daños (scratches, dents, vidrios rotos)
- 🔧 Identificación de partes vehiculares (15 clases)
- 📊 Análisis de calidad de imagen en tiempo real
- 🎨 Detección de color dominante
- 🌍 Geolocalización y validación

**Análisis Avanzado:**
- 🔍 Segmentación de carrocería vehicular
- 🏢 Clasificación de fondo (indoor/outdoor)
- 💡 Análisis de iluminación y contraste
- 📖 OCR para placas y VIN
- 🛡️ Detección de alteraciones (tamper)
- ⚖️ Análisis de severidad de rayones

**Interfaz de Usuario:**
- 📱 Diseño responsive y moderno
- 🎭 Animaciones fluidas con Framer Motion
- 🖼️ Visualización de resultados en tiempo real
- 📋 Reportes detallados de inspección
- 🚨 Sistema de alertas y validaciones

## 📁 Estructura del Proyecto

```
frontend/
├── public/               # Archivos estáticos
├── src/
│   ├── components/       # Componentes React
│   │   ├── common/       # Componentes reutilizables
│   │   ├── inspection/   # Componentes de inspección
│   │   └── ui/          # Componentes de UI
│   ├── hooks/           # Custom hooks
│   ├── services/        # Servicios API
│   ├── styles/          # Estilos globales
│   ├── types/           # Tipos TypeScript
│   ├── utils/           # Utilidades
│   ├── App.tsx          # Componente principal
│   └── main.tsx         # Punto de entrada
├── .env                 # Variables de entorno
├── package.json         # Dependencias y scripts
├── tailwind.config.js   # Configuración Tailwind
├── vite.config.ts       # Configuración Vite
└── start_frontend.sh    # Script de inicio automático
```

## 🔌 Integración con Backend

El frontend se comunica con el backend FastAPI a través de las siguientes APIs:

### Endpoints Principales
- `GET /health` - Estado del sistema y configuración
- `POST /inspection/analyze` - Análisis de imagen individual
- `POST /inspection/finalize` - Finalización de inspección
- `GET /session/{id}/images` - Obtener imágenes de sesión

### Flujo de Datos
1. **Captura** → Usuario toma fotos de diferentes ángulos
2. **Upload** → Imágenes se envían al backend para análisis
3. **Procesamiento** → IA analiza daños, partes, calidad, etc.
4. **Resultados** → Frontend muestra detecciones y métricas
5. **Finalización** → Se genera reporte completo de inspección

## 🧪 Testing

```bash
# Ejecutar tests una vez
npm run test

# Modo watch para desarrollo
npm run test:watch
```

## 📊 Métricas de Desarrollo

### Performance
- **Tiempo de carga inicial**: ~2-3 segundos
- **Tiempo de análisis por imagen**: 3-8 segundos (dependiente del backend)
- **Tamaño del bundle**: ~500KB gzipped

### Compatibilidad
- **Navegadores**: Chrome 88+, Firefox 85+, Safari 14+
- **Dispositivos**: Desktop, tablet, móvil
- **Resoluciones**: 320px - 4K

## 🔧 Desarrollo

### Verificación del Sistema
```bash
# Verificación completa del frontend
python3 verify_frontend.py

# Verificación rápida
npm run lint && npm run test
```

### Comandos Útiles
```bash
# Desarrollo con hot reload
npm run dev

# Análisis del bundle
npm run build && npx vite preview

# Linting y formato
npm run lint
npx prettier --write src/

# Limpieza de dependencias
rm -rf node_modules package-lock.json && npm install
```

### Estructura de Componentes
```
Components/
├── Inspection/
│   ├── Camera/          # Captura de imágenes
│   ├── Analysis/        # Visualización de resultados
│   ├── Results/         # Reporte final
│   └── Session/         # Gestión de sesión
├── UI/
│   ├── Button/          # Botones reutilizables
│   ├── Modal/           # Modales
│   └── Loading/         # Estados de carga
└── Common/
    ├── Header/          # Navegación
    ├── Footer/          # Pie de página
    └── Layout/          # Layout principal
```

## 🚨 Troubleshooting

### Verificación del Sistema
```bash
# Verificación completa del frontend
python3 verify_frontend.py
```

### Problemas Comunes

1. **Error de conexión con backend**
   ```bash
   # Verificar que el backend esté corriendo
   curl http://localhost:8000/health
   ```

2. **Dependencias desactualizadas**
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Puerto 5173 ocupado**
   ```bash
   # Usar puerto alternativo
   npm run dev -- --port 5174
   ```

4. **Problemas de CORS**
   - Verificar configuración en backend `API_ORIGINS`
   - Comprobar `.env` del frontend

### Logs y Debugging
- **Logs del servidor**: `frontend.log` (cuando se usa `start_system.sh`)
- **DevTools**: F12 → Console para errores del navegador
- **Network**: F12 → Network para requests fallidos

## 📝 Notas de Desarrollo

### Estado del Proyecto
- ✅ **Funcionalidad Core**: Completamente implementada
- ✅ **UI/UX**: Diseño moderno y responsive
- ✅ **Integración Backend**: APIs completamente integradas
- ✅ **Testing**: Tests básicos implementados
- 🔄 **Optimizaciones**: Pendientes mejoras de performance

### Próximas Funcionalidades
- 📱 PWA (Progressive Web App)
- 🔄 Modo offline con sincronización
- 📊 Dashboard de métricas avanzadas
- 🎯 Exportación de reportes PDF
- 🔐 Sistema de autenticación

## 🎉 Información Adicional

Este frontend forma parte del TFM (Trabajo de Fin de Máster) que estudia la aplicación de IA para inspección vehicular. La interfaz está diseñada para demostrar las capacidades de los modelos YOLO entrenados y proporcionar una experiencia de usuario intuitiva para la captura y análisis de daños vehiculares.
