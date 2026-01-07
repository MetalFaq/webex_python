# Webex Python Integration

Repositorio para seguimiento de integración entre el sdk de webex en python con agente en adk-google

This project demonstrates how to integrate Python with Webex APIs, including basic REST API usage and an interactive Bot implementation.

## Prerequisites

- Python 3.x
- Webex Account (for User Token)
- Webex Bot (for Bot Token)

## Installation

```bash
pip install -r requirements.txt
```

## Scripts

### 1. `webex_test.py`
Tests basic API connectivity using a **User Access Token**.
- Lists recent rooms.
- Creates a demo room.
- Sends a message to the room.

### 2. `bot_test.py`
Tests Bot capability to send a Direct Message.
- Requires `WEBEX_BOT_TOKEN`.
- Sends a DM to a specific user email.

### 3. `bot_server.py`
Runs an interactive Bot server using **Polling**.
- Listens for messages in rooms the bot is in (Direct or Group).
- Replies automatically to users.
- Prints verbose logs to the console.

## Usage

Set your environment variables:
```powershell
$env:WEBEX_ACCESS_TOKEN="your_user_token"
$env:WEBEX_BOT_TOKEN="your_bot_token"
```

Run a script:
```powershell
python bot_server.py
```
