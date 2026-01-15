import os
import asyncio
import requests
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try importing ADK
try:
    from google.adk.agents.llm_agent import Agent
    ADK_AVAILABLE = True
except ImportError:
    logger.warning("google-adk not installed. Using mock agent.")
    ADK_AVAILABLE = False

# Webex Configuration
WEBEX_ACCESS_TOKEN = os.getenv("WEBEX_ACCESS_TOKEN")
ROOM_ID = "YOUR_TEST_ROOM_ID"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
APP_NAME = "webex_helper_app"
USER_ID = "webex_user_001"
SESSION_ID = "session_test_001"
SESSION_STORE = Path(__file__).resolve().parent / "session_store.json"

STACKOVERFLOW_API = "https://api.stackexchange.com/2.3/search/advanced"
INFOBAE_RSS_CANDIDATES = [
    "https://www.infobae.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://www.infobae.com/rss",
    "https://www.infobae.com/feeds/rss/",
]


def stackoverflow_search(query: str) -> dict:
    """
    Search Stack Overflow via RSS (more reliable than the public API).
    Returns top 3 relevant posts with title/link.
    """
    try:
        import re
        rss_url = f"https://stackoverflow.com/feeds?search={requests.utils.quote(query)}"
        rss_headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebexBot/1.0)",
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        }
        # First try normal verify; on SSLError retry with verify=False
        try:
            resp = requests.get(rss_url, headers=rss_headers, timeout=8)
            resp.raise_for_status()
        except requests.exceptions.SSLError:
            resp = requests.get(rss_url, headers=rss_headers, timeout=8, verify=False)
            resp.raise_for_status()

        text = resp.text
        items = re.findall(r"<entry>(.*?)</entry>", text, flags=re.DOTALL | re.IGNORECASE)
        results = []
        for raw in items:
            title_match = re.search(r"<title>(.*?)</title>", raw, flags=re.DOTALL | re.IGNORECASE)
            link_match = re.search(r"<link[^>]*href=\"(.*?)\"[^>]*/>", raw, flags=re.DOTALL | re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else None
            link = link_match.group(1).strip() if link_match else None
            if title and link:
                results.append({"title": title, "link": link})
            if len(results) >= 3:
                break
        if results:
            return {"results": results, "source": "rss"}
    except Exception as e:
        rss_error = str(e)
    # Fallback: provide a static hint if everything fails
    fallback_results = [
        {"title": "Stack Overflow - Questions tagged 'python'", "link": "https://stackoverflow.com/questions/tagged/python"},
        {"title": "Stack Overflow - Questions tagged 'javascript'", "link": "https://stackoverflow.com/questions/tagged/javascript"},
        {"title": "Stack Overflow - Questions tagged 'c++'", "link": "https://stackoverflow.com/questions/tagged/c%2b%2b"},
        {"title": "Stack Overflow - Questions tagged 'java'", "link": "https://stackoverflow.com/questions/tagged/java"},
    ]
    return {
        "results": fallback_results,
        "source": f"fallback: {rss_error if 'rss_error' in locals() else 'unknown error'}"
    }


def infobae_headlines(topic: str | None = None, limit: int = 5) -> dict:
    """
    Fetch latest Infobae headlines (optionally filter by topic substring in title).
    """
    import re

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; WebexBot/1.0)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }

    errors = []
    for url in INFOBAE_RSS_CANDIDATES:
        try:
            resp = requests.get(url, headers=headers, timeout=8)
            resp.raise_for_status()
            text = resp.text

            items = re.findall(r"<item>(.*?)</item>", text, flags=re.DOTALL | re.IGNORECASE)
            results = []
            for raw in items:
                title_match = re.search(r"<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>", raw, flags=re.DOTALL | re.IGNORECASE)
                link_match = re.search(r"<link>(.*?)</link>", raw, flags=re.DOTALL | re.IGNORECASE)
                title = None
                if title_match:
                    title = title_match.group(1) or title_match.group(2)
                link = link_match.group(1).strip() if link_match else None
                if not title:
                    continue
                if topic and topic.lower() not in title.lower():
                    continue
                results.append({"title": title.strip(), "link": link})
                if len(results) >= limit:
                    break
            if results:
                return {"results": results, "source": url}
            # if no results, try next candidate
            continue
        except Exception as e:
            errors.append(f"{url}: {e}")
            continue

    if errors:
        return {"error": f"Infobae fetch failed. Tried: {errors}"}
    return {"message": "No Infobae headlines found for the given topic."}


# --- ADK Agent Setup ---
def create_agent():
    if not ADK_AVAILABLE:
        return None

    agent = Agent(
        model='gemini-2.0-flash-exp',
        name='webex_helper_agent',
        description="A helpful assistant integrated with Webex.",
        instruction=(
            "You are a helpful assistant for Webex users. "
            "Prefer Stack Overflow for programming questions. "
            "Use Infobae headlines for general news context when asked about news/current events. "
            "Do not combine tools unless needed."
        ),
        tools=[stackoverflow_search, infobae_headlines],
    )
    return agent


agent_instance = None

# Try importing Runner, session service and types
try:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types
    ADK_RUNNER_AVAILABLE = True
except ImportError:
    logger.warning("google.adk.runners or google.genai.types not found.")
    ADK_RUNNER_AVAILABLE = False
    InMemorySessionService = None

session_service = None
class PersistentInMemorySessionService(InMemorySessionService):
    """Minimal persistent wrapper around InMemorySessionService."""

    def __init__(self, store_path: Path):
        super().__init__()
        self.store_path = store_path
        self._load_sessions()

    def _load_sessions(self):
        if not self.store_path.exists():
            return
        try:
            data = json.loads(self.store_path.read_text(encoding="utf-8"))
            for record in data:
                app_name = record.get("app_name")
                user_id = record.get("user_id")
                session_id = record.get("session_id")
                state = record.get("state")
                if app_name and user_id and session_id:
                    try:
                        self.create_session_sync(
                            app_name=app_name,
                            user_id=user_id,
                            session_id=session_id,
                            state=state,
                        )
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Failed to load sessions from disk: {e}")

    def _persist(self):
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            records = []
            for sess in self.list_sessions_sync(app_name=APP_NAME):
                records.append(
                    {
                        "app_name": getattr(sess, "app_name", None),
                        "user_id": getattr(sess, "user_id", None),
                        "session_id": getattr(sess, "session_id", None),
                        "state": getattr(sess, "state", None),
                    }
                )
            self.store_path.write_text(json.dumps(records), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to persist sessions: {e}")

    async def create_session(self, *, app_name: str, user_id: str, state=None, session_id=None):
        sess = await super().create_session(app_name=app_name, user_id=user_id, state=state, session_id=session_id)
        self._persist()
        return sess

    def create_session_sync(self, *, app_name: str, user_id: str, state=None, session_id=None):
        sess = super().create_session_sync(app_name=app_name, user_id=user_id, state=state, session_id=session_id)
        self._persist()
        return sess

    async def delete_session(self, *, app_name: str, user_id: str, session_id: str):
        await super().delete_session(app_name=app_name, user_id=user_id, session_id=session_id)
        self._persist()

    def delete_session_sync(self, *, app_name: str, user_id: str, session_id: str):
        super().delete_session_sync(app_name=app_name, user_id=user_id, session_id=session_id)
        self._persist()

def ensure_initialized(non_interactive: bool = True) -> bool:
    """
    Ensure agent and session service are initialized.
    If non_interactive is True, does not prompt for GOOGLE_API_KEY.
    """
    global GOOGLE_API_KEY, agent_instance, session_service

    if not ADK_AVAILABLE:
        return False

    if not GOOGLE_API_KEY:
        if non_interactive:
            return False
        try:
            GOOGLE_API_KEY = input("Enter GOOGLE_API_KEY (leave blank to skip): ").strip()
        except EOFError:
            GOOGLE_API_KEY = ""
        if GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

    if not GOOGLE_API_KEY:
        return False

    if agent_instance is None:
        agent_instance = create_agent()
    if session_service is None and InMemorySessionService:
        session_service = PersistentInMemorySessionService(SESSION_STORE)
        # ensure file exists even if empty
        try:
            session_service._persist()
        except Exception:
            pass

    return agent_instance is not None and session_service is not None


async def ensure_session_async(user_id: str, session_id: str):
    """Create session if missing using async APIs (avoid deprecation warnings)."""
    existing = await session_service.get_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id
    )
    if existing is None:
        await session_service.create_session(
            app_name=APP_NAME,
            user_id=user_id,
            session_id=session_id
        )


def get_agent_response(user_message: str, *, user_id: str | None = None, session_id: str | None = None):
    """
    Sends message to ADK Agent and gets response using Runner.
    """
    if not ADK_AVAILABLE:
        return f"[MOCK] ADK not installed. Echo: {user_message}"
    
    if not ensure_initialized(non_interactive=True):
        return "[Error] Agent not initialized (check GOOGLE_API_KEY and ADK install)."
    
    if not ADK_RUNNER_AVAILABLE:
        return "[Error] Runner/GenAI types not found."

    if not session_service:
        return "[Error] Session service not initialized."

    uid = user_id or USER_ID
    sid = session_id or SESSION_ID

    async def run_agent_once():
        logger.info(f"Sending to Agent via Runner: {user_message}")
        await ensure_session_async(uid, sid)

        runner = Runner(
            agent=agent_instance,
            app_name=APP_NAME,
            session_service=session_service
        )
        content = types.Content(parts=[types.Part(text=user_message)])

        final_text = ""
        async for event in runner.run_async(
            user_id=uid,
            session_id=sid,
            new_message=content
        ):
            logger.info(f"Event received: {type(event)} - {event}")

            if hasattr(event, 'text') and event.text:
                final_text += event.text
            elif hasattr(event, 'parts'):
                for part in event.parts:
                    if hasattr(part, 'text') and part.text:
                        final_text += part.text
            elif hasattr(event, 'content') and event.content:
                try:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            final_text += part.text
                except Exception:
                    pass

        if not final_text:
            return "[Agent sent no text response, check logs]"
        return final_text

    try:
        # Create a fresh event loop per call to avoid 'Event loop is closed' warnings
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(run_agent_once())
    except Exception as e:
        logger.error(f"Error calling ADK Runner: {e}", exc_info=True)
        return f"[Error communicating with Agent]: {e}"
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            loop.close()


def send_webex_message(room_id, message):
    """
    Sends a message to a Webex room.
    """
    if not WEBEX_ACCESS_TOKEN:
        logger.warning("WEBEX_ACCESS_TOKEN not set, skipping send.")
        print(f"Would have sent to Webex: {message}")
        return

    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "roomId": room_id,
        "text": message
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("Message sent successfully to Webex.")
        return response.json()
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return None


def main():
    global GOOGLE_API_KEY

    if not ensure_initialized(non_interactive=False):
        print("Warning: Agent not initialized. Set GOOGLE_API_KEY and retry.")

    print("--- ADK-Google <-> Webex Integration Test ---")
    print(f"ADK Library Available: {ADK_AVAILABLE}")

    while True:
        user_input = input("\n[User (Type 'exit' to quit)]: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        agent_reply = get_agent_response(user_input)
        print(f"[Agent]: {agent_reply}")

        # Optional: send response back to Webex
        # if ROOM_ID != "YOUR_TEST_ROOM_ID":
        #     send_webex_message(ROOM_ID, agent_reply)


if __name__ == "__main__":
    main()
