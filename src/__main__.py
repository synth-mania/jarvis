import sys
from .core import MainProgram

def main():
    program = MainProgram()
    
    print("Welcome to your personal assistant! (Type 'quit' to exit)")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break
                
            if not user_input:
                continue
                
            response = program.process_query(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            continue

if __name__ == "__main__":
    main()
