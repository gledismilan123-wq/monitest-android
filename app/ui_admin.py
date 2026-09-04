from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText

from app import database as db
from app.forms_schema import get_all_dropdown_fields
from app import theme


def _toast(text):
    MDSnackbar(MDSnackbarText(text=text), y=dp(24), pos_hint={"center_x": 0.5},
               size_hint_x=0.9).open()


def _header(title, on_back, extra_buttons=None):
    header = MDBoxLayout(orientation="horizontal", md_bg_color=theme.PANEL,
                          size_hint_y=None, height=dp(56), padding=[dp(8), dp(8)], spacing=dp(6))
    header.add_widget(MDIconButton(icon="arrow-left", on_release=lambda *_: on_back()))
    header.add_widget(MDLabel(text=title, bold=True, font_style="Title", role="medium",
                               theme_text_color="Custom", text_color=theme.INK))
    for btn in (extra_buttons or []):
        header.add_widget(btn)
    return header


class ValueRow(MDCard):
    def __init__(self, item, on_toggle, on_delete, **kwargs):
        super().__init__(orientation="horizontal", padding=dp(10), spacing=dp(8),
                          md_bg_color=theme.PANEL, radius=[dp(8)] * 4,
                          size_hint=(1, None), height=dp(52), **kwargs)
        active = bool(item["active"])
        self.add_widget(MDLabel(text=item["value"], theme_text_color="Custom",
                                 text_color=theme.INK if active else theme.MUTED_LIGHT))
        self.add_widget(MDButton(
            MDButtonText(text="Attivo" if active else "Disattivo"),
            style="tonal" if active else "outlined",
            on_release=lambda *_: on_toggle(item, not active),
        ))
        self.add_widget(MDIconButton(icon="trash-can-outline", theme_text_color="Custom",
                                      text_color=theme.ERROR, on_release=lambda *_: on_delete(item)))


class AdminScreen(MDScreen):
    def __init__(self, on_back, on_open_users, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin"
        self.md_bg_color = theme.BG
        self.on_back = on_back
        self.on_open_users = on_open_users
        self.current_key = None
        self.fields = {}
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        users_btn = MDButton(MDButtonText(text="Gestione utenti"), style="filled",
                              on_release=lambda *_: self.on_open_users())
        root.add_widget(_header("Amministrazione", self.on_back, [users_btn]))

        body = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14),
                            size_hint_y=None, adaptive_height=True)

        self.fields = get_all_dropdown_fields()
        self.field_selector = MDButton(MDButtonText(text="Scegli un campo..."), style="outlined",
                                        size_hint_x=1, on_release=self._open_field_menu)
        body.add_widget(MDLabel(text="Parametri per campo (tendine)", bold=True,
                                 theme_text_color="Custom", text_color=theme.MUTED, adaptive_height=True))
        body.add_widget(self.field_selector)

        add_row = MDBoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None,
                               adaptive_height=True)
        self.new_value_field = MDTextField(MDTextFieldHintText(text="Nuovo valore"), mode="outlined")
        add_row.add_widget(self.new_value_field)
        add_row.add_widget(MDButton(MDButtonText(text="Aggiungi"), style="filled",
                                     on_release=lambda *_: self._add_value()))
        body.add_widget(add_row)

        self.values_box = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None,
                                       adaptive_height=True)
        body.add_widget(self.values_box)

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)

    def _open_field_menu(self, *_):
        items = [{"text": label, "on_release": lambda k=key, l=label: self._select_field(k, l)}
                 for key, label in self.fields.items()]
        MDDropdownMenu(caller=self.field_selector, items=items).open()

    def _select_field(self, key, label):
        self.current_key = key
        for c in self.field_selector.children:
            if hasattr(c, "text"):
                c.text = label
        self._refresh_values()

    def _refresh_values(self):
        self.values_box.clear_widgets()
        if not self.current_key:
            return
        for item in db.list_field_options(self.current_key, include_inactive=True):
            self.values_box.add_widget(ValueRow(dict(item), self._toggle_value, self._delete_value))

    def _add_value(self):
        value = (self.new_value_field.text or "").strip()
        if not value or not self.current_key:
            return
        db.add_field_option(self.current_key, value)
        self.new_value_field.text = ""
        self._refresh_values()

    def _toggle_value(self, item, new_active):
        db.set_field_option_active(item["id"], new_active)
        self._refresh_values()

    def _delete_value(self, item):
        db.delete_field_option(item["id"])
        self._refresh_values()


class UsersScreen(MDScreen):
    def __init__(self, on_back, **kwargs):
        super().__init__(**kwargs)
        self.name = "users"
        self.md_bg_color = theme.BG
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")
        root.add_widget(_header("Gestione utenti", self.on_back))

        body = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=dp(14),
                            size_hint_y=None, adaptive_height=True)

        form = MDBoxLayout(orientation="vertical", spacing=dp(8), size_hint_y=None, adaptive_height=True)
        self.username_field = MDTextField(MDTextFieldHintText(text="Nome utente"), mode="outlined")
        self.password_field = MDTextField(MDTextFieldHintText(text="Password iniziale"), mode="outlined",
                                           password=True)
        self.fullname_field = MDTextField(MDTextFieldHintText(text="Nome completo"), mode="outlined")
        self.role_button = MDButton(MDButtonText(text="Ruolo: operatore"), style="outlined",
                                     size_hint_x=1, on_release=self._open_role_menu)
        self.role_value = "operatore"
        for w in (self.username_field, self.password_field, self.fullname_field, self.role_button):
            form.add_widget(w)
        form.add_widget(MDButton(MDButtonText(text="Crea utente"), style="filled", size_hint_x=1,
                                  on_release=lambda *_: self._add_user()))
        body.add_widget(form)

        self.users_box = MDBoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None,
                                      adaptive_height=True)
        body.add_widget(self.users_box)

        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(body)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_pre_enter(self, *args):
        self._refresh()

    def _open_role_menu(self, *_):
        items = [{"text": r, "on_release": lambda r=r: self._select_role(r)} for r in ("operatore", "admin")]
        MDDropdownMenu(caller=self.role_button, items=items).open()

    def _select_role(self, role):
        self.role_value = role
        for c in self.role_button.children:
            if hasattr(c, "text"):
                c.text = f"Ruolo: {role}"

    def _refresh(self):
        self.users_box.clear_widgets()
        for u in db.list_users():
            self.users_box.add_widget(self._user_row(dict(u)))

    def _user_row(self, u):
        active = bool(u["active"])
        row = MDCard(orientation="horizontal", padding=dp(10), spacing=dp(8),
                      md_bg_color=theme.PANEL, radius=[dp(8)] * 4, size_hint=(1, None), height=dp(60))
        info = MDBoxLayout(orientation="vertical")
        info.add_widget(MDLabel(text=f"{u['full_name']} ({u['username']})", bold=True,
                                 theme_text_color="Custom", text_color=theme.INK, adaptive_height=True))
        info.add_widget(MDLabel(text=u["role"], theme_text_color="Custom", text_color=theme.MUTED,
                                 font_style="Label", role="small", adaptive_height=True))
        row.add_widget(info)
        row.add_widget(MDButton(
            MDButtonText(text="Attivo" if active else "Disattivo"),
            style="tonal" if active else "outlined",
            on_release=lambda *_: self._toggle(u["id"], not active),
        ))
        return row

    def _add_user(self):
        username = (self.username_field.text or "").strip()
        password = self.password_field.text or ""
        full_name = (self.fullname_field.text or "").strip()
        if not (username and password and full_name):
            _toast("Compila utente, password e nome completo.")
            return
        try:
            db.create_user(username, password, full_name, self.role_value)
        except Exception as e:
            _toast(f"Impossibile creare l'utente: {e}")
            return
        self.username_field.text = ""
        self.password_field.text = ""
        self.fullname_field.text = ""
        self._refresh()

    def _toggle(self, user_id, active):
        db.set_user_active(user_id, active)
        self._refresh()


class ParametersScreen(MDScreen):
    """Segnaposto: nella v1 i parametri si gestiscono direttamente da
    AdminScreen. Tenuto come schermata separata per un eventuale sviluppo
    futuro (es. gestione parametri a schermo intero)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "parameters"
