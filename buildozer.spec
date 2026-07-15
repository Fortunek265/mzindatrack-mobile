[app]
# Application title and branding
title = MzindaTrack
package.name = mzindatrack
package.domain = org.mzindatrack

# Version information
version = 1.0.0
version.filename = version.txt

# Source configuration
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ico,json,ttf
source.include_patterns = assets/*,data/*,*.py
source.exclude_exts = spec,md,yml,yaml,pyc
source.exclude_dirs = tests,bin,__pycache__,.git,.github,.buildozer,.pytest_cache,*.egg-info

# Assets
presplash.filename = data/presplash.png
presplash.imgctx = Image
icon.filename = assets/icon.png
icon.adaptive_foreground.filename = assets/icon_foreground.png
icon.adaptive_background.filename = assets/icon_background.png

# Orientation and display settings
orientation = portrait
fullscreen = 0
android.window_background_color = #0a0f1e

# Python configuration
python_version = 3.9
python_requires = >=3.9

# Requirements (pip packages)
requirements = python3==3.9,kivy==2.1.0,requests,plyer,pyjnius,android

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE,CHANGE_NETWORK_STATE

# Android SDK and NDK
android.api = 30
android.minapi = 21
android.ndk = 23c
android.ndk_api = 21
android.skip_update = False
android.accept_sdk_license = True

# Android build configuration
android.entrypoint = org.kivy.android.PythonActivity
android.apptheme = @style/Theme.AppCompat.Light.DarkActionBar
android.archs = arm64-v8a,armeabi-v7a

# Build options
android.copy_libs = 1
android.use_androidx = True
android.gradle_dependencies = 

# P4A (Python For Android) configuration
p4a.branch = develop
p4a.bootstrap = sdl2
p4a.arch = arm64-v8a

# Java and native additions
android.add_src =
android.add_java =
android.add_libs_armeabi_v7a =
android.add_libs_arm64_v8a =
android.add_libs_x86 =
android.add_libs_x86_64 =
android.add_aars =

# WebView configuration for Android
android.gradle_dependencies = androidx.webkit:webkit:1.4.0

# Release signing (optional - configure with your keystore)
# android.release_artifact = apk
# android.signing_debug = 1
# android.keystore = 1
# android.keystore_path = 
# android.keystore_alias = 
# android.keystore_password = 

# Logging
android.logcat_filters = *:S python:D

# Debug mode
android.debug = 0

# Permissions at runtime (Android 6.0+)
android.runtime_permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# Service/Activity configuration
android.services = org.kivy.android.PythonService

[buildozer]
# Build directory
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin

# Verbose output for debugging
# log_level = 4
