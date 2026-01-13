import os

import requests
import json
import logging

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

# --- ADK Agent Setup ---
def create_agent():
    if not ADK_AVAILABLE:
        return None

    # Example tool
    def get_server_status(server_name: str) -> dict:
        """Returns the status of a specific server."""
        return {"server": server_name, "status": "running", "load": "low"}

    # Define the Agent
    # Note: Ensure GOOGLE_API_KEY is set for this to work.
    agent = Agent(
        model='gemini-2.0-flash-exp', # Check for latest available model in ADK
        name='webex_helper_agent',
        description="A helpful assistant integrated with Webex.",
        instruction="You are a helpful assistant for Webex users. Use tools to answer questions.",
        tools=[get_server_status],
    )
    return agent

agent_instance = None


# Try importing Runner and types
try:
    from google.adk.runners import Runner
    from google.genai import types
    ADK_RUNNER_AVAILABLE = True
except ImportError:
    logger.warning("google.adk.runners or google.genai.types not found.")
    ADK_RUNNER_AVAILABLE = False

def get_agent_response(user_message):
    """
    Sends message to ADK Agent and gets response using Runner.
    """
    if not ADK_AVAILABLE:
        return f"[MOCK] ADK not installed. Echo: {user_message}"
    
    if not agent_instance:
        return "[Error] Agent failed to initialize."
    
    if not ADK_RUNNER_AVAILABLE:
        return "[Error] Runner/GenAI types not found."

    logger.info(f"Sending to Agent via Runner: {user_message}")
    
    try:
        runner = Runner(agent=agent_instance)
        
        # Construct content using google.genai.types
        # Note: Adjusting structure based on standard GenAI patterns
        content = types.Content(parts=[types.Part(text=user_message)])
        
        # Invoke runner.run
        # It returns a generator of events
        response_gen = runner.run(
            user_id="webex_user_001", 
            session_id="session_test_001", 
            new_message=content
        )
        
        final_text = ""
        for event in response_gen:
            # Inspection of event structure:
            # Usually events have a type and data.
            # We will accumulate text if present, or just log for now.
            logger.info(f"Event received: {type(event)} - {event}")
            
            # Heuristic to extract text from common event types
            # If the event object has 'text' attribute directly:
            if hasattr(event, 'text') and event.text:
                final_text += event.text
            # Or if it mimics a chunk
            elif hasattr(event, 'parts'):
                 for part in event.parts:
                     if hasattr(part, 'text'):
                         final_text += part.text
        
        if not final_text:
            return "[Agent sent no text response, check logs]"
            
        return final_text

    except Exception as e:
        logger.error(f"Error calling ADK Runner: {e}", exc_info=True)
        return f"[Error communicating with Agent]: {e}"

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
    global GOOGLE_API_KEY, agent_instance

    if ADK_AVAILABLE and not GOOGLE_API_KEY:
        try:
            GOOGLE_API_KEY = input("Enter GOOGLE_API_KEY (leave blank to skip): ").strip()
        except EOFError:
            GOOGLE_API_KEY = ""
        if GOOGLE_API_KEY:
            os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

    if not GOOGLE_API_KEY and ADK_AVAILABLE:
        print("Warning: GOOGLE_API_KEY not set. ADK might fail.")

    if ADK_AVAILABLE and not agent_instance:
        agent_instance = create_agent()
    
    print("--- ADK-Google <-> Webex Integration Test ---")
    print(f"ADK Library Available: {ADK_AVAILABLE}")

    # Simulate loop
    while True:
        user_input = input("\n[User (Type 'exit' to quit)]: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # 1. Get response from Google Agent
        agent_reply = get_agent_response(user_input)
        print(f"[Agent]: {agent_reply}")
        
        # 2. Send response back to Webex (Optional for local test)
        # if ROOM_ID != "YOUR_TEST_ROOM_ID":
        #    send_webex_message(ROOM_ID, agent_reply)

if __name__ == "__main__":
    main()
