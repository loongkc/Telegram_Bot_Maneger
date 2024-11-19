import sys
import requests
import customtkinter as ctk
from datetime import datetime
from threading import Thread
import tkinter as tk
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox

class TelegramChatWindow(ctk.CTkFrame):
    def __init__(self, master, bot_token, chat_id, chat_name, bot_name, on_close_callback):
        super().__init__(master)
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.chat_name = chat_name
        self.bot_name = bot_name
        self.on_close_callback = on_close_callback
        self.last_update_id = None
        self.init_ui()
        
        # Start background thread for listening to new messages
        self.is_running = True
        self.listener_thread = Thread(target=self.listen_for_messages)
        self.listener_thread.daemon = True
        self.listener_thread.start()

    def init_ui(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Chat area (using Text widget with custom styling)
        self.chat_area = ctk.CTkTextbox(self, wrap="word", state="disabled")
        self.chat_area.grid(row=0, column=0, columnspan=3, padx=10, pady=(10, 5), sticky="nsew")

        # Input area
        self.input_area = ctk.CTkEntry(self, placeholder_text="Type a message...")
        self.input_area.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="ew")
        self.input_area.bind("<Return>", lambda event: self.send_message())

        # Send button
        self.send_button = ctk.CTkButton(
            self, 
            text="Send",
            command=self.send_message,
            width=100
        )
        self.send_button.grid(row=1, column=1, padx=5, pady=(5, 10))

        # File button
        self.file_button = ctk.CTkButton(
            self,
            text="Send File",
            command=self.choose_file,
            width=100
        )
        self.file_button.grid(row=1, column=2, padx=(5, 10), pady=(5, 10))

    def send_message(self):
        message = self.input_area.get()
        if not message:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        params = {'chat_id': self.chat_id, 'text': message}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            timestamp = int(datetime.now().timestamp())
            self.display_message(message, self.bot_name, timestamp, is_sent=True)
        else:
            CTkMessagebox(title="Error", message="Failed to send message.", icon="cancel")
        
        self.input_area.delete(0, tk.END)

    def choose_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.send_file(file_path)

    def send_file(self, file_path):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendDocument"
        with open(file_path, 'rb') as file:
            files = {'document': file}
            params = {'chat_id': self.chat_id}
            response = requests.post(url, params=params, files=files)

        if response.status_code == 200:
            timestamp = int(datetime.now().timestamp())
            self.display_message(f"[File sent]: {file_path.split('/')[-1]}", self.bot_name, timestamp, is_sent=True)
        else:
            CTkMessagebox(title="Error", message="Failed to send file.", icon="cancel")

    def display_message(self, message, sender_name, timestamp, is_sent=False):
        formatted_time = self.format_timestamp(timestamp)
        
        self.chat_area.configure(state="normal")
        
        if is_sent:
            # 右对齐（自己发送的消息）
            self.chat_area.insert(tk.END, 
                f"\n{'':>50}[{formatted_time}] {self.bot_name} (You):\n"
                f"{'':>50}{message}\n", 
                "right"
            )
        else:
            # 左对齐（对方发送的消息）
            self.chat_area.insert(tk.END, 
                f"\n[{formatted_time}] {sender_name}:\n{message}\n", 
                "left"
            )
        
        # 配置文本标签
        self.chat_area.tag_config("right", justify="right")
        self.chat_area.tag_config("left", justify="left")
        
        self.chat_area.configure(state="disabled")
        self.chat_area.see(tk.END)

    def format_timestamp(self, timestamp):
        local_time = datetime.fromtimestamp(timestamp)
        return local_time.strftime('%H:%M:%S')

    def listen_for_messages(self):
        while self.is_running:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
                if self.last_update_id:
                    url += f"?offset={self.last_update_id + 1}"
                
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    updates = response.json().get('result', [])
                    for update in updates:
                        message = update.get('message', {}).get('text', '')
                        timestamp = update.get('message', {}).get('date', 0)
                        if message:
                            self.last_update_id = update['update_id']
                            sender_name = self.get_sender_name(update)
                            # Use after() to safely update GUI from thread
                            self.after(0, self.display_message, message, sender_name, timestamp, False)
            except Exception as e:
                print(f"Error in listener thread: {e}")

    def get_sender_name(self, update):
        user = update.get('message', {}).get('from', {})
        first_name = user.get('first_name', 'Unknown')
        username = user.get('username', None)
        return f"@{username}" if username else first_name or 'Unknown'

    def stop(self):
        self.is_running = False


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Telegram Bot Manager")
        self.geometry("1000x600")
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Create sidebar
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, padx=(10,0), pady=10, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)  # 允许最后一个元素可以扩展

        # Add "New Chat" button to sidebar
        self.create_window_button = ctk.CTkButton(
            self.sidebar,
            text="New Chat",
            command=self.show_input_window
        )
        self.create_window_button.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")

        # Create main content area
        self.content_area = ctk.CTkFrame(self)
        self.content_area.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Create input window
        self.create_input_window()

        # Store chat windows and buttons
        self.chat_windows = {}
        self.chat_buttons = []

    def create_input_window(self):
        self.input_frame = ctk.CTkFrame(self.content_area)
        self.input_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Add input fields
        self.input_token = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter Bot API Token"
        )
        self.input_token.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.input_chat_id = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter Chat ID"
        )
        self.input_chat_id.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.input_create_button = ctk.CTkButton(
            self.input_frame,
            text="Create Chat Window",
            command=self.create_chat_window
        )
        self.input_create_button.grid(row=2, column=0, padx=10, pady=10)

    def show_input_window(self):
        # Hide all chat windows
        for window in self.chat_windows.values():
            window.grid_remove()
        # Show input window
        self.input_frame.grid()

    def create_chat_window(self):
        bot_token = self.input_token.get()
        chat_id = self.input_chat_id.get()

        if not bot_token or not chat_id:
            CTkMessagebox(title="Error", message="API Token and Chat ID cannot be empty!", icon="cancel")
            return

        # Get chat details
        chat_name = self.get_chat_name(bot_token, chat_id)
        bot_name = self.get_bot_name(bot_token)

        chat_window_name = f"{chat_name}"
        if chat_window_name not in self.chat_windows:
            # Create new chat window
            chat_window = TelegramChatWindow(
                self.content_area,
                bot_token,
                chat_id,
                chat_name,
                bot_name,
                on_close_callback=lambda name=chat_window_name: self.close_chat_window(name)
            )
            self.chat_windows[chat_window_name] = chat_window

            # Create chat button in sidebar with close button
            chat_button_frame = ctk.CTkFrame(self.sidebar)
            chat_button_frame.grid(row=len(self.chat_buttons) + 1, column=0, padx=5, pady=2, sticky="ew")
            
            chat_button = ctk.CTkButton(
                chat_button_frame,
                text=chat_window_name,
                command=lambda name=chat_window_name: self.show_chat_window(name)
            )
            chat_button.pack(side="left", expand=True, fill="x", padx=(0,5))
            
            close_button = ctk.CTkButton(
                chat_button_frame, 
                text="X", 
                width=30,
                command=lambda name=chat_window_name, btn_frame=chat_button_frame: 
                    self.close_chat_window(name, btn_frame)
            )
            close_button.pack(side="right")

            self.chat_buttons.append(chat_button_frame)

            # Show the new chat window
            self.show_chat_window(chat_window_name)

    def close_chat_window(self, chat_window_name, button_frame=None):
        # Stop the listener thread
        if chat_window_name in self.chat_windows:
            chat_window = self.chat_windows[chat_window_name]
            chat_window.stop()
            chat_window.destroy()
            del self.chat_windows[chat_window_name]

        # Remove the corresponding button
        if button_frame:
            button_frame.destroy()
            self.chat_buttons.remove(button_frame)

        # Show input window if no chat windows remain
        if not self.chat_windows:
            self.show_input_window()

    def show_chat_window(self, chat_window_name):
        # Hide input window
        self.input_frame.grid_remove()
        
        # Hide all chat windows
        for window in self.chat_windows.values():
            window.grid_remove()
            
        # Show selected chat window
        chat_window = self.chat_windows[chat_window_name]
        chat_window.grid(row=0, column=0, sticky="nsew")

    def get_chat_name(self, bot_token, chat_id):
        url = f"https://api.telegram.org/bot{bot_token}/getChat"
        params = {'chat_id': chat_id}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                chat_info = response.json().get('result', {})
                chat_name = chat_info.get('title', chat_info.get('first_name', 'Unknown'))
                return chat_name
        except:
            pass
        return 'Unknown Chat'

    def get_bot_name(self, bot_token):
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                bot_info = response.json().get('result', {})
                return bot_info.get('first_name', 'Unknown Bot')
        except:
            pass
        return 'Unknown Bot'


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = MainWindow()
    app.mainloop()