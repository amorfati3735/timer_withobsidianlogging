# modern_timer_v2.py
#minimalist timer with Obsidian logging.
# Dependencies: pip install PySide6


import sys
import os
import datetime
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QFontDatabase, QIntValidator, QColor, QWheelEvent, QAction
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QStackedWidget, QSizePolicy, QGraphicsOpacityEffect
)

# --- USER CONFIG ---
LOG_FILE_BASE_PATH = r"C:\Users\DELL\Dropbox\DropsyncFiles\lesser amygdala\「日常」"


THEMES = {
    "acid_terminal": {
        "BACKGROUND": "#000000", "FRAME": "#333333",
        "MAIN_TEXT": "#D7FF3C", "SUB_TEXT": "#557711",
        "INPUT_BG": "#000000", "INPUT_BORDER": "#333333",
        "BUTTON_BG": "#111111", "BUTTON_ACTIVE_BG": "#2F3E0F", "PIN_ACTIVE": "#D7FF3C",
        "ALARM_COLOR": "#FF00FF",
        # -- Fonts --
        "UI_FONT": "Consolas", 
        "TIMER_FONT": "Consolas",
        "TIMER_SIZE": "32pt",
        # -- Window --
        "OPACITY": 0.95,
        "BORDER_RADIUS": "0px", # Sharp corners for terminal look
        "BORDER_WIDTH": "2px",
        "PLACEHOLDER_TASK": "exec_task", "PLACEHOLDER_TIME": "<t>"
   },
    "ember_dark": {
        # -- Colors --
        "BACKGROUND": "#0A0A12", "FRAME": "#12121A", 
        "MAIN_TEXT": "#CCFFCC", "SUB_TEXT": "#88AA88",
        "INPUT_BG": "#080810", "INPUT_BORDER": "#12121A",
        "BUTTON_BG": "#2C3128", "BUTTON_ACTIVE_BG": "#364921", "PIN_ACTIVE": "#99FF00",
        "ALARM_COLOR": "#FF3333", # Color when timer hits 0
        # -- Fonts --
        "UI_FONT": "Inter 24pt",      # Font for buttons/inputs
        "TIMER_FONT": "Inter 24pt",   # Font for the big numbers
        "TIMER_SIZE": "34pt",       # Size of big numbers
        # -- Window --
        "OPACITY": 1.0,             # 0.1 to 1.0
        "BORDER_RADIUS": "12px",
        "BORDER_WIDTH": "1px",
        "PLACEHOLDER_TASK": ">..code", "PLACEHOLDER_TIME": "min"
    },
    "minimal_gothic": {
    "BACKGROUND": "#0A0A0B",
    "FRAME": "#161617",

    "MAIN_TEXT": "#E6E0D8",
    "SUB_TEXT": "#7A7370",

    "INPUT_BG": "#0A0A0B",
    "INPUT_BORDER": "#161617",

    "BUTTON_BG": "#151518",
    "BUTTON_ACTIVE_BG": "#3A1F2A",

    "PIN_ACTIVE": "#E6E0D8",

    "ALARM_COLOR": "#8C1B3A",

    "UI_FONT": "Spectral",
    "TIMER_FONT": "Spectral",
    "TIMER_SIZE": "32pt",

    "OPACITY": 0.95,
    "BORDER_RADIUS": "0px",
    "BORDER_WIDTH": "2px",

    "PLACEHOLDER_TASK": "exec_task",
    "PLACEHOLDER_TIME": "<t>"
}


    
    # "glass_prism": {
    #     # Using RGBA for background to make it see-through but keep text opaque-ish
    #     "BACKGROUND": "rgba(20, 20, 30, 180)", "FRAME": "rgba(255, 255, 255, 30)",
    #     "MAIN_TEXT": "#FFFFFF", "SUB_TEXT": "#AAAAAA",
    #     "INPUT_BG": "rgba(0, 0, 0, 50)", "INPUT_BORDER": "rgba(255, 255, 255, 20)",
    #     "BUTTON_BG": "rgba(255, 255, 255, 10)", "BUTTON_ACTIVE_BG": "rgba(255, 255, 255, 40)", "PIN_ACTIVE": "#00FFFF",
    #     "ALARM_COLOR": "#FF9999",
    #     "UI_FONT": "Arial",
    #     "TIMER_FONT": "Arial", 
    #     "TIMER_SIZE": "36pt",
    #     "OPACITY": 1.0, # Window is solid, background color handles transparency
    #     "BORDER_RADIUS": "20px",
    #     "BORDER_WIDTH": "1px",
    #     "PLACEHOLDER_TASK": "Focus...", "PLACEHOLDER_TIME": "m"
    # },
    # "nebula_grape": {
    #     "BACKGROUND": "#09070D", "FRAME": "#110F18",
    #     "MAIN_TEXT": "#A0FFBF", "SUB_TEXT": "#78CFA0",
    #     "INPUT_BG": "#0C0A11", "INPUT_BORDER": "#110F18",
    #     "BUTTON_BG": "#241C33", "BUTTON_ACTIVE_BG": "#3A2E56", "PIN_ACTIVE": "#C78FFF",
    #     "ALARM_COLOR": "#FF00FF",
    #     "UI_FONT": "Verdana",
    #     "TIMER_FONT": "Impact", # Bold font
    #     "TIMER_SIZE": "38pt",
    #     "OPACITY": 0.98,
    #     "BORDER_RADIUS": "15px",
    #     "BORDER_WIDTH": "1px",
    #     "PLACEHOLDER_TASK": "Dream...", "PLACEHOLDER_TIME": "t"
    # },
    # "retro_writer": {
    #     "BACKGROUND": "#FDF6E3", "FRAME": "#EEE8D5",
    #     "MAIN_TEXT": "#657B83", "SUB_TEXT": "#93A1A1",
    #     "INPUT_BG": "#FDF6E3", "INPUT_BORDER": "#D33682",
    #     "BUTTON_BG": "#EEE8D5", "BUTTON_ACTIVE_BG": "#D33682", "PIN_ACTIVE": "#D33682",
    #     "ALARM_COLOR": "#DC322F",
    #     "UI_FONT": "Courier New",
    #     "TIMER_FONT": "Courier New",
    #     "TIMER_SIZE": "30pt",
    #     "OPACITY": 1.0,
    #     "BORDER_RADIUS": "4px",
    #     "BORDER_WIDTH": "2px",
    #     "PLACEHOLDER_TASK": "Type...", "PLACEHOLDER_TIME": "#"

}

# Dimensions
DEFAULT_WIDTH = 240
DEFAULT_HEIGHT = 220

class ModernTimerApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Logic State
        self.seconds_value = 0
        self.initial_seconds = 0
        self.is_running = False
        self.drag_pos = None
        self.is_pinned = True
        self.flash_state = False
        
        # Theme State
        self.theme_names = list(THEMES.keys())
        self.current_theme_index = 0
        
        # Setup
        self._setup_window()
        self._init_ui()
        
        # Timers
        self.main_timer = QTimer(self)
        self.main_timer.setInterval(1000)
        self.main_timer.timeout.connect(self._update_timer)
        
        self.alarm_timer = QTimer(self)
        self.alarm_timer.setInterval(500) # Flash every 500ms
        self.alarm_timer.timeout.connect(self._flash_alarm)

        # Initial Style
        self._apply_theme()

    def _get_current_theme(self):
        return THEMES[self.theme_names[self.current_theme_index]]

    def _setup_window(self):
        self.setWindowTitle("Custom Timer")
        self.resize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        # Frameless and Transparent background capability
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def _init_ui(self):
        self.central_frame = QFrame(self)
        self.central_frame.setObjectName("centralFrame")
        
        main_layout = QVBoxLayout(self.central_frame)
        main_layout.setContentsMargins(12, 8, 12, 12)
        main_layout.setSpacing(6)

        # 1. Header
        header_layout = self._create_header()
        
        # 2. Input Stack
        self.input_stack = self._create_input_area()
        
        # 3. Timer Display
        timer_layout = self._create_timer_display()
        
        # 4. Progress Bar (Visual candy)
        self.progress_bar = QFrame()
        self.progress_bar.setFixedHeight(2)
        self.progress_bar.setObjectName("progressBar")
        
        # 5. Controls
        controls_layout = self._create_controls()

        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.input_stack)
        main_layout.addStretch(1)
        main_layout.addLayout(timer_layout)
        main_layout.addWidget(self.progress_bar)
        main_layout.addStretch(1)
        main_layout.addLayout(controls_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.central_frame)
        self.setLayout(outer_layout)

    def _create_header(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("iconBtn")
        self.theme_btn.setToolTip("Next Theme")
        self.theme_btn.clicked.connect(self._cycle_theme)
        
        self.pin_btn = QPushButton("●")
        self.pin_btn.setObjectName("pinBtn")
        self.pin_btn.setToolTip("Toggle Always on Top")
        self.pin_btn.clicked.connect(self._toggle_pin)
        
        min_btn = QPushButton("—")
        min_btn.setObjectName("iconBtn")
        min_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("iconBtn")
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(self.theme_btn)
        layout.addWidget(self.pin_btn)
        layout.addStretch()
        layout.addWidget(min_btn)
        layout.addWidget(close_btn)
        return layout

    def _create_input_area(self):
        stack = QStackedWidget()
        stack.setFixedHeight(30)

        # Page 0: Inputs
        pg0 = QWidget()
        l0 = QHBoxLayout(pg0)
        l0.setContentsMargins(0,0,0,0); l0.setSpacing(5)
        
        self.task_input = QLineEdit()
        self.task_input.setObjectName("taskInput")
        
        self.time_input = QLineEdit()
        self.time_input.setValidator(QIntValidator(1, 999))
        self.time_input.setFixedWidth(45)
        self.time_input.setAlignment(Qt.AlignCenter)
        self.time_input.setObjectName("timeInput")
        
        l0.addWidget(self.task_input)
        l0.addWidget(self.time_input)

        # Page 1: Label (Running)
        self.task_label = QLabel()
        self.task_label.setAlignment(Qt.AlignCenter)
        self.task_label.setObjectName("taskLabel")
        
        stack.addWidget(pg0)
        stack.addWidget(self.task_label)
        return stack

    def _create_timer_display(self):
        layout = QVBoxLayout()
        layout.setSpacing(0)
        
        self.timer_val_label = QLabel("00:00:00")
        self.timer_val_label.setAlignment(Qt.AlignCenter)
        self.timer_val_label.setObjectName("timerDigits")
        
        # Sub-labels container
        sub_layout = QHBoxLayout()
        for txt in ["H", "M", "S"]:
            lbl = QLabel(txt)
            lbl.setObjectName("subLabel")
            lbl.setAlignment(Qt.AlignCenter)
            sub_layout.addWidget(lbl)
            
        layout.addWidget(self.timer_val_label)
        layout.addLayout(sub_layout)
        return layout

    def _create_controls(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        self.btn_log = QPushButton("✓")
        self.btn_log.setFixedSize(40, 40)
        self.btn_log.setObjectName("circleBtn")
        self.btn_log.setToolTip("Log to Obsidian")
        self.btn_log.clicked.connect(self._log_time)
        self.btn_log.setEnabled(False)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setFixedSize(65, 34)
        self.btn_reset.setObjectName("pillBtn")
        self.btn_reset.clicked.connect(self._reset_timer)

        self.btn_start = QPushButton("Start")
        self.btn_start.setFixedSize(80, 34)
        self.btn_start.setObjectName("pillBtnMain")
        self.btn_start.clicked.connect(self._toggle_timer)

        layout.addStretch()
        layout.addWidget(self.btn_log)
        layout.addWidget(self.btn_reset)
        layout.addWidget(self.btn_start)
        layout.addStretch()
        return layout

    # --- STYLE & THEME ENGINE ---
    def _cycle_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.theme_names)
        self._apply_theme()

    def _apply_theme(self):
        t = self._get_current_theme()
        
        # 1. Window Opacity (Base theme opacity)
        self.setWindowOpacity(t.get("OPACITY", 1.0))
        
        # 2. Update Placeholders
        self.task_input.setPlaceholderText(t["PLACEHOLDER_TASK"])
        self.time_input.setPlaceholderText(t["PLACEHOLDER_TIME"])
        
        # 3. CSS Construction
        css = f"""
            QWidget {{ font-family: '{t['UI_FONT']}'; }}
            
            #centralFrame {{
                background-color: {t['BACKGROUND']};
                border: {t['BORDER_WIDTH']} solid {t['FRAME']};
                border-radius: {t['BORDER_RADIUS']};
            }}
            
            /* --- Header Buttons --- */
            #iconBtn {{
                background: transparent;
                color: {t['SUB_TEXT']};
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            #iconBtn:hover {{ color: {t['MAIN_TEXT']}; }}
            
            #pinBtn {{ background: transparent; color: {t['SUB_TEXT']}; font-size: 16px; border: none; }}
            #pinBtn:hover {{ color: {t['MAIN_TEXT']}; }}
            #pinBtn[pinned="true"] {{ color: {t['PIN_ACTIVE']}; }}
            
            /* --- Inputs --- */
            QLineEdit {{
                background-color: {t['INPUT_BG']};
                border: 1px solid {t['INPUT_BORDER']};
                border-radius: 4px;
                color: {t['MAIN_TEXT']};
                padding: 2px 5px;
                font-size: 12px;
            }}
            QLineEdit:focus {{ border: 1px solid {t['PIN_ACTIVE']}; }}
            
            /* --- Labels --- */
            #taskLabel {{ color: {t['MAIN_TEXT']}; font-weight: bold; font-size: 13px; }}
            
            #timerDigits {{
                font-family: '{t['TIMER_FONT']}';
                font-size: {t['TIMER_SIZE']};
                color: {t['MAIN_TEXT']};
                font-weight: bold;
            }}
            #timerDigits[alarm="true"] {{ color: {t['ALARM_COLOR']}; }}
            
            #subLabel {{ color: {t['SUB_TEXT']}; font-size: 9px; font-weight: bold; letter-spacing: 1px; }}
            
            #progressBar {{ background-color: {t['FRAME']}; border: none; }}
            
            /* --- Control Buttons --- */
            #pillBtn {{
                background-color: {t['BUTTON_BG']};
                color: {t['MAIN_TEXT']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            #pillBtn:hover {{ background-color: {t['FRAME']}; }}
            
            #pillBtnMain {{
                background-color: {t['BUTTON_ACTIVE_BG']};
                color: {t['MAIN_TEXT']};
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }}
            #pillBtnMain:hover {{ background-color: {t['BUTTON_BG']}; }}
            
            #circleBtn {{
                background-color: {t['BUTTON_BG']};
                color: {t['PIN_ACTIVE']};
                border-radius: 20px; /* Perfect circle for 40px size */
                font-size: 16px;
                font-weight: bold;
            }}
            #circleBtn:hover {{ background-color: {t['FRAME']}; }}
            #circleBtn:disabled {{ color: {t['SUB_TEXT']}; background-color: transparent; border: 1px solid {t['FRAME']}; }}
        """
        self.central_frame.setStyleSheet(css)
        
        # Update dynamic properties needed for styling
        self.pin_btn.setProperty("pinned", self.is_pinned)
        self.style().polish(self.pin_btn)

    # --- LOGIC ---
    def _toggle_timer(self):
        if not self.is_running:
            if self.initial_seconds == 0:
                # Start fresh
                try:
                    mins = int(self.time_input.text())
                    if mins <= 0: return
                except ValueError:
                    return
                
                self.initial_seconds = mins * 60
                self.seconds_value = self.initial_seconds
                
                # UI Swap
                txt = self.task_input.text().strip()
                self.task_label.setText(txt if txt else "Untitled")
                self.input_stack.setCurrentIndex(1)
                self.btn_log.setEnabled(True)
                
                # Visuals
                self.btn_start.setText("Pause")
                t = self._get_current_theme()
                self.progress_bar.setStyleSheet(f"background-color: {t['PIN_ACTIVE']};")
                
                self.main_timer.start()
                self.is_running = True
            else:
                # Resume
                self.main_timer.start()
                self.is_running = True
                self.btn_start.setText("Pause")
        else:
            # Pause
            self.main_timer.stop()
            self.alarm_timer.stop() # Stop alarm if flashing
            self.is_running = False
            self.btn_start.setText("Resume")

    def _reset_timer(self):
        self.main_timer.stop()
        self.alarm_timer.stop()
        self.is_running = False
        self.seconds_value = 0
        self.initial_seconds = 0
        self.flash_state = False
        
        self.btn_start.setText("Start")
        self.input_stack.setCurrentIndex(0)
        self.task_input.clear()
        self.time_input.clear()
        self.btn_log.setEnabled(False)
        
        # Reset styling
        self.timer_val_label.setProperty("alarm", False)
        self.style().polish(self.timer_val_label)
        t = self._get_current_theme()
        self.timer_val_label.setText("00:00:00")
        self.progress_bar.setStyleSheet(f"background-color: {t['FRAME']};")

    def _update_timer(self):
        self.seconds_value -= 1
        
        # Handle Alarm Visuals
        if self.seconds_value < 0 and not self.alarm_timer.isActive():
            self.alarm_timer.start()
            
        self._update_display()

    def _flash_alarm(self):
        # Toggles property for CSS styling
        self.flash_state = not self.flash_state
        self.timer_val_label.setProperty("alarm", self.flash_state)
        self.style().polish(self.timer_val_label)

    def _update_display(self):
        is_neg = self.seconds_value < 0
        total_sec = abs(self.seconds_value)
        
        h, rem = divmod(total_sec, 3600)
        m, s = divmod(rem, 60)
        
        prefix = "-" if is_neg else ""
        self.timer_val_label.setText(f"{prefix}{h:02d}:{m:02d}:{s:02d}")

    def _log_time(self):
        try:
            today = datetime.date.today()
            fname = today.strftime("%d-%b.md")
            fpath = os.path.join(LOG_FILE_BASE_PATH, fname)
            
            title = self.task_label.text()
            elapsed = self.initial_seconds - self.seconds_value
            mins = max(1, elapsed // 60) # Minimum 1 minute log
            
            line = f"\n- [{title} - {mins}min]"
            
            os.makedirs(LOG_FILE_BASE_PATH, exist_ok=True)
            with open(fpath, 'a', encoding='utf-8') as f:
                f.write(line)
            
            # Visual feedback
            self.btn_log.setEnabled(False) # Prevent double logging
            print(f"Logged: {line}")
        except Exception as e:
            print(f"Log Error: {e}")

    # --- WINDOW EVENTS ---
    def _toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.is_pinned)
        self.show()
        self.pin_btn.setProperty("pinned", self.is_pinned)
        self.style().polish(self.pin_btn)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.LeftButton:
            self.drag_pos = e.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, e: QMouseEvent):
        if self.drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.drag_pos = None

    # DYNAMIC OPACITY CONTROL
    def wheelEvent(self, e: QWheelEvent):
        # Check if Control key is held down
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ControlModifier:
            delta = e.angleDelta().y()
            current_op = self.windowOpacity()
            
            if delta > 0:
                new_op = min(current_op + 0.05, 1.0)
            else:
                new_op = max(current_op - 0.05, 0.2) # Don't go below 0.2 visibility
                
            self.setWindowOpacity(new_op)
            e.accept()
        else:
            super().wheelEvent(e)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ModernTimerApp()
    win.show()
    sys.exit(app.exec())