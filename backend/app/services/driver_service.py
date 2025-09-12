from ..database import drivers_col
from ..utils.random_data import gen_driver_record
from typing import Optional

def seed_drivers(n=50):
    bulk = [gen_driver_record() for _ in range(n)]
    if bulk:
        drivers_col.insert_many(bulk)
    return n

def get_random_driver():
    doc = drivers_col.aggregate([{"$sample":{"size":1}}])
    for d in doc:
        d.pop("_id", None)
        return d
    seed_drivers(10)
    return get_random_driver()

def get_driver(driver_id: str) -> Optional[dict]:
    d = drivers_col.find_one({"driver_id": driver_id},{"_id":0})
    return d