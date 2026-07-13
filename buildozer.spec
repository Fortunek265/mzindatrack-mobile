[app]

# (str) Title of your application
title = MzindaTrack

# (str) Package name
package.name = mzindatrack

# (str) Package domain (used as reverse domain for package naming)
package.domain = org.mzindatrack

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,json,html,js,css

# (list) List of inclusions using pattern matching
# source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
# source.exclude_exts = spec

# (list) List of directory names to exclude
# source.exclude_dirs = tests, bin, __pycache__, .git, .github

# (list) List of exclusions using pattern matching
source.exclude_patterns = *.spec,.git/*,.github/*,__pycache__/*,build/*,dist/*,*.pyc

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# Core requirements for the app to work
requirements = python3,kivy==2.3.0,requests==2.31.0,plyer==2.1,pyjnius==1.5.0,android==1.0

# (str) Custom source folders for requirements
# requirements.source = requirements

# (list) Garden requirements
# garden_requirements =

# (str) Presplash of the application
presplash.filename = assets/presplash.png

# (str) Icon of the application
icon.filename = assets/gps.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# (str) Application versioning (method 1)
# version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Library requirements for Android
# android.add_src = 

# (list) Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_BACKGROUND_LOCATION,FOREGROUND_SERVICE,WAKE_LOCK,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25c

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
android.ndk_api = 21

# (bool) Use --private data storage (True) or --dir public storage (False)
# android.private_storage = True

# (str) Android entry point, default is 'org.kivy.android.PythonActivity'
# android.entrypoint = org.kivy.android.PythonActivity

# (list) Python-for-android whitelist
# android.p4a_whitelist =

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) Android X inclusions
# android.add_src =

# (list) Gradle dependencies to add
# Google Play Services for location and maps
android.gradle_dependencies = 'com.google.android.gms:play-services-location:21.0.1'

# (list) Java classes to add
# android.add_java_class =

# (str) python-for-android branch to use, defaults to master
# android.p4a_branch = master

# (bool) If True, skip updating the debug key.
# android.skip_update_debug_key = False

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.arch = arm64-v8a

# (bool) Show logcat output
android.logcat_filters = *:S Python:D

# (bool) Copy libs instead of packing them as assets
# android.copy_libs = False

# (list) Additionnal Java source directories to add (if you have Java code in src/java)
# android.java_src_dir =

# (list) Addtional Java .jar files to add
# android.add_jars =

# (list) Addtional Python .so files to include
# android.add_libs_armeabi_v7a =

# (str) The directory containing the aars to include
# android.aars_dir =

# (str) The directory containing the jars to include
# android.jars_dir =

#
# Python for android (p4a) specific
#

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
# android.p4a_source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# android.p4a_private_dir =

# (list) The list of the recipes to ignore for the current build (if any)
# android.p4a_ignore_recipes =

# (str) The directory in which python-for-android should look for your own components (if any)
# android.p4a_private_components =

# (list) The list of the components to include
# android.p4a_include_components =

# (list) The list of the components to exclude
# android.p4a_exclude_components =

#
# iOS Specific
#

# (str) iOS bundle identifier
# ios.bundle_identifier = org.mzindatrack.mzindatrack

# (str) iOS bundle name
# ios.bundle_name = MzindaTrack

# (str) iOS bundle version
# ios.bundle_version = 1.0.0

# (str) iOS minimum version
# ios.minimum_version = 9.0

# (str) iOS interface orientation
# ios.interface_orientation = UIInterfaceOrientationPortrait

# (str) iOS app icon
# ios.icon.filename = %(source.dir)s/assets/icon-ios.png

# (str) iOS app launch image
# ios.launch_image.filename = %(source.dir)s/assets/launch-ios.png

#
# Specific for distribution
#

# (str) Application distribution. 'release' for Google Play Store, or 'debug' for development
# osx.package_type = release

# (str) Path to a custom certificate to use for signing
# osx.package_certificate = /path/to/certificate.pem

# (str) Path to a custom key file to use for signing
# osx.package_key = /path/to/key.pem

# (str) Password for the custom key
# osx.package_password = password

# (list) List of dependencies to add to the package
# osx.package_deps = /path/to/library.dylib

# (list) List of frameworks to add to the package
# osx.package_frameworks = /path/to/framework.framework

# (list) List of resources to add to the package
# osx.package_resources = /path/to/resource

# (str) Path to the application icon for Mac OS X
# osx.icon.filename = %(source.dir)s/assets/icon-osx.icns

#
# Specific for Android
#

# (bool) Indicates if the application should be fullscreen or not
# fullscreen = 0

# (str) Window size (width x height)
# window.size = 800x600

# (str) Window minimum size (width x height)
# window.minimum_size = 400x300

# (bool) Window resizable
# window.resizable = True

# (bool) Window border
# window.border = True

# (str) Window icon
# window.icon = %(source.dir)s/data/icon.png

# (bool) If True, the window will stay on top of other windows
# window.always_on_top = False

# (list) Arguments to pass to the application. These will be accessible via sys.argv
# window.args =

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

# (str) Path to the directory where the Android SDK is stored
# android_sdk_dir = /path/to/android-sdk

# (str) Path to the directory where the Android NDK is stored
# android_ndk_dir = /path/to/android-ndk

# (str) Path to the directory where the Android Ant is stored
# android_ant_dir = /path/to/android-ant

# (str) Path to the directory where the Android Gradle is stored
# android_gradle_dir = /path/to/android-gradle

# (str) Path to the directory where the Java JDK is stored
# java_jdk_dir = /path/to/java-jdk

# (bool) If True, use the Android SDK and NDK installed via the package manager
# android_use_system_sdk = False

# (bool) If True, use the Android SDK and NDK from the local directory
# android_use_local_sdk = False

# (str) The directory where the Android SDK is stored (if android_use_local_sdk is True)
# android_local_sdk_dir = /path/to/android-sdk

# (str) The directory where the Android NDK is stored (if android_use_local_sdk is True)
# android_local_ndk_dir = /path/to/android-ndk

# (str) The directory where the Android Ant is stored (if android_use_local_sdk is True)
# android_local_ant_dir = /path/to/android-ant

# (str) The directory where the Android Gradle is stored (if android_use_local_sdk is True)
# android_local_gradle_dir = /path/to/android-gradle

# (str) The directory where the Java JDK is stored (if android_use_local_sdk is True)
# java_local_jdk_dir = /path/to/java-jdk
