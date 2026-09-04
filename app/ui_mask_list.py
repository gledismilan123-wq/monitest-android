from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import (
    MDDialog, MDDialogHeadlineText, MDDialogSupportingText,
    MDDialogButtonContainer, MDDialogContentContainer,
)

from app import database as db
from app.forms_schema import get_schema
from app.responsive import breakpoints, bind_resize
from app import theme


class ResultRow(MDCard):
    def __init__(self, record, on_open, on_delete, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(12), spacing=dp(8),
                          md_bg_color=theme.PANEL, radius=[dp(8)] * 4,
                          size_hint=(1, None), height=dp(64),
                          on_release=lambda *_: on_open(record), **kwargs)
        info = MDBoxLayout(orientation="vertical")
        info.add_widget(MDLabel(text=record["report_number"] or "(senza numero)", bold=True,
                                 theme_text_color="Custom", text_color=theme.INK, adaptive_height=True))
        sub = f"{record['customer'] or '-'}  ·  {(record['created_at'] or '')[:16]}"
        info.add_widget(MDLabel(text=sub, theme_text_color="Custom", text_color=theme.MUTED,
                                 font_style="Label", role="small", adaptive_height=True))
        self.add_widget(info)
        self.add_widget(MDIconButton(icon="trash-can-outline", theme_text_color="Custom",
                                      text_color=theme.ERROR,
                                      on_release=lambda *_: on_delete(record)))


class MaskListScreen(MDScreen):
    """Elenco delle schede di una maschera, con ricerca/filtri (equivalente
    touch della vecchia MaskWindow)."""

    def __init__(self, on_open_record, on_back, **kwargs):
        super().__init__(**kwargs)
        self.name = "mask_list"
        self.md_bg_color = theme.BG
        self.on_open_record = on_open_record
        self.on_back = on_back
        self.mask_type = None
        self.schema = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        header = MDBoxLayout(orientation="horizontal", md_bg_color=theme.PANEL,
                              size_hint_y=None, height=dp(56), padding=[dp(8), dp(8)], spacing=dp(6))
        header.add_widget(MDIconButton(icon="arrow-left", on_release=lambda *_: self.on_back()))
        self.title_label = MDLabel(text="", bold=True, font_style="Title", role="medium",
                                    theme_text_color="Custom", text_color=theme.INK)
        header.add_widget(self.title_label)
        header.add_widget(MDButton(MDButtonText(text="Nuovo record"), style="filled",
                                    on_release=lambda *_: self._new_record()))
        root.add_widget(header)

        self.filters_grid = MDGridLayout(cols=2, spacing=dp(8), padding=dp(12),
                                          size_hint_y=None, adaptive_height=True)
        self.search_field = MDTextField(MDTextFieldHintText(text="Cerca (nome, seriale, cliente, note...)"),
                                         mode="outlined")
        self.customer_field = MDTextField(MDTextFieldHintText(text="Cliente"), mode="outlined")
        self.date_from_field = MDTextField(MDTextFieldHintText(text="Data da (AAAA-MM-GG)"), mode="outlined")
        self.date_to_field = MDTextField(MDTextFieldHintText(text="Data a (AAAA-MM-GG)"), mode="outlined")
        for f in (self.search_field, self.customer_field, self.date_from_field, self.date_to_field):
            self.filters_grid.add_widget(f)
        root.add_widget(self.filters_grid)

        actions = MDBoxLayout(orientation="horizontal", spacing=dp(8), padding=[dp(12), 0],
                               size_hint_y=None, height=dp(48))
        actions.add_widget(MDButton(MDButtonText(text="Cerca"), style="tonal",
                                     on_release=lambda *_: self._run_search()))
        actions.add_widget(MDButton(MDButtonText(text="Azzera filtri"), style="outlined",
                                     on_release=lambda *_: self._clear_filters()))
        self.count_label = MDLabel(text="", theme_text_color="Custom", text_color=theme.MUTED, halign="right")
        actions.add_widget(self.count_label)
        root.add_widget(actions)

        scroll = ScrollView(do_scroll_x=False)
        self.results_box = MDBoxLayout(orientation="vertical", spacing=dp(6), padding=dp(12),
                                        size_hint_y=None, adaptive_height=True)
        scroll.add_widget(self.results_box)
        root.add_widget(scroll)

        self.add_widget(root)
        bind_resize(self._update_columns)
        self._update_columns()

    def on_pre_enter(self, *args):
        self._update_columns()

    def _update_columns(self, *_):
        self.filters_grid.cols = breakpoints.columns(one=1, two=2, three=4)

    def open_mask(self, mask_type):
        self.mask_type = mask_type
        self.schema = get_schema(mask_type)
        self.title_label.text = self.schema["title"]
        self._clear_filters()

    def refresh(self):
        self._run_search()

    def _clear_filters(self):
        self.search_field.text = ""
        self.customer_field.text = ""
        self.date_from_field.text = ""
        self.date_to_field.text = ""
        self._run_search()

    def _run_search(self):
        results = db.search_inspections(
            self.mask_type,
            text=self.search_field.text or None,
            customer=self.customer_field.text or None,
            date_from=self.date_from_field.text or None,
            date_to=self.date_to_field.text or None,
        )
        self.results_box.clear_widgets()
        for r in results:
            self.results_box.add_widget(ResultRow(r, self._open_existing, self._confirm_delete))
        self.count_label.text = f"{len(results)} risultati"

    def _open_existing(self, record):
        self.on_open_record(self.mask_type, record)

    def _new_record(self):
        self.on_open_record(self.mask_type, None)

    def _confirm_delete(self, record):
        dialog = MDDialog(
            MDDialogHeadlineText(text=self.schema["title"]),
            MDDialogSupportingText(text="Eliminare definitivamente la scheda selezionata?"),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Annulla"), style="text",
                         on_release=lambda *_: dialog.dismiss()),
                MDButton(MDButtonText(text="Elimina"), style="filled",
                         on_release=lambda *_: self._do_delete(record, dialog)),
            ),
        )
        dialog.open()

    def _do_delete(self, record, dialog):
        db.delete_inspection(record["id"])
        dialog.dismiss()
        self._run_search()
