import asyncio
from datetime import datetime, time
from .llm_interface import LLMInterface
from .data_sources import *
import subprocess
from copy import deepcopy

def say(string:str):
    return
    for char in "#*-":
        string = string.replace(char, "")
    
    command = ["flite", "-voice", "rms", "-t", string]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("An error occurred while executing the command")
        print("Error:", e.stderr)

def get_formatted_datetime() -> str:
    """Returns current date and time in a consistent, readable format."""
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

class Conversation:
    def __init__(self, sys_msg: str, max_history=10):
        self.sys_msg = {"role": "system", "content": sys_msg}
        self.messages = []
        self.max_history = max_history
    
    def add_interaction(self, role: str, content: str):
        """
        role should either be 'assistant' or 'user'
        """
        self.messages.append(
            {"role": role, "content": content}
        )

        # Keep only recent history to manage context length
        if len(self.messages) > self.max_history:
            self.messages.pop(0)
        
        # print("\n".join(str(msg) for msg in self.messages))
    
    def get_messages(self) -> list[dict]:
        return [self.sys_msg] + self.messages

class ProactiveTriggerHandler:
    def __init__(self, agent: "Agent"):
        self.agent = agent
        self.triggers = [
            # {
            #     'name': 'morning_briefing',
            #     'condition': lambda: self._is_time(time(8, 30)),  # 8:30 AM
            #     'prompt': "Generate a concise morning briefing. Consider: current time, today's calendar events, urgent emails, and outstanding tasks. Make it friendly and motivational"
            # }
            # ,{
            #     'name': 'update',
            #     'condition': lambda: self._user_update(),
            #     'prompt': "Write a brief but helpful message updating me only on what with my calendar, email, or tasks has changed."
            # }
            # Add more triggers here
        ]

    def _is_time(self, target_time: time, tolerance_minutes: int = 0) -> bool:
        now = datetime.now().time()
        target_minutes = target_time.hour * 60 + target_time.minute
        current_minutes = now.hour * 60 + now.minute
        diff = abs(current_minutes - target_minutes)
        # print(f"Time check: Current {now}, Target {target_time}, Diff {diff} minutes")  # Debug
        return diff <= tolerance_minutes
    
    def _user_update(self):
        if len(self.agent.conversation.get_messages()) == 1:
            return True
        
        response = self.agent.process_query(
            """Based on what you know about what the I am doing right now, is there anything helpful you should say to me?
For example:
If there is a new email, calendar event, or task that neither of us have mentioned, the answer is yes.
If nothing has changed, the answer is no.
If you are not sure, the answer is no.

Respond starting only with 'yes' or 'no'. Be brief.""",
            conversation_effect=False
        )
        response = response.strip().lower()
        if response.startswith("yes"):
            return True
        return False


    async def check_triggers(self):
        while True:
            # print(f"Checking triggers at {datetime.now().strftime('%H:%M')}")  # Debug
            for trigger in self.triggers:
                if trigger['condition']():
                    # print(f"Trigger '{trigger['name']}' activated!")  # Debug
                    self.agent.process_query(trigger['prompt'])
                    print("\nYou: ", end="")
                else:
                    # print(f"Trigger '{trigger['name']}' condition not met")  # Debug
                    pass
            await asyncio.sleep(60)


class Agent:
    def __init__(self, data_sources: list[DataSource], memory = None):
        self.data_sources = [source() for source in data_sources]
        self.llm_interface = LLMInterface()
        self.conversation = Conversation(
            """You are Jarvis, a helpful AI assistant with read-only access to the user's calendar, tasks, and email.
You should use the provided data sources to give accurate and helpful responses. You can only directly remember up to 10 messages, but you have access to memory which is updated after every exchange, and persists.
When referencing information from data sources, be specific about where the information came from.
If you don't have enough information to answer completely, say so."""
        )
        self.proactive = ProactiveTriggerHandler(self)
    

    def get_context(self):
        context = "Current date/time: " + get_formatted_datetime() + "\n"
        for source in self.data_sources:
            context += source.get_data()
        return context #+ "\nYour memory:\n"+self.memory+"\n(end of memories)\n"

    def process_query(self, user_input: str, conversation_effect: bool = True, use_context: bool = True):
        
        context = ""

        if use_context:
            context += f"Current data sources:\n{self.get_context()}"

        self.conversation.add_interaction("user", context + user_input)

        messages = self.conversation.get_messages()
        response = self.llm_interface.get_response(messages)

        if conversation_effect:
            self.conversation.add_interaction("assistant", response)
            # {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
            print(f"\n{datetime.now().strftime("%H:%M:%S")} Jarvis: {response}")

        return response
    

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
                
                self.process_query(user_input)

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
    """entry point function"""
    agent = Agent([GoogleCalendarSource, GmailSource, GoogleTasksSource])
    asyncio.run(agent.run())

if __name__ == "__main__":
    main()