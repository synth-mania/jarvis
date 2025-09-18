import os
import asyncio
from .core import Agent, GoogleCalendarSource, GoogleTasksSource, GmailSource
from dotenv import load_dotenv

async def run_agent(enabled_sources):
    # await Agent([GoogleCalendarSource, GoogleTasksSource, GmailSource]).run()
    await Agent(enabled_sources).run()

def main():
    load_dotenv()

    print("Welcome to your personal assistant! (Type 'quit' to exit)\n")
    
    enabled_sources = []

    if os.getenv("USE_GMAIL")=="enabled":
        print("Using gmail")
        enabled_sources.append(GmailSource)

    if os.getenv("USE_CALENDAR")=="enabled":
        print("Using calendar")
        enabled_sources.append(GoogleCalendarSource)

    if os.getenv("USE_TASKS")=="enabled":
        print("Using tasks")
        enabled_sources.append(GoogleTasksSource)
        
    try:
        asyncio.run(run_agent(enabled_sources))
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
