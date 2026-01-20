import asyncio
import logging
from typing import Callable, Iterable

try:
    from google.adk.agents.llm_agent import Agent
    from google.adk.runners import Runner
    from google.genai import types
except ImportError as e:
    raise ImportError("google-adk is required for the agent module") from e

logger = logging.getLogger(__name__)


def create_agent(tools: Iterable[Callable], model: str = "gemini-2.0-flash-exp") -> Agent:
    """
    Create an ADK Agent with the provided tools.
    """
    agent = Agent(
        model=model,
        name="webex_helper_agent",
        description="A helpful assistant integrated with Webex.",
        instruction=(
            "You are a helpful assistant for Webex users. "
            "Use the available tools when helpful. "
            "Prefer Stack Overflow tool for programming questions; "
            "use Infobae tool for headlines."
        ),
        tools=list(tools),
    )
    return agent


async def _ensure_session(session_service, app_name: str, user_id: str, session_id: str):
    existing = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )
    if existing is None:
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )


def run_agent_message(
    agent: Agent,
    session_service,
    *,
    app_name: str,
    user_id: str,
    session_id: str,
    message_text: str,
) -> str:
    """
    Run the agent for a single user message and return concatenated text from events.
    """

    async def run_once():
        await _ensure_session(session_service, app_name, user_id, session_id)

        runner = Runner(
            agent=agent,
            app_name=app_name,
            session_service=session_service,
        )
        content = types.Content(parts=[types.Part(text=message_text)])

        final_text = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            logger.info(f"Event received: {type(event)} - {event}")
            if hasattr(event, "text") and event.text:
                final_text += event.text
            elif hasattr(event, "parts"):
                for part in event.parts:
                    if hasattr(part, "text") and part.text:
                        final_text += part.text
            elif hasattr(event, "content") and event.content:
                try:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            final_text += part.text
                except Exception:
                    pass

        if not final_text:
            return "[Agent sent no text response, check logs]"
        return final_text

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_once())
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            loop.close()

