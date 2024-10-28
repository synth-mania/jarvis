import asyncio
from datetime import datetime, time
from .llm_interface import LLMInterface
from .data_sources import (
    GoogleCalendarSource,
    GoogleTasksSource,
    GmailSource
)
import subprocess

def say(string:str):
    # print(string)
    command = ["flite", "-voice", "rms", "-t", string]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        # print("Command executed successfully")
        # print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the command")
        print("Error:", e.stderr)

class DataSourceManager:
    def __init__(self):
        self.sources = {
            'calendar': GoogleCalendarSource(),
            'tasks': GoogleTasksSource(),
            'email': GmailSource(),
        }
    
    def get_context(self, source_list):
        context = ""
        for source in source_list:
            if source in self.sources:
                context += self.sources[source].get_data()
        return context


class ConversationHistory:
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history
    
    def add_interaction(self, user_input, llm_response):
        self.history.append({
            'user': user_input,
            'assistant': llm_response,
            'timestamp': datetime.now()
        })
        # Keep only recent history to manage context length
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self):
        return "\n".join([
            f"User: {interaction['user']}\nAssistant: {interaction['assistant']}"
            for interaction in self.history
        ])


class ProactiveTriggers:
    def __init__(self, main_program):
        self.main_program = main_program
        self.triggers = [
            {
                'name': 'morning_briefing',
                'condition': lambda: self._is_time(time(8, 30)),  # 8:30 AM
                'prompt': "Generate a morning briefing. Consider: current time, today's calendar events, urgent emails, and outstanding tasks. Make it friendly and motivational.",
                'sources': ['calendar', 'tasks', 'email']
            },
            {
                'name': 'helpful_prompt',
                'condition': lambda: self._user_needs_message(),
                'prompt': "Based on what you know about what the user is doing right now, and their calendar, email, and tasks, write a helpful message to them.",
                'sources': ['calendar', 'tasks', 'email']
            }
            # Add more triggers here
        ]

    def _is_time(self, target_time: time, tolerance_minutes: int = 0) -> bool:
        now = datetime.now().time()
        target_minutes = target_time.hour * 60 + target_time.minute
        current_minutes = now.hour * 60 + now.minute
        diff = abs(current_minutes - target_minutes)
        # print(f"Time check: Current {now}, Target {target_time}, Diff {diff} minutes")  # Debug
        return diff <= tolerance_minutes
    
    def _user_needs_message(self):
        initial_response = self.main_program.process_query(
            "Based on what you know about what the user is doing right now, and their calendar, email, and tasks, is there anything helpful you should say to them? Respond starting only with 'yes' or 'no'. Every message costs a little money, so if you (Jarvis) have recently given the user feedback, consider not sending anything. However, if something comes up, like a new email or task, that might justify a new message to the user, you should remind them of this."
        )
        initial_response = initial_response.strip().lower()
        if initial_response.startswith("yes"):
            return True
        return False


    async def check_triggers(self):
        while True:
            # print(f"Checking triggers at {datetime.now().strftime('%H:%M')}")  # Debug
            for trigger in self.triggers:
                if trigger['condition']():
                    # print(f"Trigger '{trigger['name']}' activated!")  # Debug
                    response = self.main_program.process_query(trigger['prompt'])
                    print(f"\nJarvis: {response}\n\nYou: ")
                    say(response)
                else:
                    # print(f"Trigger '{trigger['name']}' condition not met")  # Debug
                    pass
            await asyncio.sleep(60)


class MainProgram:
    def __init__(self):
        self.llm_interface = LLMInterface()
        self.data_manager = DataSourceManager()
        self.conversation = ConversationHistory()
        self.proactive = ProactiveTriggers(self)
        
    def process_query(self, user_input: str):
        # Existing process_query implementation...
        chat_context = self.conversation.get_context()
        sources = self.llm_interface.classify_sources(user_input, chat_context)
        
        data_context = self.data_manager.get_context(sources)
        
        full_context = f"""
Conversation History:
{chat_context}

Current Data from Sources:
{data_context}
"""
        
        final_response = self.llm_interface.get_response(user_input, full_context)
        self.conversation.add_interaction(user_input, final_response)
        return final_response

    async def run(self):
        """Run both interactive and proactive features concurrently"""
        # print("Starting proactive system...")
        
        async def input_loop():
            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input, "\nYou: "
                )
                if user_input.lower() == 'quit':
                    return
                response = self.process_query(user_input)
                print(f"Jarvis: {response}")
                say(response)

        # Run both tasks concurrently
        try:
            input_task = asyncio.create_task(input_loop())
            trigger_task = asyncio.create_task(self.proactive.check_triggers())
            
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [input_task, trigger_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                
        except asyncio.CancelledError:
            pass


def main():
    """New entry point function"""
    program = MainProgram()
    asyncio.run(program.run())

if __name__ == "__main__":
    main()