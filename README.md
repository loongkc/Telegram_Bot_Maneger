# Telegram Bot Manager

这是一个用于管理多个 Telegram Bot 聊天窗口的 Python 应用。允许用户创建多个 Telegram 聊天窗口，用户可以通过输入 Telegram Bot 的 API Token 和 Chat ID 来创建新的聊天窗口。每个聊天窗口会显示消息并支持发送文本消息和文件。

## 功能

- **多聊天窗口管理**：支持多聊天窗口管理，用户可以同时查看并与多个 Telegram 聊天互动。
- **实时接收消息**：自动监听 Telegram 的消息，并显示在聊天窗口中。
- **发送消息**：用户可以向指定的 Telegram 聊天窗口发送文字消息。
- **发送文件**：用户可以选择文件并将其发送到指定的 Telegram 聊天窗口。
- **现代化界面**：全新的现代化界面设计，主题跟随系统。
- **动态按钮效果**：按钮在鼠标悬停时具有动态放大效果，提升交互感。

## 获取 Bot API Token 和 Chat ID
### Bot API Toke
- 在 Telegram 中找到 BotFather（可以在搜索框中输入 @BotFather）。
- 发送 /newbot 命令，按照指示为您的新 Bot 命名并设置用户名。
- 创建完成后，BotFather 会给您发送一条消息，其中包含您的 Bot 的 API Token。

### Chat ID
- 访问 https://api.telegram.org/bot{Bot的API}/getUpdates
- 发送一条消息给您的 Bot，Bot 将返回您的用户 ID。

## 安装依赖

需要 Python 3.x 环境，并确保你已经安装了以下 Python 库：

- `requests`
- `customtkinter`
- `CTkMessagebox`

你可以通过以下命令安装这些依赖：

```bash
pip install requests customtkinter CTkMessagebox
```

## 使用方法
### 下载release版本或运行TGBotManager.py 
#### 下载地址
[下载 v1.0.0 版本]([https://github.com/loongkc/Telegram_Bot_Maneger/releases/download/v1.0.0/TGBotManager.exe)

- 创建聊天窗口：
打开应用后，在侧边栏点击 New Chat 按钮，输入 Bot API Token 和 Chat ID。
点击 Create Chat Window 按钮创建新的聊天窗口。
- 发送消息：
在聊天窗口的输入框中输入消息，点击 Send 按钮发送消息。
- 发送文件：
点击 Send File 按钮选择一个文件，文件将会被发送到聊天窗口。
- 查看聊天记录：
每个聊天窗口会显示来自 Telegram Bot 和其他用户的消息。

## 代码结构
- TelegramChatWindow: 管理聊天窗口的主要界面，显示消息、发送消息和文件。
- ListenerThread: 后台线程用于监听 Telegram Bot 发来的新消息。
- MainWindow: 主界面，包含侧边栏和显示区域，用于管理多个聊天窗口。

## 开源协议
该项目采用 MIT License 进行开源。

## 联系方式
如果有任何问题或建议，欢迎通过 GitHub Issues 联系我。
