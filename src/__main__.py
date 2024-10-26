import asyncio
from .core import MainProgram

async def run_assistant():
    program = MainProgram()
    await program.run()

def main():
    print("Welcome to your personal assistant! (Type 'quit' to exit)\n")
    try:
        asyncio.run(run_assistant())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
