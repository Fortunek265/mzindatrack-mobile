[app]

title = MzindaTrack
package.name = mzindatrack
package.domain = org.mzindatrack

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ico
source.include_patterns = assets/*,data/*
source.exclude_exts = spec,md,yml,yaml
source.exclude_dirs = tests,bin,.git,.github,__pycache__,.buildozer

version = 1.0.0

requirements = python3==3.10.20,kivy==2.2.1,requests,plyer,pyjnius

orientation = portrait

fullscreen = 0

presplash.filename = data/presplash.png
icon.filename = assets/icon.png

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

android.api = 33
android.minapi = 21

android.ndk = 25b
android.ndk_api = 21

android.archs = arm64-v8a

android.use_androidx = True
android.copy_libs = 1

android.accept_sdk_license = True

android.entrypoint = org.kivy.android.PythonActivity

android.apptheme = "@style/Theme.AppCompat"

android.window_background_color = #0a0f1e

android.logcat_filters = *:S python:D

android.debug = 1

p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]

log_level = 2

warn_on_root = 1

build_dir = .buildozer

bin_dir = bin
