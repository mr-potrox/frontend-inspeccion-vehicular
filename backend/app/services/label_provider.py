from functools import lru_cache
from ..config import settings

def _parse(csv: str) -> list[str]:
    return [c.strip() for c in csv.split(",") if c.strip()]

@lru_cache
def get_label_sets():
    damage = _parse(settings.DAMAGE_LABELS)
    parts = _parse(settings.PART_LABELS)
    return {
        "damage_labels": damage,
        "part_labels": parts
    }