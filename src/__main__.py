import asyncio
from .core import Agent, GoogleCalendarSource, GoogleTasksSource, GmailSource

async def run_agent():
    await Agent([GoogleCalendarSource, GoogleTasksSource, GmailSource]).run()

def main():
    print("Welcome to your personal assistant! (Type 'quit' to exit)\n")
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
