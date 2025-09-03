#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorio raíz del proyecto
PROJECT_ROOT="frontend"

echo -e "${BLUE}🚀 Creando estructura modular de frontend...${NC}"

# Crear directorio principal
mkdir -p $PROJECT_ROOT
cd $PROJECT_ROOT

echo -e "${GREEN}📁 Creando estructura de carpetas...${NC}"

# Crear todas las carpetas necesarias
mkdir -p src/{components/{common/{Button,ProgressStepper,LoadingSpinner,Modal},inspection/{ImageUpload,QualityCheck,DamageDetection,Results},layout/{Header,Footer,Layout}},hooks,services,types,utils,constants,styles,contexts}

echo -e "${GREEN}📝 Creando archivos vacíos...${NC}"

# Crear archivos de configuración vacíos
touch package.json
touch vite.config.ts
touch tsconfig.json
touch tailwind.config.js
touch postcss.config.js
touch index.html

# Crear archivos de estilos vacíos
touch src/styles/globals.css

# Crear archivos de tipos vacíos
touch src/types/inspection.ts
touch src/types/api.ts

# Crear archivos de servicios vacíos
touch src/services/api.ts
touch src/services/imageService.ts
touch src/services/inspectionService.ts

# Crear archivos de hooks vacíos
touch src/hooks/useImageProcessing.ts
touch src/hooks/useApi.ts
touch src/hooks/useInspectionStore.ts

# Crear archivos de utilidades vacíos
touch src/utils/fileUtils.ts
touch src/utils/imageUtils.ts

# Crear archivos de constantes vacíos
touch src/constants/inspection.ts


# Crear componentes comunes vacíos
touch src/components/common/Button/Button.tsx
touch src/components/common/Button/index.ts
touch src/components/common/ProgressStepper/ProgressStepper.tsx
touch src/components/common/ProgressStepper/index.ts
touch src/components/common/LoadingSpinner/LoadingSpinner.tsx
touch src/components/common/LoadingSpinner/index.ts
touch src/components/common/Modal/Modal.tsx
touch src/components/common/Modal/index.ts

# Crear componentes de inspección vacíos
touch src/components/inspection/ImageUpload/ImageUpload.tsx
touch src/components/inspection/ImageUpload/index.ts
touch src/components/inspection/QualityCheck/QualityCheck.tsx
touch src/components/inspection/QualityCheck/index.ts
touch src/components/inspection/DamageDetection/DamageDetection.tsx
touch src/components/inspection/DamageDetection/index.ts
touch src/components/inspection/Results/Results.tsx
touch src/components/inspection/Results/index.ts
touch src/components/inspection/InspectionFlow.tsx

# Crear componentes de layout vacíos
touch src/components/layout/Header/Header.tsx
touch src/components/layout/Header/index.ts
touch src/components/layout/Footer/Footer.tsx
touch src/components/layout/Footer/index.ts
touch src/components/layout/Layout/Layout.tsx
touch src/components/layout/Layout/index.ts

# Crear archivos principales de la aplicación
touch src/App.tsx
touch src/main.tsx
touch src/vite-env.d.ts

echo -e "${GREEN}✅ Estructura creada exitosamente!${NC}"
echo -e "${YELLOW}📋 Total de archivos creados:${NC}"
find . -type f | wc -l
echo -e "${YELLOW}📋 Total de carpetas creadas:${NC}"
find . -type d | wc -l

echo -e "\n${BLUE}📂 Estructura generada:${NC}"
tree -I 'node_modules|dist|.git' -a

echo -e "\n${YELLOW}🚀 Para instalar dependencias, ejecuta:${NC}"
echo "cd $PROJECT_ROOT && npm install"
