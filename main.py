#!/usr/bin/env python3
"""
MzindaTrack Mobile App - GPS Tracking Client
GPS yathu, Chitetezo chathu
Fully responsive with hamburger menu and full screen support
Version 2.1 - Fixed WebView, Settings, and Platform Compatibility
"""

import os
import re
import json
import requests
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.utils import platform
from kivy.network.urlrequest import UrlRequest
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.graphics import Color, RoundedRectangle, Rectangle

# Try to import WebView - handle platform differences
WEBVIEW_AVAILABLE = False
try:
    if platform == 'android':
        from android.webview import WebView
        WEBVIEW_AVAILABLE = True
        print("Android WebView loaded")
    elif platform == 'ios':
        from kivy_ios.webview import WebView
        WEBVIEW_AVAILABLE = True
        print("iOS WebView loaded")
    else:
        # Desktop - try Kivy WebView
        try:
            from kivy.uix.webview import WebView
            WEBVIEW_AVAILABLE = True
            print("Kivy WebView loaded")
        except ImportError:
            print("WebView not available on this platform")
except ImportError:
    print("WebView not available")

# Android permissions
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.INTERNET,
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION
        ])
    except ImportError:
        print("Android permissions not available")

# ==================== THEME / CONSTANTS ====================

class Theme:
    """Application theme constants"""
    # Colors
    PRIMARY = (0.39, 0.49, 0.92, 1)
    PRIMARY_DARK = (0.2, 0.3, 0.7, 1)
    SUCCESS = (0.3, 0.75, 0.35, 1)
    ERROR = (0.8, 0.2, 0.2, 1)
    WARNING = (1, 0.6, 0, 1)
    TEXT_PRIMARY = (0.88, 0.9, 0.93, 1)
    TEXT_SECONDARY = (0.53, 0.57, 0.62, 1)
    TEXT_MUTED = (0.4, 0.45, 0.5, 1)
    BACKGROUND = (0.04, 0.06, 0.12, 1)
    BACKGROUND_CARD = (0.15, 0.15, 0.2, 1)
    BACKGROUND_INPUT = (0.08, 0.08, 0.12, 1)
    ACCENT = (0.39, 1, 0.85, 1)
    
    # Sizes
    HEADER_HEIGHT = dp(48)
    STATUS_BAR_HEIGHT = dp(36)
    BUTTON_HEIGHT = dp(44)
    INPUT_HEIGHT = dp(42)
    TOUCH_TARGET_MIN = dp(44)
    PADDING = dp(16)
    SPACING = dp(10)
    
    # Font sizes
    FONT_LARGE = sp(20)
    FONT_MEDIUM = sp(16)
    FONT_REGULAR = sp(14)
    FONT_SMALL = sp(12)
    FONT_XSMALL = sp(10)

# ==================== CONFIGURATION ====================

DEFAULT_SERVER_URLS = [
    "https://culminate-retype-cresting.ngrok-free.dev",
    "https://unowing-earnest-gapless.ngrok-free.dev"
]

APP_NAME = "MzindaTrack"
APP_VERSION = "2.1"

# ==================== STORE SETTINGS ====================

class SettingsStore:
    """Handle persistent settings storage"""
    
    def __init__(self):
        self.store = None
        try:
            self.store = JsonStore('mzindatrack_settings.json')
        except Exception as e:
            print(f"Settings store error: {e}")
    
    def get(self, key, default=None):
        try:
            if self.store and self.store.exists(key):
                # JsonStore returns dict, we need to extract the value
                data = self.store.get(key)
                # Check if we stored as {'value': actual_value} or directly
                if isinstance(data, dict) and 'value' in data:
                    return data['value']
                return data
            return default
        except Exception as e:
            print(f"Get error: {e}")
            return default
    
    def put(self, key, value):
        try:
            if self.store:
                self.store.put(key, value=value)
                return True
        except Exception as e:
            print(f"Put error: {e}")
            return False
        return False
    
    def delete(self, key):
        try:
            if self.store and self.store.exists(key):
                self.store.delete(key)
                return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False
        return False

# ==================== CUSTOM WIDGETS ====================

class StatusBar(BoxLayout):
    """Custom status bar"""
    status_text = StringProperty("Ready")
    status_color = StringProperty("#8892b0")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = Theme.STATUS_BAR_HEIGHT
        self.padding = [dp(12), dp(6)]
        self.orientation = 'horizontal'
        self.spacing = dp(8)
        
        # Status icon
        self.status_icon = Label(
            text="●",
            font_size=sp(10),
            size_hint=(None, 1),
            width=dp(16),
            color=Theme.TEXT_MUTED
        )
        self.add_widget(self.status_icon)
        
        # Status text
        self.status_label = Label(
            text=self.status_text,
            font_size=Theme.FONT_SMALL,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, 1),
            halign='left',
            valign='middle'
        )
        self.bind(status_text=lambda _, v: setattr(self.status_label, 'text', v))
        self.add_widget(self.status_label)
        
        # Timestamp
        self.timestamp = Label(
            text=datetime.now().strftime("%H:%M"),
            font_size=Theme.FONT_XSMALL,
            color=Theme.TEXT_MUTED,
            size_hint=(None, 1),
            width=dp(50),
            halign='right'
        )
        self.add_widget(self.timestamp)
        
        Clock.schedule_interval(self.update_timestamp, 30)
    
    def update_timestamp(self, dt):
        self.timestamp.text = datetime.now().strftime("%H:%M")
    
    def set_status(self, text, color="#8892b0", icon="●"):
        self.status_text = text
        self.status_color = color
        self.status_icon.text = icon
        self.status_icon.color = self._hex_to_rgb(color)
        self.status_label.color = self._hex_to_rgb(color)
    
    def _hex_to_rgb(self, hex_color):
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
            if len(hex_color) == 6:
                r, g, b = int(hex_color[0:2], 16) / 255.0, int(hex_color[2:4], 16) / 255.0, int(hex_color[4:6], 16) / 255.0
                return (r, g, b, 1)
        return Theme.TEXT_SECONDARY

class Header(BoxLayout):
    """Custom header with hamburger menu"""
    title = StringProperty("MzindaTrack")
    page_name = StringProperty("Connect")
    status_indicator = StringProperty("⚪")
    status_tooltip = StringProperty("Disconnected")
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.size_hint_y = None
        self.height = Theme.HEADER_HEIGHT
        self.padding = [dp(8), dp(4)]
        self.spacing = dp(4)
        
        with self.canvas.before:
            Color(*Theme.BACKGROUND)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            Color(0.08, 0.1, 0.2, 0.3)
            self.gradient_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        self.build_ui()
    
    def _update_rect(self, instance, value):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.gradient_rect.pos = self.pos
        self.gradient_rect.size = self.size
    
    def build_ui(self):
        # Logo
        self.logo_label = Label(
            text="🎯 MzindaTrack",
            font_size=Theme.FONT_REGULAR,
            bold=True,
            color=Theme.ACCENT,
            size_hint=(None, 1),
            width=dp(130),
            halign='left'
        )
        self.add_widget(self.logo_label)
        
        # Spacer
        spacer = Label(size_hint=(1, 1))
        self.add_widget(spacer)
        
        # Page indicator
        self.page_indicator = Label(
            text="🔗 Connect",
            font_size=Theme.FONT_SMALL,
            color=Theme.TEXT_SECONDARY,
            size_hint=(None, 1),
            width=dp(90),
            halign='center'
        )
        self.add_widget(self.page_indicator)
        
        # Status indicator
        self.status_indicator_label = Label(
            text="⚪",
            font_size=sp(16),
            size_hint=(None, 1),
            width=dp(30),
            halign='center'
        )
        self.add_widget(self.status_indicator_label)
        
        # Auto-connect status
        self.auto_status_label = Label(
            text="",
            font_size=Theme.FONT_XSMALL,
            color=Theme.ACCENT,
            size_hint=(None, 1),
            width=dp(40),
            halign='center'
        )
        self.auto_status_label.opacity = 0
        self.add_widget(self.auto_status_label)
        
        # Hamburger menu button
        self.hamburger_btn = Button(
            text="☰",
            font_size=sp(22),
            bold=True,
            color=Theme.TEXT_PRIMARY,
            background_color=(0, 0, 0, 0),
            size_hint=(None, None),
            size=(dp(44), dp(44))
        )
        self.hamburger_btn.bind(on_press=self.app.open_hamburger_menu)
        self.add_widget(self.hamburger_btn)
    
    def update_status(self, status, tooltip):
        self.status_indicator = status
        self.status_tooltip = tooltip
        self.status_indicator_label.text = status
        
        anim = Animation(opacity=0.3, duration=0.1) + Animation(opacity=1, duration=0.2)
        anim.start(self.status_indicator_label)
    
    def update_page(self, page_name):
        self.page_name = page_name
        self.page_indicator.text = page_name

class CustomPopup(Popup):
    """Custom styled popup"""
    
    def __init__(self, title, content, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.size_hint = (0.9, None)
        self.height = min(dp(350), Window.height * 0.7)
        self.auto_dismiss = True
        self.separator_height = dp(1)
        self.separator_color = (0.2, 0.2, 0.3, 1)
        self.title_color = Theme.TEXT_PRIMARY
        self.title_size = Theme.FONT_MEDIUM
        self.title_align = 'center'

# ==================== HAMBURGER MENU ====================

class HamburgerMenu(Popup):
    """Hamburger menu popup"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = "Menu"
        self.size_hint = (0.8, None)
        self.height = dp(420)
        self.auto_dismiss = True
        self.background_color = (0.04, 0.06, 0.12, 0.95)
        self.build_ui()
    
    def build_ui(self):
        content = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            padding=[dp(12), dp(8), dp(12), dp(8)]
        )
        
        # App name
        app_name = Label(
            text="🎯 MzindaTrack",
            font_size=Theme.FONT_LARGE,
            bold=True,
            color=Theme.ACCENT,
            size_hint=(1, None),
            height=dp(44),
            halign='center'
        )
        content.add_widget(app_name)
        content.add_widget(self._create_separator())
        
        # Menu items
        menu_items = [
            ("🔗 Connect", self.app.switch_to_connect, True),
            ("🌐 View", self.app.switch_to_view, True),
            ("👤 Account", self.app.switch_to_account, True),
            ("🗺️ Open Map", self.app.open_map, self.app.verified),
            ("📱 Phone Tracker", self.app.open_phone, self.app.verified),
        ]
        
        for text, callback, enabled in menu_items:
            btn = Button(
                text=text,
                font_size=Theme.FONT_REGULAR,
                size_hint=(1, None),
                height=Theme.BUTTON_HEIGHT,
                background_color=Theme.BACKGROUND_CARD if enabled else (0.08, 0.08, 0.12, 1),
                color=Theme.TEXT_PRIMARY if enabled else Theme.TEXT_MUTED,
                disabled=not enabled
            )
            btn.bind(on_press=callback)
            content.add_widget(btn)
        
        content.add_widget(self._create_separator())
        
        # Auto-connect toggle
        auto_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=Theme.BUTTON_HEIGHT
        )
        self.auto_check = ToggleButton(
            text="🔄 Auto-Connect",
            state='down' if self.app.auto_connect_enabled else 'normal',
            font_size=Theme.FONT_REGULAR,
            size_hint=(1, 1),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY
        )
        self.auto_check.bind(state=self.toggle_auto_connect)
        auto_layout.add_widget(self.auto_check)
        content.add_widget(auto_layout)
        
        # Full screen toggle
        self.fullscreen_btn = Button(
            text="⛶ Full Screen",
            font_size=Theme.FONT_REGULAR,
            size_hint=(1, None),
            height=Theme.BUTTON_HEIGHT,
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY
        )
        self.fullscreen_btn.bind(on_press=self.toggle_fullscreen)
        content.add_widget(self.fullscreen_btn)
        
        content.add_widget(self._create_separator())
        
        # Disconnect button
        self.disconnect_btn = Button(
            text="🚪 Disconnect",
            font_size=Theme.FONT_REGULAR,
            size_hint=(1, None),
            height=Theme.BUTTON_HEIGHT,
            background_color=Theme.ERROR,
            color=(1, 1, 1, 1),
            disabled=not self.app.verified
        )
        self.disconnect_btn.bind(on_press=self.app.disconnect)
        content.add_widget(self.disconnect_btn)
        
        # Version info
        version = Label(
            text=f"MzindaTrack v{APP_VERSION}",
            font_size=Theme.FONT_XSMALL,
            color=Theme.TEXT_MUTED,
            size_hint=(1, None),
            height=dp(24),
            halign='center'
        )
        content.add_widget(version)
        
        self.content = content
        self.bind(on_dismiss=self.on_close)
    
    def _create_separator(self):
        return Label(text="", size_hint=(1, None), height=dp(4))
    
    def toggle_auto_connect(self, instance, state):
        enabled = state == 'down'
        self.app.auto_connect_enabled = enabled
        if enabled and not self.app.verified:
            self.app.start_auto_connect()
        elif not enabled:
            self.app.stop_auto_connect()
        self.app.save_settings()
        self.app.update_auto_indicator()
    
    def toggle_fullscreen(self, instance):
        self.app.toggle_fullscreen()
        self.dismiss()
    
    def on_close(self, instance):
        pass

# ==================== API CLIENT ====================

class MzindaTrackAPI:
    """API client for MzindaTrack server"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url.rstrip('/') if base_url else None
        self._request_timeout = 15
        self._retry_count = 2
    
    def set_base_url(self, url):
        self.base_url = url.rstrip('/') if url else None
    
    def verify_token(self, token, callback, retry=True):
        if not self.base_url:
            callback({'valid': False, 'error': 'No server URL set'})
            return
        
        url = f"{self.base_url}/api/user_info/{token}"
        
        def on_success(req, result):
            if result:
                callback({
                    'valid': True,
                    'user_info': result,
                    'token': token
                })
            else:
                callback({'valid': False, 'error': 'Invalid response from server'})
        
        def on_failure(req, result):
            if result and hasattr(result, 'status_code') and result.status_code == 403:
                callback({'valid': False, 'error': 'Token is invalid or expired'})
            else:
                error_msg = f'Server error: {result.status_code if result and hasattr(result, "status_code") else "unknown"}'
                if retry and self._retry_count > 0:
                    self._retry_count -= 1
                    Clock.schedule_once(
                        lambda dt: self.verify_token(token, callback, False),
                        1.0
                    )
                else:
                    callback({'valid': False, 'error': error_msg})
        
        def on_error(req, error):
            if retry and self._retry_count > 0:
                self._retry_count -= 1
                Clock.schedule_once(
                    lambda dt: self.verify_token(token, callback, False),
                    2.0
                )
            else:
                callback({'valid': False, 'error': f'Connection error: {str(error)}'})
        
        UrlRequest(
            url,
            on_success=on_success,
            on_failure=on_failure,
            on_error=on_error,
            timeout=self._request_timeout,
            method='GET'
        )
    
    def register_user(self, full_name, email, organisation, callback):
        if not self.base_url:
            callback({'success': False, 'error': 'No server URL set'})
            return
        
        url = f"{self.base_url}/api/register"
        
        UrlRequest(
            url,
            on_success=lambda req, result: callback(result),
            on_failure=lambda req, result: callback({
                'success': False,
                'error': f'Server error: {result.status_code if result and hasattr(result, "status_code") else "unknown"}'
            }),
            on_error=lambda req, error: callback({
                'success': False,
                'error': f'Connection error: {str(error)}'
            }),
            timeout=15,
            method='POST',
            req_body=json.dumps({
                'full_name': full_name,
                'email': email,
                'organisation': organisation
            }),
            req_headers={'Content-Type': 'application/json'}
        )
    
    def get_health(self, callback):
        if not self.base_url:
            callback({'status': 'unknown'})
            return
        
        url = f"{self.base_url}/health"
        
        UrlRequest(
            url,
            on_success=lambda req, result: callback(result),
            on_failure=lambda req, result: callback({'status': 'unhealthy'}),
            on_error=lambda req, error: callback({'status': 'unreachable'}),
            timeout=5,
            method='GET'
        )

# ==================== LOADING SPINNER ====================

class LoadingSpinner(BoxLayout):
    """Custom loading spinner"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, 1)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        
        spinner_layout = BoxLayout(
            orientation='vertical',
            size_hint=(0.3, 0.3),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        self.spinner_label = Label(
            text="⏳",
            font_size=sp(48),
            size_hint=(1, 0.7),
            halign='center',
            valign='middle'
        )
        spinner_layout.add_widget(self.spinner_label)
        
        self.message_label = Label(
            text="Loading...",
            font_size=Theme.FONT_REGULAR,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, 0.3),
            halign='center'
        )
        spinner_layout.add_widget(self.message_label)
        
        self.add_widget(spinner_layout)
        
        self._rotation_angle = 0
        self._rotation_event = Clock.schedule_interval(self._rotate_spinner, 0.1)
    
    def _rotate_spinner(self, dt):
        self._rotation_angle = (self._rotation_angle + 30) % 360
        self.spinner_label.font_size = sp(48 + abs((self._rotation_angle % 180) - 90) / 5)
    
    def set_message(self, message):
        self.message_label.text = message
    
    def stop(self):
        if self._rotation_event:
            self._rotation_event.cancel()
            self._rotation_event = None

# ==================== MAIN APP ====================

class MzindaTrackApp(App):
    """Main MzindaTrack Mobile Application"""
    
    def build(self):
        self.title = APP_NAME
        self.api = MzindaTrackAPI()
        self.verified = False
        self.current_token = None
        self.user_info = None
        self.auto_connect_enabled = True
        self.auto_connect_active = False
        self.is_fullscreen = False
        self.hamburger_menu = None
        self.recent_tokens = []
        
        # Setup theme
        self.setup_theme()
        
        # Settings store
        self.settings = SettingsStore()
        
        # Main screen manager
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Create screens
        self.connect_screen = ConnectScreen(self, name='connect')
        self.view_screen = ViewScreen(self, name='view')
        self.account_screen = AccountScreen(self, name='account')
        
        self.screen_manager.add_widget(self.connect_screen)
        self.screen_manager.add_widget(self.view_screen)
        self.screen_manager.add_widget(self.account_screen)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Header
        self.header = Header(self)
        self.header.title = APP_NAME
        main_layout.add_widget(self.header)
        
        # Content
        main_layout.add_widget(self.screen_manager)
        
        # Status bar
        self.status_bar = StatusBar()
        self.status_bar.set_status("Ready", "#8892b0", "●")
        main_layout.add_widget(self.status_bar)
        
        # Load settings
        self.load_settings()
        
        # Start auto-connect if enabled
        if self.auto_connect_enabled:
            Clock.schedule_once(lambda dt: self.start_auto_connect(), 1.5)
        
        # Keyboard event listener
        Window.bind(on_keyboard=self._on_keyboard)
        
        return main_layout
    
    def setup_theme(self):
        Window.clearcolor = Theme.BACKGROUND
    
    def _on_keyboard(self, window, key, scancode, codepoint, modifier):
        if key == 27:  # ESC key
            if self.hamburger_menu and self.hamburger_menu._is_open:
                self.hamburger_menu.dismiss()
                self.hamburger_menu = None
                return True
        return False
    
    def load_settings(self):
        """Load settings from storage"""
        settings = self.settings.get('settings')
        if settings and isinstance(settings, dict):
            self.auto_connect_enabled = settings.get('auto_connect_enabled', True)
            server_url = settings.get('server_url', '')
            if server_url:
                self.connect_screen.server_input.text = server_url
                self.api.set_base_url(server_url)
            
            recent_tokens = settings.get('recent_tokens', [])
            self.recent_tokens = recent_tokens[:5] if isinstance(recent_tokens, list) else []
            self.update_recent_list()
            
            # Load saved token
            token = self.settings.get('token')
            if token:
                self.connect_screen.token_input.text = token
        
        if not self.api.base_url:
            self.connect_screen.server_input.text = DEFAULT_SERVER_URLS[0]
            self.api.set_base_url(DEFAULT_SERVER_URLS[0])
        
        self.connect_screen.auto_connect_check.state = 'down' if self.auto_connect_enabled else 'normal'
        self.update_auto_indicator()
    
    def save_settings(self):
        """Save settings to storage"""
        settings = {
            'auto_connect_enabled': self.auto_connect_enabled,
            'server_url': self.connect_screen.server_input.text.strip(),
            'recent_tokens': self.recent_tokens[:5]
        }
        self.settings.put('settings', settings)
    
    def update_recent_list(self):
        """Update recent connections list"""
        if self.recent_tokens:
            texts = []
            for t in self.recent_tokens[:5]:
                display = t[:20] + "..." if len(t) > 20 else t
                texts.append(f"• {display}")
            self.connect_screen.recent_list.text = "\n".join(texts)
            self.connect_screen.recent_list.color = Theme.PRIMARY
        else:
            self.connect_screen.recent_list.text = "No recent connections"
            self.connect_screen.recent_list.color = Theme.TEXT_MUTED
    
    def update_auto_indicator(self):
        """Update auto-connect indicator"""
        if self.auto_connect_enabled:
            self.header.auto_status_label.text = "🔄"
            self.header.auto_status_label.opacity = 1
            self.header.auto_status_label.color = Theme.ACCENT
        else:
            self.header.auto_status_label.text = ""
            self.header.auto_status_label.opacity = 0
    
    def start_auto_connect(self):
        """Start auto-connect process"""
        if not self.auto_connect_enabled or self.verified:
            return
        if self.auto_connect_active:
            return
        
        self.auto_connect_active = True
        self.header.update_status("🔄", "Auto-connecting...")
        self.status_bar.set_status("🔄 Auto-connecting...", "#64ffda", "●")
        
        token = self.settings.get('token')
        
        if not token:
            self.auto_connect_active = False
            self.header.update_status("⚪", "Disconnected")
            self.status_bar.set_status("No saved token", "#8892b0", "●")
            return
        
        self.connect_screen.token_input.text = token
        server_url = self.connect_screen.server_input.text.strip()
        
        if server_url:
            self.api.set_base_url(server_url)
            self.connect_screen.verify_btn.disabled = True
            self.status_bar.set_status("🔄 Verifying saved token...", "#8892b0", "●")
            
            def on_verify(result):
                self.auto_connect_active = False
                if result.get('valid'):
                    self.on_verification_success(result)
                    self.status_bar.set_status("✅ Auto-connected successfully", "#4CAF50", "●")
                    self.header.update_status("✅", "Connected")
                else:
                    self._try_alternate_servers(token)
            
            self.api.verify_token(token, on_verify)
    
    def _try_alternate_servers(self, token):
        """Try connecting with alternate servers"""
        def try_next_server(server_index):
            if server_index >= len(DEFAULT_SERVER_URLS):
                self.on_verification_failure({'error': 'All servers unreachable'}, auto=True)
                self.status_bar.set_status("⚠️ Auto-connect failed", "#FF9800", "●")
                self.header.update_status("⚪", "Disconnected")
                self.connect_screen.verify_btn.disabled = False
                return
            
            url = DEFAULT_SERVER_URLS[server_index]
            if url == self.api.base_url:
                try_next_server(server_index + 1)
                return
            
            self.api.set_base_url(url)
            self.connect_screen.server_input.text = url
            
            def on_verify(result):
                if result.get('valid'):
                    self.on_verification_success(result)
                    self.status_bar.set_status("✅ Auto-connected successfully", "#4CAF50", "●")
                    self.header.update_status("✅", "Connected")
                else:
                    try_next_server(server_index + 1)
            
            self.api.verify_token(token, on_verify)
        
        try_next_server(0)
    
    def stop_auto_connect(self):
        """Stop auto-connect process"""
        self.auto_connect_active = False
        self.status_bar.set_status("Auto-connect stopped", "#8892b0", "●")
        self.header.update_status("⚪", "Disconnected")
        self.update_auto_indicator()
    
    def on_verification_success(self, result):
        """Handle successful verification"""
        self.verified = True
        self.current_token = result.get('token')
        self.user_info = result.get('user_info', {})
        
        # Save token
        self.settings.put('token', self.current_token)
        
        # Update recent tokens
        if self.current_token not in self.recent_tokens:
            self.recent_tokens.insert(0, self.current_token)
            self.recent_tokens = self.recent_tokens[:5]
        self.save_settings()
        self.update_recent_list()
        
        # Update connect screen
        self.connect_screen.status_label.text = "✅ Token verified successfully!"
        self.connect_screen.status_label.color = Theme.SUCCESS
        self.connect_screen.progress.opacity = 0
        self.connect_screen.verify_btn.disabled = False
        
        # Update account screen
        user = self.user_info
        self.account_screen.name_label.text = f"👤 {user.get('full_name', 'User')}"
        self.account_screen.email_label.text = f"📧 {user.get('email', '')}"
        
        if user.get('organisation'):
            self.account_screen.org_label.text = f"🏢 {user['organisation']}"
        else:
            self.account_screen.org_label.text = ""
        
        self.account_screen.status_label.text = "✅ Account Active"
        self.account_screen.status_label.color = Theme.SUCCESS
        self.account_screen.disconnect_btn.disabled = False
        
        # Update header
        self.header.update_status("✅", "Connected - Access granted")
        self.header.update_page("Connected")
        
        # Update status bar
        self.status_bar.set_status("✅ Access granted - Welcome!", "#4CAF50", "●")
        
        # Update hamburger menu if open
        if self.hamburger_menu:
            self.hamburger_menu.disconnect_btn.disabled = False
    
    def on_verification_failure(self, result, auto=False):
        """Handle verification failure"""
        self.verified = False
        error_msg = result.get('error', 'Invalid token')
        
        self.connect_screen.status_label.text = f"❌ {error_msg}"
        self.connect_screen.status_label.color = Theme.ERROR
        self.connect_screen.progress.opacity = 0
        self.connect_screen.verify_btn.disabled = False
        
        self.header.update_status("⚪", "Disconnected")
        self.status_bar.set_status("❌ Verification failed", "#f44336", "●")
        
        if not auto:
            self.show_message(
                "Verification Failed",
                f"❌ {error_msg}\n\nPossible solutions:\n• Check your internet connection\n• Verify the token is correct\n• Try a different server URL\n• Contact support if issue persists",
                "error"
            )
    
    def show_registration_dialog(self):
        """Show registration dialog"""
        server_url = self.connect_screen.server_input.text.strip()
        if not server_url:
            self.show_message("Warning", "Please enter the server URL first", "warning")
            return
        
        if not server_url.startswith('http://') and not server_url.startswith('https://'):
            server_url = 'http://' + server_url
            self.connect_screen.server_input.text = server_url
        
        self.api.set_base_url(server_url)
        dialog = RegistrationPopup(self)
        dialog.open()
    
    def open_hamburger_menu(self, instance=None):
        """Open hamburger menu"""
        if self.hamburger_menu and self.hamburger_menu._is_open:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None
        else:
            self.hamburger_menu = HamburgerMenu(self)
            self.hamburger_menu.open()
    
    def switch_to_connect(self, instance=None):
        """Switch to connect screen"""
        if self.is_fullscreen:
            self.toggle_fullscreen()
        self.screen_manager.current = 'connect'
        self.header.update_page("🔗 Connect")
        if self.hamburger_menu:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None
    
    def switch_to_view(self, instance=None):
        """Switch to view screen"""
        self.screen_manager.current = 'view'
        self.header.update_page("🌐 View")
        if self.hamburger_menu:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None
    
    def switch_to_account(self, instance=None):
        """Switch to account screen"""
        if self.is_fullscreen:
            self.toggle_fullscreen()
        self.screen_manager.current = 'account'
        self.header.update_page("👤 Account")
        if self.hamburger_menu:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None
    
    def toggle_fullscreen(self, instance=None):
        """Toggle full screen mode"""
        self.is_fullscreen = not self.is_fullscreen
        
        if self.is_fullscreen:
            anim1 = Animation(opacity=0, duration=0.3)
            anim1.start(self.header)
            anim1.start(self.status_bar)
            self.header.disabled = True
            self.status_bar.disabled = True
            try:
                Window.fullscreen = 'auto'
            except:
                Window.fullscreen = True
        else:
            anim2 = Animation(opacity=1, duration=0.3)
            anim2.start(self.header)
            anim2.start(self.status_bar)
            self.header.disabled = False
            self.status_bar.disabled = False
            try:
                Window.fullscreen = False
            except:
                pass
    
    def open_map(self, instance=None):
        """Open map view"""
        if not self.verified or not self.current_token:
            self.show_message("Warning", "Please verify your token first", "warning")
            return
        
        url = f"{self.api.base_url}/map/{self.current_token}"
        self.view_screen.load_url(url)
        self.view_screen.set_home_url(url)
        self.screen_manager.current = 'view'
        self.header.update_page("🗺️ Map")
        self.status_bar.set_status("Loading map...", "#8892b0", "●")
        
        if self.hamburger_menu:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None
    
    def open_phone(self, instance=None):
        """Open phone tracker"""
        if not self.verified or not self.current_token:
            self.show_message("Warning", "Please verify your token first", "warning")
            return
        
        url = f"{self.api.base_url}/phone/{self.current_token}"
        self.view_screen.load_url(url)
        self.view_screen.set_home_url(url)
        self.screen_manager.current = 'view'
        self.header.update_page("📱 Phone Tracker")
        self.status_bar.set_status("Loading phone tracker...", "#8892b0", "●")
        
        if self.hamburger_menu:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None
    
    def disconnect(self, instance=None):
        """Disconnect from server with confirmation"""
        if not self.verified:
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        msg = Label(
            text="Are you sure you want to disconnect from MzindaTrack?\n\nYou will need to verify again to access your data.",
            font_size=Theme.FONT_REGULAR,
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=dp(80),
            text_size=(Window.width - dp(80), None)
        )
        content.add_widget(msg)
        
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=Theme.BUTTON_HEIGHT
        )
        
        yes_btn = Button(
            text="Yes, Disconnect",
            background_color=Theme.ERROR,
            color=(1, 1, 1, 1)
        )
        no_btn = Button(
            text="Cancel",
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY
        )
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title="Disconnect",
            content=content,
            size_hint=(0.85, None),
            height=dp(200),
            auto_dismiss=True
        )
        
        def on_yes(instance):
            popup.dismiss()
            self._do_disconnect()
            if self.hamburger_menu:
                self.hamburger_menu.dismiss()
                self.hamburger_menu = None
        
        def on_no(instance):
            popup.dismiss()
        
        yes_btn.bind(on_press=on_yes)
        no_btn.bind(on_press=on_no)
        popup.open()
    
    def _do_disconnect(self):
        """Perform disconnection"""
        self.verified = False
        self.current_token = None
        self.user_info = None
        
        # Update account screen
        self.account_screen.name_label.text = "Not logged in"
        self.account_screen.email_label.text = ""
        self.account_screen.org_label.text = ""
        self.account_screen.status_label.text = "Status: Disconnected"
        self.account_screen.status_label.color = Theme.WARNING
        self.account_screen.disconnect_btn.disabled = True
        
        # Update header
        self.header.update_status("⚪", "Disconnected")
        self.header.update_page("Connect")
        
        # Update status bar
        self.status_bar.set_status("Disconnected", "#8892b0", "●")
        
        # Switch to connect screen
        self.screen_manager.current = 'connect'
        
        # Clear token
        self.settings.delete('token')
        
        # Update hamburger menu if open
        if self.hamburger_menu:
            self.hamburger_menu.disconnect_btn.disabled = True
        
        # Restart auto-connect if enabled
        if self.auto_connect_enabled:
            Clock.schedule_once(lambda dt: self.start_auto_connect(), 2)
    
    def show_message(self, title, message, msg_type="info"):
        """Show a message popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        icon = "ℹ️" if msg_type == "info" else "⚠️" if msg_type == "warning" else "❌" if msg_type == "error" else "✅"
        
        msg_label = Label(
            text=f"{icon} {message}",
            font_size=Theme.FONT_REGULAR,
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=min(dp(200), max(dp(80), len(message) * 1.5)),
            text_size=(Window.width - dp(80), None)
        )
        content.add_widget(msg_label)
        
        close_btn = Button(
            text="OK",
            size_hint=(1, None),
            height=Theme.BUTTON_HEIGHT,
            background_color=Theme.PRIMARY,
            color=(1, 1, 1, 1)
        )
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.85, None),
            height=min(dp(350), dp(180 + len(message) * 1.5)),
            auto_dismiss=True
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass
    
    def on_stop(self):
        if self.hamburger_menu and self.hamburger_menu._is_open:
            self.hamburger_menu.dismiss()
            self.hamburger_menu = None

# ==================== SCREENS ====================

class ConnectScreen(Screen):
    """Connection/Verification screen"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self._progress_event = None
        self.build_ui()
    
    def build_ui(self):
        padding = Theme.PADDING
        spacing = Theme.SPACING
        
        layout = BoxLayout(orientation='vertical', padding=padding, spacing=spacing)
        scroll = ScrollView(size_hint=(1, 1))
        
        content = BoxLayout(
            orientation='vertical',
            spacing=spacing,
            size_hint_y=None,
            padding=[dp(4), dp(4)]
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Title
        title = Label(
            text="🔑 Connect to MzindaTrack",
            font_size=Theme.FONT_LARGE,
            bold=True,
            color=Theme.PRIMARY,
            size_hint=(1, None),
            height=dp(44),
            halign='center',
            text_size=(Window.width - padding * 2, None)
        )
        content.add_widget(title)
        
        # Subtitle
        subtitle = Label(
            text="Enter your MzindaTrack token or the public URL you received via email.",
            font_size=Theme.FONT_REGULAR,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(56),
            halign='center',
            valign='middle',
            text_size=(Window.width - padding * 2, None)
        )
        content.add_widget(subtitle)
        
        # Server URL section
        server_group = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint_y=None,
            height=dp(140)
        )
        
        server_label = Label(
            text="Server URL",
            font_size=Theme.FONT_REGULAR,
            bold=True,
            size_hint=(1, None),
            height=dp(24),
            halign='left',
            color=Theme.TEXT_PRIMARY
        )
        server_group.add_widget(server_label)
        
        server_input_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(6),
            size_hint_y=None,
            height=Theme.INPUT_HEIGHT
        )
        
        self.server_input = TextInput(
            multiline=False,
            hint_text="Enter server URL",
            size_hint=(0.6, 1),
            background_color=Theme.BACKGROUND_INPUT,
            foreground_color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        server_input_layout.add_widget(self.server_input)
        
        self.server_spinner = Spinner(
            text='Select default...',
            values=['Select default...'] + DEFAULT_SERVER_URLS,
            size_hint=(0.25, 1),
            background_color=Theme.BACKGROUND_INPUT,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SMALL
        )
        self.server_spinner.bind(text=self.on_server_selected)
        server_input_layout.add_widget(self.server_spinner)
        
        self.test_btn = Button(
            text="Test",
            size_hint=(0.15, 1),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SMALL
        )
        self.test_btn.bind(on_press=self.test_server)
        server_input_layout.add_widget(self.test_btn)
        
        server_group.add_widget(server_input_layout)
        content.add_widget(server_group)
        
        # Token section
        token_group = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint_y=None,
            height=dp(110)
        )
        
        token_label = Label(
            text="Token or Access URL",
            font_size=Theme.FONT_REGULAR,
            bold=True,
            size_hint=(1, None),
            height=dp(24),
            halign='left',
            color=Theme.TEXT_PRIMARY
        )
        token_group.add_widget(token_label)
        
        token_input_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(6),
            size_hint_y=None,
            height=Theme.INPUT_HEIGHT
        )
        
        self.token_input = TextInput(
            multiline=False,
            hint_text="Paste your token or URL here",
            size_hint=(0.85, 1),
            background_color=Theme.BACKGROUND_INPUT,
            foreground_color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        token_input_layout.add_widget(self.token_input)
        
        self.paste_btn = Button(
            text="📋",
            size_hint=(0.15, 1),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.paste_btn.bind(on_press=self.paste_token)
        token_input_layout.add_widget(self.paste_btn)
        
        token_group.add_widget(token_input_layout)
        content.add_widget(token_group)
        
        # Auto-connect
        auto_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=Theme.BUTTON_HEIGHT
        )
        
        self.auto_connect_check = ToggleButton(
            text="🔄 Auto-connect on startup",
            state='down',
            size_hint=(1, None),
            height=Theme.BUTTON_HEIGHT,
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.auto_connect_check.bind(state=self.toggle_auto_connect)
        auto_layout.add_widget(self.auto_connect_check)
        content.add_widget(auto_layout)
        
        # Buttons
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=Theme.BUTTON_HEIGHT
        )
        
        self.verify_btn = Button(
            text="🔐 Verify Token",
            size_hint=(0.6, 1),
            background_color=Theme.PRIMARY,
            color=(1, 1, 1, 1),
            font_size=Theme.FONT_REGULAR
        )
        self.verify_btn.bind(on_press=self.verify_token)
        btn_layout.add_widget(self.verify_btn)
        
        self.register_btn = Button(
            text="📝 Register",
            size_hint=(0.4, 1),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.register_btn.bind(on_press=self.open_registration)
        btn_layout.add_widget(self.register_btn)
        
        content.add_widget(btn_layout)
        
        # Progress
        self.progress = ProgressBar(
            value=0,
            size_hint=(1, None),
            height=dp(6)
        )
        self.progress.opacity = 0
        content.add_widget(self.progress)
        
        # Status
        self.status_label = Label(
            text="",
            font_size=Theme.FONT_REGULAR,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(32),
            halign='center',
            valign='middle'
        )
        content.add_widget(self.status_label)
        
        # Recent connections
        recent_group = BoxLayout(
            orientation='vertical',
            spacing=dp(4),
            size_hint_y=None,
            height=dp(80)
        )
        
        recent_label = Label(
            text="Recent Connections",
            font_size=Theme.FONT_REGULAR,
            bold=True,
            size_hint=(1, None),
            height=dp(24),
            halign='left',
            color=Theme.TEXT_PRIMARY
        )
        recent_group.add_widget(recent_label)
        
        self.recent_list = Label(
            text="No recent connections",
            font_size=Theme.FONT_SMALL,
            color=Theme.TEXT_MUTED,
            size_hint=(1, None),
            height=dp(50),
            halign='center',
            valign='middle'
        )
        recent_group.add_widget(self.recent_list)
        content.add_widget(recent_group)
        
        # Footer
        footer = Label(
            text="🔐 MzindaTrack - GPS yathu, Chitetezo chathu\nSecure GPS tracking with 2-meter precision",
            font_size=Theme.FONT_XSMALL,
            color=Theme.TEXT_MUTED,
            size_hint=(1, None),
            height=dp(50),
            halign='center',
            valign='middle'
        )
        content.add_widget(footer)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def on_server_selected(self, spinner, text):
        if text and text != 'Select default...':
            self.server_input.text = text
            self.app.api.set_base_url(text)
    
    def test_server(self, instance):
        url = self.server_input.text.strip()
        if not url:
            self.show_message("Warning", "Please enter a server URL", "warning")
            return
        
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
            self.server_input.text = url
        
        self.app.api.set_base_url(url)
        self.test_btn.text = "Testing..."
        self.test_btn.disabled = True
        
        def on_result(result):
            self.test_btn.text = "Test"
            self.test_btn.disabled = False
            
            if result.get('status') == 'healthy':
                self.app.status_bar.set_status("✅ Connected to server", "#4CAF50", "●")
                self.app.header.update_status("✅", "Connected to server")
                self.show_message(
                    "Connection Test",
                    "✅ Successfully connected to MzindaTrack server!\n\nYou can now verify your token.",
                    "success"
                )
            else:
                self.app.status_bar.set_status("❌ Could not connect to server", "#f44336", "●")
                self.app.header.update_status("⚪", "Disconnected")
                self.show_message(
                    "Connection Failed",
                    "❌ Could not connect to the server.\n\nPlease check:\n• The URL is correct\n• Your internet connection\n• The server is running",
                    "error"
                )
        
        self.app.api.get_health(on_result)
    
    def paste_token(self, instance):
        try:
            from kivy.core.clipboard import Clipboard
            text = Clipboard.paste()
            if text:
                self.token_input.text = text
        except Exception as e:
            print(f"Clipboard paste error: {e}")
            try:
                self.token_input.paste()
            except:
                self.show_message("Info", "Please paste the token manually", "info")
    
    def verify_token(self, instance):
        token = self.token_input.text.strip()
        if not token:
            self.show_message("Warning", "Please enter your token", "warning")
            return
        
        server_url = self.server_input.text.strip()
        if not server_url:
            self.show_message("Warning", "Please enter the server URL", "warning")
            return
        
        if not server_url.startswith('http://') and not server_url.startswith('https://'):
            server_url = 'http://' + server_url
            self.server_input.text = server_url
        
        self.app.api.set_base_url(server_url)
        
        self.verify_btn.disabled = True
        self.register_btn.disabled = True
        self.progress.opacity = 1
        self.progress.value = 0
        self.status_label.text = "Verifying token..."
        self.status_label.color = Theme.PRIMARY
        
        if self._progress_event:
            self._progress_event.cancel()
        self._progress_event = Clock.schedule_interval(self._update_progress, 0.05)
        
        def on_verify(result):
            if self._progress_event:
                self._progress_event.cancel()
                self._progress_event = None
            
            self.progress.value = 100
            self.verify_btn.disabled = False
            self.register_btn.disabled = False
            
            Clock.schedule_once(lambda dt: setattr(self.progress, 'opacity', 0), 0.5)
            
            if result.get('valid'):
                self.app.on_verification_success(result)
            else:
                self.app.on_verification_failure(result)
        
        self.app.api.verify_token(token, on_verify)
    
    def _update_progress(self, dt):
        if self.progress.value < 90:
            self.progress.value += 5
    
    def open_registration(self, instance):
        self.app.show_registration_dialog()
    
    def toggle_auto_connect(self, instance, state):
        enabled = state == 'down'
        self.app.auto_connect_enabled = enabled
        if enabled and not self.app.verified:
            self.app.start_auto_connect()
        elif not enabled:
            self.app.stop_auto_connect()
        self.app.save_settings()
        self.app.update_auto_indicator()
    
    def show_message(self, title, message, msg_type="info"):
        self.app.show_message(title, message, msg_type)

class ViewScreen(Screen):
    """Web view screen with improved controls"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_url = ""
        self.home_url = ""
        self.webview_loaded = False
        self.webview = None
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            padding=[dp(6), dp(4)],
            spacing=dp(4)
        )
        
        # Navigation buttons
        self.back_btn = Button(
            text="◀",
            size_hint=(None, None),
            size=(dp(36), dp(32)),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.back_btn.bind(on_press=self.go_back)
        
        self.forward_btn = Button(
            text="▶",
            size_hint=(None, None),
            size=(dp(36), dp(32)),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.forward_btn.bind(on_press=self.go_forward)
        
        self.refresh_btn = Button(
            text="⟳",
            size_hint=(None, None),
            size=(dp(36), dp(32)),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.refresh_btn.bind(on_press=self.refresh)
        
        # URL bar
        self.url_bar = TextInput(
            multiline=False,
            hint_text="Enter URL or wait for loading",
            size_hint=(1, None),
            height=dp(32),
            background_color=Theme.BACKGROUND_INPUT,
            foreground_color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_SMALL
        )
        self.url_bar.bind(on_text_validate=self.on_url_enter)
        
        # Action buttons
        self.home_btn = Button(
            text="🏠",
            size_hint=(None, None),
            size=(dp(36), dp(32)),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.home_btn.bind(on_press=self.go_home)
        
        self.open_btn = Button(
            text="↗",
            size_hint=(None, None),
            size=(dp(36), dp(32)),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.open_btn.bind(on_press=self.open_in_browser)
        
        self.fullscreen_btn = Button(
            text="⛶",
            size_hint=(None, None),
            size=(dp(36), dp(32)),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.fullscreen_btn.bind(on_press=self.toggle_fullscreen)
        
        toolbar.add_widget(self.back_btn)
        toolbar.add_widget(self.forward_btn)
        toolbar.add_widget(self.refresh_btn)
        toolbar.add_widget(self.url_bar)
        toolbar.add_widget(self.home_btn)
        toolbar.add_widget(self.open_btn)
        toolbar.add_widget(self.fullscreen_btn)
        
        layout.add_widget(toolbar)
        
        # WebView or placeholder
        if WEBVIEW_AVAILABLE:
            try:
                self.webview = WebView()
                self.webview.size_hint = (1, 1)
                layout.add_widget(self.webview)
                self.webview_loaded = True
                print("WebView loaded successfully")
            except Exception as e:
                print(f"WebView initialization error: {e}")
                self._create_placeholder(layout)
        else:
            self._create_placeholder(layout)
        
        self.add_widget(layout)
    
    def _create_placeholder(self, layout):
        """Create placeholder when WebView is not available"""
        placeholder_layout = BoxLayout(orientation='vertical')
        
        placeholder_icon = Label(
            text="🌐",
            font_size=sp(64),
            size_hint=(1, 0.6),
            halign='center',
            valign='middle'
        )
        placeholder_layout.add_widget(placeholder_icon)
        
        placeholder_text = Label(
            text="Web View Not Available\n\nOpen in browser instead",
            halign='center',
            valign='middle',
            color=Theme.TEXT_SECONDARY,
            font_size=Theme.FONT_MEDIUM,
            size_hint=(1, 0.4)
        )
        placeholder_layout.add_widget(placeholder_text)
        
        layout.add_widget(placeholder_layout)
        self.webview_loaded = False
        self.webview = None
    
    def on_url_enter(self, instance):
        url = self.url_bar.text.strip()
        if url:
            self.load_url(url)
    
    def load_url(self, url):
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        
        self.current_url = url
        self.url_bar.text = url
        
        if self.webview_loaded and self.webview:
            try:
                self.webview.load(url)
                self.app.status_bar.set_status(f"Loading: {url[:50]}...", "#8892b0", "●")
                return
            except Exception as e:
                print(f"WebView load error: {e}")
        
        # Fallback: open in browser
        self.app.status_bar.set_status(f"Opening in browser...", "#8892b0", "●")
        webbrowser.open(url)
    
    def set_home_url(self, url):
        self.home_url = url
    
    def go_home(self, instance=None):
        if self.home_url:
            self.load_url(self.home_url)
    
    def go_back(self, instance=None):
        if self.webview_loaded and self.webview:
            try:
                self.webview.go_back()
                return
            except Exception as e:
                print(f"WebView go_back error: {e}")
        if self.home_url:
            self.load_url(self.home_url)
    
    def go_forward(self, instance=None):
        if self.webview_loaded and self.webview:
            try:
                self.webview.go_forward()
                return
            except Exception as e:
                print(f"WebView go_forward error: {e}")
    
    def refresh(self, instance=None):
        if self.webview_loaded and self.webview:
            try:
                self.webview.reload()
                return
            except Exception as e:
                print(f"WebView reload error: {e}")
        if self.current_url:
            webbrowser.open(self.current_url)
    
    def open_in_browser(self, instance=None):
        if self.current_url:
            webbrowser.open(self.current_url)
            self.app.status_bar.set_status("Opened in browser", "#8892b0", "●")
    
    def toggle_fullscreen(self, instance=None):
        self.app.toggle_fullscreen()

class AccountScreen(Screen):
    """Account information screen"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.build_ui()
    
    def build_ui(self):
        padding = Theme.PADDING
        layout = BoxLayout(orientation='vertical', padding=padding, spacing=Theme.SPACING)
        
        # Card
        card = BoxLayout(
            orientation='vertical',
            padding=padding,
            spacing=dp(8),
            size_hint=(1, None),
            height=dp(280)
        )
        
        with card.canvas.before:
            Color(*Theme.BACKGROUND_CARD)
            self.card_rect = RoundedRectangle(
                pos=card.pos,
                size=card.size,
                radius=[dp(12)]
            )
            Color(0.25, 0.25, 0.35, 0.3)
            self.card_border = RoundedRectangle(
                pos=(card.pos[0] + 1, card.pos[1] + 1),
                size=(card.size[0] - 2, card.size[1] - 2),
                radius=[dp(12)]
            )
        
        card.bind(pos=self._update_card, size=self._update_card)
        
        # Avatar
        avatar = Label(
            text="👤",
            font_size=sp(48),
            size_hint=(1, None),
            height=dp(60),
            halign='center'
        )
        card.add_widget(avatar)
        
        self.name_label = Label(
            text="Not logged in",
            font_size=Theme.FONT_MEDIUM,
            bold=True,
            color=Theme.TEXT_PRIMARY,
            size_hint=(1, None),
            height=dp(32),
            halign='center'
        )
        card.add_widget(self.name_label)
        
        self.email_label = Label(
            text="",
            font_size=Theme.FONT_REGULAR,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(28),
            halign='center'
        )
        card.add_widget(self.email_label)
        
        self.org_label = Label(
            text="",
            font_size=Theme.FONT_REGULAR,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(28),
            halign='center'
        )
        card.add_widget(self.org_label)
        
        self.status_label = Label(
            text="Status: Disconnected",
            font_size=Theme.FONT_REGULAR,
            color=Theme.WARNING,
            size_hint=(1, None),
            height=dp(30),
            halign='center'
        )
        card.add_widget(self.status_label)
        
        self.disconnect_btn = Button(
            text="🚪 Disconnect",
            size_hint=(1, None),
            height=Theme.BUTTON_HEIGHT,
            background_color=Theme.ERROR,
            color=(1, 1, 1, 1),
            disabled=True,
            font_size=Theme.FONT_REGULAR
        )
        self.disconnect_btn.bind(on_press=self.app.disconnect)
        card.add_widget(self.disconnect_btn)
        
        layout.add_widget(card)
        
        # Info
        info = Label(
            text="⛶ Full screen available in web view\n📱 GPS tracking with 2-meter precision",
            font_size=Theme.FONT_SMALL,
            color=Theme.TEXT_MUTED,
            size_hint=(1, None),
            height=dp(50),
            halign='center'
        )
        layout.add_widget(info)
        
        self.add_widget(layout)
        self.card = card
    
    def _update_card(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*Theme.BACKGROUND_CARD)
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(12)]
            )
            Color(0.25, 0.25, 0.35, 0.3)
            RoundedRectangle(
                pos=(instance.pos[0] + 1, instance.pos[1] + 1),
                size=(instance.size[0] - 2, instance.size[1] - 2),
                radius=[dp(12)]
            )

class RegistrationPopup(Popup):
    """Registration dialog"""
    
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.title = "Register for MzindaTrack"
        self.size_hint = (0.85, None)
        self.height = dp(420)
        self.auto_dismiss = True
        self.build_ui()
    
    def build_ui(self):
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(12))
        
        header = Label(
            text="🎯 Register for MzindaTrack\nGPS yathu, Chitetezo chathu",
            font_size=Theme.FONT_MEDIUM,
            bold=True,
            color=Theme.PRIMARY,
            size_hint=(1, None),
            height=dp(60),
            halign='center'
        )
        content.add_widget(header)
        
        form = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(170)
        )
        
        self.name_input = TextInput(
            multiline=False,
            hint_text="Full Name *",
            size_hint=(1, None),
            height=Theme.INPUT_HEIGHT,
            background_color=Theme.BACKGROUND_INPUT,
            foreground_color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        form.add_widget(self.name_input)
        
        self.email_input = TextInput(
            multiline=False,
            hint_text="Email Address *",
            size_hint=(1, None),
            height=Theme.INPUT_HEIGHT,
            background_color=Theme.BACKGROUND_INPUT,
            foreground_color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        form.add_widget(self.email_input)
        
        self.org_input = TextInput(
            multiline=False,
            hint_text="Organisation (Optional)",
            size_hint=(1, None),
            height=Theme.INPUT_HEIGHT,
            background_color=Theme.BACKGROUND_INPUT,
            foreground_color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        form.add_widget(self.org_input)
        
        content.add_widget(form)
        
        info = Label(
            text="📌 You will receive a payment link via email.\nAfter payment, your access will be activated.",
            font_size=Theme.FONT_SMALL,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(50),
            halign='center'
        )
        content.add_widget(info)
        
        btn_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(8),
            size_hint_y=None,
            height=Theme.BUTTON_HEIGHT
        )
        
        self.register_btn = Button(
            text="✅ Register",
            size_hint=(0.6, 1),
            background_color=Theme.SUCCESS,
            color=(1, 1, 1, 1),
            font_size=Theme.FONT_REGULAR
        )
        self.register_btn.bind(on_press=self.register)
        
        self.cancel_btn = Button(
            text="Cancel",
            size_hint=(0.4, 1),
            background_color=Theme.BACKGROUND_CARD,
            color=Theme.TEXT_PRIMARY,
            font_size=Theme.FONT_REGULAR
        )
        self.cancel_btn.bind(on_press=self.dismiss)
        
        btn_layout.add_widget(self.register_btn)
        btn_layout.add_widget(self.cancel_btn)
        content.add_widget(btn_layout)
        
        self.status_label = Label(
            text="",
            font_size=Theme.FONT_SMALL,
            color=Theme.TEXT_SECONDARY,
            size_hint=(1, None),
            height=dp(28),
            halign='center'
        )
        content.add_widget(self.status_label)
        
        self.content = content
    
    def register(self, instance):
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        org = self.org_input.text.strip()
        
        if not name:
            self.status_label.text = "❌ Please enter your full name"
            self.status_label.color = Theme.ERROR
            self.name_input.focus = True
            return
        
        if not email or '@' not in email or '.' not in email:
            self.status_label.text = "❌ Please enter a valid email"
            self.status_label.color = Theme.ERROR
            self.email_input.focus = True
            return
        
        self.register_btn.disabled = True
        self.register_btn.text = "Registering..."
        self.status_label.text = "⏳ Contacting server..."
        self.status_label.color = Theme.PRIMARY
        
        def on_result(result):
            self.register_btn.disabled = False
            self.register_btn.text = "✅ Register"
            
            if result.get('success'):
                self.status_label.text = f"✅ {result.get('message', 'Registration successful')}"
                self.status_label.color = Theme.SUCCESS
                
                payment_url = result.get('payment_url')
                if payment_url:
                    self.app.show_message(
                        "Registration Successful",
                        f"✅ Registration successful!\n\nPayment link sent to {email}\n\nTap OK to open payment page.",
                        "success"
                    )
                    Clock.schedule_once(lambda dt: webbrowser.open(payment_url), 1.5)
                
                Clock.schedule_once(lambda dt: self.dismiss(), 3)
            else:
                error_msg = result.get('error', 'Registration failed')
                self.status_label.text = f"❌ {error_msg}"
                self.status_label.color = Theme.ERROR
                
                if "email" in error_msg.lower():
                    self.email_input.focus = True
        
        self.app.api.register_user(name, email, org, on_result)

# ==================== MAIN ====================

if __name__ == "__main__":
    MzindaTrackApp().run()
