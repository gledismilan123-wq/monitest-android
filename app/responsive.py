"""
responsive.py
Aiuta le schermate ad adattarsi a qualsiasi risoluzione (telefono normale,
Galaxy Z Fold 8 chiuso o aperto, tablet...), sullo stesso principio dei
"breakpoint" usati nei siti web responsive: si guarda quanto e' larga la
finestra ORA (Kivy la ridimensiona da solo quando il telefono si piega/apre)
e si sceglie il numero di colonne di conseguenza.

- compact  (< 600dp): telefono in verticale, copertina del Fold chiuso.
- medium   (600-839dp): Fold aperto in verticale, tablet piccolo.
- expanded (>= 840dp): Fold aperto in orizzontale, tablet grande.
"""

from kivy.core.window import Window
from kivy.event import EventDispatcher
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty


def _classify(width_dp):
    if width_dp < 600:
        return "compact"
    if width_dp < 840:
        return "medium"
    return "expanded"


class Breakpoints(EventDispatcher):
    """Singolo oggetto condiviso da tutte le schermate: osserva Window.size e
    espone la fascia corrente. Usare bind(breakpoint=...) per reagire ai
    cambi (es. rotazione, apertura/chiusura del Fold)."""

    breakpoint = StringProperty("compact")
    width_dp = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(size=self._on_window_size)
        self._on_window_size(Window, Window.size)

    def _on_window_size(self, window, size):
        width_dp = size[0] / (dp(1))
        self.width_dp = width_dp
        self.breakpoint = _classify(width_dp)

    def columns(self, one=1, two=2, three=3):
        # Ricalcola sempre dalla larghezza ATTUALE della finestra (non da un
        # valore salvato): su Kivy, subito dopo l'avvio, la finestra vera puo'
        # essere creata/ridimensionata un istante dopo che questo oggetto e'
        # stato inizializzato, quindi affidarsi solo al valore gia' salvato in
        # 'breakpoint' rischierebbe di usare una misura non piu' aggiornata.
        current = _classify(Window.size[0] / dp(1))
        if current == "compact":
            return one
        if current == "medium":
            return two
        return three


breakpoints = Breakpoints()


def bind_resize(callback):
    """Chiama callback() ad ogni cambio di dimensione della finestra (rotazione,
    apertura/chiusura del Fold...). Si aggancia direttamente a Window.size
    (non al solo cambio di 'fascia') cosi' scatta in modo affidabile ad ogni
    ridimensionamento reale, anche quando due ridimensionamenti in rapida
    successione ricadono nella stessa fascia intermedia."""
    Window.bind(size=lambda *_: callback())
