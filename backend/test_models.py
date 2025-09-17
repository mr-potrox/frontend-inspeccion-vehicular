#!/usr/bin/env python3
"""
Script para verificar que los modelos de IA se cargan correctamente
"""

import sys
import os
from pathlib import Path

# Agregar el path del proyecto
sys.path.append(str(Path(__file__).resolve().parent))

from app.config import settings
from app.yolo_model import load_models, _safe_load

def test_models():
    print("🔍 VERIFICACIÓN DE MODELOS DE IA")
    print("=" * 50)
    
    # Verificar configuración
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    print(f"🎯 Modelo de daños: {settings.DAMAGE_MODEL_PATH}")
    print(f"🎯 Modelo de partes: {settings.PARTS_MODEL_PATH}")
    print()
    
    # Verificar existencia de archivos
    damage_exists = os.path.exists(settings.DAMAGE_MODEL_PATH)
    parts_exists = os.path.exists(settings.PARTS_MODEL_PATH)
    
    print("📂 EXISTENCIA DE ARCHIVOS:")
    print(f"   Modelo de daños: {'✅' if damage_exists else '❌'} {settings.DAMAGE_MODEL_PATH}")
    print(f"   Modelo de partes: {'✅' if parts_exists else '❌'} {settings.PARTS_MODEL_PATH}")
    print()
    
    if not damage_exists or not parts_exists:
        print("❌ ERROR: Faltan archivos de modelos")
        return False
    
    # Verificar tamaños
    damage_size = os.path.getsize(settings.DAMAGE_MODEL_PATH) / (1024*1024)
    parts_size = os.path.getsize(settings.PARTS_MODEL_PATH) / (1024*1024)
    
    print("📊 TAMAÑOS DE ARCHIVOS:")
    print(f"   Modelo de daños: {damage_size:.1f} MB")
    print(f"   Modelo de partes: {parts_size:.1f} MB")
    print()
    
    # Intentar cargar modelos
    print("🔄 CARGANDO MODELOS...")
    try:
        bundle = load_models()
        
        damage_loaded = bundle.damage is not None
        parts_loaded = bundle.parts is not None
        
        print("✅ CARGA DE MODELOS:")
        print(f"   Modelo de daños: {'✅' if damage_loaded else '❌'}")
        print(f"   Modelo de partes: {'✅' if parts_loaded else '❌'}")
        print()
        
        if damage_loaded and parts_loaded:
            print("🎉 ¡TODOS LOS MODELOS SE CARGARON EXITOSAMENTE!")
            print()
            print("📋 INFORMACIÓN DE MODELOS:")
            
            # Info del modelo de daños
            if bundle.damage:
                damage_names = getattr(bundle.damage, 'names', {})
                print(f"   Daños - Clases: {list(damage_names.values()) if damage_names else 'No disponible'}")
            
            # Info del modelo de partes
            if bundle.parts:
                parts_names = getattr(bundle.parts, 'names', {})
                print(f"   Partes - Clases: {list(parts_names.values()) if parts_names else 'No disponible'}")
            
            return True
        else:
            print("❌ ERROR: No se pudieron cargar todos los modelos")
            return False
            
    except Exception as e:
        print(f"❌ ERROR AL CARGAR MODELOS: {e}")
        return False

if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)
