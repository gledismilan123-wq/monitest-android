"""
main.py
Punto di ingresso dell'app Android MoniTest (Kivy/KivyMD).
"""

import os

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from app import paths
from app.database import init_db
from app.ui_login import LoginScreen
from app.ui_dashboard import DashboardScreen
from app.ui_mask_list import MaskListScreen
from app.ui_record_form import RecordFormScreen
from app.ui_admin import AdminScreen, UsersScreen, ParametersScreen

# Solo per lo sviluppo su PC: apre la finestra gia' alla risoluzione tipica di
# un telefono, cosi' il layout si vede subito come su Android (su Android
# questa riga non ha effetto: la finestra e' sempre a schermo intero).
if os.environ.get("MONITEST_DEV_WINDOW", "1") == "1" and not os.environ.get("ANDROID_ARGUMENT"):
    Window.size = (412, 915)


class MoniTestApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        paths.set_base_dir(self.user_data_dir)
        init_db()

        self.sm = MDScreenManager()
        self.current_user = None

        self.login_screen = LoginScreen(on_success=self._on_login_success)
        self.dashboard_screen = DashboardScreen(
            on_open_mask=self._open_mask,
            on_open_admin=self._open_admin,
            on_logout=self._logout,
        )
        self.mask_list_screen = MaskListScreen(
            on_open_record=self._open_record,
            on_back=self._back_to_dashboard,
        )
        self.record_form_screen = RecordFormScreen(on_back=self._back_to_mask_list)
        self.admin_screen = AdminScreen(
            on_back=self._back_to_dashboard,
            on_open_users=self._open_users,
        )
        self.users_screen = UsersScreen(on_back=self._back_to_admin)
        self.parameters_screen = ParametersScreen()

        for screen in (self.login_screen, self.dashboard_screen, self.mask_list_screen,
                       self.record_form_screen, self.admin_screen, self.users_screen):
            self.sm.add_widget(screen)

        self.sm.current = "login"
        return self.sm

    def _on_login_success(self, user):
        self.current_user = user
        self.dashboard_screen.set_user(user)
        self.sm.current = "dashboard"

    def _logout(self):
        self.current_user = None
        self.sm.current = "login"

    def _open_mask(self, mask_type):
        self.mask_list_screen.open_mask(mask_type)
        self.sm.current = "mask_list"

    def _open_record(self, mask_type, record):
        self.record_form_screen.open_record(self.current_user, mask_type, record)
        self.sm.current = "record_form"

    def _back_to_dashboard(self):
        self.sm.current = "dashboard"

    def _back_to_mask_list(self, refresh=True):
        if refresh:
            self.mask_list_screen.refresh()
        self.sm.current = "mask_list"

    def _open_admin(self):
        self.sm.current = "admin"

    def _open_users(self):
        self.sm.current = "users"

    def _back_to_admin(self):
        self.sm.current = "admin"


if __name__ == "__main__":
    MoniTestApp().run()
