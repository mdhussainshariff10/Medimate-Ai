import math

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton
)


# ==========================================
# WAVEFORM
# ==========================================

class Waveform(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(75)
        self.phase = 0.0
        self.active = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def animate(self):
        if self.active:
            self.phase += 0.12
            self.update()

    def set_active(self, active):
        self.active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = self.width()
        height = self.height()
        center_y = height / 2

        bar_count = 43
        spacing = width / (bar_count + 1)

        for i in range(bar_count):

            x = spacing * (i + 1)

            wave = (
                math.sin(i * 0.42 + self.phase) * 0.5
                + math.sin(i * 0.18 - self.phase * 1.3) * 0.3
                + math.sin(i * 0.7 + self.phase * 0.6) * 0.2
            )

            strength = 1.0 if self.active else 0.12

            bar_height = (
                9 + abs(wave) * 30
            ) * strength

            color = QColor(
                "#38BDF8" if i % 4 == 0 else "#14B8A6"
            )

            pen = QPen(color, 3)
            pen.setCapStyle(
                Qt.PenCapStyle.RoundCap
            )

            painter.setPen(pen)

            painter.drawLine(
                int(x),
                int(center_y - bar_height),
                int(x),
                int(center_y + bar_height)
            )

        painter.end()


# ==========================================
# STATUS CARD
# ==========================================

class StatusCard(QFrame):

    def __init__(self, icon, title, status="Ready"):
        super().__init__()

        self.setObjectName("statusCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(17, 15, 17, 15)
        layout.setSpacing(9)

        top = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setObjectName("statusIcon")

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")

        top.addWidget(icon_label)
        top.addWidget(title_label)
        top.addStretch()

        self.status_label = QLabel(status)
        self.status_label.setObjectName("readyBadge")

        self.progress = QFrame()
        self.progress.setObjectName("progressTrack")
        self.progress.setFixedHeight(9)

        self.progress_fill = QFrame(self.progress)
        self.progress_fill.setObjectName("progressFill")
        self.progress_fill.setGeometry(0, 0, 200, 9)

        layout.addLayout(top)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)

    def set_status(self, status):
        self.status_label.setText(status)


# ==========================================
# MEDIMATE DASHBOARD
# ==========================================

class MediMateDashboard(QMainWindow):

    scan_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "MediMate AI - Health Assistant"
        )

        self.resize(1450, 900)
        self.setMinimumSize(1100, 720)

        # ==================================
        # STYLESHEET
        # ==================================

        self.setStyleSheet("""
            QMainWindow {
                background: #F4F8FF;
            }

            QWidget {
                font-family: 'Segoe UI';
                color: #142B50;
            }

            #header {
                background: white;
                border-bottom: 1px solid #E5EDF7;
            }

            #brand {
                font-size: 25px;
                font-weight: 800;
                color: #12335B;
            }

            #sidebar {
                background: white;
                border-right: 1px solid #E6EDF7;
            }

            #navItem {
                background: transparent;
                border-radius: 12px;
                padding: 13px;
                font-size: 15px;
                font-weight: 600;
                color: #274263;
            }

            #navActive {
                background: #13B8A6;
                color: white;
                border-radius: 12px;
                padding: 13px;
                font-size: 15px;
                font-weight: 700;
            }

            #sectionTitle {
                font-size: 19px;
                font-weight: 800;
                color: #142B50;
            }

            #statusCard, #infoCard {
                background: white;
                border: 1px solid #E7EEF8;
                border-radius: 18px;
            }

            #cardTitle {
                font-size: 15px;
                font-weight: 700;
            }

            #statusIcon {
                font-size: 25px;
                color: #0D9E9A;
            }

            #readyBadge {
                background: #D9FBEA;
                color: #12834B;
                border-radius: 10px;
                padding: 5px 12px;
                font-weight: 700;
            }

            #progressTrack {
                background: #E5EDF7;
                border-radius: 5px;
            }

            #progressFill {
                background: #13B8A6;
                border-radius: 5px;
            }

            #message {
                background: #F0F7FF;
                border: 1px solid #E0EDF9;
                border-radius: 12px;
                padding: 15px;
                color: #244365;
                font-size: 14px;
            }

            #listening {
                font-size: 30px;
                font-weight: 800;
                color: #12335B;
            }

            #subtitle {
                color: #66809D;
                font-size: 14px;
            }

            #micCircle {
                background: #13B8A6;
                border: 8px solid #D8F8F3;
                border-radius: 48px;
                color: white;
                font-size: 32px;
                font-weight: bold;
            }

            #online {
                background: #DDF9EE;
                color: #087A50;
                border-radius: 15px;
                padding: 8px;
                font-weight: 700;
            }

            #scanButton {
                background: #13B8A6;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                font-weight: 700;
            }

            #scanButton:hover {
                background: #0F9F94;
            }

            #scanButton:disabled {
                background: #9BBDBA;
            }
        """)

        # ==================================
        # ROOT WIDGET
        # ==================================

        root = QWidget()
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==================================
        # HEADER
        # ==================================

        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(76)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(28, 10, 28, 10)

        brand = QLabel("〰 MediMate AI")
        brand.setObjectName("brand")

        assistant_tag = QLabel("✚  Health Assistant")

        assistant_tag.setStyleSheet("""
            background: #E7F8F6;
            color: #087F79;
            padding: 10px 18px;
            border-radius: 18px;
            font-weight: 700;
        """)

        user_label = QLabel("👤  User")

        user_label.setStyleSheet("""
            background: #F0F5FC;
            padding: 10px 18px;
            border-radius: 18px;
            font-weight: 700;
        """)

        header_layout.addWidget(brand)
        header_layout.addSpacing(22)
        header_layout.addWidget(assistant_tag)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("🔔"))
        header_layout.addSpacing(22)
        header_layout.addWidget(QLabel("⚙"))
        header_layout.addSpacing(22)
        header_layout.addWidget(user_label)

        main_layout.addWidget(header)

        # ==================================
        # BODY
        # ==================================

        body = QHBoxLayout()
        body.setSpacing(0)
        body.setContentsMargins(0, 0, 0, 0)

        main_layout.addLayout(body)

        # ==================================
        # SIDEBAR
        # ==================================

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)

        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(17, 25, 17, 20)
        side_layout.setSpacing(12)

        nav_items = [
            ("⌂", "Dashboard", True),
            ("▱", "Medicine Reader", False),
            ("▣", "Prescription Scanner", False),
            ("▦", "Reminders", False),
            ("▤", "Medicine Info", False),
            ("◷", "History", False),
            ("⚙", "Settings", False)
        ]

        for icon, name, active in nav_items:

            item = QLabel(f"{icon}    {name}")

            item.setObjectName(
                "navActive" if active else "navItem"
            )

            side_layout.addWidget(item)

        side_layout.addStretch()

        illustration = QLabel("✚")
        illustration.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        illustration.setStyleSheet("""
            font-size: 90px;
            color: #13B8A6;
            background: #E9FAF8;
            border-radius: 75px;
            padding: 20px;
        """)

        online = QLabel("●  System Online")
        online.setObjectName("online")
        online.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        version = QLabel("MediMate AI v1.0")
        version.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        version.setStyleSheet(
            "color: #71849D; padding: 8px;"
        )

        side_layout.addWidget(illustration)
        side_layout.addWidget(online)
        side_layout.addWidget(version)

        body.addWidget(sidebar)

        # ==================================
        # MAIN CONTENT
        # ==================================

        content = QWidget()

        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(22, 22, 22, 22)
        content_layout.setSpacing(18)

        body.addWidget(content, 1)

        # ==================================
        # LEFT STATUS COLUMN
        # ==================================

        left_column = QVBoxLayout()
        left_column.setSpacing(13)

        title = QLabel("▥  System Status")
        title.setObjectName("sectionTitle")

        left_column.addWidget(title)

        self.voice_card = StatusCard(
            "🎙", "Voice Recognition"
        )

        self.speech_card = StatusCard(
            "🔊", "Text to Speech"
        )

        self.camera_card = StatusCard(
            "📷", "Camera Scanner", "Standby"
        )

        self.database_card = StatusCard(
            "▤", "Medicine Database"
        )

        left_column.addWidget(self.voice_card)
        left_column.addWidget(self.speech_card)
        left_column.addWidget(self.camera_card)

        # CAMERA BUTTON

        self.scan_button = QPushButton(
            "📷  Scan Medicine"
        )

        self.scan_button.setObjectName("scanButton")

        self.scan_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.scan_button.clicked.connect(
            self.scan_requested.emit
        )

        left_column.addWidget(self.scan_button)

        left_column.addWidget(self.database_card)
        left_column.addStretch()

        content_layout.addLayout(left_column, 3)

        # ==================================
        # CENTER VOICE COLUMN
        # ==================================

        center_column = QVBoxLayout()

        center_column.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        center_column.setSpacing(13)

        self.waveform = Waveform()

        center_column.addWidget(self.waveform)

        self.listening_label = QLabel(
            "Starting microphone..."
        )

        self.listening_label.setObjectName("listening")

        self.listening_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitle = QLabel(
            "Your AI Health Companion"
        )

        subtitle.setObjectName("subtitle")

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.mic_circle = QLabel("🎙")

        self.mic_circle.setObjectName("micCircle")
        self.mic_circle.setFixedSize(100, 100)

        self.mic_circle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        mic_row = QHBoxLayout()

        mic_row.addStretch()
        mic_row.addWidget(self.mic_circle)
        mic_row.addStretch()

        center_column.addWidget(subtitle)
        center_column.addWidget(self.listening_label)
        center_column.addLayout(mic_row)
        center_column.addSpacing(20)

        self.command_hint = QLabel(
            "Say a command such as: Hello MediMate"
        )

        self.command_hint.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.command_hint.setObjectName("subtitle")

        center_column.addWidget(self.command_hint)
        center_column.addStretch()

        content_layout.addLayout(center_column, 4)

        # ==================================
        # RIGHT INFORMATION COLUMN
        # ==================================

        right_column = QVBoxLayout()
        right_column.setSpacing(14)

        # RECOGNIZED COMMAND CARD

        command_card = QFrame()
        command_card.setObjectName("infoCard")

        command_layout = QVBoxLayout(command_card)

        command_layout.setContentsMargins(
            17, 17, 17, 17
        )

        command_layout.setSpacing(12)

        command_title = QLabel(
            "▸  Recognized Command"
        )

        command_title.setObjectName("sectionTitle")

        self.command_text = QLabel(
            "Waiting for your voice command..."
        )

        self.command_text.setObjectName("message")
        self.command_text.setWordWrap(True)

        command_layout.addWidget(command_title)
        command_layout.addWidget(self.command_text)

        # RESPONSE CARD

        response_card = QFrame()
        response_card.setObjectName("infoCard")

        response_layout = QVBoxLayout(response_card)

        response_layout.setContentsMargins(
            17, 17, 17, 17
        )

        response_layout.setSpacing(12)

        response_title = QLabel(
            "✿  MediMate Response"
        )

        response_title.setObjectName("sectionTitle")

        self.response_text = QLabel(
            "Hello! I am MediMate AI. Waiting for your command."
        )

        self.response_text.setObjectName("message")
        self.response_text.setWordWrap(True)
        self.response_text.setMinimumHeight(120)

        response_layout.addWidget(response_title)
        response_layout.addWidget(self.response_text)

        # ACTIVITY CARD

        activity_card = QFrame()
        activity_card.setObjectName("infoCard")

        activity_layout = QVBoxLayout(activity_card)

        activity_layout.setContentsMargins(
            17, 17, 17, 17
        )

        activity_title = QLabel(
            "◷  Recent Activity"
        )

        activity_title.setObjectName("sectionTitle")

        activity_layout.addWidget(activity_title)

        self.activity_text = QLabel(
            "No recent activity yet.\n\n"
            "Your recognized voice commands will appear here."
        )

        self.activity_text.setObjectName("message")
        self.activity_text.setWordWrap(True)

        activity_layout.addWidget(self.activity_text)

        right_column.addWidget(command_card)
        right_column.addWidget(response_card)
        right_column.addWidget(activity_card)
        right_column.addStretch()

        content_layout.addLayout(right_column, 4)

    # ======================================
    # DASHBOARD UPDATE METHODS
    # ======================================

    def update_command(self, command):
        self.command_text.setText(
            f"“{command}”"
        )

    def update_response(self, response):
        self.response_text.setText(response)

    def update_status(self, status):
        self.listening_label.setText(status)

    def closeEvent(self, event):
        event.accept()