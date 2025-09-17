#!/bin/bash

# Script para iniciar el backend del Inspector Vehicular
# Este script maneja la configuración del entorno virtual automáticamente

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚗 INSPECTOR VEHICULAR - BACKEND"
echo "================================="

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Verificar si están instaladas las dependencias básicas
if ! python -c "import pydantic_settings" 2>/dev/null; then
    echo "📋 Instalando dependencias básicas..."
    pip install pydantic pydantic-settings python-dotenv
fi

# Verificar configuración
echo "🔍 Verificando configuración..."
if python scripts/verify_setup.py; then
    echo ""
    echo "🚀 Iniciando servidor FastAPI..."
    echo "   URL: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
    echo ""
    echo "Para detener el servidor: Ctrl+C"
    echo ""
    
    # Intentar instalar FastAPI y uvicorn si no están
    if ! python -c "import fastapi, uvicorn" 2>/dev/null; then
        echo "📦 Instalando FastAPI y uvicorn..."
        pip install fastapi uvicorn
    fi
    
    # Iniciar servidor
    uvicorn app.main:app --reload --port 8000
else
    echo "❌ Error en la configuración. Revisa los mensajes anteriores."
    exit 1
fi
