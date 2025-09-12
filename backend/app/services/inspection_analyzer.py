import hashlib, time
from typing import Dict, Any, List, Tuple
from fastapi.concurrency import run_in_threadpool
from prometheus_client import Counter

from ..config import settings
from ..logging_utils import log_event
from ..repositories import session_repo as repo
from ..services.vehicle_service import get_or_create_vehicle
from ..yolo_model import detect_damage, detect_parts
from ..utils.color_detection import detect_dominant_color
from ..utils.exif_geo import extract_exif_geo, haversine_meters
from ..quality import check_quality
from ..services.rules_engine import evaluate_rules
from ..websocket_manager import manager

CACHE_HITS = Counter("analyze_cache_hits_total", "Total cache hits analyze")
ANALYZE_ABORTS = Counter("analyze_aborts_total", "Total aborts during analyze")

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

async def _run_damage(img: bytes, conf: float):
    return await run_in_threadpool(detect_damage, img, conf)

async def _run_parts(img: bytes, conf: float):
    return await run_in_threadpool(detect_parts, img, conf)

async def analyze_image(
    *,
    session_id: str,
    plate: str,
    img_bytes: bytes,
    conf_damage: float,
    conf_parts: float,
    note: str | None,
    browser_lat: float | None,
    browser_lon: float | None
) -> Dict[str, Any]:
    t0 = time.time()
    await manager.broadcast(session_id, {"event": "analyze:start", "session_id": session_id})
    repo.ensure_session(session_id)

    aborted, abort_reason = repo.is_aborted(session_id)
    existing_images_count = len(repo.list_images(session_id))

    if aborted:
        return _response(
            session_id, [], {}, [], {}, None,
            repo.list_flags(session_id),
            repo.list_review_flags(session_id),
            True, abort_reason, existing_images_count
        )

    if existing_images_count >= settings.MAX_IMAGES_PER_SESSION:
        repo.set_abort(session_id, "TOO_MANY_IMAGES")
        return _response(
            session_id, [], {}, [], {}, None,
            repo.list_flags(session_id) + ["TOO_MANY_IMAGES"],
            repo.list_review_flags(session_id),
            True, "TOO_MANY_IMAGES", existing_images_count
        )

    vehicle = get_or_create_vehicle(plate)
    vehicle_color = (vehicle.get("color") or "").strip()

    img_hash = _sha(img_bytes)
    for im in repo.list_images(session_id):
        if im.get("image_hash") == img_hash and im.get("analysis"):
            log_event("cache_hit", session_id=session_id)
            CACHE_HITS.inc()
            cached = _decorate(vehicle_color, im["analysis"], session_id)
            await manager.broadcast(session_id, {
                "event": "analyze:result",
                "session_id": session_id,
                "cached": True,
                "images_in_session": cached["images_in_session"],
                "fraud_flags": cached["fraud_flags"],
                "review_flags": cached["review_flags"],
                "aborted": cached["aborted"]
            })
            return cached

    quality_ok = check_quality(img_bytes)

    damage = await _run_damage(img_bytes, conf_damage)
    parts_res = await _run_parts(img_bytes, conf_parts)
    color_info = detect_dominant_color(img_bytes)
    exif_geo = extract_exif_geo(img_bytes)
    missing = [p for p, i in parts_res["parts_presence"].items() if not i["present"]]

    fraud_flags: List[str] = []
    review_flags: List[str] = []
    if not quality_ok:
        review_flags.append("LOW_IMAGE_QUALITY")

    prev_geo: List[Tuple[float, float]] = []
    for im in repo.list_images(session_id):
        lat = im.get("exif_lat"); lon = im.get("exif_lon")
        if lat is not None and lon is not None:
            prev_geo.append((lat, lon))

    browser_distance = 0.0
    if exif_geo and browser_lat is not None and browser_lon is not None:
        browser_distance = haversine_meters(exif_geo[0], exif_geo[1], browser_lat, browser_lon)
        if browser_distance > settings.GEO_WARN_DISTANCE:
            fraud_flags.append("GEO_BROWSER_MISMATCH")

    geo_mismatch = False
    if exif_geo and prev_geo:
        for p in prev_geo:
            if haversine_meters(exif_geo[0], exif_geo[1], p[0], p[1]) > settings.GEO_HARD_DISTANCE:
                geo_mismatch = True
                break
    if geo_mismatch:
        repo.increment_geo_mismatch(session_id)
        if repo.get_geo_mismatch_count(session_id) >= settings.GEO_ABORT_AFTER_WARN:
            repo.set_abort(session_id, "GEO_HARD_MISMATCH")
            fraud_flags.append("GEO_HARD_MISMATCH")
            ANALYZE_ABORTS.inc()
        else:
            review_flags.append("GEO_INCONSISTENT")

    detected_color = (color_info.get("color_name") or "").strip()
    aborted_now = False
    abort_reason_now = None
    color_mismatch = False
    if detected_color and vehicle_color and detected_color.lower() != vehicle_color.lower():
        color_mismatch = True
        if settings.COLOR_MISMATCH_POLICY.upper() == "ABORT":
            repo.set_abort(session_id, "COLOR_MISMATCH")
            aborted_now = True
            abort_reason_now = "COLOR_MISMATCH"
            fraud_flags.append("COLOR_MISMATCH")
            ANALYZE_ABORTS.inc()
        else:
            review_flags.append("COLOR_MISMATCH")

    analysis = {
        "damage": damage,
        "parts_presence": parts_res["parts_presence"],
        "missing_parts": missing,
        "color": color_info,
        "exif_geo": exif_geo
    }

    context = {
        "damage": {"count": len(damage)},
        "parts": {"missing_count": len(missing)},
        "geo": {
            "browser_distance": browser_distance,
            "hard_mismatch": geo_mismatch
        },
        "color": {"mismatch": color_mismatch},
        "quality": {"ok": quality_ok},
        "session": {"images": existing_images_count + 1}
    }
    rule_fraud, rule_review = evaluate_rules(context)
    fraud_flags = list(set(fraud_flags + rule_fraud))
    review_flags = list(set(review_flags + rule_review))

    repo.append_image(session_id, {
        "image_hash": img_hash,
        "browser_lat": browser_lat,
        "browser_lon": browser_lon,
        "exif_lat": exif_geo[0] if exif_geo else None,
        "exif_lon": exif_geo[1] if exif_geo else None,
        "analysis": analysis
    })
    if note:
        repo.add_note(session_id, note)
    for f in fraud_flags:
        repo.add_flag(session_id, f)
    for rf in review_flags:
        repo.add_review_flag(session_id, rf)

    log_event(
        "analyze_done",
        session_id=session_id,
        damage=len(damage),
        missing=len(missing),
        elapsed_ms=round((time.time() - t0) * 1000, 2),
        fraud=fraud_flags,
        review=review_flags,
        quality_ok=quality_ok
    )

    result = _decorate(
        vehicle_color, analysis, session_id,
        aborted_now, abort_reason_now,
        fraud_flags, review_flags
    )

    await manager.broadcast(session_id, {
        "event": "analyze:result",
        "session_id": session_id,
        "aborted": result["aborted"],
        "fraud_flags": result["fraud_flags"],
        "review_flags": result["review_flags"],
        "images_in_session": result["images_in_session"]
    })
    if result["aborted"]:
        await manager.broadcast(session_id, {
            "event": "session:aborted",
            "reason": result["abort_reason"]
        })

    return result

def _decorate(
    vehicle_color: str,
    analysis: Dict[str, Any],
    session_id: str,
    aborted: bool = False,
    abort_reason: str | None = None,
    extra_fraud: List[str] | None = None,
    extra_review: List[str] | None = None
):
    detected = (analysis["color"].get("color_name") or "").strip()
    color_match = bool(
        detected and vehicle_color and detected.lower() == vehicle_color.lower() and not aborted
    )
    all_fraud = list({*repo.list_flags(session_id), *(extra_fraud or [])})
    all_review = list({*repo.list_review_flags(session_id), *(extra_review or [])})
    return {
        "session_id": session_id,
        "damage": analysis["damage"],
        "parts_presence": analysis["parts_presence"],
        "missing_parts": analysis["missing_parts"],
        "color_detected": analysis["color"],
        "vehicle_color_db": vehicle_color,
        "color_match": color_match,
        "exif_geo": analysis["exif_geo"],
        "fraud_flags": all_fraud,
        "review_flags": all_review,
        "aborted": aborted or repo.is_aborted(session_id)[0],
        "abort_reason": abort_reason or repo.is_aborted(session_id)[1],
        "images_in_session": len(repo.list_images(session_id))
    }

def _response(
    session_id: str,
    damage,
    parts_presence,
    missing_parts,
    color,
    exif,
    fraud,
    review,
    aborted: bool,
    abort_reason: str | None,
    images_count: int
):
    return {
        "session_id": session_id,
        "damage": damage,
        "parts_presence": parts_presence,
        "missing_parts": missing_parts,
        "color_detected": color,
        "vehicle_color_db": None,
        "color_match": False,
        "exif_geo": exif,
        "fraud_flags": fraud,
        "review_flags": review,
        "aborted": aborted,
        "abort_reason": abort_reason,
        "images_in_session": images_count
    }