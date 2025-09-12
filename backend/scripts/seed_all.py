import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import vehicles_col, drivers_col
from app.services.vehicle_service import seed_vehicles
from app.services.driver_service import seed_drivers

DEFAULT_VEHICLES = 120
DEFAULT_DRIVERS = 120

def main():
    v_count = vehicles_col.estimated_document_count()
    d_count = drivers_col.estimated_document_count()
    if v_count == 0:
        seed_vehicles(DEFAULT_VEHICLES)
    if d_count == 0:
        seed_drivers(DEFAULT_DRIVERS)
    print(f"Seed complete. vehicles={vehicles_col.estimated_document_count()} drivers={drivers_col.estimated_document_count()}")

if __name__ == "__main__":
    main()