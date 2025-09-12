from fastapi import APIRouter
from .services.rules_engine import reload_rules
from .services.vehicle_service import seed_vehicles
from .services.driver_service import seed_drivers

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reload-rules")
def admin_reload_rules():
    reload_rules()
    return {"status": "ok"}

@router.post("/seed")
def admin_seed(vehicles: int = 50, drivers: int = 50):
    seed_vehicles(vehicles)
    seed_drivers(drivers)
    return {"status": "ok", "vehicles": vehicles, "drivers": drivers}