from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt6.QtGui import (
    QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
)
from PyQt6.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")

# --- Bulletproof Cross-Platform Path Handling ---
GUI_FILE_PATH = os.path.abspath(__file__)
FRONTEND_DIR = os.path.dirname(GUI_FILE_PATH)
PROJECT_ROOT = os.path.dirname(FRONTEND_DIR)

TempDirPath = os.path.join(FRONTEND_DIR, "Files")
GraphicsDirPath = os.path.join(FRONTEND_DIR, "Graphics")

old_chat_message = ""


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "who", "where", "when", "why", 
        "which", "whose", "whom", "can you", "what's", "where's", "how's"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()


def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)


def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)


def SetMicrophoneStatus(Command):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(TempDirectoryPath('Mic.data'), "w", encoding='utf-8') as file:
            file.write(Command)
    except Exception:
        pass


def GetMicrophoneStatus():
    try:
        with open(TempDirectoryPath('Mic.data'), "r", encoding='utf-8') as file:
            return file.read()
    except Exception:
        return "False"


def SetAssistantStatus(Status):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
            file.write(Status)
    except Exception:
        pass


def GetAssistantStatus():
    try:
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            return file.read()
    except Exception:
        return ""


def MicButtonInitialed():
    SetMicrophoneStatus("False")
    SetAssistantStatus("Speaking...")


def MicButtonClosed():
    SetMicrophoneStatus("True")
    SetAssistantStatus("Mute...")


def ShowTextToScreen(Text):
    try:
        os.makedirs(TempDirPath, exist_ok=True)
        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(Text)
    except Exception:
        pass


class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.Shape.NoFrame)
        layout.addWidget(self.chat_text_edit)
        
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        
        text_color = QColor("blue")
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.label)
        
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(50)
        
        self.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height:20px;
            }
            
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()

                if not messages or len(messages) <= 1:
                    pass
                elif str(old_chat_message) == str(messages):
                    pass
                else:
                    self.addMessage(message=messages, color='white')
                    old_chat_message = messages
        except Exception:
            pass

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
        except Exception:
            pass

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format_char = QTextCharFormat()
        format_block = QTextBlockFormat()
        format_block.setTopMargin(10)
        format_block.setLeftMargin(10)
        format_char.setForeground(QColor(color))
        cursor.setCharFormat(format_char)
        cursor.setBlockFormat(format_block)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 10, 0, 20)
        content_layout.setSpacing(10)
        
        # 1. Top Stretch Spacer
        content_layout.addStretch(1)
        
        # 2. Enlarged Centered GIF Ring (520x520)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        movie.setScaledSize(QSize(520, 520))
        gif_label.setMovie(movie)
        gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        movie.start()
        content_layout.addWidget(gif_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 3. Status Text Label ("Speaking...", "Mute...")
        self.label = QLabel("Speaking...")
        self.label.setStyleSheet("color: white; font-size: 20px; font-weight: 500; background: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 4. Mic Icon Button
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(65, 65)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 5. Bottom Stretch Spacer
        content_layout.addStretch(1)
        
        self.setLayout(content_layout)
        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(50)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages.strip():
                    self.label.setText(messages)
        except Exception:
            pass

    def load_icon(self, path, width=50, height=50):
        if os.path.exists(path):
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(new_pixmap)
        else:
            print(f"Icon missing at: {path}")

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 50, 50)
            MicButtonInitialed()
            self.label.setText("Speaking...")
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 50, 50)
            MicButtonClosed()
            self.label.setText("Mute...")
            
        self.toggled = not self.toggled


class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")

    
class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.draggable = True
        self.offset = None
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText("  Home")
        home_button.setStyleSheet("height:35px; background-color:white; color: black; padding: 0 10px;")
        
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText("  Chat")
        message_button.setStyleSheet("height:35px; background-color:white; color: black; padding: 0 10px;")
        
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white; height:35px; width:35px;")
        minimize_button.clicked.connect(self.minimizeWindow)
        
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white; height:35px; width:35px;")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white; height:35px; width:35px;")
        close_button.clicked.connect(self.closeWindow)
        
        title_label = QLabel(f" {str(Assistantname).capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px; font-weight: bold; background-color:white; padding: 5px;")
        
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("white"))
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        QApplication.quit()
        sys.exit(0)

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPosition().toPoint() - self.offset
            self.parent().move(new_pos)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        self.resize(1280, 720)
        
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 1280) // 2
        y = (screen.height() - 720) // 2
        self.move(x, y)
        
        self.setStyleSheet("background-color: black;")

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen(self)
        message_screen = MessageScreen(self)
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        top_bar = CustomTopBar(self, stacked_widget)

        layout.addWidget(top_bar)
        layout.addWidget(stacked_widget)

        self.setCentralWidget(central_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    GraphicalUserInterface()