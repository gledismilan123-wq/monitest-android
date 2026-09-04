from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from app.database import verify_login
from app.paths import asset_path
from app import theme
import os

LOGO_PATH = asset_path("assets", "logo.png")


class LoginScreen(MDScreen):
    def __init__(self, on_success, **kwargs):
        super().__init__(**kwargs)
        self.name = "login"
        self.on_success = on_success
        self.md_bg_color = theme.BG
        self._build_ui()

    def _build_ui(self):
        anchor = AnchorLayout(anchor_x="center", anchor_y="center")

        card = MDBoxLayout(orientation="vertical", spacing=dp(14), padding=dp(24),
                            md_bg_color=theme.PANEL, radius=[dp(14)] * 4,
                            size_hint=(None, None), width=dp(360))
        card.bind(minimum_height=card.setter("height"))

        if os.path.exists(LOGO_PATH):
            img = Image(source=LOGO_PATH, size_hint=(1, None), height=dp(70), allow_stretch=True)
            card.add_widget(img)

        card.add_widget(MDLabel(text="Gestionale Ispezioni NDT", font_style="Headline", role="small",
                                 adaptive_height=True, theme_text_color="Custom", text_color=theme.INK))
        card.add_widget(MDLabel(text="Accedi con il tuo account aziendale",
                                 theme_text_color="Custom", text_color=theme.MUTED, adaptive_height=True))

        self.user_field = MDTextField(MDTextFieldHintText(text="Utente"), mode="outlined")
        card.add_widget(self.user_field)

        self.pwd_field = MDTextField(MDTextFieldHintText(text="Password"), mode="outlined", password=True)
        card.add_widget(self.pwd_field)

        self.error_label = MDLabel(text="", theme_text_color="Custom", text_color=theme.ERROR,
                                    adaptive_height=True)
        card.add_widget(self.error_label)

        login_btn = MDButton(MDButtonText(text="Accedi"), style="filled",
                              size_hint_x=1, on_release=lambda *_: self._try_login())
        card.add_widget(login_btn)

        card.add_widget(MDLabel(text="Credenziali di primo accesso: admin / admin",
                                 theme_text_color="Custom", text_color=theme.MUTED_LIGHT,
                                 font_style="Label", role="small", adaptive_height=True))

        from kivy.core.window import Window

        def _fit_width(*_):
            card.width = min(dp(360), Window.width - dp(32))

        Window.bind(size=_fit_width)
        _fit_width()

        anchor.add_widget(card)
        self.add_widget(anchor)

    def on_pre_enter(self, *args):
        self.user_field.text = ""
        self.pwd_field.text = ""
        self.error_label.text = ""

    def _try_login(self):
        username = (self.user_field.text or "").strip()
        password = self.pwd_field.text or ""
        if not username or not password:
            self.error_label.text = "Inserisci utente e password."
            return
        user = verify_login(username, password)
        if user is None:
            self.error_label.text = "Credenziali non valide o utente disattivato."
            return
        self.on_success(user)
