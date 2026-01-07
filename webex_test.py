import os
import sys
from webexpythonsdk import WebexAPI, ApiError

def main():
    # Try to get token from environment variable
    access_token = os.environ.get("WEBEX_ACCESS_TOKEN")
    
    # If not in env, ask user for input
    if not access_token:
        print("WEBEX_ACCESS_TOKEN environment variable not set.")
        try:
            access_token = input("Please paste your Webex Access Token: ").strip()
        except EOFError:
            print("Error: Could not read input. Please set WEBEX_ACCESS_TOKEN environment variable.")
            return

    if not access_token:
        print("Error: No access token provided.")
        return

    try:
        # Initialize the API
        api = WebexAPI(access_token=access_token)
        print("\nSuccessfully connected to Webex API wrapper.")

        # Test 1: Get 'me' information to verify token
        me = api.people.me()
        print(f"Authenticated as: {me.displayName} ({me.emails[0]})")

        # Test 2: List Rooms (last 5)
        print("\n--- Recent Rooms ---")
        # Note: max=5 in .list() usually controls page size, not total items yielded.
        # We manually limit the loop to 5 items.
        rooms = api.rooms.list(max=5)
        for i, room in enumerate(rooms):
            if i >= 5:
                break
            print(f"- {room.title} (ID: ...{room.id[-10:]})")

        # Test 3: Create a Room and Send Message
        print("\n--- Creating Test Room & Sending Message ---")
        demo_room = api.rooms.create(title="Python Webex Test Room")
        print(f"Created room: {demo_room.title} (ID: {demo_room.id})")

        message_text = "Hello! This is a test message from your Python script to a new group room."
        sent_message = api.messages.create(roomId=demo_room.id, text=message_text)
        
        print(f"Message sent successfully!")
        print(f"Message ID: {sent_message.id}")
        print(f"Content: {sent_message.text}")

    except ApiError as e:
        print(f"\nWebex API Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
