from fastapi import FastAPI, File, UploadFile, Form
from typing import Optional
from app.quality import check_quality
from app.db_sim import verify_vehicle
# from app.yolo_model import detect_damage  # Implementar luego
# from app.session_store import (
#     save_image, get_result, save_note, generate_report
# )

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/inspection/verify")
def inspection_verify(plate: str):
    info = verify_vehicle(plate)
    return info

@app.post("/inspection/quality")
async def inspection_quality(file: UploadFile = File(...)):
    img_bytes = await file.read()
    quality_ok = check_quality(img_bytes)
    if not quality_ok:
        return {"success": False, "message": "Imagen no cumple requisitos de calidad"}
    return {"success": True, "message": "Imagen válida"}

@app.post("/inspection/damage")
async def inspection_damage(file: UploadFile = File(...)):
    img_bytes = await file.read()
    # IA: Detecta daños en la imagen
    result = detect_damage(img_bytes)
    return {"success": True, "damage": result}

@app.post("/inspection/upload")
async def inspection_upload(
    file: UploadFile = File(...),
    tipo: str = Form(...),
    lat: Optional[float] = Form(None),
    lon: Optional[float] = Form(None),
    session_id: str = Form(...)
):
    img_bytes = await file.read()
    # Guarda imagen y metadatos en la sesión
    save_image(session_id, tipo, img_bytes, lat, lon)
    return {"success": True, "message": "Imagen guardada"}

@app.get("/inspection/result")
def inspection_result(session_id: str):
    result = get_result(session_id)
    return result

@app.post("/inspection/note")
def inspection_note(session_id: str = Form(...), note: str = Form(...)):
    save_note(session_id, note)
    return {"success": True, "message": "Nota guardada"}

@app.get("/inspection/report")
def inspection_report(session_id: str):
    report = generate_report(session_id)
    return report  # Puede ser JSON o archivo PDF