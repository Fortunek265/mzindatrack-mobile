#!/usr/bin/env python3
"""
MzindaTrack Desktop Client - Hamburger Menu Navigation with Compact Toolbar
Tabs integrated into hamburger menu with status indicator
With continuous auto-connect functionality and Full Screen toggle
"""

import sys
import os
import re
import json
import requests
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QDesktopServices, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QStackedWidget,
    QMessageBox, QProgressBar, QTextEdit, QTabWidget, QGroupBox,
    QGridLayout, QScrollArea, QSizePolicy, QSplitter, QToolBar,
    QAction, QStatusBar, QCheckBox, QComboBox, QRadioButton,
    QButtonGroup, QDialog, QDialogButtonBox, QFormLayout,
    QSpacerItem, QMenu, QSystemTrayIcon, QStyle, QDesktopWidget,
    QToolButton, QShortcut
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings

# ==================== APPLICATION ICON ====================
def get_app_icon():
    """Load application icon from gps.icon file"""
    icon_paths = [
        "gps.icon",  # Current directory
        os.path.join(os.path.dirname(__file__), "gps.icon"),  # Script directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "gps.icon"),  # Absolute path
        os.path.join(os.getcwd(), "gps.icon"),  # Working directory
        os.path.join(os.path.dirname(sys.executable), "gps.icon") if hasattr(sys, 'frozen') else None,  # Bundled app
    ]
    
    # Also try common icon formats
    icon_extensions = [".icon", ".ico", ".png", ".svg", ".jpg", ".jpeg", ".bmp"]
    
    for base_path in icon_paths:
        if base_path is None:
            continue
            
        # Try exact filename
        if os.path.exists(base_path):
            try:
                icon = QIcon(base_path)
                if not icon.isNull():
                    return icon
            except:
                pass
        
        # Try with different extensions
        for ext in icon_extensions:
            test_path = base_path.rsplit('.', 1)[0] + ext if '.' in base_path else base_path + ext
            if os.path.exists(test_path):
                try:
                    icon = QIcon(test_path)
                    if not icon.isNull():
                        return icon
                except:
                    pass
    
    # Try to find any icon file in the application directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(app_dir):
        if file.lower().startswith('gps') and any(file.lower().endswith(ext) for ext in ['.icon', '.ico', '.png', '.svg']):
            try:
                icon = QIcon(os.path.join(app_dir, file))
                if not icon.isNull():
                    return icon
            except:
                pass
    
    # Return a default icon if no icon file found
    return QIcon()

def create_default_icon():
    """Create a default GPS icon programmatically if no icon file exists"""
    # This creates a simple GPS-style icon as a fallback
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    
    from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw a circular background
    painter.setBrush(QBrush(QColor(102, 126, 234)))  # #667eea
    painter.setPen(QPen(Qt.NoPen))
    painter.drawEllipse(4, 4, 56, 56)
    
    # Draw a GPS pin shape
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.setPen(QPen(Qt.NoPen))
    
    # Draw circle for pin head
    painter.drawEllipse(20, 20, 24, 24)
    
    # Draw crosshair
    painter.setPen(QPen(QColor(102, 126, 234), 3))
    painter.drawLine(32, 10, 32, 18)
    painter.drawLine(32, 30, 32, 38)
    painter.drawLine(10, 32, 18, 32)
    painter.drawLine(30, 32, 38, 32)
    
    # Draw outer ring
    painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(14, 14, 36, 36)
    
    painter.end()
    
    return QIcon(pixmap)

# ==================== DEFAULT SERVER URLS ====================
DEFAULT_SERVER_URLS = [
    "https://culminate-retype-cresting.ngrok-free.dev",
    "https://unowing-earnest-gapless.ngrok-free.dev"
]

# ==================== RESPONSIVE STYLESHEET ====================
def get_responsive_style(screen_size):
    """Generate responsive styles based on screen size with optimal proportions"""
    
    if screen_size == 'small':  # Phones
        font_size = '13px'
        padding = '6px 10px'
        border_radius = '8px'
        button_height = '36px'
        input_height = '38px'
        header_height = '40px'
        spacing = '6px'
        icon_size = '18px'
        margin = '8px'
    elif screen_size == 'medium':  # Tablets
        font_size = '14px'
        padding = '8px 14px'
        border_radius = '10px'
        button_height = '40px'
        input_height = '42px'
        header_height = '48px'
        spacing = '8px'
        icon_size = '20px'
        margin = '12px'
    else:  # Desktop
        font_size = '13px'
        padding = '8px 16px'
        border_radius = '10px'
        button_height = '38px'
        input_height = '40px'
        header_height = '50px'
        spacing = '10px'
        icon_size = '22px'
        margin = '16px'
    
    return f"""
    QMainWindow {{
        background-color: #0a0f1e;
    }}
    
    QWidget {{
        background-color: #0a0f1e;
        color: #e0e6ed;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: {font_size};
    }}
    
    QLabel {{
        color: #e0e6ed;
    }}
    
    QLineEdit {{
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: {border_radius};
        padding: {padding};
        color: #e0e6ed;
        font-size: {font_size};
        selection-background-color: #667eea;
        min-height: {input_height};
        max-height: {input_height};
    }}
    
    QLineEdit:focus {{
        border-color: #667eea;
        background-color: rgba(255, 255, 255, 0.12);
    }}
    
    QLineEdit::placeholder {{
        color: #6b7a8f;
    }}
    
    QPushButton {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #667eea, stop: 1 #764ba2);
        border: none;
        border-radius: {border_radius};
        padding: {padding};
        color: white;
        font-size: {font_size};
        font-weight: 600;
        min-height: {button_height};
        max-height: {button_height};
    }}
    
    QPushButton:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #7b93f5, stop: 1 #8b5fbf);
    }}
    
    QPushButton:pressed {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #5a6fd6, stop: 1 #6a3f8f);
    }}
    
    QPushButton:disabled {{
        opacity: 0.5;
    }}
    
    QPushButton#dangerBtn {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #f44336, stop: 1 #e53935);
    }}
    
    QPushButton#dangerBtn:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #ff6659, stop: 1 #ff4d4d);
    }}
    
    QPushButton#successBtn {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #4CAF50, stop: 1 #45a049);
    }}
    
    QPushButton#successBtn:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #66bb6a, stop: 1 #4caf50);
    }}
    
    QPushButton#warningBtn {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #FF9800, stop: 1 #F57C00);
    }}
    
    QPushButton#warningBtn:hover {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #ffb74d, stop: 1 #ff9800);
    }}
    
    QPushButton#secondaryBtn {{
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    QPushButton#secondaryBtn:hover {{
        background: rgba(255, 255, 255, 0.2);
    }}
    
    QPushButton#iconBtn {{
        background: transparent;
        border: none;
        border-radius: {border_radius};
        padding: 2px;
        min-height: 24px;
        max-height: 24px;
        min-width: 24px;
        max-width: 24px;
        font-size: 12px;
    }}
    
    QPushButton#iconBtn:hover {{
        background: rgba(255, 255, 255, 0.1);
    }}
    
    QPushButton#pasteBtn {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: {border_radius};
        padding: 4px 8px;
        font-size: 14px;
        min-height: {input_height};
        max-height: {input_height};
        min-width: 40px;
        max-width: 40px;
    }}
    
    QPushButton#pasteBtn:hover {{
        background: rgba(255, 255, 255, 0.15);
        border-color: #667eea;
    }}
    
    QToolButton {{
        background: transparent;
        border: none;
        border-radius: {border_radius};
        padding: {padding};
        color: #e0e6ed;
        font-size: {font_size};
        min-height: {button_height};
        max-height: {button_height};
    }}
    
    QToolButton:hover {{
        background: rgba(255, 255, 255, 0.1);
    }}
    
    QToolButton::menu-indicator {{
        image: none;
    }}
    
    /* HAMBURGER BUTTON STYLES - FIXED */
    QToolButton#hamburgerBtn {{
        color: #e0e6ed;
        background: transparent;
        border: none;
        padding: 2px;
        font-family: 'Segoe UI', 'Arial Unicode MS', 'DejaVu Sans', sans-serif;
        font-size: 20px;
        font-weight: bold;
    }}
    
    QToolButton#hamburgerBtn:hover {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }}
    
    QToolButton#hamburgerBtn:pressed {{
        background: rgba(255, 255, 255, 0.15);
    }}
    
    QFrame {{
        background-color: transparent;
    }}
    
    QFrame#cardFrame {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: {int(border_radius.replace('px',''))*2}px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: {margin};
    }}
    
    QFrame#headerFrame {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 rgba(102, 126, 234, 0.2),
                                   stop: 1 rgba(118, 75, 162, 0.2));
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        min-height: {header_height};
        max-height: {header_height};
    }}
    
    QFrame#webToolbar {{
        background: rgba(255, 255, 255, 0.03);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        min-height: 32px;
        max-height: 36px;
    }}
    
    QProgressBar {{
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 6px;
        height: 6px;
        text-align: center;
        min-height: 6px;
        max-height: 6px;
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #667eea, stop: 1 #764ba2);
        border-radius: 6px;
    }}
    
    QStackedWidget {{
        background: transparent;
    }}
    
    QStatusBar {{
        background-color: rgba(0, 0, 0, 0.3);
        color: #8892b0;
        min-height: 24px;
        max-height: 24px;
    }}
    
    QStatusBar QLabel {{
        color: #8892b0;
    }}
    
    QCheckBox {{
        color: #e0e6ed;
        spacing: {spacing};
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.05);
    }}
    
    QCheckBox::indicator:checked {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #667eea, stop: 1 #764ba2);
        border-color: #667eea;
    }}
    
    QScrollBar:vertical {{
        background: rgba(255, 255, 255, 0.05);
        border-radius: 4px;
        width: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background: rgba(255, 255, 255, 0.2);
        border-radius: 4px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: rgba(255, 255, 255, 0.3);
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}
    
    QMessageBox {{
        background-color: #0a0f1e;
    }}
    
    QMessageBox QLabel {{
        color: #e0e6ed;
    }}
    
    QMessageBox QPushButton {{
        min-width: 70px;
        min-height: {button_height};
        max-height: {button_height};
    }}
    
    QComboBox {{
        background-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: {border_radius};
        padding: {padding};
        color: #e0e6ed;
        min-height: {input_height};
        max-height: {input_height};
    }}
    
    QComboBox::drop-down {{
        border: none;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #8892b0;
        margin-right: 6px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: #1a1f2e;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: {border_radius};
        selection-background-color: #667eea;
    }}
    
    QGroupBox {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: {border_radius};
        margin-top: 8px;
        padding-top: 6px;
    }}
    
    QGroupBox::title {{
        color: #64ffda;
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
    }}
    
    QRadioButton {{
        color: #e0e6ed;
        spacing: {spacing};
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        background: rgba(255, 255, 255, 0.05);
    }}
    
    QRadioButton::indicator:checked {{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                   stop: 0 #667eea, stop: 1 #764ba2);
        border-color: #667eea;
    }}
    
    QMenu {{
        background-color: #1a1f2e;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 3px;
        min-width: 180px;
    }}
    
    QMenu::item {{
        padding: 6px 20px 6px 14px;
        border-radius: 6px;
        min-height: 28px;
    }}
    
    QMenu::item:selected {{
        background: rgba(102, 126, 234, 0.3);
    }}
    
    QMenu::separator {{
        height: 1px;
        background: rgba(255, 255, 255, 0.1);
        margin: 2px 6px;
    }}
    """

# ==================== RESPONSIVE LAYOUT MANAGER ====================
class ResponsiveLayoutManager:
    """Manages responsive behavior across the application"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_size = 'desktop'
        self.screen_width = 0
        self.screen_height = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_screen_size)
        self.timer.start(500)
    
    def check_screen_size(self):
        desktop = QApplication.desktop()
        if not desktop:
            return
            
        screen = desktop.screenGeometry()
        width = screen.width()
        height = screen.height()
        
        if width != self.screen_width or height != self.screen_height:
            self.screen_width = width
            self.screen_height = height
            self.update_layout()
    
    def update_layout(self):
        if self.screen_width <= 480:
            size_category = 'small'
        elif self.screen_width <= 1024:
            size_category = 'medium'
        else:
            size_category = 'desktop'
        
        if size_category != self.current_size:
            self.current_size = size_category
            self.apply_responsive_styles()
            if hasattr(self.parent, 'adjust_for_screen_size'):
                self.parent.adjust_for_screen_size(size_category)
    
    def apply_responsive_styles(self):
        style = get_responsive_style(self.current_size)
        self.parent.setStyleSheet(style)

# ==================== COMPACT WEB VIEW ====================
class TouchFriendlyWebView(QWidget):
    """Web view with compact toolbar"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Compact toolbar
        self.toolbar = QFrame()
        self.toolbar.setObjectName("webToolbar")
        toolbar_layout = QHBoxLayout(self.toolbar)
        toolbar_layout.setContentsMargins(4, 2, 4, 2)
        toolbar_layout.setSpacing(2)
        
        # Small navigation buttons
        self.back_btn = QPushButton("◀")
        self.back_btn.setObjectName("iconBtn")
        self.back_btn.setFixedSize(24, 24)
        self.back_btn.clicked.connect(self.go_back)
        
        self.forward_btn = QPushButton("▶")
        self.forward_btn.setObjectName("iconBtn")
        self.forward_btn.setFixedSize(24, 24)
        self.forward_btn.clicked.connect(self.go_forward)
        
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setObjectName("iconBtn")
        self.refresh_btn.setFixedSize(24, 24)
        self.refresh_btn.clicked.connect(self.refresh)
        
        # Compact URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL")
        self.url_bar.setMinimumHeight(22)
        self.url_bar.setMaximumHeight(26)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 11px;
                color: #e0e6ed;
                min-height: 22px;
                max-height: 26px;
            }
            QLineEdit:focus {
                border-color: #667eea;
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Small home and open buttons
        self.home_btn = QPushButton("🏠")
        self.home_btn.setObjectName("iconBtn")
        self.home_btn.setFixedSize(24, 24)
        self.home_btn.clicked.connect(self.go_home)
        
        self.open_btn = QPushButton("↗")
        self.open_btn.setObjectName("iconBtn")
        self.open_btn.setFixedSize(24, 24)
        self.open_btn.clicked.connect(self.open_in_browser)
        
        # Full screen toggle button (in web toolbar)
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setObjectName("iconBtn")
        self.fullscreen_btn.setFixedSize(24, 24)
        self.fullscreen_btn.setToolTip("Toggle Full Screen (F11)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        # Add widgets
        toolbar_layout.addWidget(self.back_btn)
        toolbar_layout.addWidget(self.forward_btn)
        toolbar_layout.addWidget(self.refresh_btn)
        toolbar_layout.addWidget(self.url_bar, 1)
        toolbar_layout.addWidget(self.home_btn)
        toolbar_layout.addWidget(self.open_btn)
        toolbar_layout.addWidget(self.fullscreen_btn)
        
        self.layout.addWidget(self.toolbar)
        
        # Web view
        self.web_view = QWebEngineView()
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.urlChanged.connect(self.on_url_changed)
        self.web_view.titleChanged.connect(self.on_title_changed)
        
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)
        profile.setPersistentStoragePath(os.path.join(os.getcwd(), "web_cache"))
        
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        
        self.layout.addWidget(self.web_view)
        
        self.current_url = None
        self.home_url = None
        self.is_fullscreen = False
    
    def set_compact_mode(self, compact=True):
        """Toggle compact mode for small screens"""
        if compact:
            self.home_btn.setVisible(False)
            self.open_btn.setVisible(False)
            self.forward_btn.setVisible(False)
            self.back_btn.setVisible(True)
            self.refresh_btn.setVisible(True)
            self.fullscreen_btn.setVisible(True)
            self.toolbar.setMinimumHeight(24)
            self.toolbar.setMaximumHeight(28)
            self.url_bar.setMinimumHeight(18)
            self.url_bar.setMaximumHeight(22)
            self.url_bar.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                    padding: 1px 6px;
                    font-size: 10px;
                    color: #e0e6ed;
                    min-height: 18px;
                    max-height: 22px;
                }
                QLineEdit:focus {
                    border-color: #667eea;
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
        else:
            self.home_btn.setVisible(True)
            self.open_btn.setVisible(True)
            self.forward_btn.setVisible(True)
            self.back_btn.setVisible(True)
            self.refresh_btn.setVisible(True)
            self.fullscreen_btn.setVisible(True)
            self.toolbar.setMinimumHeight(28)
            self.toolbar.setMaximumHeight(32)
            self.url_bar.setMinimumHeight(22)
            self.url_bar.setMaximumHeight(26)
            self.url_bar.setStyleSheet("""
                QLineEdit {
                    background-color: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 6px;
                    padding: 2px 8px;
                    font-size: 11px;
                    color: #e0e6ed;
                    min-height: 22px;
                    max-height: 26px;
                }
                QLineEdit:focus {
                    border-color: #667eea;
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
    
    def toggle_fullscreen(self):
        """Toggle full screen mode for the web view only"""
        if self.parent_app:
            self.parent_app.toggle_web_fullscreen()
    
    def load_url(self, url):
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
        self.current_url = url
        self.web_view.load(QUrl(url))
    
    def set_home_url(self, url):
        self.home_url = url
    
    def go_home(self):
        if self.home_url:
            self.load_url(self.home_url)
    
    def go_back(self):
        self.web_view.back()
    
    def go_forward(self):
        self.web_view.forward()
    
    def refresh(self):
        self.web_view.reload()
    
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if url:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            self.load_url(url)
    
    def open_in_browser(self):
        if self.current_url:
            QDesktopServices.openUrl(QUrl(self.current_url))
    
    def on_load_finished(self, ok):
        if ok:
            self.url_bar.setText(self.web_view.url().toString())
    
    def on_url_changed(self, url):
        self.current_url = url.toString()
        self.url_bar.setText(self.current_url)
    
    def on_title_changed(self, title):
        if title and not title.startswith("http"):
            if not self.is_fullscreen:
                self.parent().setWindowTitle(f"MzindaTrack - {title[:50]}")

# ==================== API CLIENT ====================
class MzindaTrackAPI:
    """API client for MzindaTrack server"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url.rstrip('/') if base_url else None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MzindaTrack-Desktop/1.0'
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

# ==================== TOKEN VERIFICATION WORKER ====================
class VerifyWorker(QThread):
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    
    def __init__(self, api, token):
        super().__init__()
        self.api = api
        self.token = token
    
    def run(self):
        self.status.emit("Verifying MzindaTrack token...")
        self.progress.emit(20)
        
        token = self.token.strip()
        
        if token.startswith('http://') or token.startswith('https://'):
            parsed = urlparse(token)
            path_parts = parsed.path.split('/')
            
            for part in path_parts:
                if len(part) > 20 and re.match(r'^[A-Za-z0-9_-]+$', part):
                    token = part
                    self.api.set_base_url(f"{parsed.scheme}://{parsed.netloc}")
                    break
            else:
                params = parse_qs(parsed.query)
                if 'token' in params:
                    token = params['token'][0]
                elif 't' in params:
                    token = params['t'][0]
        
        self.progress.emit(50)
        self.status.emit("Checking with MzindaTrack server...")
        
        result = self.api.verify_token(token)
        
        self.progress.emit(90)
        self.status.emit("Verification complete")
        
        result['token'] = token
        
        self.progress.emit(100)
        self.finished.emit(result)

# ==================== REGISTRATION DIALOG ====================
class ResponsiveRegistrationDialog(QDialog):
    def __init__(self, api, parent=None):
        super().__init__(parent)
        self.api = api
        self.setWindowTitle("Register for MzindaTrack")
        self.setModal(True)
        
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            width = min(400, screen_geometry.width() - 40)
            height = min(460, screen_geometry.height() - 40)
            self.setFixedSize(width, height)
        else:
            self.setFixedSize(400, 460)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("🎯 Register for MzindaTrack")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #64ffda;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setWordWrap(True)
        layout.addWidget(header)
        
        subtitle = QLabel("GPS yathu, Chitetezo chathu")
        subtitle.setStyleSheet("color: #8892b0; font-size: 13px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(8)
        
        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setMinimumHeight(36)
        self.name_input.setMaximumHeight(40)
        form.addRow("Full Name:", self.name_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your@email.com")
        self.email_input.setMinimumHeight(36)
        self.email_input.setMaximumHeight(40)
        form.addRow("Email:", self.email_input)
        
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("Optional")
        self.org_input.setMinimumHeight(36)
        self.org_input.setMaximumHeight(40)
        form.addRow("Organisation:", self.org_input)
        
        layout.addLayout(form)
        
        info = QLabel(
            "📌 You will receive a payment link via email.\n"
            "After payment verification, your access will be activated."
        )
        info.setStyleSheet("color: #8892b0; font-size: 11px; padding: 8px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.register_btn = QPushButton("✅ Register")
        self.register_btn.setObjectName("successBtn")
        self.register_btn.setMinimumHeight(36)
        self.register_btn.setMaximumHeight(40)
        self.register_btn.clicked.connect(self.register)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondaryBtn")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setMaximumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.register_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #8892b0; font-size: 11px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
    
    def register(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        org = self.org_input.text().strip()
        
        if not name:
            self.status_label.setText("❌ Please enter your full name")
            self.status_label.setStyleSheet("color: #f44336;")
            return
        
        if not email or '@' not in email:
            self.status_label.setText("❌ Please enter a valid email address")
            self.status_label.setStyleSheet("color: #f44336;")
            return
        
        self.register_btn.setEnabled(False)
        self.register_btn.setText("Registering...")
        self.status_label.setText("⏳ Contacting MzindaTrack server...")
        self.status_label.setStyleSheet("color: #64ffda;")
        
        result = self.api.register_user(name, email, org)
        
        if result.get('success'):
            self.status_label.setText(f"✅ {result['message']}")
            self.status_label.setStyleSheet("color: #4CAF50;")
            
            if result.get('payment_url'):
                msg = QMessageBox(self)
                msg.setWindowTitle("Registration Successful")
                msg.setText(
                    f"✅ Registration successful!\n\n"
                    f"A payment link has been sent to {email}\n\n"
                    f"Or click the button below to open the payment page."
                )
                msg.setStyleSheet(self.styleSheet())
                
                open_btn = msg.addButton("Open Payment Page", QMessageBox.ButtonRole.AcceptRole)
                close_btn = msg.addButton("Close", QMessageBox.ButtonRole.RejectRole)
                
                msg.exec()
                
                if msg.clickedButton() == open_btn:
                    QDesktopServices.openUrl(QUrl(result['payment_url']))
            
            self.accept()
        else:
            self.status_label.setText(f"❌ {result.get('error', 'Registration failed')}")
            self.status_label.setStyleSheet("color: #f44336;")
            self.register_btn.setEnabled(True)
            self.register_btn.setText("✅ Register")

# ==================== AUTO-CONNECT MANAGER ====================
class AutoConnectManager:
    """Manages continuous auto-connect attempts when app opens"""
    
    def __init__(self, parent):
        self.parent = parent
        self.is_connecting = False
        self.attempt_count = 0
        self.max_attempts = 10
        self.retry_delay = 3000  # 3 seconds between attempts
        self.auto_connect_timer = QTimer()
        self.auto_connect_timer.timeout.connect(self.attempt_auto_connect)
        self.auto_connect_timer.setSingleShot(False)
        
    def start_auto_connect(self, delay=1000):
        """Start automatic connection attempts"""
        if self.is_connecting:
            return
        
        self.is_connecting = True
        self.attempt_count = 0
        self.parent.status_bar.showMessage("🔄 Auto-connecting to MzindaTrack...")
        
        # Start with initial delay
        QTimer.singleShot(delay, self.attempt_auto_connect)
        
    def stop_auto_connect(self):
        """Stop automatic connection attempts"""
        self.is_connecting = False
        self.auto_connect_timer.stop()
        self.parent.status_bar.showMessage("Auto-connect stopped")
        self.parent.auto_status_label.setVisible(False)
        self.parent.auto_indicator.setVisible(False)
        
    def attempt_auto_connect(self):
        """Attempt to connect with stored credentials"""
        if not self.is_connecting:
            return
            
        self.attempt_count += 1
        
        # Check if already connected
        if self.parent.verified:
            self.is_connecting = False
            self.auto_connect_timer.stop()
            self.parent.status_bar.showMessage("✅ Already connected to MzindaTrack")
            self.parent.auto_status_label.setText("✅ Connected")
            self.parent.auto_status_label.setStyleSheet("font-size: 9px; color: #4CAF50;")
            return
            
        # Get stored settings
        settings = self.parent.load_settings_data()
        
        if not settings or not settings.get('server_url') or not settings.get('auto_connect_enabled', True):
            self.is_connecting = False
            self.auto_connect_timer.stop()
            self.parent.status_bar.showMessage("No saved credentials for auto-connect")
            self.parent.auto_status_label.setVisible(False)
            return
            
        # Check if we've exceeded max attempts
        if self.attempt_count > self.max_attempts:
            self.is_connecting = False
            self.auto_connect_timer.stop()
            self.parent.status_bar.showMessage("⚠️ Auto-connect failed after multiple attempts")
            self.parent.verify_status.setText("⚠️ Auto-connect failed. Please try manually.")
            self.parent.verify_status.setStyleSheet("color: #FF9800;")
            self.parent.auto_status_label.setText("⚠️ Failed")
            self.parent.auto_status_label.setStyleSheet("font-size: 9px; color: #f44336;")
            return
            
        # Get token and server URL
        server_url = settings.get('server_url', '')
        token = settings.get('token', '')
        
        if not server_url or not token:
            self.is_connecting = False
            self.auto_connect_timer.stop()
            self.parent.status_bar.showMessage("No saved credentials for auto-connect")
            self.parent.auto_status_label.setVisible(False)
            return
            
        # Set server URL
        self.parent.server_input.setText(server_url)
        self.parent.api.set_base_url(server_url)
        
        # Update status
        self.parent.status_bar.showMessage(f"🔄 Auto-connect attempt {self.attempt_count}/{self.max_attempts}...")
        self.parent.verify_status.setText(f"⏳ Auto-connecting (attempt {self.attempt_count}/{self.max_attempts})...")
        self.parent.verify_status.setStyleSheet("color: #64ffda;")
        self.parent.auto_status_label.setText(f"🔄 {self.attempt_count}/{self.max_attempts}")
        self.parent.auto_status_label.setStyleSheet("font-size: 9px; color: #64ffda;")
        self.parent.auto_status_label.setVisible(True)
        
        # Start verification
        self.parent.token_input.setText(token)
        self.parent.do_verify_token()
        
        # Schedule next attempt if not connected (will be stopped by on_verification_complete)
        if not self.parent.verified and self.is_connecting:
            self.auto_connect_timer.start(self.retry_delay)
        else:
            self.auto_connect_timer.stop()
    
    def on_verification_complete(self, success):
        """Called when verification completes"""
        if success:
            self.is_connecting = False
            self.auto_connect_timer.stop()
            self.parent.status_bar.showMessage("✅ Auto-connected to MzindaTrack")
            self.parent.auto_status_label.setText("✅ Connected")
            self.parent.auto_status_label.setStyleSheet("font-size: 9px; color: #4CAF50;")
            self.parent.auto_status_label.setVisible(True)
            self.parent.auto_indicator.setVisible(False)
        elif self.is_connecting and self.attempt_count < self.max_attempts:
            # Continue retrying - timer is already running
            self.parent.status_bar.showMessage(f"🔄 Retry {self.attempt_count}/{self.max_attempts}...")
            self.parent.auto_status_label.setText(f"🔄 {self.attempt_count}/{self.max_attempts}")
            self.parent.auto_status_label.setStyleSheet("font-size: 9px; color: #64ffda;")
        else:
            self.is_connecting = False
            self.auto_connect_timer.stop()
            self.parent.status_bar.showMessage("⚠️ Auto-connect failed")
            self.parent.auto_status_label.setText("⚠️ Failed")
            self.parent.auto_status_label.setStyleSheet("font-size: 9px; color: #f44336;")
            self.parent.auto_status_label.setVisible(True)

# ==================== MAIN APPLICATION ====================
class MzindaTrackApp(QMainWindow):
    """Main MzindaTrack Desktop Application with Hamburger Menu"""
    
    def __init__(self):
        super().__init__()
        
        # Application state
        self.api = MzindaTrackAPI()
        self.current_token = None
        self.user_info = None
        self.verified = False
        self.base_url = None
        self.recent_tokens = []
        self.current_size = 'desktop'
        self.current_page = 0  # 0=Connect, 1=View, 2=Account
        self.auto_connect_enabled = True
        self.settings_data = {}
        self.is_web_fullscreen = False
        self.header_visible = True
        self.statusbar_visible = True
        
        # Setup responsive layout manager
        self.responsive_manager = ResponsiveLayoutManager(self)
        
        # Setup auto-connect manager
        self.auto_connect_manager = AutoConnectManager(self)
        
        # Set application icon
        self.setup_app_icon()
        
        self.setup_ui()
        self.setup_shortcuts()
        self.apply_style()
        
        # Load saved settings
        self.load_settings()
        
        # Start auto-connect after UI is fully loaded
        QTimer.singleShot(1500, self.start_auto_connect)
    
    def setup_app_icon(self):
        """Setup application icon"""
        # Try to load from gps.icon file
        icon = get_app_icon()
        
        # If no icon found, create a default one
        if icon.isNull():
            icon = create_default_icon()
        
        # Set the application icon
        if not icon.isNull():
            self.setWindowIcon(icon)
            # Also set for the application
            QApplication.setWindowIcon(icon)
            
            # Log that icon was loaded
            print("✅ Application icon loaded successfully")
        else:
            print("⚠️ Could not load application icon")
    
    def setup_ui(self):
        self.setWindowTitle("MzindaTrack - GPS yathu, Chitetezo chathu")
        self.setMinimumSize(320, 480)
        self.center_window()
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Header with hamburger menu - REDUCED HEIGHT
        self.header = QFrame()
        self.header.setObjectName("headerFrame")
        self.header.setMinimumHeight(40)
        self.header.setMaximumHeight(50)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 3, 10, 3)
        header_layout.setSpacing(8)
        
        # Logo - SMALLER FONT
        logo_label = QLabel("🎯 MzindaTrack")
        logo_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #64ffda;")
        header_layout.addWidget(logo_label)
        
        header_layout.addStretch()
        
        # Current page indicator - SMALLER
        self.page_indicator = QLabel("🔗 Connect")
        self.page_indicator.setStyleSheet("color: #8892b0; font-size: 11px; padding: 2px 6px;")
        header_layout.addWidget(self.page_indicator)
        
        # Status indicator - SMALLER
        self.status_indicator = QLabel("⚪")
        self.status_indicator.setStyleSheet("font-size: 14px; padding: 2px 6px;")
        self.status_indicator.setToolTip("Disconnected")
        header_layout.addWidget(self.status_indicator)
        
        # Auto-connect status label - SMALLER
        self.auto_status_label = QLabel("")
        self.auto_status_label.setStyleSheet("font-size: 9px; color: #64ffda; padding: 1px 4px;")
        self.auto_status_label.setVisible(False)
        header_layout.addWidget(self.auto_status_label)
        
        # === HAMBURGER MENU BUTTON ===
        self.hamburger_btn = QToolButton()
        self.hamburger_btn.setText("☰")
        self.hamburger_btn.setObjectName("hamburgerBtn")
        self.hamburger_btn.setFixedSize(32, 32)
        self.hamburger_btn.setPopupMode(QToolButton.InstantPopup)
        
        # Explicit font and stylesheet to ensure visibility
        self.hamburger_btn.setFont(QFont("Segoe UI", 16, QFont.Bold))
        self.hamburger_btn.setStyleSheet("""
            QToolButton#hamburgerBtn {
                color: #e0e6ed;
                background: transparent;
                border: none;
                padding: 2px;
                font-family: 'Segoe UI', 'Arial Unicode MS', 'DejaVu Sans', sans-serif;
                font-size: 20px;
                font-weight: bold;
            }
            QToolButton#hamburgerBtn:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
            QToolButton#hamburgerBtn:pressed {
                background: rgba(255, 255, 255, 0.15);
            }
        """)
        
        # Ensure it's visible
        self.hamburger_btn.setVisible(True)
        self.hamburger_btn.setEnabled(True)
        
        # Create hamburger menu with compact styling
        self.hamburger_menu = QMenu(self)
        self.hamburger_menu.setStyleSheet("""
            QMenu {
                background-color: #1a1f2e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 3px;
                min-width: 180px;
            }
            QMenu::item {
                padding: 6px 20px 6px 14px;
                border-radius: 6px;
                min-height: 28px;
            }
            QMenu::item:selected {
                background: rgba(102, 126, 234, 0.3);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 0.1);
                margin: 2px 6px;
            }
        """)
        
        # Menu actions
        self.connect_action = QAction("🔗 Connect", self)
        self.connect_action.triggered.connect(lambda: self.switch_page(0))
        self.hamburger_menu.addAction(self.connect_action)
        
        self.view_action = QAction("🌐 View", self)
        self.view_action.triggered.connect(lambda: self.switch_page(1))
        self.hamburger_menu.addAction(self.view_action)
        
        self.account_action = QAction("👤 Account", self)
        self.account_action.triggered.connect(lambda: self.switch_page(2))
        self.hamburger_menu.addAction(self.account_action)
        
        self.hamburger_menu.addSeparator()
        
        self.map_action = QAction("🗺️ Open Map", self)
        self.map_action.triggered.connect(self.open_map)
        self.map_action.setEnabled(False)
        self.hamburger_menu.addAction(self.map_action)
        
        self.phone_action = QAction("📱 Phone Tracker", self)
        self.phone_action.triggered.connect(self.open_phone)
        self.phone_action.setEnabled(False)
        self.hamburger_menu.addAction(self.phone_action)
        
        self.hamburger_menu.addSeparator()
        
        # Auto-connect toggle
        self.auto_connect_action = QAction("🔄 Auto-Connect", self)
        self.auto_connect_action.setCheckable(True)
        self.auto_connect_action.setChecked(True)
        self.auto_connect_action.triggered.connect(self.toggle_auto_connect)
        self.hamburger_menu.addAction(self.auto_connect_action)
        
        # Full screen toggle in menu
        self.fullscreen_action = QAction("⛶ Full Screen", self)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.triggered.connect(self.toggle_web_fullscreen)
        self.hamburger_menu.addAction(self.fullscreen_action)
        
        self.hamburger_menu.addSeparator()
        
        self.disconnect_action = QAction("🚪 Disconnect", self)
        self.disconnect_action.triggered.connect(self.disconnect)
        self.disconnect_action.setEnabled(False)
        self.hamburger_menu.addAction(self.disconnect_action)
        
        # Attach menu to button
        self.hamburger_btn.setMenu(self.hamburger_menu)
        header_layout.addWidget(self.hamburger_btn)
        
        self.main_layout.addWidget(self.header)
        
        # Stacked widget for pages (replaces tab widget)
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Page: Connect/Verify
        self.connect_page = self.create_connect_page()
        self.stacked_widget.addWidget(self.connect_page)
        
        # Page: Web View
        self.web_page = QWidget()
        web_layout = QVBoxLayout(self.web_page)
        web_layout.setContentsMargins(0, 0, 0, 0)
        self.web_view = TouchFriendlyWebView(self)
        web_layout.addWidget(self.web_view)
        self.stacked_widget.addWidget(self.web_page)
        
        # Page: Account
        self.account_page = self.create_account_page()
        self.stacked_widget.addWidget(self.account_page)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Show connect page by default
        self.switch_page(0)
    
    def center_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.switch_page(0))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.switch_page(1))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.switch_page(2))
        QShortcut(QKeySequence("F5"), self, self.web_view.refresh)
        QShortcut(QKeySequence("F11"), self, self.toggle_web_fullscreen)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+A"), self, self.start_auto_connect)
        QShortcut(QKeySequence("Ctrl+S"), self, self.stop_auto_connect)
        QShortcut(QKeySequence("Escape"), self, self.exit_fullscreen_if_active)
    
    def toggle_web_fullscreen(self):
        """Toggle full screen mode for the web view only"""
        if self.is_web_fullscreen:
            self.exit_web_fullscreen()
        else:
            self.enter_web_fullscreen()
    
    def enter_web_fullscreen(self):
        """Enter full screen mode showing only the web view"""
        self.is_web_fullscreen = True
        
        # Save current visibility state
        self.header_visible = self.header.isVisible()
        self.statusbar_visible = self.status_bar.isVisible()
        
        # Hide header and status bar
        self.header.setVisible(False)
        self.status_bar.setVisible(False)
        
        # Update fullscreen menu item
        self.fullscreen_action.setText("⛶ Exit Full Screen")
        
        # Update window title
        self.setWindowTitle("MzindaTrack - Full Screen")
        
        # Show only the web page
        if self.current_page != 1:
            self.switch_page(1)
        
        self.status_bar.showMessage("Full Screen Mode - Press F11 or click ⛶ to exit")
    
    def exit_web_fullscreen(self):
        """Exit full screen mode"""
        self.is_web_fullscreen = False
        
        # Restore header and status bar
        self.header.setVisible(self.header_visible)
        self.status_bar.setVisible(self.statusbar_visible)
        
        # Update fullscreen menu item
        self.fullscreen_action.setText("⛶ Full Screen")
        
        # Restore window title
        self.setWindowTitle("MzindaTrack - GPS yathu, Chitetezo chathu")
        
        self.status_bar.showMessage("Exited Full Screen Mode")
    
    def exit_fullscreen_if_active(self):
        """Exit full screen if active (for Escape key)"""
        if self.is_web_fullscreen:
            self.exit_web_fullscreen()
    
    def switch_page(self, index):
        """Switch to a different page"""
        self.current_page = index
        self.stacked_widget.setCurrentIndex(index)
        
        page_names = ["Connect", "View", "Account"]
        page_icons = ["🔗", "🌐", "👤"]
        self.page_indicator.setText(f"{page_icons[index]} {page_names[index]}")
        
        # Update menu check marks
        self.connect_action.setChecked(index == 0)
        self.view_action.setChecked(index == 1)
        self.account_action.setChecked(index == 2)
        
        # If switching to view page and in fullscreen, ensure proper display
        if index == 1 and self.is_web_fullscreen:
            self.header.setVisible(False)
            self.status_bar.setVisible(False)
    
    def create_connect_page(self):
        """Create the connection/verification page with inline paste button"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        # Title with auto-connect indicator
        title_container = QHBoxLayout()
        title = QLabel("🔑 Connect to MzindaTrack")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title_container.addWidget(title)
        
        self.auto_indicator = QLabel("🔄")
        self.auto_indicator.setStyleSheet("font-size: 13px; color: #64ffda; padding: 0 6px;")
        self.auto_indicator.setToolTip("Auto-connect enabled")
        self.auto_indicator.setVisible(False)
        title_container.addWidget(self.auto_indicator)
        content_layout.addLayout(title_container)
        
        subtitle = QLabel(
            "Enter your MzindaTrack token or the public URL you received via email.\n"
            "You can also register for a new account using the link below."
        )
        subtitle.setStyleSheet("color: #8892b0; font-size: 12px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        content_layout.addWidget(subtitle)
        
        # Server URL input
        server_group = QGroupBox("Server URL")
        server_layout = QHBoxLayout()
        server_layout.setSpacing(8)
        
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("Enter server URL")
        self.server_input.setMinimumHeight(34)
        self.server_input.setMaximumHeight(38)
        self.server_input.textChanged.connect(self.on_server_changed)
        
        # Add default server URL selector
        self.server_selector = QComboBox()
        self.server_selector.addItem("Select default server...")
        for url in DEFAULT_SERVER_URLS:
            self.server_selector.addItem(url)
        self.server_selector.setMinimumHeight(34)
        self.server_selector.setMaximumHeight(38)
        self.server_selector.currentIndexChanged.connect(self.on_server_selected)
        
        self.test_btn = QPushButton("🔍 Test")
        self.test_btn.setObjectName("secondaryBtn")
        self.test_btn.setMinimumHeight(34)
        self.test_btn.setMaximumHeight(38)
        self.test_btn.setMinimumWidth(60)
        self.test_btn.clicked.connect(self.test_server)
        
        server_layout.addWidget(self.server_input, 2)
        server_layout.addWidget(self.server_selector)
        server_layout.addWidget(self.test_btn)
        server_group.setLayout(server_layout)
        content_layout.addWidget(server_group)
        
        # Token input with inline paste button
        token_group = QGroupBox("Token or Access URL")
        token_layout = QVBoxLayout()
        token_layout.setSpacing(8)
        
        # Create a horizontal layout for token input and paste button
        token_input_layout = QHBoxLayout()
        token_input_layout.setSpacing(6)
        
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Paste your MzindaTrack token or URL here")
        self.token_input.setMinimumHeight(38)
        self.token_input.setMaximumHeight(42)
        
        # Paste button inside the field
        self.paste_btn = QPushButton("📋")
        self.paste_btn.setObjectName("pasteBtn")
        self.paste_btn.setToolTip("Paste from clipboard")
        self.paste_btn.clicked.connect(self.paste_token)
        
        token_input_layout.addWidget(self.token_input, 1)
        token_input_layout.addWidget(self.paste_btn)
        
        token_layout.addLayout(token_input_layout)
        
        token_group.setLayout(token_layout)
        content_layout.addWidget(token_group)
        
        # Auto-connect toggle on page
        auto_layout = QHBoxLayout()
        self.auto_connect_check = QCheckBox("🔄 Auto-connect on startup")
        self.auto_connect_check.setChecked(True)
        self.auto_connect_check.toggled.connect(self.toggle_auto_connect_from_ui)
        auto_layout.addWidget(self.auto_connect_check)
        auto_layout.addStretch()
        content_layout.addLayout(auto_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.verify_btn = QPushButton("🔐 Verify Token")
        self.verify_btn.setMinimumHeight(38)
        self.verify_btn.setMaximumHeight(42)
        self.verify_btn.clicked.connect(self.verify_token)
        
        self.register_btn = QPushButton("📝 Register")
        self.register_btn.setObjectName("secondaryBtn")
        self.register_btn.setMinimumHeight(38)
        self.register_btn.setMaximumHeight(42)
        self.register_btn.clicked.connect(self.open_registration)
        
        btn_layout.addWidget(self.verify_btn, 2)
        btn_layout.addWidget(self.register_btn, 1)
        content_layout.addLayout(btn_layout)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMinimumHeight(6)
        self.progress.setMaximumHeight(6)
        content_layout.addWidget(self.progress)
        
        # Status message
        self.verify_status = QLabel()
        self.verify_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verify_status.setWordWrap(True)
        self.verify_status.setStyleSheet("font-size: 12px; padding: 6px;")
        content_layout.addWidget(self.verify_status)
        
        # Recent tokens
        recent_group = QGroupBox("Recent Connections")
        recent_layout = QVBoxLayout()
        self.recent_list = QLabel("No recent connections")
        self.recent_list.setStyleSheet("color: #8892b0; padding: 6px; font-size: 12px;")
        self.recent_list.setWordWrap(True)
        recent_layout.addWidget(self.recent_list)
        recent_group.setLayout(recent_layout)
        content_layout.addWidget(recent_group)
        
        # Info footer
        info = QLabel(
            "🔐 MzindaTrack - GPS yathu, Chitetezo chathu\n"
            "Secure GPS tracking with 2-meter precision"
        )
        info.setStyleSheet("color: #6b7a8f; font-size: 10px; text-align: center; padding: 12px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(info)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return widget
    
    def on_server_selected(self, index):
        """Handle server selection from dropdown"""
        if index > 0:  # Skip the "Select default server..." item
            url = self.server_selector.currentText()
            if url:
                self.server_input.setText(url)
                self.api.set_base_url(url)
                # Auto-test the server
                QTimer.singleShot(500, self.test_server)
    
    def create_account_page(self):
        """Create the account information page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        card = QFrame()
        card.setObjectName("cardFrame")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(16, 16, 16, 16)
        
        self.account_name = QLabel("Not logged in")
        self.account_name.setStyleSheet("font-size: 17px; font-weight: bold;")
        self.account_name.setWordWrap(True)
        
        self.account_email = QLabel("")
        self.account_email.setStyleSheet("color: #8892b0; font-size: 13px;")
        self.account_email.setWordWrap(True)
        
        self.account_org = QLabel("")
        self.account_org.setStyleSheet("color: #8892b0; font-size: 13px;")
        self.account_org.setWordWrap(True)
        
        self.account_status = QLabel("Status: Disconnected")
        self.account_status.setStyleSheet("color: #FF9800; font-size: 13px;")
        
        card_layout.addWidget(self.account_name)
        card_layout.addWidget(self.account_email)
        card_layout.addWidget(self.account_org)
        card_layout.addWidget(self.account_status)
        
        # Full screen info
        fullscreen_info = QLabel("⛶ Press F11 or click the fullscreen button in the web toolbar to enter full screen mode")
        fullscreen_info.setStyleSheet("color: #6b7a8f; font-size: 10px; text-align: center; padding: 12px;")
        fullscreen_info.setWordWrap(True)
        card_layout.addWidget(fullscreen_info)
        
        layout.addWidget(card)
        layout.addStretch()
        
        return widget
    
    def apply_style(self):
        style = get_responsive_style(self.current_size)
        self.setStyleSheet(style)
    
    def adjust_for_screen_size(self, size_category):
        self.current_size = size_category
        
        if size_category == 'small':
            self.header.setMinimumHeight(36)
            self.header.setMaximumHeight(42)
            self.hamburger_btn.setFixedSize(28, 28)
            self.hamburger_btn.setStyleSheet("""
                QToolButton#hamburgerBtn {
                    color: #e0e6ed;
                    background: transparent;
                    border: none;
                    padding: 2px;
                    font-family: 'Segoe UI', 'Arial Unicode MS', 'DejaVu Sans', sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                }
                QToolButton#hamburgerBtn:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                }
                QToolButton#hamburgerBtn:pressed {
                    background: rgba(255, 255, 255, 0.15);
                }
            """)
            # Make web toolbar more compact on small screens
            if hasattr(self, 'web_view'):
                self.web_view.set_compact_mode(True)
            # Adjust paste button size for small screens
            if hasattr(self, 'paste_btn'):
                self.paste_btn.setMinimumWidth(32)
                self.paste_btn.setMaximumWidth(32)
            # Hide server selector on small screens
            if hasattr(self, 'server_selector'):
                self.server_selector.setVisible(False)
        else:
            self.header.setMinimumHeight(40)
            self.header.setMaximumHeight(50)
            self.hamburger_btn.setFixedSize(32, 32)
            self.hamburger_btn.setStyleSheet("""
                QToolButton#hamburgerBtn {
                    color: #e0e6ed;
                    background: transparent;
                    border: none;
                    padding: 2px;
                    font-family: 'Segoe UI', 'Arial Unicode MS', 'DejaVu Sans', sans-serif;
                    font-size: 20px;
                    font-weight: bold;
                }
                QToolButton#hamburgerBtn:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 4px;
                }
                QToolButton#hamburgerBtn:pressed {
                    background: rgba(255, 255, 255, 0.15);
                }
            """)
            if hasattr(self, 'web_view'):
                self.web_view.set_compact_mode(False)
            if hasattr(self, 'paste_btn'):
                self.paste_btn.setMinimumWidth(36)
                self.paste_btn.setMaximumWidth(36)
            if hasattr(self, 'server_selector'):
                self.server_selector.setVisible(True)
        
        self.apply_style()
    
    def load_settings_data(self):
        """Load settings without applying to UI"""
        settings_file = "mzindatrack_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def load_settings(self):
        settings_file = "mzindatrack_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                self.settings_data = settings
                
                # Set server URL from settings or use first default
                if 'server_url' in settings and settings['server_url']:
                    self.server_input.setText(settings['server_url'])
                    self.api.set_base_url(settings['server_url'])
                else:
                    # Set first default server URL
                    self.server_input.setText(DEFAULT_SERVER_URLS[0])
                    self.api.set_base_url(DEFAULT_SERVER_URLS[0])
                    # Try to test it
                    QTimer.singleShot(1000, self.test_server)
                
                if 'recent_tokens' in settings:
                    self.recent_tokens = settings['recent_tokens'][:5]
                    if self.recent_tokens:
                        self.recent_list.setText("\n".join([
                            f"• {t[:20]}..." if len(t) > 20 else f"• {t}"
                            for t in self.recent_tokens
                        ]))
                        self.recent_list.setStyleSheet("color: #64ffda; padding: 6px; font-size: 12px;")
                
                if 'auto_connect_enabled' in settings:
                    self.auto_connect_enabled = settings['auto_connect_enabled']
                    self.auto_connect_check.setChecked(self.auto_connect_enabled)
                    self.auto_connect_action.setChecked(self.auto_connect_enabled)
                    if self.auto_connect_enabled:
                        self.auto_indicator.setVisible(True)
                        self.auto_status_label.setText("🔄 Auto")
                        self.auto_status_label.setVisible(True)
                    else:
                        self.auto_indicator.setVisible(False)
                        self.auto_status_label.setVisible(False)
            except:
                # If settings load fails, use default server
                self.server_input.setText(DEFAULT_SERVER_URLS[0])
                self.api.set_base_url(DEFAULT_SERVER_URLS[0])
    
    def save_settings(self):
        settings_file = "mzindatrack_settings.json"
        try:
            settings = {
                'recent_tokens': self.recent_tokens[:5] if hasattr(self, 'recent_tokens') else [],
                'server_url': self.server_input.text().strip(),
                'auto_connect_enabled': self.auto_connect_enabled,
                'token': self.current_token if self.current_token else ''
            }
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except:
            pass
    
    def on_server_changed(self, text):
        if text.strip():
            self.api.set_base_url(text.strip())
    
    def test_server(self):
        url = self.server_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a server URL")
            return
        
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
            self.server_input.setText(url)
        
        self.api.set_base_url(url)
        
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.status_bar.showMessage("Testing connection...")
        
        result = self.api.get_health()
        
        self.test_btn.setEnabled(True)
        self.test_btn.setText("🔍 Test")
        
        if result.get('status') == 'healthy':
            self.status_indicator.setText("✅")
            self.status_indicator.setToolTip("Connected to server")
            self.status_bar.showMessage("✅ Connected to MzindaTrack server")
            QMessageBox.information(self, "Connection Test", "✅ Successfully connected to MzindaTrack server!")
        else:
            self.status_indicator.setText("⚪")
            self.status_indicator.setToolTip("Disconnected")
            self.status_bar.showMessage("❌ Could not connect to server")
            QMessageBox.warning(self, "Connection Failed", "❌ Could not connect to the server.\nPlease check the URL and try again.")
    
    def paste_token(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.token_input.setText(text)
    
    def do_verify_token(self):
        """Internal verification method used by auto-connect"""
        token = self.token_input.text().strip()
        
        if not token:
            return False
        
        server_url = self.server_input.text().strip()
        if not server_url:
            return False
        
        if not server_url.startswith('http://') and not server_url.startswith('https://'):
            server_url = 'http://' + server_url
            self.server_input.setText(server_url)
        
        self.api.set_base_url(server_url)
        
        # Don't disable buttons during auto-connect
        if not self.auto_connect_manager.is_connecting:
            self.verify_btn.setEnabled(False)
            self.register_btn.setEnabled(False)
            self.progress.setVisible(True)
            self.progress.setValue(0)
        
        self.status_bar.showMessage("Verifying token...")
        
        self.worker = VerifyWorker(self.api, token)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.status.connect(lambda s: self.status_bar.showMessage(s))
        self.worker.finished.connect(self.on_verification_complete)
        self.worker.start()
        
        return True
    
    def verify_token(self):
        """Manual token verification"""
        if self.auto_connect_manager.is_connecting:
            self.auto_connect_manager.stop_auto_connect()
        
        self.do_verify_token()
    
    def on_verification_complete(self, result):
        self.progress.setVisible(False)
        
        if not self.auto_connect_manager.is_connecting:
            self.verify_btn.setEnabled(True)
            self.register_btn.setEnabled(True)
        
        if result.get('valid'):
            self.verified = True
            self.current_token = result['token']
            self.user_info = result.get('user_info', {})
            
            if self.current_token not in self.recent_tokens:
                self.recent_tokens.insert(0, self.current_token)
                self.recent_tokens = self.recent_tokens[:5]
                self.save_settings()
            
            self.verify_status.setText("✅ Token verified successfully!")
            self.verify_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.status_indicator.setText("✅")
            self.status_indicator.setToolTip("Connected - Access granted")
            self.status_bar.showMessage("✅ Token verified - MzindaTrack access granted")
            
            user = self.user_info
            self.account_name.setText(f"👤 {user.get('full_name', 'User')}")
            self.account_email.setText(f"📧 {user.get('email', '')}")
            if user.get('organisation'):
                self.account_org.setText(f"🏢 {user['organisation']}")
            self.account_status.setText("✅ Account Active")
            self.account_status.setStyleSheet("color: #4CAF50;")
            
            # Enable disconnect in menu
            self.disconnect_action.setEnabled(True)
            self.map_action.setEnabled(True)
            self.phone_action.setEnabled(True)
            
            # Notify auto-connect manager
            if self.auto_connect_manager.is_connecting:
                self.auto_connect_manager.on_verification_complete(True)
                return
            
            # Show success message for manual connection
            if not self.auto_connect_manager.is_connecting:
                msg = QMessageBox(self)
                msg.setWindowTitle("Access Granted")
                msg.setText(
                    f"✅ Welcome to MzindaTrack, {user.get('full_name', 'User')}!\n\n"
                    f"Your token has been verified.\n"
                    f"You can now access the map and phone tracker."
                )
                msg.setStyleSheet(self.styleSheet())
                
                map_btn = msg.addButton("🗺️ Open Map", QMessageBox.ButtonRole.AcceptRole)
                phone_btn = msg.addButton("📱 Phone Tracker", QMessageBox.ButtonRole.ActionRole)
                close_btn = msg.addButton("Close", QMessageBox.ButtonRole.RejectRole)
                
                msg.exec()
                
                if msg.clickedButton() == map_btn:
                    self.open_map()
                elif msg.clickedButton() == phone_btn:
                    self.open_phone()
                
                self.switch_page(1)
            
        else:
            self.verified = False
            self.verify_status.setText(f"❌ {result.get('error', 'Invalid token')}")
            self.verify_status.setStyleSheet("color: #f44336;")
            self.status_bar.showMessage("❌ Token verification failed")
            
            # Notify auto-connect manager
            if self.auto_connect_manager.is_connecting:
                self.auto_connect_manager.on_verification_complete(False)
                return
            
            # Show error for manual connection
            if not self.auto_connect_manager.is_connecting:
                QMessageBox.warning(self, "Verification Failed", 
                    f"❌ {result.get('error', 'Invalid token')}\n\n"
                    "Please check your token and try again.\n"
                    "If you don't have a token, click 'Register New Account'."
                )
    
    def start_auto_connect(self):
        """Start the auto-connect process"""
        if not self.auto_connect_enabled:
            return
        
        if self.verified:
            return
        
        self.auto_connect_manager.start_auto_connect(delay=1000)
        self.auto_status_label.setText("🔄 Connecting...")
        self.auto_status_label.setStyleSheet("font-size: 9px; color: #64ffda;")
        self.auto_status_label.setVisible(True)
        self.auto_indicator.setVisible(True)
        self.auto_indicator.setToolTip("Auto-connect in progress")
    
    def stop_auto_connect(self):
        """Stop the auto-connect process"""
        self.auto_connect_manager.stop_auto_connect()
        self.auto_status_label.setVisible(False)
        self.auto_indicator.setVisible(False)
        self.status_bar.showMessage("Auto-connect stopped")
    
    def toggle_auto_connect(self):
        """Toggle auto-connect from menu"""
        self.auto_connect_enabled = not self.auto_connect_enabled
        self.auto_connect_action.setChecked(self.auto_connect_enabled)
        self.auto_connect_check.setChecked(self.auto_connect_enabled)
        
        if self.auto_connect_enabled:
            self.auto_indicator.setVisible(True)
            self.auto_indicator.setToolTip("Auto-connect enabled")
            self.status_bar.showMessage("Auto-connect enabled")
            # Start auto-connect if not connected
            if not self.verified:
                self.start_auto_connect()
        else:
            self.auto_indicator.setVisible(False)
            self.auto_status_label.setVisible(False)
            self.stop_auto_connect()
            self.status_bar.showMessage("Auto-connect disabled")
        
        self.save_settings()
    
    def toggle_auto_connect_from_ui(self, checked):
        """Toggle auto-connect from UI checkbox"""
        self.auto_connect_enabled = checked
        self.auto_connect_action.setChecked(checked)
        
        if checked:
            self.auto_indicator.setVisible(True)
            self.auto_indicator.setToolTip("Auto-connect enabled")
            if not self.verified:
                self.start_auto_connect()
        else:
            self.auto_indicator.setVisible(False)
            self.auto_status_label.setVisible(False)
            self.stop_auto_connect()
        
        self.save_settings()
    
    def open_registration(self):
        server_url = self.server_input.text().strip()
        if not server_url:
            QMessageBox.warning(self, "Warning", "Please enter the server URL first")
            return
        
        if not server_url.startswith('http://') and not server_url.startswith('https://'):
            server_url = 'http://' + server_url
            self.server_input.setText(server_url)
        
        self.api.set_base_url(server_url)
        
        dialog = ResponsiveRegistrationDialog(self.api, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.status_bar.showMessage("Registration successful! Please check your email for payment link.")
    
    def open_map(self):
        if not self.verified or not self.current_token:
            QMessageBox.warning(self, "Warning", "Please verify your token first")
            return
        
        url = f"{self.api.base_url}/map/{self.current_token}"
        self.web_view.set_home_url(url)
        self.web_view.load_url(url)
        self.switch_page(1)
        self.status_bar.showMessage("🗺️ Loading MzindaTrack 3D Map...")
    
    def open_phone(self):
        if not self.verified or not self.current_token:
            QMessageBox.warning(self, "Warning", "Please verify your token first")
            return
        
        url = f"{self.api.base_url}/phone/{self.current_token}"
        self.web_view.set_home_url(url)
        self.web_view.load_url(url)
        self.switch_page(1)
        self.status_bar.showMessage("📱 Loading MzindaTrack Phone Tracker...")
    
    def disconnect(self):
        if not self.verified:
            return
        
        confirm = QMessageBox.question(
            self,
            "Disconnect",
            "Are you sure you want to disconnect from MzindaTrack?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.verified = False
            self.current_token = None
            self.user_info = None
            
            self.account_name.setText("Not logged in")
            self.account_email.setText("")
            self.account_org.setText("")
            self.account_status.setText("Status: Disconnected")
            self.account_status.setStyleSheet("color: #FF9800;")
            
            self.disconnect_action.setEnabled(False)
            self.map_action.setEnabled(False)
            self.phone_action.setEnabled(False)
            
            self.status_indicator.setText("⚪")
            self.status_indicator.setToolTip("Disconnected")
            self.status_bar.showMessage("Disconnected from MzindaTrack")
            
            self.switch_page(0)
            
            # Restart auto-connect if enabled
            if self.auto_connect_enabled:
                QTimer.singleShot(2000, self.start_auto_connect)
            
            QMessageBox.information(self, "Disconnected", "You have been disconnected from MzindaTrack.")
    
    def closeEvent(self, event):
        # Exit full screen if active
        if self.is_web_fullscreen:
            self.exit_web_fullscreen()
        
        self.save_settings()
        if hasattr(self, 'auto_connect_manager'):
            self.auto_connect_manager.stop_auto_connect()
        if hasattr(self, 'web_view'):
            try:
                profile = QWebEngineProfile.defaultProfile()
                profile.clearHttpCache()
            except:
                pass
        event.accept()

# ==================== MAIN ====================
def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("MzindaTrack")
    app.setOrganizationName("MzindaTrack")
    
    # Set application icon before creating window
    icon = get_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    else:
        # Create a default icon if no icon file exists
        icon = create_default_icon()
        if not icon.isNull():
            app.setWindowIcon(icon)
    
    window = MzindaTrackApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()