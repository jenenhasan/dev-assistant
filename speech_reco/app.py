import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QScrollArea, QHBoxLayout, QFrame,
    QGraphicsOpacityEffect, QSizePolicy, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QTimer, QSize, QRectF, QPointF
)
from PyQt5.QtGui import (
    QIcon, QColor, QPalette, QFont,
    QLinearGradient, QBrush, QPixmap, QMovie, QPainter, 
    QPen, QPainterPath
)
from main import VoiceAssistant # Assuming this is your voice assistant module

# Dummy VoiceAssistant class to simulate
class Assistant:
    def __init__(self):
        self.voiceAssistant = VoiceAssistant()
    def start(self):
        self.voiceAssistant.startA() 
        print("Assistant started")
        
    def stop(self):
        print("Assistant stopped")


class AssistantThread(QThread):
    update_status = pyqtSignal(str)
    update_message = pyqtSignal(str, str)
    thinking_signal = pyqtSignal(bool)
    listening_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.assistant = VoiceAssistant()

    def run(self):
        self.assistant.startA()
        self.listening_signal.emit(True)
        # Simulate processing time
        self.thinking_signal.emit(True)
        QTimer.singleShot(1500, lambda: self.thinking_signal.emit(False))
        # Simulate receiving a message
        QTimer.singleShot(2000, lambda: self.update_message.emit("Hello! How can I help you today?", "assistant"))

    def stop(self):
        self.listening_signal.emit(False)
        self.assistant.stop()


class VoiceIndicator(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background: transparent; border: none;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Main listening circle
        self.main_circle = self.scene().addEllipse(QRectF(-40, -40, 80, 80), 
                          QPen(Qt.NoPen), QColor(66, 133, 244, 150))
        
        # State text
        self.state_text = self.scene().addSimpleText("Listening")
        self.state_text.setBrush(QColor("#333333"))
        self.state_text.setFont(QFont("Arial", 14, QFont.Bold))
        self.state_text.setPos(-self.state_text.boundingRect().width()/2, 60)
        
        # Instruction text
        self.instruction_text = self.scene().addSimpleText("Start speaking")
        self.instruction_text.setBrush(QColor("#666666"))
        self.instruction_text.setFont(QFont("Arial", 12))
        self.instruction_text.setPos(-self.instruction_text.boundingRect().width()/2, 90)
        
        # Cancel text
        self.cancel_text = self.scene().addSimpleText("Tap to cancel")
        self.cancel_text.setBrush(QColor("#666666"))
        self.cancel_text.setFont(QFont("Arial", 10))
        self.cancel_text.setPos(-self.cancel_text.boundingRect().width()/2, 120)
        
        # Animation circles
        self.animation_circles = []
        for i in range(3):
            circle = self.scene().addEllipse(QRectF(-40, -40, 80, 80), 
                                           QPen(Qt.NoPen), QColor(66, 133, 244, 30))
            circle.setVisible(False)
            self.animation_circles.append(circle)
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"")
        self.animation.setDuration(2000)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.update_animation)
        
        self.current_state = "idle"
        self.set_state("idle")

    def set_state(self, state):
        self.current_state = state
        if state == "listening":
            self.state_text.setText("Listening")
            self.instruction_text.setText("Start speaking")
            self.main_circle.setBrush(QColor(66, 133, 244, 150))
            for circle in self.animation_circles:
                circle.setVisible(True)
            self.animation.start()
        elif state == "thinking":
            self.state_text.setText("Thinking")
            self.instruction_text.setText("")
            self.main_circle.setBrush(QColor(234, 67, 53, 150))
            for circle in self.animation_circles:
                circle.setVisible(False)
            self.animation.stop()
        else:  # idle
            self.state_text.setText("")
            self.instruction_text.setText("")
            self.main_circle.setBrush(QColor(66, 133, 244, 0))
            for circle in self.animation_circles:
                circle.setVisible(False)
            self.animation.stop()

    def update_animation(self, value):
        for i, circle in enumerate(self.animation_circles):
            progress = (value + i * 0.3) % 1.0
            scale = 1.0 + progress * 0.8
            opacity = 1.0 - progress
            circle.setScale(scale)
            circle.setOpacity(opacity)
            if self.current_state == "listening":
                circle.setBrush(QColor(66, 133, 244, int(opacity * 100)))


class SimpleVoiceButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4285F4;
                border-radius: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #3367D6;
            }
            QPushButton:pressed {
                background-color: #2A56C6;
            }
        """)
        self.setIcon(QIcon("mic_icon.png"))  # Replace with your mic icon
        self.setIconSize(QSize(30, 30))


class ChatBubble(QFrame):
    def __init__(self, text, sender="user"):
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(400)
        
        # Animation setup
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setWordWrap(True)
        label.setFont(QFont("Segoe UI", 11))
        label.setStyleSheet("color: #333333;")

        if sender == "user":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4facfe, stop:1 #00f2fe);
                    border-radius: 12px;
                    padding: 12px;
                    margin: 8px 8px 8px 60px;
                }
            """)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a1c4fd, stop:1 #c2e9fb);
                    border-radius: 12px;
                    padding: 12px;
                    margin: 8px 60px 8px 8px;
                }
            """)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(label)
        self.setLayout(layout)
        
        # Start animation when created
        QTimer.singleShot(50, self.animation.start)


class AppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Healthcare Assistant")
        self.setWindowIcon(QIcon("assistant_icon.png"))  # Add your icon file
        self.setGeometry(300, 200, 500, 700)
        
        # Modern gradient background
        self.setAutoFillBackground(True)
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#f5f7fa"))
        gradient.setColorAt(1, QColor("#c3cfe2"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

        self.thread = None
        self.listening = False

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with logo and status
        header = QHBoxLayout()
        
        # Logo label
        logo = QLabel()
        logo.setPixmap(QPixmap("health_icon.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(logo)
        
        # Title and status
        title_layout = QVBoxLayout()
        title = QLabel("Smart Healthcare Assistant")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        
        self.status_label = QLabel("🟡 Idle")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #7f8c8d;")
        
        title_layout.addWidget(title)
        title_layout.addWidget(self.status_label)
        header.addLayout(title_layout)
        header.addStretch()
        
        main_layout.addLayout(header)

        # Scrollable chat area
        self.chat_area = QVBoxLayout()
        self.chat_area.setSpacing(5)
        self.chat_area.addStretch()

        chat_container = QWidget()
        chat_container.setLayout(self.chat_area)
        chat_container.setStyleSheet("background: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(chat_container)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #dfe6e9;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #b2bec3;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        main_layout.addWidget(scroll)

        # Voice indicator (centered)
        self.voice_indicator = VoiceIndicator()
        self.voice_indicator.setFixedSize(300, 200)
        main_layout.addWidget(self.voice_indicator, alignment=Qt.AlignCenter)

        # Bottom area with voice button
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        self.voice_button = SimpleVoiceButton()
        self.voice_button.clicked.connect(self.toggle_assistant)
        bottom_layout.addWidget(self.voice_button)
        
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def toggle_assistant(self):
        if not self.listening:
            self.start_assistant()
        else:
            self.stop_assistant()

    def start_assistant(self):
        self.listening = True
        self.thread = AssistantThread()
        self.thread.update_message.connect(self.display_message)
        self.thread.thinking_signal.connect(self.set_thinking_state)
        self.thread.listening_signal.connect(self.set_listening_state)
        self.thread.start()
        
        self.animate_status_change("🟢 Listening...", "#2ecc71")
        self.voice_indicator.set_state("listening")

    def stop_assistant(self):
        self.listening = False
        if self.thread:
            self.thread.stop()
            self.thread.quit()
            self.thread.wait()
        
        self.animate_status_change("🟡 Idle", "#f39c12")
        self.voice_indicator.set_state("idle")

    def set_listening_state(self, listening):
        if listening:
            self.voice_indicator.set_state("listening")
        else:
            self.voice_indicator.set_state("idle")

    def set_thinking_state(self, thinking):
        if thinking:
            self.voice_indicator.set_state("thinking")
        else:
            self.voice_indicator.set_state("listening")

    def animate_status_change(self, text, color):
        animation = QPropertyAnimation(self.status_label, b"styleSheet")
        animation.setDuration(500)
        animation.setStartValue(self.status_label.styleSheet())
        animation.setEndValue(f"color: {color};")
        animation.start()
        self.status_label.setText(text)

    def display_message(self, text, sender="user"):
        bubble = ChatBubble(text, sender)
        self.chat_area.insertWidget(self.chat_area.count() - 1, bubble)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())