import json
import logging
from pathlib import Path

try:
    from google.adk.sessions import InMemorySessionService
except ImportError:
    InMemorySessionService = None

logger = logging.getLogger(__name__)


class PersistentInMemorySessionService(InMemorySessionService):
    """In-memory session service with disk persistence."""

    def __init__(self, store_path: Path, app_name: str):
        super().__init__()
        self.store_path = store_path
        self.app_name = app_name
        self._load()

    def _load(self):
        if not self.store_path.exists():
            return
        try:
            data = json.loads(self.store_path.read_text(encoding="utf-8"))
            for record in data:
                if record.get("app_name") != self.app_name:
                    continue
                user_id = record.get("user_id")
                session_id = record.get("session_id")
                state = record.get("state")
                if user_id and session_id:
                    try:
                        self.create_session_sync(
                            app_name=self.app_name,
                            user_id=user_id,
                            session_id=session_id,
                            state=state,
                        )
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Failed to load sessions: {e}")

    def _persist(self):
        try:
            self.store_path.parent.mkdir(parents=True, exist_ok=True)
            records = []
            for sess in self.list_sessions_sync(app_name=self.app_name):
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


def make_session_service(store_path: Path, app_name: str):
    """
    Create the default session service (persistent in-memory).
    Swap this for another backend (Redis/Firestore) if needed.
    """
    if not InMemorySessionService:
        raise ImportError("google.adk.sessions not available")
    return PersistentInMemorySessionService(store_path, app_name)

