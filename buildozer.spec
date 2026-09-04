[app]

title = MoniTest
package.name = monitest
package.domain = org.monitestndt

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,ttf
source.include_patterns = assets/*,assets/**/*

version = 0.1
requirements = python3,kivy==2.3.1,kivymd==2.0.0,pillow,reportlab,plyer,pyjnius

orientation = portrait,landscape,portrait-reverse,landscape-reverse
fullscreen = 0
icon.filename = %(source.dir)s/assets/logo.png

android.permissions = CAMERA,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

# Cartelle create in automatico dall'app (data/foto/PDF/template) NON vanno
# incluse nel pacchetto sorgente.
source.exclude_dirs = devdata,.venv,.github,bin,.buildozer

[buildozer]
log_level = 2
warn_on_root = 1
