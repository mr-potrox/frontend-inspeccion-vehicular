#!/bin/bash

# Script maestro para iniciar el sistema completo Inspector Vehicular
# Inicia backend (FastAPI) y frontend (React+Vite) automáticamente

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚗 INSPECTOR VEHICULAR - SISTEMA COMPLETO"
echo "=========================================="

# Verificar estructura de directorios
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: No se encontraron las carpetas backend/ y frontend/"
    echo "   Ejecuta este script desde la carpeta inspector-vehicular/"
    exit 1
fi

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servicios..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "✅ Servicios detenidos"
    exit 0
}

# Configurar trap para limpieza
trap cleanup SIGINT SIGTERM

echo "📋 Verificando dependencias..."

# Verificar Python para backend
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar Node.js para frontend
if ! command -v node &> /dev/null; then
    echo "❌ Node.js no está instalado"
    exit 1
fi

echo "✅ Dependencias OK"

# Iniciar backend en background
echo ""
echo "🔧 Iniciando backend..."
cd backend
if [ ! -f "start_backend.sh" ]; then
    echo "❌ Script start_backend.sh no encontrado"
    exit 1
fi

# Hacer ejecutable si no lo es
chmod +x start_backend.sh

# Iniciar backend en background con logs
./start_backend.sh > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "✅ Backend iniciado (PID: $BACKEND_PID)"
echo "   Logs: backend.log"

# Esperar un poco para que el backend se inicie
echo "⏳ Esperando que el backend esté listo..."
sleep 5

# Verificar que el backend esté corriendo
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Error: El backend no se pudo iniciar"
    echo "   Revisa backend.log para más detalles"
    tail -10 ../backend.log
    exit 1
fi

# Probar conexión al backend
for i in {1..10}; do
    if curl -s --connect-timeout 2 http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend listo en http://localhost:8000"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠️  Backend tardando en responder, continuando..."
        break
    fi
    sleep 2
done

# Iniciar frontend
echo ""
echo "🎨 Iniciando frontend..."
cd ../frontend

if [ ! -f "start_frontend.sh" ]; then
    echo "❌ Script start_frontend.sh no encontrado"
    cleanup
    exit 1
fi

# Hacer ejecutable si no lo es
chmod +x start_frontend.sh

# Iniciar frontend en background con logs
./start_frontend.sh > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
echo "   Logs: frontend.log"

# Mostrar información del sistema
echo ""
echo "🎉 SISTEMA INSPECTOR VEHICULAR INICIADO"
echo "======================================="
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs disponibles:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 Para detener: Ctrl+C"
echo ""

# Mantener el script corriendo y mostrar logs en tiempo real
echo "📊 Monitoreando servicios (mostrando logs del backend)..."
echo "----------------------------------------"

# Mostrar logs del backend en tiempo real
tail -f backend.log &
TAIL_PID=$!

# Esperar a que se presione Ctrl+C
wait

# Esta línea no debería ejecutarse nunca debido al trap
cleanup
