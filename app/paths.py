"""
paths.py
Percorsi centralizzati dell'applicazione (versione Android/Kivy).

Su Android i dati (database, foto, PDF esportati) vivono nella cartella privata
dell'app, ottenuta da Kivy con App.user_data_dir e impostata qui all'avvio con
set_base_dir(). In sviluppo locale su PC (senza set_base_dir chiamato) si usa
una cartella "devdata" accanto al progetto, cosi' si puo' lanciare `python
main.py` su Windows per controllare a occhio schermate e layout.

asset_path() punta invece alle risorse in sola lettura incluse nel pacchetto
(es. il logo): sono file del progetto, mai scritti, quindi restano relativi
alla cartella del codice sorgente sia su PC sia (una volta impacchettati
dentro l'apk ed estratti da python-for-android) su Android.
"""

import os

_override_base_dir = None


def set_base_dir(path):
    """Chiamata una volta all'avvio dell'app (vedi main.py) con la cartella
    dati privata e scrivibile fornita dal sistema operativo."""
    global _override_base_dir
    _override_base_dir = path
    os.makedirs(path, exist_ok=True)


def base_dir():
    if _override_base_dir:
        return _override_base_dir
    path = os.path.join(_project_root(), "devdata")
    os.makedirs(path, exist_ok=True)
    return path


def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def asset_path(*parts):
    return os.path.join(_project_root(), *parts)


def data_dir():
    path = os.path.join(base_dir(), "data")
    os.makedirs(path, exist_ok=True)
    return path


def photos_dir():
    path = os.path.join(base_dir(), "assets", "photos")
    os.makedirs(path, exist_ok=True)
    return path


def reports_dir():
    path = os.path.join(base_dir(), "reports")
    os.makedirs(path, exist_ok=True)
    return path
