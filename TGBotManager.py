import sys
import requests
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QFileDialog, QStackedWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect, QPointF
from PyQt5.QtGui import QColor

from PyQt5.QtWidgets import QTextBrowser

class TelegramChatWindow(QWidget):
    def __init__(self, bot_token, chat_id, chat_name, bot_name):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.bot_name = bot_name
        self.last_update_id = None
        self.init_ui()
        self.setWindowTitle(f"{chat_name}")

        # 启动后台线程监听新消息
        self.listener_thread = ListenerThread(self.bot_token, self.chat_id, self.chat_name)
        self.listener_thread.new_message_signal.connect(self.display_message)
        self.listener_thread.start()

    def init_ui(self):
        # 设置卡片式布局
        self.setStyleSheet("""
            QWidget {
                border-radius: 10px;
                background-color: #f5f5f5;
            }
        """)

        layout = QVBoxLayout()

        # 使用 QTextBrowser 替代 QTextEdit 显示消息
        self.chat_area = QTextBrowser(self)
        self.chat_area.setOpenExternalLinks(True)
        self.chat_area.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.chat_area)

        # 输入区域
        self.input_area = QLineEdit(self)
        self.input_area.setPlaceholderText("Type a message...")
        self.input_area.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
        """)
        layout.addWidget(self.input_area)

        # 发送按钮
        self.send_button = QPushButton('Send', self)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        layout.addWidget(self.send_button)

        # 选择文件按钮
        self.file_button = QPushButton('Send File', self)
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.file_button.clicked.connect(self.choose_file)

        layout.addWidget(self.file_button)

        self.setLayout(layout)

    def send_message(self):
        message = self.input_area.text()
        if not message:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = {'chat_id': self.chat_id, 'text': message}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            timestamp = int(datetime.now().timestamp())  # 获取当前时间戳
            self.display_message(message, self.bot_name, timestamp)
        else:
            print("Failed to send message.")
        
        # 清空输入框
        self.input_area.clear()

    def choose_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File")
        if file_path:
            self.send_file(file_path)

    def send_file(self, file_path):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {'document': file}
            params = {'chat_id': self.chat_id}
            response = requests.post(url, params=params, files=files)

        if response.status_code == 200:
            self.chat_area.append(f"<div style='text-align:right; margin-bottom: 10px;'><span style='font-weight: bold;'>[File sent]:</span><br>"
                                  f"<span style='background-color: #2196F3; border-radius: 10px; padding: 10px;'>{file_path.split('/')[-1]}</span></div>")
        else:
            print("Failed to send file.")

    def display_message(self, message, sender_name, timestamp):
        formatted_time = self.format_timestamp(timestamp)

        # 判断发送者是自己（Bot）还是其他人，决定消息样式和对齐方式
        if sender_name == self.bot_name:
            sender_display = f"[You]{self.bot_name}"
            message_style = """
                background-color: #DCF8C6; 
                border-radius: 15px; 
                padding: 10px 15px; 
                max-width: 70%;
                word-wrap: break-word;
                display: inline-block;
                margin: 5px 0;
            """
            alignment = "right"  # 右对齐，自己发送的消息
        else:
            sender_display = sender_name
            message_style = """
                background-color: #E5E5E5;
                border-radius: 15px;
                padding: 10px 15px;
                max-width: 70%;
                word-wrap: break-word;
                display: inline-block;
                margin: 5px 0;
            """
            alignment = "left"  # 左对齐，其他人发送的消息

        # 生成消息的 HTML 内容
        message_html = f'<div style="text-align:{alignment}; margin-bottom: 10px;">' \
                       f'<span style="font-weight: bold;">[{formatted_time}] {sender_display}:</span><br>' \
                       f'<span style="{message_style}">{message}</span></div>'

        # 将消息添加到 QTextBrowser 中
        self.chat_area.append(message_html)

        # 确保光标始终在最新消息处
        self.chat_area.moveCursor(self.chat_area.textCursor().End)

    def format_timestamp(self, timestamp):
        # 将时间戳转换为本地时区的时间
        local_time = datetime.fromtimestamp(timestamp)  # 获取本地时间
        return local_time.strftime('%H:%M:%S')  # 格式化为时:分:秒
    
    def closeEvent(self, event):
        self.listener_thread.stop()  # 关闭时停止线程
        event.accept()


class ListenerThread(QThread):
    new_message_signal = pyqtSignal(str, str, int)  # 传递消息、发送者名称和时间戳

    def __init__(self, bot_token, chat_id, chat_name):
        super().__init__()
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.is_running = True
        self.last_update_id = None

    def run(self):
        # 持续监听新消息
        while self.is_running:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates?offset={self.last_update_id + 1 if self.last_update_id else ''}&timeout=30"
            response = requests.get(url)
            if response.status_code == 200:
                updates = response.json().get('result', [])
                for update in updates:
                    message = update.get('message', {}).get('text', '')
                    timestamp = update.get('message', {}).get('date', 0)
                    if message:
                        self.last_update_id = update['update_id']
                        sender_name = self.get_sender_name(update)
                        self.new_message_signal.emit(message, sender_name, timestamp)

    def stop(self):
        self.is_running = False
        self.quit()
        self.wait()

    def get_sender_name(self, update):
        # 获取发送者名称
        user = update.get('message', {}).get('from', {})
        first_name = user.get('first_name', 'Unknown')
        username = user.get('username', None)
        
        if username:
            return f"@{username}"
        else:
            return first_name or 'Unknown'


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telegram Bot Manager")
        self.setGeometry(100, 100, 800, 600)

        # 主程序界面布局
        self.main_layout = QHBoxLayout()

        # 侧边栏设置为固定宽度
        self.sidebar = QWidget(self)
        self.sidebar.setFixedWidth(200)
        self.main_layout.addWidget(self.sidebar)

        # 显示区域
        self.display_area = QStackedWidget(self)
        self.main_layout.addWidget(self.display_area)

        self.main_widget = QWidget(self)
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        # 侧边栏布局（标签按顺序固定间隔排列）
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        # 添加“创建窗口”标签
        self.create_window_button = QPushButton("New Chat", self.sidebar)
        self.create_window_button.clicked.connect(self.show_input_window)
        self.add_button_hover_effect(self.create_window_button)
        self.sidebar_layout.addWidget(self.create_window_button)

        # 添加间隔，避免标签过于紧凑
        self.sidebar_layout.addStretch()

        # 存储聊天窗口引用
        self.chat_windows = {}

        # 创建输入窗口
        self.input_window = QWidget()
        self.input_layout = QVBoxLayout(self.input_window)

        self.input_token = QLineEdit(self.input_window)
        self.input_token.setPlaceholderText("Enter Bot API Token")
        self.input_layout.addWidget(self.input_token)

        self.input_chat_id = QLineEdit(self.input_window)
        self.input_chat_id.setPlaceholderText("Enter Chat ID")
        self.input_layout.addWidget(self.input_chat_id)

        self.input_create_button = QPushButton("Create Chat Window", self.input_window)
        self.input_create_button.clicked.connect(self.create_chat_window)
        self.add_button_hover_effect(self.input_create_button)
        self.input_layout.addWidget(self.input_create_button)

        self.display_area.addWidget(self.input_window)

        # 用于管理侧边栏标签
        self.chat_buttons = []

    def add_button_hover_effect(self, button):
        """给按钮添加动画效果，使按钮在鼠标悬停时放大，并有颜色变化"""
        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        
        # 初始样式
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # 动画效果：按钮点击时放大
        animation.setStartValue(button.geometry())
        animation.setEndValue(button.geometry().adjusted(-5, -5, 5, 5))
        animation.start()


    def show_input_window(self):
        """显示创建新聊天窗口的输入窗口"""
        self.display_area.setCurrentWidget(self.input_window)

    def create_chat_window(self):
        bot_token = self.input_token.text()
        chat_id = self.input_chat_id.text()

        if not bot_token or not chat_id:
            print("API Token and Chat ID cannot be empty!")
            return

        # 获取聊天对象的详细信息（例如群名或用户名称）
        chat_name = self.get_chat_name(bot_token, chat_id)
        bot_name = self.get_bot_name(bot_token)

        # 创建新的聊天窗口
        chat_window_name = f"{chat_name}"
        if chat_window_name not in self.chat_windows:
            chat_window = TelegramChatWindow(bot_token, chat_id, chat_name, bot_name)
            self.chat_windows[chat_window_name] = chat_window
            self.display_area.addWidget(chat_window)

            # 创建聊天窗口按钮并添加到侧边栏
            chat_button = QPushButton(chat_window_name, self.sidebar)
            chat_button.clicked.connect(lambda: self.show_chat_window(chat_window_name))
            self.add_button_hover_effect(chat_button)
            self.sidebar_layout.addWidget(chat_button)

            # 添加间隔，避免标签过于紧凑
            self.sidebar_layout.addStretch()

            self.chat_buttons.append(chat_button)

            # 设置为当前显示窗口
            self.show_chat_window(chat_window_name)

    def show_chat_window(self, chat_window_name):
        """切换到对应的聊天窗口"""
        chat_window = self.chat_windows.get(chat_window_name)
        if chat_window:
            index = self.display_area.indexOf(chat_window)
            self.display_area.setCurrentIndex(index)

    def get_chat_name(self, bot_token, chat_id):
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {'chat_id': chat_id}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            chat_info = response.json().get('result', {})
            chat_name = chat_info.get('title', chat_info.get('first_name', 'Unknown'))
            return chat_name
        return 'Unknown Chat'

    def get_bot_name(self, bot_token):
        """获取 Bot 的名字"""
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url)
        if response.status_code == 200:
            bot_info = response.json().get('result', {})
            return bot_info.get('first_name', 'Unknown Bot')
        return 'Unknown Bot'


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
