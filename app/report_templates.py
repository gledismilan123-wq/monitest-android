"""
report_templates.py
Gestisce il "layout" (posizione/dimensione di ogni riquadro) del PDF di ogni
maschera. Ogni maschera ha un file JSON in <programma>/templates/<maschera>.json
con la posizione di logo, titolo, ogni campo, e il testo a pie' di pagina.

Le coordinate sono in punti (1/72 di pollice), origine IN ALTO A SINISTRA
(x cresce verso destra, y cresce verso il basso) - piu' intuitivo da editare
a schermo. La conversione al sistema di reportlab (origine in basso) avviene
solo al momento di generare il PDF, in pdf_export.py.
"""

import os
import json

from app.paths import base_dir
from app.forms_schema import get_schema

PAGE_W = 595   # A4 in punti
PAGE_H = 842


def template_path(mask_type):
    folder = os.path.join(base_dir(), "templates")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, mask_type.replace(" ", "_").replace("/", "-") + ".json")


def default_template(mask_type):
    schema = get_schema(mask_type)
    elements = [
        {"id": "logo", "type": "logo", "x": 30, "y": 26, "w": 150, "h": 46},
        {"id": "title", "type": "static_text",
         "text": f"NDT INSPECTION REPORT {schema['title']}",
         "x": 190, "y": 40, "w": 375, "h": 24, "font_size": 13, "bold": True, "align": "center"},
    ]
    y = 96
    for f in schema.get("left_fields", []) + schema.get("right_fields", []):
        elements.append({
            "id": f"field:{f['key']}", "type": "field", "field_key": f["key"], "label": f["label"],
            "x": 30, "y": y, "w": 535, "h": 22, "label_width": 150, "font_size": 9, "visible": True,
        })
        y += 25
    n_photos = schema.get("photo_slots", 0)
    for i in range(n_photos):
        elements.append({
            "id": f"photo:{i}", "type": "photo",
            "x": 30 + i * 115, "y": y + 14, "w": 100, "h": 100,
        })
    elements.append({
        "id": "footer", "type": "static_text",
        "text": "Il risultato dell'ispezione rappresenta un giudizio in buona fede e non "
                "costituisce garanzia di qualita' o utilizzabilita' dell'utensile ispezionato.",
        "x": 30, "y": 812, "w": 535, "h": 20, "font_size": 6.5, "bold": False, "align": "left",
    })
    return {"page_w": PAGE_W, "page_h": PAGE_H, "elements": elements}


def load_template(mask_type):
    path = template_path(mask_type)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            tmpl = json.load(fh)
    else:
        tmpl = default_template(mask_type)
        save_template(mask_type, tmpl)
        return tmpl

    # Migrazione automatica: se la maschera prevede foto e il layout salvato
    # non le ha ancora (es. layout creato prima di questa funzione), le
    # aggiunge sotto ai campi senza toccare le posizioni gia' personalizzate.
    schema = get_schema(mask_type)
    n_photos = schema.get("photo_slots", 0)
    existing_photo_ids = {el["id"] for el in tmpl["elements"] if el["type"] == "photo"}
    changed = False
    if n_photos:
        field_bottom = max(
            [el["y"] + el["h"] for el in tmpl["elements"] if el["type"] == "field" and el.get("visible", True)],
            default=96,
        )
        for i in range(n_photos):
            pid = f"photo:{i}"
            if pid not in existing_photo_ids:
                tmpl["elements"].append({
                    "id": pid, "type": "photo",
                    "x": 30 + i * 115, "y": field_bottom + 14, "w": 100, "h": 100,
                })
                changed = True
    if changed:
        save_template(mask_type, tmpl)
    return tmpl


def save_template(mask_type, data):
    with open(template_path(mask_type), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def reset_template(mask_type):
    tmpl = default_template(mask_type)
    save_template(mask_type, tmpl)
    return tmpl
