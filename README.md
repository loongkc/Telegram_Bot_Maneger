# Telegram Bot Manager

这是一个用于管理多个 Telegram 聊天窗口的 Python 应用，用户可以通过输入 Telegram Bot 的 API Token 和 Chat ID 来创建新的聊天窗口。每个聊天窗口会显示消息并支持发送文本消息和文件。

## 功能

- **多聊天窗口管理**：支持同时管理多个 Telegram 聊天窗口。
- **实时接收消息**：自动监听 Telegram Bot 发送的消息，并显示在聊天窗口中。
- **发送消息**：用户可以向指定的 Telegram 聊天窗口发送消息。
- **发送文件**：用户可以选择文件并将其发送到 Telegram 聊天窗口。
- **卡片式设计**：聊天窗口和操作按钮使用现代化的卡片式设计，提供流畅的用户体验。
- **动态按钮效果**：按钮在鼠标悬停时具有动态放大效果，提升交互感。

## 安装依赖

确保你已经安装了以下 Python 库：

- `requests`
- `PyQt5`

你可以通过以下命令安装这些依赖：

```bash
pip install requests PyQt5
```

## 使用方法
- 创建聊天窗口：
-- 打开应用后，在侧边栏点击 New Chat 按钮，输入 Bot API Token 和 Chat ID。
-- 点击 Create Chat Window 按钮创建新的聊天窗口。
- 发送消息：
-- 在聊天窗口的输入框中输入消息，点击 Send 按钮发送消息。
- 发送文件：
-- 点击 Send File 按钮选择一个文件，文件将会被发送到聊天窗口。
- 查看聊天记录：
-- 每个聊天窗口会显示来自 Telegram Bot 和其他用户的消息。

## 代码结构
- TelegramChatWindow: 管理聊天窗口的主要界面，显示消息、发送消息和文件。
- ListenerThread: 后台线程用于监听 Telegram Bot 发来的新消息。
- MainWindow: 主界面，包含侧边栏和显示区域，用于管理多个聊天窗口。

## 开源协议
该项目采用 MIT License 进行开源。

## 致谢
感谢 PyQt5 提供的 GUI 库，使得开发图形界面变得更加简单。

## 联系方式
如果有任何问题或建议，欢迎通过 GitHub Issues 联系我。
