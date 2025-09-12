from typing import Dict, Any, Optional, List
from datetime import datetime
from ..database import sessions_col

def _now():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_session(session_id: str):
    sessions_col.update_one(
        {"session_id": session_id},
        {"$setOnInsert": {
            "session_id": session_id,
            "created_at": _now(),
            "images": [],
            "flags": [],
            "review_flags": [],
            "notes": [],
            "aborted": False,
            "abort_reason": None,
            "geo_mismatch_count": 0
        }},
        upsert=True
    )
def count_images(session_id: str) -> int:
    s = get_session(session_id)
    if not s: return 0
    return len(s.get("images", []))

def store_image_analysis(session_id: str, plate: str, analysis: Dict[str, Any], raw_bytes: bytes):
    """
    Envuelve append_image almacenando análisis, bytes crudos y metadatos mínimos.
    """
    ensure_session(session_id)
    image_doc = {
        "ts": _now(),
        "plate": plate,
        "analysis": analysis,
        "raw": raw_bytes,
        "photo_key": analysis.get("photo_key") or analysis.get("step")
    }
    append_image(session_id, image_doc)

def set_identity(session_id: str, payload: Dict[str, Any]):
    ensure_session(session_id)
    sessions_col.update_one({"session_id": session_id}, {"$set": {"identity": payload}})

def get_identity(session_id: str) -> Optional[Dict[str, Any]]:
    s = get_session(session_id)
    return s.get("identity") if s else None

def set_vehicle_history(session_id: str, payload: Dict[str, Any]):
    ensure_session(session_id)
    sessions_col.update_one({"session_id": session_id}, {"$set": {"vehicle_history": payload}})

def get_vehicle_history(session_id: str) -> Optional[Dict[str, Any]]:
    s = get_session(session_id)
    return s.get("vehicle_history") if s else None

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    return sessions_col.find_one({"session_id": session_id})

def append_image(session_id: str, image_doc: Dict[str, Any]):
    ensure_session(session_id)
    sessions_col.update_one({"session_id": session_id}, {"$push": {"images": image_doc}})

def add_flag(session_id: str, flag: str):
    sessions_col.update_one({"session_id": session_id}, {"$addToSet": {"flags": flag}})

def add_review_flag(session_id: str, flag: str):
    sessions_col.update_one({"session_id": session_id}, {"$addToSet": {"review_flags": flag}})

def add_note(session_id: str, note: str):
    sessions_col.update_one({"session_id": session_id}, {"$push": {"notes": note}})

def set_abort(session_id: str, reason: str):
    sessions_col.update_one({"session_id": session_id}, {"$set": {"aborted": True, "abort_reason": reason}})

def increment_geo_mismatch(session_id: str):
    sessions_col.update_one({"session_id": session_id}, {"$inc": {"geo_mismatch_count": 1}})

def get_geo_mismatch_count(session_id: str) -> int:
    s=get_session(session_id)
    return s.get("geo_mismatch_count",0) if s else 0

def is_aborted(session_id: str):
    s=get_session(session_id)
    if not s: return False, None
    return s.get("aborted",False), s.get("abort_reason")

def list_images(session_id: str)->List[Dict[str,Any]]:
    s=get_session(session_id)
    return s.get("images",[]) if s else []

def list_flags(session_id: str)->List[str]:
    s=get_session(session_id)
    return s.get("flags",[]) if s else []

def list_review_flags(session_id: str)->List[str]:
    s=get_session(session_id)
    return s.get("review_flags",[]) if s else []

def list_notes(session_id: str)->List[str]:
    s=get_session(session_id)
    return s.get("notes",[]) if s else []

def clear_session(session_id: str):
    sessions_col.delete_one({"session_id": session_id})