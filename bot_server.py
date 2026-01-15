import os
import time
import datetime
from dotenv import load_dotenv
from webexpythonsdk import WebexAPI, ApiError

# Load environment variables from .env if present
load_dotenv()

# ADK agent integration
from adk_integration import get_agent_response, ensure_initialized

def main():
    # 1. Authentication
    bot_token = os.environ.get("WEBEX_BOT_TOKEN")
    if not bot_token:
        print("WEBEX_BOT_TOKEN environment variable not set.")
        try:
            bot_token = input("Please paste your Webex Bot Access Token: ").strip()
        except EOFError:
            return
    
    if not bot_token:
        print("No token provided. Exiting.")
        return

    api = WebexAPI(access_token=bot_token) 
    
    # Get Bot Identity
    try:
        me = api.people.me()
        bot_id = me.id
        print(f"Bot '{me.displayName}' started. (ID: ...{bot_id[-10:]})")
        print("Polling for messages (Ctrl+C to stop)...")
    except ApiError as e:
        print(f"Authentication failed: {e}")
        return

    # Initialize ADK agent (non-interactive; requires GOOGLE_API_KEY in env)
    agent_ready = ensure_initialized(non_interactive=True)
    if not agent_ready:
        print("Warning: ADK agent not initialized (set GOOGLE_API_KEY to enable agent replies).")

    # Track processed message IDs to avoid duplicates
    # Initial state: we don't know past messages, so we might want to ignore old ones 
    # or just start fresh. For simplicity, let's fetch the latest message first and ignore it/them.
    processed_message_ids = set()
    
    # Pre-fetch to establish baseline (optional, but good to avoid replying to old stuff)
    try:
        recent = api.messages.list(max=10)
        for msg in recent:
            processed_message_ids.add(msg.id)
    except Exception:
        pass

    poll_interval = 3 # seconds
    startup_utc = datetime.datetime.utcnow()

    first_run = True

    while True:
        try:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Checking messages...", end='\r')
            
            # Fetch recent messages by iterating through Rooms
            # A Bot can only see messages in rooms it's part of.
            # 1. List Rooms
            rooms = list(api.rooms.list(max=10, type='direct')) # Focus on Direct messages (1-on-1) first or 'group'
            # Note: For a general bot, we might check all rooms. For this test, let's look at recent rooms.
            
            for room in rooms:
                # 2. List messages in this room
                try:
                    room_msgs = list(api.messages.list(roomId=room.id, max=3))
                except Exception:
                    continue

                for msg in reversed(room_msgs):
                    if msg.id in processed_message_ids:
                        continue

                    # On first run, just mark existing messages as processed (avoid replying to history)
                    if first_run:
                        processed_message_ids.add(msg.id)
                        continue
                    
                    # Mark as processed
                    processed_message_ids.add(msg.id)
                    
                    # Ignore messages from self (the bot)
                    if msg.personId == bot_id:
                        continue

                    # --- New Message Found ---
                    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] New Message in {room.title}!")
                    print(f"From: {msg.personEmail}")
                    print(f"Text: {msg.text}")
                    
                    # --- Reply Logic (ADK Agent if ready, else echo) ---
                    if agent_ready:
                        user_id = msg.personId
                        session_id = f"{room.id}:{msg.personId}"
                        reply_text = get_agent_response(msg.text, user_id=user_id, session_id=session_id)
                    else:
                        reply_text = f"I received: '{msg.text}' in room '{room.title}'"

                    print(f"Replying: {reply_text}")
                    
                    # Send Reply
                    api.messages.create(roomId=room.id, text=reply_text)
                    print("Reply sent successfully.\n")

            # After first sweep, enable replies
            if first_run:
                first_run = False

            time.sleep(poll_interval)

        except ApiError as e:
            print(f"\nAPI Error: {e}")
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            time.sleep(poll_interval)

if __name__ == "__main__":
    main()
