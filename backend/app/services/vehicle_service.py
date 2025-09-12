from typing import Optional, List
from ..database import vehicles_col
from ..utils.random_data import gen_vehicle_record

def get_vehicle(plate: str):
    return vehicles_col.find_one({"plate": plate.upper()},{"_id":0})

def create_vehicle(plate: Optional[str] = None):
    doc = gen_vehicle_record(plate)
    vehicles_col.insert_one(doc)
    doc.pop("_id", None)
    return doc

def get_or_create_vehicle(plate: str):
    existing = get_vehicle(plate)
    if existing:
        return existing
    return create_vehicle(plate)

def seed_vehicles(n: int = 50):
    bulk = [gen_vehicle_record() for _ in range(n)]
    if bulk:
        vehicles_col.insert_many(bulk)
    return n

def list_vehicle_plates(limit=50) -> List[str]:
    cur = vehicles_col.find({}, {"plate":1, "_id":0}).limit(limit)
    return [c["plate"] for c in cur]