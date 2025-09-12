from datetime import datetime
from typing import Dict, Any, List

SECTION_BAR = "\n---\n"

def _fmt_damage(damage: List[Dict[str, Any]]) -> str:
    if not damage:
        return "_Sin detecciones de daño._"
    lines = []
    for d in damage:
        lbl = d.get("label", "damage")
        conf = d.get("confidence", 0)
        box = d.get("box", [])
        lines.append(f"- {lbl} ({conf*100:.1f}%) box={box}")
    return "\n".join(lines)

def _fmt_parts(parts_presence: Dict[str, Any], missing: List[str]) -> str:
    if not parts_presence:
        return "_Sin análisis de partes._"
    lines = []
    for k, v in parts_presence.items():
        lines.append(
            f"- {k}: {'OK' if v.get('present') else 'NO'} ({v.get('confidence',0)*100:.1f}%)"
        )
    if missing:
        lines.append(f"\nFaltantes: {', '.join(missing)}")
    return "\n".join(lines)

def _fmt_verdict(verdict: Dict[str, Any] | None) -> str:
    if not verdict:
        return "_Sin veredicto (posible aborto o fallo geo)._"
    conds = verdict.get("conditions", [])
    conds_md = "".join([f"  - {c}\n" for c in conds]) if conds else "  - (sin condiciones)\n"
    return (
        f"Veredicto: **{verdict.get('verdict','N/A')}**  \n"
        f"Puntaje: {verdict.get('score','?')}  \n"
        f"Condiciones:\n{conds_md}"
    )

def _fmt_flags(title: str, items: List[str]) -> str:
    if not items:
        return f"{title}: _Ninguno_"
    return f"{title}:\n" + "\n".join([f"- {f}" for f in items])

def _fmt_notes(notes: List[str]) -> str:
    if not notes:
        return "_Sin notas manuales._"
    return "\n".join([f"- {n}" for n in notes])

def _fmt_identity(identity_payload: Dict[str, Any] | None, identity_validated: bool | None) -> str:
    if not identity_payload:
        return "_No se registró validación de identidad._"
    driver = identity_payload.get("matched_driver") or identity_payload
    name = driver.get("name") or driver.get("full_name") or "N/D"
    doc = driver.get("document") or "N/D"
    valid_txt = "VALIDADA" if identity_validated else "NO COINCIDE"
    return (
        f"Estado: **{valid_txt}**  \n"
        f"Nombre (DB): {name}  \n"
        f"Documento: {doc}"
    )

def _fmt_vehicle(vehicle: Dict[str, Any] | None, history: Dict[str, Any] | None) -> str:
    if not vehicle:
        return "_Sin datos de vehículo._"
    lines = [
        f"Placa: **{vehicle.get('plate','N/D')}**",
        f"Marca / Modelo / Año: {vehicle.get('brand','?')} / {vehicle.get('model','?')} / {vehicle.get('year','?')}",
        f"Color DB: {vehicle.get('color','?')}",
        f"Propietario (DB): {vehicle.get('owner','?')}",
    ]
    if history:
        lines.append("")
        lines.append("Historial:")
        lines.append(f"- Infracciones: {history.get('infractions',0)}")
        lines.append(f"- Dueños previos: {history.get('previous_owners',1)}")
        lines.append(f"- Técnica vigente: {'Sí' if history.get('tech_ok',True) else 'No'}")
        notes = history.get("notes") or []
        if notes:
            lines.append("- Notas:")
            for n in notes:
                lines.append(f"  - {n}")
    return "\n".join(lines)

def _fmt_quality(images: List[Dict[str, Any]]) -> str:
    if not images:
        return "_Sin imágenes en sesión._"
    laps = []
    edges = []
    scratches_total = 0
    rows = []
    for idx, im in enumerate(images, start=1):
        an = im.get("analysis") or {}
        pre = an.get("preproc_metrics") or {}
        lap = pre.get("lap_var")
        edge = pre.get("edge_density")
        qs = an.get("quality_status", "n/a")
        sc = (an.get("scratch") or {}).get("count", 0)
        scratches_total += sc
        laps.append(lap if lap is not None else 0)
        edges.append(edge if edge is not None else 0)
        rows.append(f"| {idx} | {lap if lap is not None else '-'} | {edge if edge is not None else '-'} | {qs} | {sc} |")
    avg_lap = round(sum(laps)/len(laps),2) if laps else 0
    avg_edge = round(sum(edges)/len(edges),4) if edges else 0
    table = (
        "| Img | LapVar | EdgeDensity | Calidad | Scratches |\n"
        "|-----|--------|-------------|---------|-----------|\n" +
        "\n".join(rows)
    )
    return (
        f"Promedio LapVar: {avg_lap}  \n"
        f"Promedio EdgeDensity: {avg_edge}  \n"
        f"Total scratches candidatos: {scratches_total}\n\n" +
        table
    )

def build_markdown_report(doc: Dict[str, Any]) -> str:
    # doc contiene FinalizeResponse + campos auxiliares
    header = f"# Reporte Inspección\n\nID Sesión: **{doc.get('session_id')}**  \nFecha: {datetime.utcnow().isoformat()}Z\n"
    status = f"Estado final: **{doc.get('status','N/A')}**"
    identity_section = (
        "## Identidad\n" +
        _fmt_identity(doc.get("identity_payload"), doc.get("identity_validated")) +
        SECTION_BAR
    )
    vehicle_section = (
        "## Vehículo\n" +
        _fmt_vehicle(doc.get("vehicle"), doc.get("vehicle_history")) +
        SECTION_BAR
    )
    quality_section = "## Calidad de Imágenes\n" + _fmt_quality(doc.get("images", [])) + SECTION_BAR
    damage_section = "## Daños Detectados\n" + _fmt_damage(doc.get("damage_detections", [])) + SECTION_BAR
    parts_section = "## Partes Detectadas\n" + _fmt_parts(doc.get("parts_presence", {}), doc.get("missing_parts", [])) + SECTION_BAR
    verdict_section = "## Veredicto\n" + _fmt_verdict(doc.get("verdict")) + SECTION_BAR
    flags_section = (
        "## Flags\n" +
        _fmt_flags("Fraud Flags", doc.get("fraud_flags", [])) + "\n" +
        _fmt_flags("Review Flags", doc.get("review_flags", [])) +
        SECTION_BAR
    )
    notes_section = "## Notas Manuales\n" + _fmt_notes(doc.get("notes", [])) + SECTION_BAR

    color_match_line = ""
    if doc.get("color_match") is not None:
        color_match_line = f"\nColor coincide con DB: **{'Sí' if doc['color_match'] else 'No'}**\n"

    return (
        header + status + "\n\n" +
        identity_section +
        vehicle_section +
        quality_section +
        damage_section +
        parts_section +
        verdict_section +
        flags_section +
        notes_section +
        f"Color referencial DB: {doc.get('vehicle_color_db','?')}{color_match_line}"
    )