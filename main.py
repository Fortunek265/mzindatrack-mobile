"""
MzindaTrack Mobile - GPS Tracking Application
Mobile version with Kivy UI
"""

import os
import sys
import json
import requests
import threading
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from plyer import gps
    from jnius import autoclass
    
    # Request permissions on Android
    request_permissions([
        Permission.INTERNET,
        Permission.ACCESS_FINE_LOCATION,
        Permission.ACCESS_COARSE_LOCATION,
        Permission.ACCESS_BACKGROUND_LOCATION,
        Permission.FOREGROUND_SERVICE,
        Permission.WAKE_LOCK,
        Permission.ACCESS_NETWORK_STATE,
        Permission.ACCESS_WIFI_STATE
    ])

# Default server URLs
DEFAULT_SERVER_URLS = [
    "https://culminate-retype-cresting.ngrok-free.dev",
    "https://unowing-earnest-gapless.ngrok-free.dev"
]

class MzindaTrackAPI:
    """API client for MzindaTrack server"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url.rstrip('/') if base_url else None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MzindaTrack-Mobile/1.0'
        })
    
    def set_base_url(self, url):
        self.base_url = url.rstrip('/') if url else None
    
    def verify_token(self, token):
        if not self.base_url:
            return {'valid': False, 'error': 'No server URL set'}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/user_info/{token}",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'valid': True,
                    'user_info': data,
                    'token': token
                }
            elif response.status_code == 403:
                return {
                    'valid': False,
                    'error': 'Token is invalid or expired'
                }
            else:
                return {
                    'valid': False,
                    'error': f'Server error: {response.status_code}'
                }
        except requests.exceptions.ConnectionError:
            return {'valid': False, 'error': 'Cannot connect to server'}
        except requests.exceptions.Timeout:
            return {'valid': False, 'error': 'Connection timeout'}
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def register_user(self, full_name, email, organisation=''):
        if not self.base_url:
            return {'success': False, 'error': 'No server URL set'}
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/register",
                json={
                    'full_name': full_name,
                    'email': email,
                    'organisation': organisation
                },
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': data.get('message', 'Registration successful'),
                    'payment_url': data.get('payment_url')
                }
            else:
                data = response.json() if response.text else {}
                return {
                    'success': False,
                    'error': data.get('error', f'Server error: {response.status_code}')
                }
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Cannot connect to server'}
        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Connection timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_health(self):
        if not self.base_url:
            return {'status': 'unknown'}
        
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return {'status': 'unhealthy'}
        except:
            return {'status': 'unreachable'}

class GradientButton(Button):
    """Custom button with gradient background"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.color = (1, 1, 1, 1)
        self.bind(size=self.update_canvas)
        self.bind(pos=self.update_canvas)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.4, 0.49, 0.92, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[10])

class ConnectScreen(Screen):
    """Connection screen for MzindaTrack"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = MzindaTrackAPI()
        self.verified = False
        self.current_token = None
        self.user_info = None
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header with icon and title
        header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        
        # App icon
        icon = Image(
            source='assets/gps.png' if os.path.exists('assets/gps.png') else '',
            size_hint=(None, None),
            size=(dp(64), dp(64)),
            pos_hint={'center_x': 0.5}
        )
        header.add_widget(icon)
        
        title = Label(
            text='MzindaTrack',
            font_size='28sp',
            bold=True,
            color=(0.39, 1.0, 0.85, 1.0),
            size_hint_y=None,
            height=dp(40)
        )
        header.add_widget(title)
        
        subtitle = Label(
            text='GPS yathu, Chitetezo chathu',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0),
            size_hint_y=None,
            height=dp(25)
        )
        header.add_widget(subtitle)
        
        layout.add_widget(header)
        
        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Server URL
        server_label = Label(
            text='Server URL',
            size_hint_y=None,
            height=dp(25),
            halign='left',
            text_size=(Window.width - dp(40), None),
            color=(0.88, 0.9, 0.93, 1.0)
        )
        content.add_widget(server_label)
        
        self.server_input = TextInput(
            text=DEFAULT_SERVER_URLS[0],
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.1, 0.12, 0.18, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0),
            cursor_color=(0.4, 0.49, 0.92, 1.0),
            padding=(dp(10), dp(10))
        )
        content.add_widget(self.server_input)
        
        # Token
        token_label = Label(
            text='Access Token',
            size_hint_y=None,
            height=dp(25),
            halign='left',
            text_size=(Window.width - dp(40), None),
            color=(0.88, 0.9, 0.93, 1.0)
        )
        content.add_widget(token_label)
        
        self.token_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_color=(0.1, 0.12, 0.18, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0),
            cursor_color=(0.4, 0.49, 0.92, 1.0),
            padding=(dp(10), dp(10)),
            hint_text='Paste your token here',
            hint_text_color=(0.42, 0.48, 0.56, 1.0)
        )
        content.add_widget(self.token_input)
        
        # Status
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(0.88, 0.9, 0.93, 1.0)
        )
        content.add_widget(self.status_label)
        
        # Progress
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(6)
        )
        self.progress.opacity = 0
        content.add_widget(self.progress)
        
        # Buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(120))
        
        self.verify_btn = Button(
            text='🔐 Verify Token',
            background_color=(0.4, 0.49, 0.92, 1.0),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(48),
            bold=True
        )
        self.verify_btn.bind(on_press=self.verify_token)
        btn_layout.add_widget(self.verify_btn)
        
        register_btn = Button(
            text='📝 Register New Account',
            background_color=(0.2, 0.22, 0.32, 1.0),
            color=(0.88, 0.9, 0.93, 1.0),
            size_hint_y=None,
            height=dp(48)
        )
        register_btn.bind(on_press=self.open_registration)
        btn_layout.add_widget(register_btn)
        
        content.add_widget(btn_layout)
        
        # Info
        info = Label(
            text='🔐 Secure GPS tracking with 2-meter precision',
            font_size='12sp',
            color=(0.42, 0.48, 0.56, 1.0),
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(info)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def verify_token(self, instance):
        """Verify the token"""
        token = self.token_input.text.strip()
        server_url = self.server_input.text.strip()
        
        if not token:
            self.status_label.text = '❌ Please enter your token'
            self.status_label.color = (1, 0.27, 0.21, 1.0)
            return
        
        if not server_url:
            self.status_label.text = '❌ Please enter server URL'
            self.status_label.color = (1, 0.27, 0.21, 1.0)
            return
        
        # Add http:// if missing
        if not server_url.startswith('http://') and not server_url.startswith('https://'):
            server_url = 'http://' + server_url
            self.server_input.text = server_url
        
        self.api.set_base_url(server_url)
        self.verify_btn.disabled = True
        self.status_label.text = '⏳ Verifying token...'
        self.status_label.color = (0.39, 1.0, 0.85, 1.0)
        self.progress.opacity = 1
        self.progress.value = 20
        
        # Perform verification in background thread
        def do_verify():
            result = self.api.verify_token(token)
            Clock.schedule_once(lambda dt: self.verification_complete(result), 0.1)
        
        threading.Thread(target=do_verify, daemon=True).start()
    
    def verification_complete(self, result):
        """Handle verification completion"""
        self.progress.value = 100
        Clock.schedule_once(lambda dt: setattr(self.progress, 'opacity', 0), 0.5)
        self.verify_btn.disabled = False
        
        if result.get('valid'):
            self.verified = True
            self.current_token = result['token']
            self.user_info = result.get('user_info', {})
            
            self.status_label.text = '✅ Token verified successfully!'
            self.status_label.color = (0.3, 0.78, 0.31, 1.0)
            
            # Show success popup
            user_info = self.user_info
            popup_content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            popup_content.add_widget(Label(
                text=f"Welcome {user_info.get('full_name', 'User')}!",
                font_size='18sp'
            ))
            popup_content.add_widget(Label(
                text=f"Email: {user_info.get('email', '')}",
                font_size='14sp'
            ))
            
            btn = Button(
                text='Continue to Map',
                size_hint_y=None,
                height=dp(48),
                background_color=(0.4, 0.49, 0.92, 1.0)
            )
            popup_content.add_widget(btn)
            
            popup = Popup(
                title='Access Granted',
                content=popup_content,
                size_hint=(0.8, 0.5)
            )
            
            def continue_to_map(instance):
                popup.dismiss()
                # Navigate to map
                self.parent.show_account_screen(user_info)
                self.parent.open_map(self.current_token, self.api.base_url)
            
            btn.bind(on_press=continue_to_map)
            popup.open()
            
        else:
            self.verified = False
            self.status_label.text = f'❌ {result.get("error", "Invalid token")}'
            self.status_label.color = (1, 0.27, 0.21, 1.0)
            
            # Show error popup
            popup = Popup(
                title='Verification Failed',
                content=Label(
                    text=result.get('error', 'Invalid token'),
                    text_size=(Window.width - dp(40), None),
                    halign='center'
                ),
                size_hint=(0.8, 0.3)
            )
            popup.open()
    
    def open_registration(self, instance):
        """Open registration dialog"""
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        
        # Name input
        name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Full Name',
            background_color=(0.1, 0.12, 0.18, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0),
            padding=(dp(10), dp(10))
        )
        popup_layout.add_widget(name_input)
        
        # Email input
        email_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Email Address',
            background_color=(0.1, 0.12, 0.18, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0),
            padding=(dp(10), dp(10))
        )
        popup_layout.add_widget(email_input)
        
        # Organisation input
        org_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            hint_text='Organisation (optional)',
            background_color=(0.1, 0.12, 0.18, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0),
            padding=(dp(10), dp(10))
        )
        popup_layout.add_widget(org_input)
        
        # Status label
        status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(0.88, 0.9, 0.93, 1.0)
        )
        popup_layout.add_widget(status_label)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        register_btn = Button(text='Register', background_color=(0.3, 0.78, 0.31, 1.0), color=(1,1,1,1))
        cancel_btn = Button(text='Cancel', background_color=(0.2, 0.22, 0.32, 1.0), color=(0.88,0.9,0.93,1))
        btn_layout.add_widget(register_btn)
        btn_layout.add_widget(cancel_btn)
        popup_layout.add_widget(btn_layout)
        
        popup = Popup(
            title='Register for MzindaTrack',
            content=popup_layout,
            size_hint=(0.9, 0.7)
        )
        
        def register(instance):
            name = name_input.text.strip()
            email = email_input.text.strip()
            org = org_input.text.strip()
            
            if not name or not email:
                status_label.text = '❌ Please fill all required fields'
                status_label.color = (1, 0.27, 0.21, 1.0)
                return
            
            register_btn.disabled = True
            status_label.text = '⏳ Registering...'
            status_label.color = (0.39, 1.0, 0.85, 1.0)
            
            server_url = self.server_input.text.strip()
            self.api.set_base_url(server_url)
            
            def do_register():
                result = self.api.register_user(name, email, org)
                Clock.schedule_once(lambda dt: register_complete(result), 0.1)
            
            def register_complete(result):
                if result.get('success'):
                    status_label.text = f'✅ {result["message"]}'
                    status_label.color = (0.3, 0.78, 0.31, 1.0)
                    
                    if result.get('payment_url'):
                        payment_msg = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
                        payment_msg.add_widget(Label(text=f'Payment link sent to {email}'))
                        payment_msg.add_widget(Label(text='Check your email for payment instructions', font_size='12sp'))
                        
                        btn = Button(text='OK', size_hint_y=None, height=dp(48))
                        payment_popup = Popup(
                            title='Registration Successful',
                            content=payment_msg,
                            size_hint=(0.8, 0.4)
                        )
                        btn.bind(on_press=payment_popup.dismiss)
                        payment_msg.add_widget(btn)
                        payment_popup.open()
                    
                    Clock.schedule_once(lambda dt: popup.dismiss(), 2)
                else:
                    status_label.text = f'❌ {result.get("error", "Registration failed")}'
                    status_label.color = (1, 0.27, 0.21, 1.0)
                
                register_btn.disabled = False
            
            threading.Thread(target=do_register, daemon=True).start()
        
        register_btn.bind(on_press=register)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

class MapScreen(Screen):
    """Map view screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Top bar
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(55), padding=dp(10))
        top_bar.canvas.before.clear()
        with top_bar.canvas.before:
            Color(0.06, 0.08, 0.15, 1)
            Rectangle(pos=top_bar.pos, size=top_bar.size)
        
        back_btn = Button(
            text='← Back',
            size_hint_x=None,
            width=dp(70),
            background_color=(0.2, 0.22, 0.32, 1.0),
            color=(0.88, 0.9, 0.93, 1.0)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='🗺️ Map View',
            color=(0.39, 1.0, 0.85, 1.0),
            font_size='18sp',
            bold=True,
            size_hint_x=1
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Map placeholder with GPS indicator
        map_content = BoxLayout(orientation='vertical')
        
        self.map_label = Label(
            text='📍 GPS Tracking\n\nWaiting for location...',
            color=(0.88, 0.9, 0.93, 1.0),
            font_size='20sp',
            halign='center'
        )
        map_content.add_widget(self.map_label)
        
        # GPS status
        self.gps_status = Label(
            text='GPS: Disabled',
            color=(0.53, 0.57, 0.69, 1.0),
            font_size='14sp',
            size_hint_y=None,
            height=dp(30)
        )
        map_content.add_widget(self.gps_status)
        
        layout.add_widget(map_content)
        
        self.add_widget(layout)
        self.map_token = None
        self.map_server = None
        self.is_tracking = False
    
    def load_map(self, token, server_url):
        """Load the map"""
        self.map_token = token
        self.map_server = server_url
        self.map_label.text = f'📍 GPS Tracking Active\n\nToken: {token[:20]}...\nServer: {server_url[:30]}...'
        self.start_gps()
    
    def start_gps(self):
        """Start GPS tracking on Android"""
        if platform == 'android':
            try:
                def on_location(**kwargs):
                    lat = kwargs.get('lat', '0')
                    lon = kwargs.get('lon', '0')
                    self.map_label.text = f'📍 GPS Tracking\n\nLatitude: {lat}\nLongitude: {lon}\nAccuracy: {kwargs.get("accuracy", "N/A")}m'
                    self.gps_status.text = 'GPS: Active ✅'
                    self.gps_status.color = (0.3, 0.78, 0.31, 1.0)
                
                def on_status(**kwargs):
                    status = kwargs.get('status', '')
                    if status == 'provider_enabled':
                        self.gps_status.text = 'GPS: Enabled'
                        self.gps_status.color = (0.39, 1.0, 0.85, 1.0)
                    elif status == 'provider_disabled':
                        self.gps_status.text = 'GPS: Disabled'
                        self.gps_status.color = (0.53, 0.57, 0.69, 1.0)
                
                gps.configure(on_location=on_location, on_status=on_status)
                gps.start(1000, 0)  # Update every second
                self.is_tracking = True
                self.gps_status.text = 'GPS: Starting...'
                self.gps_status.color = (0.39, 1.0, 0.85, 1.0)
            except Exception as e:
                self.gps_status.text = f'GPS Error: {str(e)[:30]}'
                self.gps_status.color = (1, 0.27, 0.21, 1.0)
        else:
            self.gps_status.text = 'GPS: Desktop (simulated)'
            self.gps_status.color = (0.53, 0.57, 0.69, 1.0)
            # Simulate GPS for testing
            self.simulate_gps()
    
    def simulate_gps(self):
        """Simulate GPS for desktop testing"""
        import random
        def update_location(dt):
            if not self.is_tracking:
                return
            lat = -13.9833 + random.uniform(-0.01, 0.01)
            lon = 33.7833 + random.uniform(-0.01, 0.01)
            self.map_label.text = f'📍 GPS Tracking (Simulated)\n\nLatitude: {lat:.6f}\nLongitude: {lon:.6f}'
        Clock.schedule_interval(update_location, 1)
    
    def stop_gps(self):
        """Stop GPS tracking"""
        if platform == 'android' and self.is_tracking:
            try:
                gps.stop()
                self.is_tracking = False
                self.gps_status.text = 'GPS: Stopped'
                self.gps_status.color = (0.53, 0.57, 0.69, 1.0)
            except:
                pass
    
    def go_back(self, instance):
        """Go back to connect screen"""
        self.stop_gps()
        self.manager.current = 'connect'

class AccountScreen(Screen):
    """Account information screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Header
        header = Label(
            text='👤 Account',
            font_size='24sp',
            bold=True,
            color=(0.39, 1.0, 0.85, 1.0),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(header)
        
        # Card background
        card = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(15))
        card.canvas.before.clear()
        with card.canvas.before:
            Color(0.08, 0.1, 0.18, 1)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[15])
        card.bind(pos=card.update_canvas, size=card.update_canvas)
        
        self.name_label = Label(
            text='Not logged in',
            font_size='18sp',
            bold=True,
            color=(0.88, 0.9, 0.93, 1.0),
            size_hint_y=None,
            height=dp(35)
        )
        card.add_widget(self.name_label)
        
        self.email_label = Label(
            text='',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0),
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(self.email_label)
        
        self.org_label = Label(
            text='',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0),
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(self.org_label)
        
        # Divider
        divider = Widget(size_hint_y=None, height=dp(1))
        with divider.canvas:
            Color(0.2, 0.22, 0.32, 1)
            Rectangle(pos=divider.pos, size=divider.size)
        divider.bind(pos=divider.update_canvas, size=divider.update_canvas)
        card.add_widget(divider)
        
        self.status_label = Label(
            text='Status: Disconnected',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0),
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(self.status_label)
        
        layout.add_widget(card)
        
        # Disconnect button
        disconnect_btn = Button(
            text='🚪 Disconnect',
            background_color=(0.96, 0.26, 0.21, 1.0),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(48),
            bold=True,
            pos_hint={'center_x': 0.5}
        )
        disconnect_btn.bind(on_press=self.disconnect)
        layout.add_widget(disconnect_btn)
        
        # Version info
        version = Label(
            text='MzindaTrack v1.0.0',
            font_size='12sp',
            color=(0.42, 0.48, 0.56, 1.0),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(version)
        
        layout.add_widget(Widget())  # Spacer
        
        self.add_widget(layout)
        self.user_info = None
    
    def update_canvas(self, instance, *args):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.08, 0.1, 0.18, 1)
            RoundedRectangle(pos=instance.pos, size=instance.size, radius=[15])
    
    def set_user_info(self, user_info):
        """Set user information"""
        self.user_info = user_info
        self.name_label.text = f'👤 {user_info.get("full_name", "User")}'
        self.email_label.text = f'📧 {user_info.get("email", "")}'
        if user_info.get('organisation'):
            self.org_label.text = f'🏢 {user_info["organisation"]}'
        self.status_label.text = '✅ Account Active'
        self.status_label.color = (0.3, 0.78, 0.31, 1.0)
    
    def disconnect(self, instance):
        """Disconnect from the app"""
        self.user_info = None
        self.name_label.text = 'Not logged in'
        self.email_label.text = ''
        self.org_label.text = ''
        self.status_label.text = 'Status: Disconnected'
        self.status_label.color = (0.53, 0.57, 0.69, 1.0)
        
        # Stop GPS if running
        if hasattr(self.manager, 'get_screen'):
            map_screen = self.manager.get_screen('map')
            if map_screen:
                map_screen.stop_gps()
        
        self.manager.current = 'connect'

class MzindaTrackApp(App):
    """Main application class"""
    
    def build(self):
        # Set window size for desktop
        Window.size = (400, 700)
        Window.clearcolor = (0.04, 0.06, 0.12, 1.0)
        
        # Set app title
        self.title = 'MzindaTrack'
        
        # Create screen manager
        self.sm = ScreenManager()
        
        # Add screens
        self.connect_screen = ConnectScreen(name='connect')
        self.sm.add_widget(self.connect_screen)
        
        self.map_screen = MapScreen(name='map')
        self.sm.add_widget(self.map_screen)
        
        self.account_screen = AccountScreen(name='account')
        self.sm.add_widget(self.account_screen)
        
        return self.sm
    
    def show_account_screen(self, user_info):
        """Show account screen with user info"""
        self.account_screen.set_user_info(user_info)
        self.sm.current = 'account'
    
    def open_map(self, token, server_url):
        """Open the map screen"""
        self.map_screen.load_map(token, server_url)
        self.sm.current = 'map'
    
    def on_stop(self):
        """Stop GPS when app closes"""
        if hasattr(self, 'map_screen'):
            self.map_screen.stop_gps()

def main():
    """Main entry point"""
    app = MzindaTrackApp()
    app.run()

if __name__ == '__main__':
    main()
