[app]
title = MzindaTrack
package.name = mzindatrack
package.domain = org.mzindatrack
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ico,json
source.include_patterns = assets/*,data/*,*.py
source.exclude_exts = spec,md,yml,yaml
source.exclude_dirs = tests, bin, __pycache__, .git, .github, .buildozer
version = 1.0.0

# Pin both hostpython and python to 3.10.20 (matches the runner)
requirements = hostpython3==3.10.20,python3==3.10.20,kivy==2.2.1,requests,plyer,pyjnius,android

presplash.filename = data/presplash.png
icon.filename = assets/icon.png
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 30
android.minapi = 21
android.ndk = 28c
android.ndk_api = 21
android.skip_update = False
android.accept_sdk_license = True
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = "@style/Theme.AppCompat"
android.archs = arm64-v8a
android.copy_libs = 1
android.use_androidx = True
p4a.branch = master
p4a.bootstrap = sdl2

android.add_src =
android.add_java =
android.add_libs_armeabi_v7a =
android.add_libs_arm64_v8a =
android.add_libs_x86 =
android.add_libs_x86_64 =
android.add_aars =
android.gradle_dependencies =
android.window_background_color = #0a0f1e
android.logcat_filters = *:S python:D
android.debug = 1

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
