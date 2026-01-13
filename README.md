# Webex Python Integration

Repositorio para seguimiento de integracion entre el SDK de Webex en Python y un agente basico usando Google ADK.

This project demonstrates three steps:
1) User token + Webex Python SDK.
2) Bot token + Webex Python SDK.
3) Webex bot integration with a basic Google ADK agent.

## Prerequisites

- Python 3.x
- Webex Account (for User Token)
- Webex Bot (for Bot Token)

## Installation

```bash
pip install -r requirements.txt
```

## Scripts

### 1. `webex_test.py` (Paso 1)
Tests basic API connectivity using a **User Access Token** (SDK).
- Lists recent rooms.
- Creates a demo room.
- Sends a message to the room.

### 2. `bot_test.py` (Paso 2)
Tests Bot capability to send a Direct Message (SDK).
- Requires `WEBEX_BOT_TOKEN`.
- Sends a DM to a specific user email.

### 3. `bot_server.py` (Paso 2)
Runs an interactive Bot server using **Polling** (SDK).
- Listens for messages in rooms the bot is in (Direct or Group).
- Replies automatically to users.
- Prints verbose logs to the console.

### 4. `adk_integration.py` (Paso 3)
Prototype that sends user input to a Google ADK agent and prints the response.
- Uses `google.adk` Agent + Runner.
- Includes a simple tool example (`get_server_status`).
- Intended to later send responses back to Webex (optional, commented).

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