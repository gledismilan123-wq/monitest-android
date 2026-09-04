"""
pdf_export.py
Genera il PDF di una scheda usando il LAYOUT salvato per quella maschera
(vedi report_templates.py / ui_template_editor.py): ogni campo, il logo e il
titolo vengono disegnati esattamente dove sono stati posizionati nell'editor.

Sotto ai campi posizionati vengono aggiunte in automatico, una sotto l'altra,
le eventuali tabelle (attrezzature, dettaglio) e le foto.
"""

import os
from datetime import datetime

from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from app.paths import asset_path, reports_dir
from app.forms_schema import EQUIPMENT_TABLE_COLUMNS
from app import report_templates as rt

INK = colors.HexColor("#151A1E")
STEEL = colors.HexColor("#2F5C94")
LINE = colors.HexColor("#D6DBE0")


def _field_display_value(field_key, data):
    value = data.get(field_key, "")
    note = data.get(field_key + "_note", "")
    if note:
        value = f"{value} - {note}".strip(" -")
    return str(value) if value is not None else ""


def _draw_field(c, el, data, page_h):
    x = el["x"]
    y_top = el["y"]
    w = el["w"]
    h = el["h"]
    y_bottom = page_h - y_top - h

    if not el.get("visible", True):
        return

    value = _field_display_value(el.get("field_key", ""), data)

    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.rect(x, y_bottom, w, h, stroke=1, fill=0)

    label_w = el.get("label_width", 150)
    font_size = el.get("font_size", 9)

    c.setFont("Helvetica", max(font_size - 2, 6))
    c.setFillColor(colors.HexColor("#4B565C"))
    c.drawString(x + 4, y_bottom + h - 11, el.get("label", ""))

    if value:
        c.setFont("Helvetica-Bold", font_size)
        c.setFillColor(INK)
        max_value_width = w - label_w - 6 if w - label_w > 40 else w - 8
        value_x = x + label_w if w - label_w > 40 else x + 4
        value_y = y_bottom + (2 if h <= 24 else h - 24)

        lines = simpleSplit(value, "Helvetica-Bold", font_size, max_value_width)
        for i, line in enumerate(lines[:3]):
            c.drawString(value_x, value_y - i * (font_size + 2), line)


def _draw_static_text(c, el, page_h):
    x, y_top, w, h = el["x"], el["y"], el["w"], el["h"]
    y_bottom = page_h - y_top - h
    font_name = "Helvetica-Bold" if el.get("bold") else "Helvetica"
    font_size = el.get("font_size", 9)
    c.setFont(font_name, font_size)
    c.setFillColor(INK)
    align = el.get("align", "left")
    lines = simpleSplit(el.get("text", ""), font_name, font_size, w)
    for i, line in enumerate(lines):
        ly = y_bottom + h - (i + 1) * (font_size + 2)
        if align == "center":
            c.drawCentredString(x + w / 2, ly, line)
        elif align == "right":
            c.drawRightString(x + w, ly, line)
        else:
            c.drawString(x, ly, line)


def _draw_photo(c, el, photo_path, page_h):
    x, y_top, w, h = el["x"], el["y"], el["w"], el["h"]
    y_bottom = page_h - y_top - h
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.rect(x, y_bottom, w, h, stroke=1, fill=0)
    if photo_path and os.path.exists(photo_path):
        try:
            c.drawImage(photo_path, x + 2, y_bottom + 2, width=w - 4, height=h - 4,
                        preserveAspectRatio=True, mask="auto")
        except Exception:
            pass


def _draw_logo(c, el, page_h):
    logo_path = asset_path("assets", "logo.png")
    if not os.path.exists(logo_path):
        return
    x, y_top, w, h = el["x"], el["y"], el["w"], el["h"]
    y_bottom = page_h - y_top - h
    try:
        c.drawImage(logo_path, x, y_bottom, width=w, height=h,
                    preserveAspectRatio=True, mask="auto")
    except Exception:
        pass


def _simple_table_flowable(columns, rows, small=False):
    font_size = 6.5 if small else 8
    header = [Paragraph(f"<b>{c}</b>", ParagraphStyle(name="h", fontSize=font_size, textColor=colors.white))
              for c in columns]
    data = [header]
    for r in rows:
        if isinstance(r, dict):
            data.append([Paragraph(str(r.get(c, "")), ParagraphStyle(name="c", fontSize=font_size)) for c in columns])
        else:
            data.append([Paragraph(str(v), ParagraphStyle(name="c", fontSize=font_size)) for v in r])
    if len(data) == 1:
        return None
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), STEEL),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def export_inspection_pdf(schema, mask_type, report_number, data, output_path=None):
    if output_path is None:
        safe_name = report_number.replace("/", "-").replace("\\", "-")
        output_path = os.path.join(reports_dir(), f"{safe_name}_{mask_type.replace(' ', '_')}.pdf")

    template = rt.load_template(mask_type)
    page_w, page_h = template.get("page_w", rt.PAGE_W), template.get("page_h", rt.PAGE_H)

    c = pdfcanvas.Canvas(output_path, pagesize=(page_w, page_h))

    max_field_bottom_y = 96  # y (dall'alto) sotto cui iniziano tabelle
    photos_data = data.get("_photos")
    photo_elements = [el for el in template["elements"] if el["type"] == "photo"]

    for el in template["elements"]:
        if el["type"] == "logo":
            _draw_logo(c, el, page_h)
        elif el["type"] == "static_text":
            _draw_static_text(c, el, page_h)
        elif el["type"] == "field":
            _draw_field(c, el, data, page_h)
            if el.get("visible", True):
                max_field_bottom_y = max(max_field_bottom_y, el["y"] + el["h"])

    if isinstance(photos_data, dict) and photos_data.get("items") and photo_elements:
        # Nuovo formato: riproduce ESATTAMENTE la disposizione (posizione e
        # dimensione) sistemata nella maschera, in scala nell'area foto del layout.
        region_x0 = min(e["x"] for e in photo_elements)
        region_y0 = min(e["y"] for e in photo_elements)
        region_x1 = max(e["x"] + e["w"] for e in photo_elements)
        region_y1 = max(e["y"] + e["h"] for e in photo_elements)
        region_w, region_h = region_x1 - region_x0, region_y1 - region_y0
        board_w = photos_data.get("board_w") or 1
        board_h = photos_data.get("board_h") or 1
        for item in photos_data["items"]:
            mapped = {
                "x": region_x0 + (item["x"] / board_w) * region_w,
                "y": region_y0 + (item["y"] / board_h) * region_h,
                "w": (item["w"] / board_w) * region_w,
                "h": (item["h"] / board_h) * region_h,
            }
            _draw_photo(c, mapped, item.get("path"), page_h)
        max_field_bottom_y = max(max_field_bottom_y, region_y1)
    else:
        # Formato precedente (o nessuna foto caricata): un percorso per ogni
        # riquadro foto del layout, in ordine.
        photos_list = photos_data if isinstance(photos_data, list) else []
        for el in photo_elements:
            idx = int(el["id"].split(":")[-1])
            photo_path = photos_list[idx] if idx < len(photos_list) else None
            _draw_photo(c, el, photo_path, page_h)
            max_field_bottom_y = max(max_field_bottom_y, el["y"] + el["h"])

    cursor_y_top = max_field_bottom_y + 14  # prossimo contenuto (tabelle), da y dall'alto
    cursor_y_top = min(cursor_y_top, page_h - 140)  # margine di sicurezza: mai troppo vicino al fondo

    def y_bottom_for(y_top, h):
        return page_h - y_top - h

    # Tabella attrezzature
    if schema.get("equipment_table"):
        eq_rows = data.get("_equipment_rows", [])
        table = _simple_table_flowable(EQUIPMENT_TABLE_COLUMNS, eq_rows)
        if table:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.HexColor("#4B565C"))
            c.drawString(30, y_bottom_for(cursor_y_top, 10), "Attrezzature usate")
            cursor_y_top += 14
            tw, th = table.wrapOn(c, page_w - 60, page_h)
            table.drawOn(c, 30, y_bottom_for(cursor_y_top, th))
            cursor_y_top += th + 16

    # Tabella di dettaglio
    detail = schema.get("detail_table")
    if detail:
        rows_data = data.get("_detail_rows", [])
        table = _simple_table_flowable(detail["columns"], rows_data, small=True)
        if table:
            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(colors.HexColor("#4B565C"))
            c.drawString(30, y_bottom_for(cursor_y_top, 10), detail["label"])
            cursor_y_top += 14
            tw, th = table.wrapOn(c, page_w - 60, page_h)
            table.drawOn(c, 30, y_bottom_for(cursor_y_top, th))
            cursor_y_top += th + 16

    c.showPage()
    c.save()
    return output_path
