import os
import sys
from webexpythonsdk import WebexAPI, ApiError

def main():
    # Try to get bot token from environment variable
    bot_token = os.environ.get("WEBEX_BOT_TOKEN")
    
    # If not in env, ask user for input
    if not bot_token:
        print("WEBEX_BOT_TOKEN environment variable not set.")
        try:
            bot_token = input("Please paste your Webex Bot Access Token: ").strip()
        except EOFError:
            print("Error: Could not read input. Please set WEBEX_BOT_TOKEN environment variable.")
            return

    if not bot_token:
        print("Error: No bot token provided.")
        return

    try:
        # Initialize the API
        api = WebexAPI(access_token=bot_token)
        print("\nSuccessfully connected to Webex API as Bot.")

        # Verify Bot Identity
        me = api.people.me()
        print(f"Bot Name: {me.displayName}")
        print(f"Bot Email: {me.emails[0]}")
        print(f"Bot ID: ...{me.id[-10:]}")

        # Get Target User Email for DM
        print("\n--- Direct Message Test ---")
        target_email = input("Enter the user email to send a DM to: ").strip()
        
        if not target_email:
            print("Error: No target email provided.")
            return

        message_text = f"Hello! This is a test Direct Message from your Python Bot, {me.displayName}."
        
        print(f"Sending message to {target_email}...")
        sent_message = api.messages.create(toPersonEmail=target_email, text=message_text)
        
        print(f"Direct Message sent successfully!")
        print(f"Message ID: {sent_message.id}")
        print(f"Content: {sent_message.text}")

    except ApiError as e:
        print(f"\nWebex API Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
