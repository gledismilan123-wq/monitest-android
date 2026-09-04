"""
database.py
Gestione del database SQLite dell'applicazione.
"""

import sqlite3
import hashlib
import os
import json
from datetime import datetime
from app.paths import data_dir

DB_PATH = os.path.join(data_dir(), "monitest.db")

# Le 15 maschere di ispezione, in ordine di visualizzazione nella dashboard
MASK_TYPES = [
    "DrillCollar",
    "DrillPipe",
    "HWDP",
    "Eddy Current",
    "Dry Penetrant",
    "Lifting Gear",
    "MPI",
    "Lifting Gear 2",
    "Proof Load Test",
    "Rotary Tool Description",
    "Thorough Examination",
    "Ultrasonic",
    "UT-Thickness",
    "Visual",
    "Workorder",
]


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'operatore',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    # Elenchi valori per ogni campo a tendina (Customer, Inspector, Material, Standards, ecc.)
    # field_key identifica IL CAMPO (es. 'customer', 'material', 'standard'); value e' la voce dell'elenco.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS field_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_key TEXT NOT NULL,
            value TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Una riga per ogni scheda/certificato compilato, qualunque sia la maschera.
    # 'data_json' contiene TUTTI i valori dei campi della maschera (compresi i percorsi delle foto).
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inspections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mask_type TEXT NOT NULL,
            report_number TEXT,
            customer TEXT,
            data_json TEXT NOT NULL,
            created_by INTEGER REFERENCES users(id),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?,?,?,?,?)",
            ("admin", _hash_password("admin"), "Amministratore", "admin", datetime.now().isoformat()),
        )
        conn.commit()

    conn.close()


# ---------- Utenti ----------

def verify_login(username: str, password: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ? AND active = 1", (username,)).fetchone()
    conn.close()
    if row and row["password_hash"] == _hash_password(password):
        return row
    return None


def create_user(username, password, full_name, role="operatore"):
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?,?,?,?,?)",
        (username, _hash_password(password), full_name, role, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def list_users():
    conn = get_connection()
    rows = conn.execute("SELECT id, username, full_name, role, active FROM users ORDER BY full_name").fetchall()
    conn.close()
    return rows


def set_user_active(user_id, active: bool):
    conn = get_connection()
    conn.execute("UPDATE users SET active = ? WHERE id = ?", (1 if active else 0, user_id))
    conn.commit()
    conn.close()


# ---------- Opzioni per i campi a tendina ----------

def list_field_options(field_key, include_inactive=False):
    conn = get_connection()
    if include_inactive:
        rows = conn.execute(
            "SELECT * FROM field_options WHERE field_key = ? ORDER BY value", (field_key,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM field_options WHERE field_key = ? AND active = 1 ORDER BY value", (field_key,)
        ).fetchall()
    conn.close()
    return rows


def add_field_option(field_key, value):
    conn = get_connection()
    conn.execute("INSERT INTO field_options (field_key, value, active) VALUES (?,?,1)", (field_key, value))
    conn.commit()
    conn.close()


def set_field_option_active(option_id, active: bool):
    conn = get_connection()
    conn.execute("UPDATE field_options SET active = ? WHERE id = ?", (1 if active else 0, option_id))
    conn.commit()
    conn.close()


def delete_field_option(option_id):
    conn = get_connection()
    conn.execute("DELETE FROM field_options WHERE id = ?", (option_id,))
    conn.commit()
    conn.close()


# ---------- Schede di ispezione ----------

def next_report_number():
    """
    Genera il prossimo numero di report, sequenziale su TUTTE le maschere
    (esattamente come M.2026_5551, M.2026_5552... nel tuo programma attuale).
    Usa l'id autoincrementale della tabella unica 'inspections', quindi la
    sequenza e' naturalmente condivisa fra tutte le 15 maschere.
    """
    conn = get_connection()
    row = conn.execute("SELECT seq FROM sqlite_sequence WHERE name='inspections'").fetchone()
    conn.close()
    next_id = (row["seq"] + 1) if row else 1
    year = datetime.now().year
    return f"M.{year}_{next_id}"


def save_inspection(mask_type, report_number, customer, data_dict, user_id, inspection_id=None):
    conn = get_connection()
    now = datetime.now().isoformat()
    payload = json.dumps(data_dict, ensure_ascii=False)
    if inspection_id:
        conn.execute(
            "UPDATE inspections SET report_number=?, customer=?, data_json=?, updated_at=? WHERE id=?",
            (report_number, customer, payload, now, inspection_id),
        )
    else:
        conn.execute(
            "INSERT INTO inspections (mask_type, report_number, customer, data_json, created_by, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (mask_type, report_number, customer, payload, user_id, now, now),
        )
        inspection_id = conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    conn.commit()
    conn.close()
    return inspection_id


def list_inspections(mask_type):
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, report_number, customer, created_at FROM inspections WHERE mask_type=? ORDER BY id DESC",
        (mask_type,),
    ).fetchall()
    conn.close()
    return rows


def search_inspections(mask_type, text=None, customer=None, inspector=None,
                        date_from=None, date_to=None):
    """
    Ricerca schede di una maschera con filtri opzionali.
    - text: cerca liberamente dentro numero report, cliente, e in tutti i valori
      dei campi salvati (nome, seriale, ecc. - qualunque campo della maschera).
    - customer / inspector: filtro esatto (facoltativo) sui rispettivi elenchi.
    - date_from / date_to: filtro sulla data di creazione (formato ISO YYYY-MM-DD).
    """
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM inspections WHERE mask_type=? ORDER BY id DESC", (mask_type,)
    ).fetchall()
    conn.close()

    results = []
    for row in rows:
        data = json.loads(row["data_json"])
        if customer and (row["customer"] or "").strip().lower() != customer.strip().lower():
            continue
        if inspector and str(data.get("inspector", "")).strip().lower() != inspector.strip().lower():
            continue
        if date_from and row["created_at"][:10] < date_from:
            continue
        if date_to and row["created_at"][:10] > date_to:
            continue
        if text:
            haystack = " ".join([
                row["report_number"] or "", row["customer"] or "",
                *[str(v) for v in data.values() if isinstance(v, (str, int, float))]
            ]).lower()
            if text.strip().lower() not in haystack:
                continue
        result = dict(row)
        result["data"] = data
        results.append(result)
    return results


def get_field_history(field_key, limit=20):
    """Valori gia' usati in passato per un campo di testo (in tutte le maschere),
    dai piu' usati ai meno usati - alimenta i suggerimenti automatici in scrittura."""
    from collections import Counter
    conn = get_connection()
    rows = conn.execute("SELECT data_json FROM inspections").fetchall()
    conn.close()
    counter = Counter()
    for row in rows:
        try:
            d = json.loads(row["data_json"])
        except (json.JSONDecodeError, TypeError):
            continue
        v = d.get(field_key)
        if isinstance(v, str) and v.strip():
            counter[v.strip()] += 1
    return [v for v, _ in counter.most_common(limit)]


def get_inspection(inspection_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM inspections WHERE id=?", (inspection_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    result["data"] = json.loads(result["data_json"])
    return result


def delete_inspection(inspection_id):
    conn = get_connection()
    conn.execute("DELETE FROM inspections WHERE id=?", (inspection_id,))
    conn.commit()
    conn.close()
