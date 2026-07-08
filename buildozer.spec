[app]
# (Asegúrate de que estos valores coincidan con tu proyecto)
title = Calculadora
package.name = calculadora
package.domain = org.test
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
# ¡Esta línea es clave para evitar errores de licencias!
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
