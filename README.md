# TG-Chat-Manager

TG-Chat-Manager is a Telegram bot and desktop application designed for receiving and processing messages, files, and notifications, all managed through an SQLite database. The app supports various message types, including text, photos, documents, voice messages, and notifications, with full messaging capabilities through the desktop client.

## Description

The project consists of several main components:
1. **tg-server.py**: Runs a Telegram bot that receives incoming messages and files, saving them to a database.
2. **tg-client.py**: A fully functional desktop application that allows users to send and receive messages, manage files, and view notifications in real time.
3. **database.py**: A module for working with an SQLite database, creating user-specific tables, and managing message storage.

## Features

- **Message Handling**: The bot and client support text messages, photos, documents, voice messages, and audio files.
- **File Management**: Uploaded files are saved in user-specific folders, organized by message type.
- **Notifications**: Desktop notifications are displayed for new messages.
- **Full Messaging Capabilities**: The TG-Client application allows users to send messages and files, view message history, and respond to messages.
- **Database Management**: Stores messages and user data in an SQLite database, with the ability to mark messages as read and delete them.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/username/TG-Chat-Manager.git
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Configure the `config.py` file with your Telegram token and database settings.

## Usage

1. Start the server for the Telegram bot:
    ```bash
    python tg-server.py
    ```
2. Launch the client application:
    ```bash
    python tg-client.py
    ```
3. Connect the bot to your Telegram account and use the desktop client to send messages, files, and respond to incoming messages.

## Dependencies

- **telebot**: For working with the Telegram Bot API.
- **sqlite3**: For working with the SQLite database.
- **PyQt5**: For creating the desktop application and notification interface.

## Project Structure

- **tg-server.py**: Telegram bot logic.
- **tg-client.py**: Desktop application for messaging, file management, and notifications.
- **database.py**: Module for working with the database.
