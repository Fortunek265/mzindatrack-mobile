"""
MzindaTrack Mobile - GPS Tracking Application
Main entry point for Android and desktop
"""

import os
import sys
import json
import requests
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
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android import mActivity
    from jnius import autoclass
    from plyer import gps
    
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
                timeout=10
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
                timeout=15
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

class ConnectScreen(Screen):
    """Connection screen for MzindaTrack"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api = MzindaTrackAPI()
        self.verified = False
        self.current_token = None
        self.user_info = None
        
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        
        # Title
        title = Label(
            text='🎯 MzindaTrack',
            font_size='24sp',
            color=(0.39, 1.0, 0.85, 1.0),
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)
        
        subtitle = Label(
            text='GPS yathu, Chitetezo chathu',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0),
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(subtitle)
        
        # Server URL
        server_layout = BoxLayout(orientation='vertical', spacing=dp(8))
        server_label = Label(
            text='Server URL',
            size_hint_y=None,
            height=dp(25),
            halign='left',
            text_size=(Window.width - dp(32), None)
        )
        server_layout.add_widget(server_label)
        
        self.server_input = TextInput(
            text=DEFAULT_SERVER_URLS[0],
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=(0.1, 0.12, 0.15, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0)
        )
        server_layout.add_widget(self.server_input)
        layout.add_widget(server_layout)
        
        # Token
        token_layout = BoxLayout(orientation='vertical', spacing=dp(8))
        token_label = Label(
            text='Token or Access URL',
            size_hint_y=None,
            height=dp(25),
            halign='left',
            text_size=(Window.width - dp(32), None)
        )
        token_layout.add_widget(token_label)
        
        self.token_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=(0.1, 0.12, 0.15, 1.0),
            foreground_color=(0.88, 0.9, 0.93, 1.0),
            hint_text='Paste your token here'
        )
        token_layout.add_widget(self.token_input)
        layout.add_widget(token_layout)
        
        # Status
        self.status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30),
            color=(0.88, 0.9, 0.93, 1.0)
        )
        layout.add_widget(self.status_label)
        
        # Progress
        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(6)
        )
        self.progress.opacity = 0
        layout.add_widget(self.progress)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(48))
        
        self.verify_btn = Button(
            text='🔐 Verify Token',
            background_color=(0.4, 0.49, 0.92, 1.0),
            color=(1, 1, 1, 1)
        )
        self.verify_btn.bind(on_press=self.verify_token)
        btn_layout.add_widget(self.verify_btn)
        
        register_btn = Button(
            text='📝 Register',
            background_color=(0.2, 0.22, 0.28, 1.0),
            color=(1, 1, 1, 1)
        )
        register_btn.bind(on_press=self.open_registration)
        btn_layout.add_widget(register_btn)
        
        layout.add_widget(btn_layout)
        
        # Info
        info = Label(
            text='🔐 Secure GPS tracking with 2-meter precision',
            font_size='12sp',
            color=(0.42, 0.48, 0.56, 1.0),
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(info)
        
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
        
        self.api.set_base_url(server_url)
        self.verify_btn.disabled = True
        self.status_label.text = '⏳ Verifying token...'
        self.status_label.color = (0.39, 1.0, 0.85, 1.0)
        self.progress.opacity = 1
        self.progress.value = 20
        
        # Perform verification in background thread
        Clock.schedule_once(lambda dt: self.do_verify(token), 0.1)
    
    def do_verify(self, token):
        """Perform verification in background"""
        result = self.api.verify_token(token)
        Clock.schedule_once(lambda dt: self.verification_complete(result), 0.1)
    
    def verification_complete(self, result):
        """Handle verification completion"""
        self.progress.value = 100
        self.progress.opacity = 0
        self.verify_btn.disabled = False
        
        if result.get('valid'):
            self.verified = True
            self.current_token = result['token']
            self.user_info = result.get('user_info', {})
            
            self.status_label.text = '✅ Token verified successfully!'
            self.status_label.color = (0.3, 0.78, 0.31, 1.0)
            
            # Save token
            user_info = self.user_info
            self.parent.show_account_screen(user_info)
            self.parent.open_map(self.current_token, self.api.base_url)
        else:
            self.verified = False
            self.status_label.text = f'❌ {result.get("error", "Invalid token")}'
            self.status_label.color = (1, 0.27, 0.21, 1.0)
            
            # Show error popup
            popup = Popup(
                title='Verification Failed',
                content=Label(text=result.get('error', 'Invalid token')),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def open_registration(self, instance):
        """Open registration dialog"""
        popup_layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            hint_text='Full Name'
        )
        popup_layout.add_widget(name_input)
        
        email_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            hint_text='Email'
        )
        popup_layout.add_widget(email_input)
        
        org_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            hint_text='Organisation (optional)'
        )
        popup_layout.add_widget(org_input)
        
        status_label = Label(
            text='',
            size_hint_y=None,
            height=dp(30)
        )
        popup_layout.add_widget(status_label)
        
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(8), size_hint_y=None, height=dp(40))
        register_btn = Button(text='Register', background_color=(0.3, 0.78, 0.31, 1.0))
        cancel_btn = Button(text='Cancel', background_color=(0.2, 0.22, 0.28, 1.0))
        btn_layout.add_widget(register_btn)
        btn_layout.add_widget(cancel_btn)
        popup_layout.add_widget(btn_layout)
        
        popup = Popup(
            title='Register for MzindaTrack',
            content=popup_layout,
            size_hint=(0.9, 0.8)
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
            result = self.api.register_user(name, email, org)
            
            if result.get('success'):
                status_label.text = f'✅ {result["message"]}'
                status_label.color = (0.3, 0.78, 0.31, 1.0)
                
                if result.get('payment_url'):
                    payment_popup = Popup(
                        title='Registration Successful',
                        content=Label(text=f'Payment link sent to {email}\nClick OK to open payment page'),
                        size_hint=(0.8, 0.4)
                    )
                    payment_popup.open()
            else:
                status_label.text = f'❌ {result.get("error", "Registration failed")}'
                status_label.color = (1, 0.27, 0.21, 1.0)
            
            register_btn.disabled = False
        
        register_btn.bind(on_press=register)
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()

class MapScreen(Screen):
    """Map view screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        
        # Top bar
        top_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=dp(10))
        
        back_btn = Button(
            text='← Back',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.2, 0.22, 0.28, 1.0)
        )
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        
        title = Label(
            text='🗺️ MzindaTrack Map',
            color=(0.39, 1.0, 0.85, 1.0),
            size_hint_x=1
        )
        top_bar.add_widget(title)
        
        layout.add_widget(top_bar)
        
        # Map placeholder
        self.map_label = Label(
            text='Map View\n(WebView not available on mobile yet)',
            color=(0.88, 0.9, 0.93, 1.0),
            font_size='20sp'
        )
        layout.add_widget(self.map_label)
        
        self.add_widget(layout)
        self.map_token = None
        self.map_server = None
    
    def load_map(self, token, server_url):
        """Load the map (placeholder for now)"""
        self.map_token = token
        self.map_server = server_url
        self.map_label.text = f'🗺️ Map loaded\nToken: {token[:20]}...'
    
    def go_back(self, instance):
        """Go back to connect screen"""
        self.manager.current = 'connect'

class AccountScreen(Screen):
    """Account information screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
        
        self.name_label = Label(
            text='Not logged in',
            font_size='18sp',
            bold=True,
            color=(0.88, 0.9, 0.93, 1.0)
        )
        layout.add_widget(self.name_label)
        
        self.email_label = Label(
            text='',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0)
        )
        layout.add_widget(self.email_label)
        
        self.org_label = Label(
            text='',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0)
        )
        layout.add_widget(self.org_label)
        
        self.status_label = Label(
            text='Status: Disconnected',
            font_size='14sp',
            color=(0.53, 0.57, 0.69, 1.0)
        )
        layout.add_widget(self.status_label)
        
        # Disconnect button
        disconnect_btn = Button(
            text='🚪 Disconnect',
            background_color=(0.96, 0.26, 0.21, 1.0),
            size_hint_y=None,
            height=dp(48),
            pos_hint={'center_x': 0.5}
        )
        disconnect_btn.bind(on_press=self.disconnect)
        layout.add_widget(disconnect_btn)
        
        layout.add_widget(Label())  # Spacer
        
        self.add_widget(layout)
        self.user_info = None
    
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
        
        self.manager.current = 'connect'

class MzindaTrackApp(App):
    """Main application class"""
    
    def build(self):
        Window.size = (400, 700)
        Window.clearcolor = (0.04, 0.06, 0.12, 1.0)
        
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

def main():
    """Main entry point"""
    app = MzindaTrackApp()
    app.run()

if __name__ == '__main__':
    main()