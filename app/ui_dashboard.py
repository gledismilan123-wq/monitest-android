import os
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.card import MDCard

from app.database import MASK_TYPES
from app.forms_schema import get_schema
from app.paths import asset_path
from app.responsive import breakpoints, bind_resize
from app import theme

LOGO_PATH = asset_path("assets", "logo.png")


class MaskCard(MDCard):
    def __init__(self, mask_type, title, on_press, **kwargs):
        super().__init__(orientation="vertical", padding=dp(14), spacing=dp(6),
                          md_bg_color=theme.PANEL, radius=[dp(10)] * 4,
                          size_hint=(1, None), height=dp(96),
                          on_release=lambda *_: on_press(mask_type), **kwargs)
        self.add_widget(MDLabel(text=title, bold=True, theme_text_color="Custom",
                                 text_color=theme.INK, adaptive_height=True,
                                 font_style="Title", role="small"))
        self.add_widget(MDBoxLayout())
        self.add_widget(MDLabel(text="Apri maschera ->", theme_text_color="Custom",
                                 text_color=theme.STEEL, bold=True, adaptive_height=True,
                                 font_style="Label", role="medium"))


class DashboardScreen(MDScreen):
    def __init__(self, on_open_mask, on_open_admin, on_logout, **kwargs):
        super().__init__(**kwargs)
        self.name = "dashboard"
        self.md_bg_color = theme.BG
        self.on_open_mask = on_open_mask
        self.on_open_admin = on_open_admin
        self.on_logout = on_logout
        self.user = None
        self._build_ui()

    def _build_ui(self):
        root = MDBoxLayout(orientation="vertical")

        self.topbar = MDBoxLayout(orientation="horizontal", md_bg_color=theme.PANEL,
                                   size_hint_y=None, height=dp(56), padding=[dp(12), dp(6)],
                                   spacing=dp(8))
        left = MDBoxLayout(orientation="vertical")
        if os.path.exists(LOGO_PATH):
            left.add_widget(Image(source=LOGO_PATH, size_hint=(None, 1), width=dp(100),
                                   allow_stretch=True))
        else:
            left.add_widget(MDLabel(text="MoniTest NDT", bold=True, theme_text_color="Custom",
                                     text_color=theme.ACCENT, adaptive_height=True))
        self.topbar.add_widget(left)

        self.user_label = MDLabel(text="", theme_text_color="Custom", text_color=theme.MUTED,
                                   halign="right", valign="middle", font_style="Label", role="small")
        self.topbar.add_widget(self.user_label)

        # Su schermo stretto (telefono/copertina Fold) i pulsanti mostrano solo
        # l'icona; da tablet in su (Fold aperto) mostrano anche il testo.
        self.admin_btn_wide = MDButton(MDButtonText(text="Amministrazione"), style="outlined",
                                        on_release=lambda *_: self.on_open_admin())
        self.admin_btn_narrow = MDIconButton(icon="shield-account-outline",
                                              on_release=lambda *_: self.on_open_admin())
        self.logout_btn_wide = MDButton(MDButtonText(text="Esci"), style="filled",
                                         on_release=lambda *_: self.on_logout())
        self.logout_btn_narrow = MDIconButton(icon="logout",
                                               on_release=lambda *_: self.on_logout())

        root.add_widget(self.topbar)

        scroll = ScrollView(do_scroll_x=False)
        self.grid = MDGridLayout(cols=2, spacing=dp(10), padding=dp(16),
                                  size_hint_y=None, adaptive_height=True)
        for mask in MASK_TYPES:
            title = get_schema(mask)["title"]
            self.grid.add_widget(MaskCard(mask, title, self.on_open_mask))
        scroll.add_widget(self.grid)
        root.add_widget(scroll)

        self.add_widget(root)
        bind_resize(self._update_layout)
        self._update_layout()

    def on_pre_enter(self, *args):
        self._update_layout()

    def _update_layout(self, *_):
        self.grid.cols = breakpoints.columns(one=2, two=3, three=4)
        wide = breakpoints.columns(one=False, two=True, three=True)

        self.user_label.opacity = 1 if wide else 0
        self.user_label.size_hint_x = 1 if wide else None
        self.user_label.width = 0 if not wide else self.user_label.width

        for btn in (self.admin_btn_wide, self.admin_btn_narrow,
                    self.logout_btn_wide, self.logout_btn_narrow):
            if btn.parent:
                self.topbar.remove_widget(btn)
        show_admin = self.user is None or self.user["role"] == "admin"
        if show_admin:
            self.topbar.add_widget(self.admin_btn_wide if wide else self.admin_btn_narrow)
        self.topbar.add_widget(self.logout_btn_wide if wide else self.logout_btn_narrow)

    def set_user(self, user):
        self.user = user
        self.user_label.text = f"{user['full_name']}  ·  {user['role']}"
        self._update_layout()
