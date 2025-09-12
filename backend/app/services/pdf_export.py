from io import BytesIO
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from textwrap import wrap
import base64
import datetime

def _wrap(text: str, width: int = 110) -> str:
    out = []
    for line in text.splitlines():
        if not line.strip():
            out.append("")
            continue
        out.extend(wrap(line, width=width))
    return "\n".join(out)

def build_images_table(images: List[Dict[str, Any]], max_w: int = 520):
    """
    Crea flujo (list) de elementos reportlab con miniaturas y datos de calidad.
    Cada imagen en session_repo debería tener estructura {"analysis": {...}, "raw_bytes": ..., etc}.
    """
    flow = []
    if not images:
        return flow
    styles = getSampleStyleSheet()
    title = Paragraph("<b>Imágenes Capturadas</b>", styles["Heading3"])
    flow.append(title)
    flow.append(Spacer(1, 6))

    rows = [["#", "Calidad", "Scratches", "LapVar", "EdgeDen", "Vista"]]
    for idx, im in enumerate(images, start=1):
        an = im.get("analysis", {})
        qs = an.get("quality_status", "-")
        sc = (an.get("scratch") or {}).get("count", 0)
        pre = an.get("preproc_metrics") or {}
        lap = pre.get("lap_var", "-")
        edge = pre.get("edge_density", "-")
        view = im.get("photo_key") or im.get("tipo") or "-"
        rows.append([idx, qs, sc, lap, edge, view])

    tbl = Table(rows, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    flow.append(tbl)
    flow.append(Spacer(1, 10))

    # Miniaturas (si raw guardado o debug overlay b64)
    for idx, im in enumerate(images, start=1):
        an = im.get("analysis", {})
        b64_overlay = (an.get("debug_images") or {}).get("overlay_b64")
        raw_bytes = im.get("raw") or im.get("raw_bytes")
        # prefer overlay if exists
        img_bytes = None
        if b64_overlay:
            try:
                img_bytes = base64.b64decode(b64_overlay)
            except Exception:
                pass
        if not img_bytes and raw_bytes:
            img_bytes = raw_bytes

        if not img_bytes:
            continue
        flow.append(Paragraph(f"<b>Imagen {idx}</b>", styles["Normal"]))
        try:
            img = ImageReader(BytesIO(img_bytes))
            iw, ih = img.getSize()
            scale = 1.0
            if iw > max_w:
                scale = max_w / float(iw)
            w = iw * scale
            h = ih * scale
            # Canvas image will be added later (we are using SimpleDocTemplate -> need flowable)
            from reportlab.platypus import Image
            flow.append(Image(BytesIO(img_bytes), width=w, height=h))
        except Exception:
            flow.append(Paragraph("No se pudo renderizar imagen.", styles["Italic"]))
        flow.append(Spacer(1, 6))
    return flow

def markdown_to_pdf_bytes(markdown_text: str, doc_meta: Dict[str, Any]) -> bytes:
    """
    Conversión simple Markdown -> PDF (subset):
    - Negritas ** ** y encabezados # se dejan como texto plano estilizado parcial.
    - Para un reporte formal podrías migrar a md->HTML->WeasyPrint.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            leftMargin=36, rightMargin=36,
                            topMargin=42, bottomMargin=42)
    story = []
    styles = getSampleStyleSheet()

    title = doc_meta.get("pdf_title") or "Reporte Inspección"
    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generado: {datetime.datetime.utcnow().isoformat()}Z", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Procesamiento simple del markdown a párrafos
    # Partimos por secciones separadas por --- ya producido en build_markdown_report
    sections = markdown_text.split("\n---\n")
    for sec in sections:
        sec_stripped = sec.strip()
        if not sec_stripped:
            continue
        # Quitar # inicial para encabezados
        lines = sec_stripped.splitlines()
        heading = None
        if lines and lines[0].startswith("#"):
            heading = lines[0].lstrip("# ").strip()
            content = "\n".join(lines[1:])
        else:
            content = sec_stripped
        if heading:
            story.append(Paragraph(f"<b>{heading}</b>", styles["Heading3"]))
        # Reemplazo muy básico de **bold**
        content = content.replace("**", "")
        # persist wrap
        content = _wrap(content, width=115)
        for paragraph in content.split("\n\n"):
            story.append(Paragraph(paragraph.replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 4))
        story.append(Spacer(1, 8))

    # Adjuntar tabla de imágenes si se pasó (desde build_pdf_report)
    images_list = doc_meta.get("images_list")
    if images_list:
        story.extend(build_images_table(images_list))

    doc.build(story)
    return buffer.getvalue()

def build_full_pdf(doc: Dict[str, Any]) -> bytes:
    """
    Crea el PDF completo usando el markdown ya existente + miniaturas de imágenes.
    doc debe contener 'report_markdown' y opcional 'images'.
    """
    md = doc.get("report_markdown", "")
    images = doc.get("images", [])
    meta = {
        "pdf_title": doc.get("pdf_title") or "Reporte Inspección Vehicular",
        "images_list": images
    }
    return markdown_to_pdf_bytes(md, meta)