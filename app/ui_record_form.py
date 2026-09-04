from datetime import datetime

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import (
    MDDialog, MDDialogHeadlineText, MDDialogSupportingText,
    MDDialogButtonContainer, MDDialogContentContainer,
)
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from app import database as db
from app.responsive import breakpoints, bind_resize
from app.ui_photo_widget import PhotoBoard
from app import theme


def _toast(text):
    MDSnackbar(MDSnackbarText(text=text), y=dp(24), pos_hint={"center_x": 0.5},
               size_hint_x=0.9).open()


class TextField(MDTextField):
    """Campo di testo semplice, con cronologia dei valori gia' usati come
    suggerimento (equivalente touch dell'autocompletamento della versione PC:
    qui i suggerimenti si vedono aprendo il menu sotto al campo)."""

    def __init__(self, label, value, history_key=None, multiline=False, **kwargs):
        super().__init__(MDTextFieldHintText(text=label), mode="outlined",
                          text=value or "", multiline=multiline, **kwargs)
        if multiline:
            self.size_hint_y = None
            self.height = dp(80)
        self.history_key = history_key
        self._menu = None
        if history_key:
            self.bind(focus=self._on_focus)

    def _on_focus(self, instance, value):
        if not value:
            return
        history = db.get_field_history(self.history_key, limit=8)
        if not history:
            return
        items = [{"text": v, "on_release": lambda v=v: self._pick(v)} for v in history]
        self._menu = MDDropdownMenu(caller=self, items=items)
        self._menu.open()

    def _pick(self, value):
        self.text = value
        if self._menu:
            self._menu.dismiss()


class DropdownField(MDTextField):
    """Campo a tendina: tocca per scegliere un valore fra quelli gestiti in
    Amministrazione > Parametri."""

    def __init__(self, label, value, options_key, **kwargs):
        super().__init__(MDTextFieldHintText(text=label), mode="outlined",
                          text=value or "", readonly=True, **kwargs)
        self.options_key = options_key
        self.bind(focus=self._on_focus)

    def _on_focus(self, instance, value):
        if not value:
            return
        options = [o["value"] for o in db.list_field_options(self.options_key)]
        if not options:
            _toast("Nessuna opzione configurata (Amministrazione > Parametri).")
            return
        items = [{"text": v, "on_release": lambda v=v: self._pick(v)} for v in options]
        menu = MDDropdownMenu(caller=self, items=items)
        menu.open()

    def _pick(self, value):
        self.text = value
        self.focus = False


class TableRowCard(MDCard):
    def __init__(self, columns, row_data, on_remove, **kwargs):
        super().__init__(orientation="vertical", padding=dp(10), spacing=dp(2),
                          md_bg_color=theme.PANEL, radius=[dp(8)] * 4,
                          size_hint=(1, None), **kwargs)
        top = MDBoxLayout(size_hint_y=None, height=dp(28))
        top.add_widget(MDLabel(text=columns[0], bold=True, theme_text_color="Custom",
                                text_color=theme.INK, adaptive_height=True))
        top.add_widget(MDIconButton(icon="trash-can-outline", theme_text_color="Custom",
                                     text_color=theme.ERROR, on_release=lambda *_: on_remove()))
        self.add_widget(top)
        self.add_widget(MDLabel(text=str(row_data.get(columns[0], "")), theme_text_color="Custom",
                                 text_color=theme.MUTED, adaptive_height=True))
        for c in columns[1:]:
            v = row_data.get(c, "")
            if v:
                self.add_widget(MDLabel(text=f"{c}: {v}", theme_text_color="Custom",
                                         text_color=theme.MUTED, font_style="Label", role="small",
                                         adaptive_height=True))
        self.bind(minimum_height=self.setter("height"))


class RecordFormScreen(MDScreen):
    def __init__(self, on_back, **kwargs):
        super().__init__(**kwargs)
        self.name = "record_form"
        self.md_bg_color = theme.BG
        self.on_back = on_back
        self.user = None
        self.mask_type = None
        self.schema = None
        self.record = None
        self.data = {}
        self.field_widgets = {}
        self.table_data = {}
        self.table_boxes = {}
        self.photo_board = None
        self._build_static_ui()

    def _build_static_ui(self):
        root = MDBoxLayout(orientation="vertical")

        header = MDBoxLayout(orientation="horizontal", md_bg_color=theme.PANEL,
                              size_hint_y=None, height=dp(56), padding=[dp(8), dp(8)], spacing=dp(6))
        header.add_widget(MDIconButton(icon="arrow-left", on_release=lambda *_: self._back()))
        self.title_label = MDLabel(text="", bold=True, font_style="Title", role="medium",
                                    theme_text_color="Custom", text_color=theme.INK)
        header.add_widget(self.title_label)
        self.report_label = MDLabel(text="", theme_text_color="Custom", text_color=theme.ACCENT,
                                     bold=True, halign="right")
        header.add_widget(self.report_label)
        header.add_widget(MDButton(MDButtonText(text="PDF"), style="outlined",
                                    on_release=lambda *_: self._export_pdf()))
        root.add_widget(header)

        self.scroll = ScrollView(do_scroll_x=False)
        self.body = MDBoxLayout(orientation="vertical", spacing=dp(14), padding=dp(14),
                                 size_hint_y=None, adaptive_height=True)
        self.scroll.add_widget(self.body)
        root.add_widget(self.scroll)

        self.add_widget(root)
        bind_resize(self._rebuild_fields)

    # ---------------- apertura scheda ----------------

    def open_record(self, user, mask_type, record):
        from app.forms_schema import get_schema
        self.user = user
        self.mask_type = mask_type
        self.schema = get_schema(mask_type)
        self.record = record
        self.data = dict(record["data"]) if record else {}
        self.inspection_id = record["id"] if record else None

        report_number = self.data.get("report_number") or \
            (record["report_number"] if record else db.next_report_number())
        self.data["report_number"] = report_number

        self.title_label.text = self.schema["title"]
        self.report_label.text = f"N. {report_number}"

        self._rebuild_all()

    def _back(self):
        self.on_back()

    # ---------------- costruzione UI dinamica ----------------

    def _rebuild_all(self):
        self.body.clear_widgets()
        self.field_widgets = {}
        self.table_data = {}
        self.table_boxes = {}
        self.photo_board = None

        self.fields_grid = MDGridLayout(cols=1, spacing=dp(12), size_hint_y=None, adaptive_height=True)
        self.body.add_widget(self.fields_grid)
        self._rebuild_fields()

        n_photos = self.schema.get("photo_slots", 0)
        if n_photos:
            self.body.add_widget(MDLabel(text="Foto", bold=True, theme_text_color="Custom",
                                          text_color=theme.MUTED, adaptive_height=True))
            self.photo_board = PhotoBoard(n_photos, size_hint_x=1)
            saved_photos = self.data.get("_photos")
            if isinstance(saved_photos, dict):
                self.photo_board.set_photo_data(saved_photos)
            elif saved_photos:
                self.photo_board.set_paths(saved_photos)
            self.body.add_widget(self.photo_board)

        if self.schema.get("equipment_table"):
            from app.forms_schema import EQUIPMENT_TABLE_COLUMNS
            self._build_table_section("Attrezzature usate", EQUIPMENT_TABLE_COLUMNS, "_equipment_rows")

        if self.schema.get("detail_table"):
            dt = self.schema["detail_table"]
            self._build_table_section(dt["label"], dt["columns"], "_detail_rows")

        save_btn = MDButton(MDButtonText(text="Salva record"), style="filled",
                             size_hint_x=1, on_release=lambda *_: self._save())
        self.body.add_widget(save_btn)

    def _rebuild_fields(self):
        if not self.schema:
            return
        # Se la finestra viene ridimensionata (es. si apre/chiude il Fold)
        # mentre la scheda e' gia' aperta, i campi vengono ricreati per usare
        # il nuovo numero di colonne: prima si salva pero' cio' che l'utente
        # ha gia' scritto, altrimenti verrebbe perso.
        for key, widget in self.field_widgets.items():
            self.data[key] = widget.text
        self.fields_grid.clear_widgets()
        cols = breakpoints.columns(one=1, two=2, three=2)
        self.fields_grid.cols = cols

        all_fields = self.schema.get("left_fields", []) + self.schema.get("right_fields", [])
        if cols == 1:
            columns_fields = [all_fields]
        else:
            def weight(f):
                return 3 if f["type"] == "textarea" else 1
            col_fields, col_weight = [[], []], [0, 0]
            for f in all_fields:
                i = 0 if col_weight[0] <= col_weight[1] else 1
                col_fields[i].append(f)
                col_weight[i] += weight(f)
            columns_fields = col_fields

        for fields in columns_fields:
            col_box = MDBoxLayout(orientation="vertical", spacing=dp(10),
                                   size_hint_y=None, adaptive_height=True)
            for field in fields:
                col_box.add_widget(self._make_field_widget(field))
            self.fields_grid.add_widget(col_box)

    def _make_field_widget(self, field):
        key, label, ftype = field["key"], field["label"], field["type"]

        if ftype == "textarea":
            w = TextField(label, self.data.get(key, ""), multiline=True)
            self.field_widgets[key] = w
            return w

        if ftype in ("dropdown", "dropdown_free"):
            options_key = field.get("field_key", key)
            wrap = MDBoxLayout(orientation="vertical" if ftype == "dropdown_free" else "horizontal",
                                spacing=dp(8), size_hint_y=None, adaptive_height=True)
            dd = DropdownField(label, self.data.get(key, ""), options_key)
            self.field_widgets[key] = dd
            wrap.add_widget(dd)
            if ftype == "dropdown_free":
                note = TextField("Dettagli (facoltativo)", self.data.get(key + "_note", ""),
                                  history_key=key + "_note")
                self.field_widgets[key + "_note"] = note
                wrap.add_widget(note)
            return wrap

        if ftype == "date":
            default = datetime.now().strftime("%Y-%m-%d")
            w = TextField(label, self.data.get(key, default))
            self.field_widgets[key] = w
            return w

        w = TextField(label, self.data.get(key, ""), history_key=key)
        self.field_widgets[key] = w
        return w

    # ---------------- tabelle (attrezzature / dettaglio) ----------------

    def _build_table_section(self, label, columns, data_key):
        self.table_data[data_key] = list(self.data.get(data_key, []))

        self.body.add_widget(MDLabel(text=label, bold=True, theme_text_color="Custom",
                                      text_color=theme.MUTED, adaptive_height=True))
        box = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, adaptive_height=True)
        self.table_boxes[data_key] = (box, columns)
        self.body.add_widget(box)

        add_btn = MDButton(MDButtonText(text=f"Aggiungi riga a: {label}"), style="tonal",
                            size_hint_x=1, on_release=lambda *_: self._add_row_dialog(data_key, columns))
        self.body.add_widget(add_btn)

        self._render_table_rows(data_key)

    def _render_table_rows(self, data_key):
        box, columns = self.table_boxes[data_key]
        box.clear_widgets()
        for idx, row in enumerate(self.table_data[data_key]):
            box.add_widget(TableRowCard(columns, row, on_remove=lambda i=idx: self._remove_row(data_key, i)))

    def _remove_row(self, data_key, idx):
        del self.table_data[data_key][idx]
        self._render_table_rows(data_key)

    def _add_row_dialog(self, data_key, columns):
        fields_box = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None,
                                  adaptive_height=True)
        entries = {}
        for c in columns:
            tf = MDTextField(MDTextFieldHintText(text=c), mode="outlined")
            entries[c] = tf
            fields_box.add_widget(tf)

        scroll = ScrollView(size_hint=(1, None), height=dp(360))
        scroll.add_widget(fields_box)

        def confirm(*_):
            row = {c: entries[c].text for c in columns}
            self.table_data[data_key].append(row)
            self._render_table_rows(data_key)
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text="Nuova riga"),
            MDDialogContentContainer(scroll),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Annulla"), style="text",
                         on_release=lambda *_: dialog.dismiss()),
                MDButton(MDButtonText(text="Aggiungi"), style="filled", on_release=confirm),
            ),
        )
        dialog.open()

    # ---------------- salvataggio / PDF ----------------

    def _collect_data(self):
        data = dict(self.data)
        for key, widget in self.field_widgets.items():
            data[key] = widget.text
        data["_photos"] = self.photo_board.get_photo_data() if self.photo_board else None
        for data_key in self.table_data:
            data[data_key] = self.table_data[data_key]
        return data

    def _save(self, silent=False):
        data = self._collect_data()
        customer = data.get("customer", "")
        report_number = data.get("report_number") or db.next_report_number()
        self.inspection_id = db.save_inspection(
            self.mask_type, report_number, customer, data, self.user["id"], self.inspection_id
        )
        self.data = data
        if not silent:
            _toast("Scheda salvata correttamente.")
            self.on_back()

    def _export_pdf(self):
        self._save(silent=True)
        try:
            from app.pdf_export import export_inspection_pdf
            path = export_inspection_pdf(self.schema, self.mask_type, self.data["report_number"], self.data)
        except Exception as e:
            _toast(f"Errore nella generazione del PDF: {e}")
            return
        _toast(f"PDF generato: {path}")
        self._share_pdf(path)

    def _share_pdf(self, path):
        try:
            from kivy.utils import platform
            if platform == "android":
                from jnius import autoclass, cast
                from android import mActivity

                Intent = autoclass("android.content.Intent")
                File = autoclass("java.io.File")
                FileProvider = autoclass("androidx.core.content.FileProvider")

                pkg = autoclass("org.kivy.android.PythonActivity").mActivity.getPackageName()
                file_obj = File(path)
                uri = FileProvider.getUriForFile(mActivity, pkg + ".fileprovider", file_obj)

                intent = Intent(Intent.ACTION_SEND)
                intent.setType("application/pdf")
                intent.putExtra(Intent.EXTRA_STREAM, cast("android.os.Parcelable", uri))
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                mActivity.startActivity(Intent.createChooser(intent, "Condividi PDF Report"))
        except Exception:
            pass
