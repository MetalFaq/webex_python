import datetime
import logging
import time
from webexpythonsdk import WebexAPI, ApiError

from .agent import create_agent, run_agent_message
from .config import Settings
from .sessions import make_session_service
from .tools import build_tools

logger = logging.getLogger(__name__)


def run_webex_bot(settings: Settings, poll_interval: int = 3):
    """
    Run a simple polling Webex bot that delegates replies to the ADK agent.
    """
    api = WebexAPI(access_token=settings.webex_bot_token)
    try:
        me = api.people.me()
        bot_id = me.id
        logger.info(f"Bot '{me.displayName}' started. (ID: ...{bot_id[-10:]})")
        print(f"Bot '{me.displayName}' started. (ID: ...{bot_id[-10:]})")
        print("Polling for messages (Ctrl+C to stop)...")
    except ApiError as e:
        raise SystemExit(f"Authentication failed: {e}")

    # Init agent and session service
    tools = build_tools()
    agent = create_agent(tools)
    session_service = make_session_service(settings.session_store, settings.app_name)

    processed_message_ids = set()
    startup_time = datetime.datetime.now(datetime.timezone.utc)
    first_run = True

    while True:
        try:
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Checking messages...", end="\r")

            rooms = list(api.rooms.list(max=10, type="direct"))

            for room in rooms:
                try:
                    room_msgs = list(api.messages.list(roomId=room.id, max=5))
                except Exception:
                    continue

                for msg in reversed(room_msgs):
                    if msg.id in processed_message_ids:
                        continue

                    # Mark existing history on first sweep
                    if first_run:
                        processed_message_ids.add(msg.id)
                        continue

                    processed_message_ids.add(msg.id)

                    if msg.personId == bot_id:
                        continue

                    # Ignore messages created before startup
                    try:
                        created_at = datetime.datetime.fromisoformat(msg.created.replace("Z", "+00:00"))
                        if created_at <= startup_time:
                            continue
                    except Exception:
                        pass

                    print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] New Message in {room.title}!")
                    print(f"From: {msg.personEmail}")
                    print(f"Text: {msg.text}")

                    user_id = msg.personId
                    session_id = f"{room.id}:{msg.personId}"

                    try:
                        reply_text = run_agent_message(
                            agent,
                            session_service,
                            app_name=settings.app_name,
                            user_id=user_id,
                            session_id=session_id,
                            message_text=msg.text or "",
                        )
                    except Exception as e:
                        logger.error(f"Agent error: {e}", exc_info=True)
                        reply_text = f"[Agent error]: {e}"

                    print(f"Replying: {reply_text}")
                    api.messages.create(roomId=room.id, text=reply_text)
                    print("Reply sent successfully.\n")

            if first_run:
                first_run = False

            time.sleep(poll_interval)

        except ApiError as e:
            logger.error(f"API Error: {e}")
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            time.sleep(poll_interval)

