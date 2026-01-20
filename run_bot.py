import logging
from adk_agent.config import load_settings
from adk_agent.webex_bot import run_webex_bot


def main():
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    run_webex_bot(settings)


if __name__ == "__main__":
    main()
