_sessions = {}

def save_image(session_id, tipo, img_bytes, lat, lon):
    if session_id not in _sessions:
        _sessions[session_id] = {"images": [], "notes": []}
    _sessions[session_id]["images"].append({
        "tipo": tipo,
        "img_bytes": img_bytes,
        "lat": lat,
        "lon": lon
    })

def save_note(session_id, note):
    if session_id not in _sessions:
        _sessions[session_id] = {"images": [], "notes": []}
    _sessions[session_id]["notes"].append(note)

def get_result(session_id):
    return _sessions.get(session_id, {})

def generate_report(session_id):
    # Aquí puedes generar un PDF o devolver el JSON
    return _sessions.get(session_id, {})