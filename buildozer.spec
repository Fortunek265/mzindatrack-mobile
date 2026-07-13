[app]

# (str) Title of your application
title = MzindaTrack

# (str) Package name
package.name = mzindatrack

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mzindatrack

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ico,json

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,data/*,*.py

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,md,yml,yaml

# (list) List of directory names to not include
source.exclude_dirs = tests, bin, __pycache__, .git, .github, .buildozer

# (str) Application versioning
version = 1.0.0

# (list) Application requirements - REMOVED 'android' from here
requirements = python3==3.9.5,kivy==2.1.0,requests,plyer

# (str) Presplash of the application
presplash.filename = data/presplash.png

# (str) Icon of the application
icon.filename = assets/icon.png

# (str) Supported orientation
orientation = portrait

#
# Android Specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version
android.sdk = 33

# (str) Android NDK version - Changed to match system
android.ndk = 25c

# (int) Android NDK API - Changed to match your system's NDK
android.ndk_api = 21

# (bool) Skip updating SDK/NDK to use system versions
android.skip_update = True

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.apptheme = "@style/Theme.AppCompat"

# (str) The Android arch to build for - Just one arch for faster build
android.arch = arm64-v8a

# (list) Android features to enable
android.features = android.hardware.location.gps

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (bool) Enable AndroidX support
android.use_androidx = True

# (str) Python-for-android branch
p4a.branch = develop

# (str) Bootstrap to use
p4a.bootstrap = sdl2

[buildozer]

# (int) Log level
log_level = 2

# (int) Warn if root
warn_on_root = 1

# (str) Build directory
build_dir = ./.buildozer

# (str) Binary directory
bin_dir = ./bin
