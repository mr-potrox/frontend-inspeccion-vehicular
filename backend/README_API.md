# TFM Inspector API

## Endpoints Principales
- GET /health
- POST /admin/seed (vehicles, drivers)
- GET /vehicles/{plate}
- GET /vehicles?limit=30
- POST /inspection/analyze (FormData: file, plate, conf_damage?, conf_parts?, persist?)
- GET /inspection/history/{plate}

## Flujo Frontend
1. Capturar imagen vehículo.
2. Enviar a /inspection/analyze con placa.
3. Mostrar detecciones (daños) y partes presentes/faltantes.
4. Visualizar metadata vehículo + conductor (simulados).
5. Consultar historial si se requiere.

## Estructura de respuesta /inspection/analyze (resumen)
{
  damage: [{label, confidence, box}],
  parts: {part: {present, confidence, box|null}},
  missing_parts: [part,...],
  vehicle: {... metadata ...},
  driver: {... simulado ...},
  inspection_record: {... (si persist=True) ...}
}

## Semillas
python -m scripts.seed_all

## Poner en marcha
uvicorn app.main:app --reload --port 8000