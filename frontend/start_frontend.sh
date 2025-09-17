#!/bin/bash

# Script para iniciar el frontend del Inspector Vehicular
# React + Vite frontend para el sistema de inspección vehicular

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚗 INSPECTOR VEHICULAR - FRONTEND"
echo "=================================="

# Verificar si Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado. Por favor instalar Node.js 16+ desde:"
    echo "   https://nodejs.org/"
    exit 1
fi

# Verificar si npm está instalado
if ! command -v npm &> /dev/null; then
    echo "❌ npm no está disponible"
    exit 1
fi

# Mostrar versiones
echo "📋 Versiones:"
echo "   Node: $(node --version)"
echo "   npm: $(npm --version)"

# Verificar package.json
if [ ! -f "package.json" ]; then
    echo "❌ package.json no encontrado"
    exit 1
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    echo "VITE_API_BASE_URL=http://localhost:8000" > .env
fi

# Verificar node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
else
    echo "✅ Dependencias ya instaladas"
fi

# Verificar configuración
echo "🔍 Verificando configuración..."
API_URL=$(grep VITE_API_BASE_URL .env | cut -d '=' -f2 || echo "http://localhost:8000")
echo "   API URL: $API_URL"

# Verificar que el backend esté disponible (opcional)
echo "🔗 Verificando conexión con backend..."
if curl -s --connect-timeout 3 "$API_URL/health" > /dev/null 2>&1; then
    echo "✅ Backend disponible en $API_URL"
else
    echo "⚠️  Backend no disponible en $API_URL"
    echo "   Asegúrate de que el backend esté ejecutándose:"
    echo "   cd ../backend && ./start_backend.sh"
    echo ""
fi

echo ""
echo "🚀 Iniciando servidor de desarrollo..."
echo "   URL: http://localhost:5173"
echo "   Backend: $API_URL"
echo ""
echo "Para detener el servidor: Ctrl+C"
echo ""

# Iniciar servidor de desarrollo
npm run dev
