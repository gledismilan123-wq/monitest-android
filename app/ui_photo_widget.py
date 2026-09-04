"""
ui_photo_widget.py
Riquadri foto per la maschera (versione touch): tocca un riquadro per
scattare una foto con la fotocamera o sceglierne una dalla galleria.

A differenza della versione Windows non si trascina/ridimensiona a mano
(quell'editor visivo e' rimandato a dopo): la disposizione delle foto nel
PDF resta comunque ordinata, perche' ogni riquadro occupa una posizione
fissa in una griglia di riferimento salvata insieme al percorso della foto
(stesso formato dati "_photos" gia' usato da pdf_export.py).
"""

import os
import uuid

from kivy.metrics import dp
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogButtonContainer
from kivy.uix.image import Image

from app.paths import photos_dir
from app.responsive import breakpoints, bind_resize
from app import theme

SLOT_SIZE = dp(110)
GRID_GAP = dp(12)


class PhotoSlot(MDBoxLayout):
    def __init__(self, index, on_changed, **kwargs):
        super().__init__(orientation="vertical", size_hint=(None, None),
                          width=SLOT_SIZE, height=SLOT_SIZE + dp(4),
                          md_bg_color=theme.PANEL, radius=[dp(8)] * 4, **kwargs)
        self.index = index
        self.on_changed = on_changed
        self.path = None

        self.image = Image(size_hint=(1, 1), allow_stretch=True, keep_ratio=True)
        self.placeholder = MDLabel(text="Foto\ntocca per aggiungere", halign="center",
                                    theme_text_color="Custom", text_color=theme.MUTED_LIGHT,
                                    font_style="Label", role="small")
        self.add_widget(self.placeholder)

        from kivy.uix.behaviors import ButtonBehavior
        from kivy.uix.widget import Widget

        class Tappable(ButtonBehavior, Widget):
            pass

        self._tap_layer = Tappable(size_hint=(1, 1))
        self._tap_layer.bind(on_release=lambda *_: self._on_tap())
        self.add_widget(self._tap_layer)

    def _on_tap(self):
        actions = []
        if platform == "android":
            actions.append(("Scatta foto", self._take_photo))
        actions.append(("Scegli da galleria", self._pick_photo))
        if self.path:
            actions.append(("Rimuovi foto", self._remove_photo))
        self._show_menu(actions)

    def _show_menu(self, actions):
        buttons = []
        dialog_ref = {}

        def make_cb(fn):
            def _cb(*_):
                dialog_ref["dialog"].dismiss()
                fn()
            return _cb

        for label, fn in actions:
            buttons.append(MDButton(MDButtonText(text=label), style="text",
                                     on_release=make_cb(fn)))
        buttons.append(MDButton(MDButtonText(text="Annulla"), style="text",
                                 on_release=lambda *_: dialog_ref["dialog"].dismiss()))
        dialog = MDDialog(
            MDDialogHeadlineText(text="Foto"),
            MDDialogButtonContainer(*buttons),
        )
        dialog_ref["dialog"] = dialog
        dialog.open()

    def _take_photo(self):
        from plyer import camera
        os.makedirs(photos_dir(), exist_ok=True)
        out_path = os.path.join(photos_dir(), f"{uuid.uuid4().hex}.jpg")
        try:
            camera.take_picture(out_path, lambda p: self._on_photo_ready(p))
        except NotImplementedError:
            pass

    def _pick_photo(self):
        from plyer import filechooser
        try:
            filechooser.open_file(
                title="Scegli una foto",
                filters=[("Immagini", "*.jpg", "*.jpeg", "*.png")],
                on_selection=self._on_filechooser_selection,
            )
        except NotImplementedError:
            pass

    def _on_filechooser_selection(self, selection):
        if not selection:
            return
        self._import_photo(selection[0])

    def _import_photo(self, source_path):
        os.makedirs(photos_dir(), exist_ok=True)
        out_path = os.path.join(photos_dir(), f"{uuid.uuid4().hex}.jpg")
        try:
            from PIL import Image as PILImage
            img = PILImage.open(source_path).convert("RGB")
            img.thumbnail((1600, 1600))
            img.save(out_path, "JPEG", quality=88)
        except Exception:
            import shutil
            shutil.copyfile(source_path, out_path)
        self._on_photo_ready(out_path)

    def _on_photo_ready(self, path):
        if not path or not os.path.exists(path):
            return
        self.path = path
        self.image.source = path
        self.image.reload()
        if self.placeholder in self.children:
            self.remove_widget(self.placeholder)
            self.add_widget(self.image)
            self.add_widget(self._tap_layer)
        if self.on_changed:
            self.on_changed()

    def _remove_photo(self):
        self.path = None
        if self.image in self.children:
            self.remove_widget(self.image)
            self.add_widget(self.placeholder)
            self.add_widget(self._tap_layer)
        if self.on_changed:
            self.on_changed()

    def set_path(self, path):
        if path and os.path.exists(path):
            self._on_photo_ready(path)


class PhotoBoard(MDBoxLayout):
    """Griglia responsive di riquadri foto per una maschera."""

    def __init__(self, n_slots, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, adaptive_height=True, **kwargs)
        self.n_slots = n_slots
        self.board_w = 4 * (SLOT_SIZE + GRID_GAP) - GRID_GAP
        self.board_h = 3 * (SLOT_SIZE + GRID_GAP) - GRID_GAP

        self.grid = MDGridLayout(cols=2, spacing=GRID_GAP, size_hint_y=None, adaptive_height=True)
        self.slots = [PhotoSlot(i, on_changed=lambda: None) for i in range(n_slots)]
        for s in self.slots:
            self.grid.add_widget(s)
        self.add_widget(self.grid)

        bind_resize(self._update_columns)
        self._update_columns()

    def _update_columns(self, *_):
        self.grid.cols = breakpoints.columns(one=2, two=3, three=4)

    def _slot_rect(self, idx):
        per_row = 4
        r, c = divmod(idx, per_row)
        x = c * (SLOT_SIZE + GRID_GAP)
        y = r * (SLOT_SIZE + GRID_GAP)
        return x / dp(1), y / dp(1), SLOT_SIZE / dp(1), SLOT_SIZE / dp(1)

    def get_photo_data(self):
        items = []
        for i, slot in enumerate(self.slots):
            if slot.path:
                x, y, w, h = self._slot_rect(i)
                items.append({"path": slot.path, "x": x, "y": y, "w": w, "h": h})
        return {"board_w": self.board_w / dp(1), "board_h": self.board_h / dp(1), "items": items}

    def set_photo_data(self, data):
        items = data.get("items", []) if isinstance(data, dict) else []
        for i, item in enumerate(items[:self.n_slots]):
            self.slots[i].set_path(item.get("path"))

    def set_paths(self, paths):
        for i, p in enumerate(paths[:self.n_slots]):
            self.slots[i].set_path(p)
