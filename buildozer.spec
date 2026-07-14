[app]

# (str) Force NDK path - REMOVED for CI/CD
# android.ndk_path = 

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

# (list) Application requirements
requirements = python3==3.9,kivy==2.1.0,requests,plyer,pyjnius,android,kivy-garden.xwebview

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
android.api = 30

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version - Use 23c for compatibility
android.ndk = 23c

# (int) Android NDK API
android.ndk_api = 21

# (bool) Skip updating SDK/NDK to use system versions
android.skip_update = False

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme
android.apptheme = "@style/Theme.AppCompat"

# (list) The Android archs to build for
android.archs = arm64-v8a

# (list) Android features to enable
android.features = android.hardware.location.gps

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (bool) Enable AndroidX support
android.use_androidx = True

# (str) Python-for-android branch - Use stable release that exists
p4a.branch = release-2022.7.0

# (str) Bootstrap to use
p4a.bootstrap = sdl2

# (list) Android addons to include
android.add_src =

# (list) Java classes to add
android.add_java =

# (list) Android libraries to include
android.add_libs_armeabi_v7a =
android.add_libs_arm64_v8a =
android.add_libs_x86 =
android.add_libs_x86_64 =

# (list) Android AAR libraries to include
android.add_aars =

# (list) Gradle dependencies to include
android.gradle_dependencies =

# (str) Android window background color
android.window_background_color = #0a0f1e

# (str) Android logcat filters
android.logcat_filters = *:S python:D

# (bool) Enable Android debug mode
android.debug = 1

[buildozer]

# (int) Log level
log_level = 2

# (int) Warn if root
warn_on_root = 1

# (str) Build directory
build_dir = ./.buildozer

# (str) Binary directory
bin_dir = ./bin
