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
#source.include_patterns = assets/*,*.py

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory names to not include
#source.exclude_dirs = tests, bin, __pycache__, .git, .github

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license, files/*.txt

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# requirements = python3,kivy
requirements = python3,kivy,requests,plyer,android

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = assets/GPS.ico

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# OSX icon filename
#osx.icon.filename = %(source.dir)s/data/icon.icns

# OSX bundle identifier
#osx.bundle_identifier = com.yourcompany.mzindatrack

#
# Android Specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 31

# (str) Android NDK version to use
#android.ndk = 23b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
#android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only.
# android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@style/Theme.AppCompat"

# (list) Pattern to whitelist for the whole APK
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/lib/*.jar
#android.add_src =

# (list) List of Java files to add to the project
#android.add_src =

# (list) Java AAR archives to add
# android.add_aars =

# (list) Gradle dependencies to add
android.gradle_dependencies = 'com.google.android.gms:play-services-location:21.0.1'

# (bool) Enable AndroidX support. Enable when using AndroidX
#android.use_androidx = False

# (str) android.gradle_plugin_dependencies =
# android.gradle_plugin_dependencies = 'com.google.gms:google-services:4.3.13'

# (bool) Enable automated signing of the release APK
# android.force_apk_obfuscation = False

# (bool) Enable automated signing of the release APK
#android.enable_apk_signing = True

# (str) keystore file path
# android.keystore_path = path/to/keystore

# (str) keystore password
# android.keystore_password = your_password

# (str) keystore alias
# android.keystore_alias = your_alias

# (str) keystore alias password
# android.keystore_alias_password = your_alias_password

# (str) Path to custom certificate for APK signing (PEM format)
# android.release_cert =

# (str) Path to custom private key for APK signing (PKCS8 format)
# android.release_key =

# (list) List of Android features to enable (e.g. android.hardware.usb.host)
#android.features = android.hardware.location.gps

# (list) List of Android features to disable
# android.features_disable =

# (list) List of Android libraries to include
# android.libraries =

# (list) List of Android activities to add
# android.activities =

# (str) Android manifest.xml element to add (quoted string)
# android.manifest_application_element =
# android.manifest_activity_element =
# android.manifest_activity_launchMode =
# android.manifest_activity_taskAffinity =

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
# android.copy_libs = 1

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = armeabi-v7a

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
#p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
#p4a.local_recipes =

# (str) Filename to the hook for p4a
#p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = sdl2

# (bool) If True, use the SDL 2 back-end instead of SDL 1.2 (default True)
#ios.use_sdl2 = True

# (bool) If True, use the iOS back-end instead of the kivy back-end (default False)
#ios.use_kivy = False

# (list) List of iOS frameworks to add
#ios.frameworks = UIKit, CoreLocation, MapKit

# (list) List of iOS plist elements to add
#ios.plist_elems = <key>UIBackgroundModes</key><array><string>location</string></array>

# (str) iOS bundle identifier
#ios.bundle_identifier = com.yourcompany.mzindatrack

#
# iOS specific
#

# (str) iOS bundle identifier
# ios.bundle_identifier = com.yourcompany.mzindatrack

# (str) iOS bundle name
# ios.bundle_name = MzindaTrack

# (str) iOS bundle version
# ios.bundle_version = 1.0.0

# (str) iOS minimum version
# ios.minimum_version = 9.0

# (str) iOS interface orientation
# ios.interface_orientation = UIInterfaceOrientationPortrait

# (str) iOS team identifier (for signing)
# ios.team_id =

# (str) iOS provisioning profile
# ios.provisioning_profile =

# (str) iOS code signing identity
# ios.codesign_identity =

# (str) iOS deployment target
# ios.deployment_target = 9.0

# (bool) Enable iOS bitcode support
# ios.enable_bitcode = False

# (list) iOS frameworks to add
#ios.frameworks = UIKit, CoreLocation, MapKit, WebKit

# (list) iOS plist elements to add
#ios.plist_elems = <key>UIBackgroundModes</key><array><string>location</string></array>

# (str) iOS app icon
#ios.icon.filename = %(source.dir)s/data/icon.png

# (str) iOS launch image
#ios.launch_image.filename = %(source.dir)s/data/launch.png

# (list) iOS source files to include
#ios.source.include_exts = py,png,jpg,kv,atlas,ico,json

# (list) iOS source files to exclude
#ios.source.exclude_exts = spec

#
# Windows specific
#

# (list) Windows requirements
# windows.requirements = kivy

# (str) Windows entry point
# windows.entrypoint = main.py

# (str) Windows icon
# windows.icon.filename = %(source.dir)s/data/icon.ico

#
# Web specific
#

# (str) Web entry point
# web.entrypoint = main.py

# (str) Web title
# web.title = MzindaTrack

# (str) Web icon
# web.icon.filename = %(source.dir)s/data/icon.png

# (str) Web manifest
# web.manifest.filename = %(source.dir)s/data/manifest.json

# (list) Web source files to include
#web.source.include_exts = py,png,jpg,kv,atlas,ico,json

# (list) Web source files to exclude
#web.source.exclude_exts = spec

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] / source.exclude_patterns.
#    Instead of doing:
#
#[app]
#source.exclude_patterns = license,data/audio/*.wav,data/images/original/*
#
#    This can be transformed into:
#
#[app]
#source.exclude_patterns = license
#source.exclude_patterns = data/audio/*.wav
#source.exclude_patterns = data/images/original/*
#
#    ---------------------------------------------------------------------
#    Profiles
#
#    You can extend section / key with a profile
#    For example, you want to deploy a "development" APK which is not restricted
#    to a specific key (like dev-keystore) or and it's not signed.
#    You can do this:
#
#    [app:development]
#    android.keystore_path = /path/to/dev/keystore
#    android.keystore_password = dev_password
#    android.keystore_alias = dev_alias
#
#    So, you have to use the --profile development when invoking buildozer:
#
#    $ buildozer --profile development android debug
