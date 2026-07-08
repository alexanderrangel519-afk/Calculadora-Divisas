[app]

# (Importante: Estas son las 4 líneas que te pedía el error)
title = Calculadora
package.name = calculadora
package.domain = org.test
source.dir = .

# (Configuraciones adicionales necesarias)
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
