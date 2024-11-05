import asyncio
from datetime import datetime, time
from .llm_interface import LLMInterface
from .data_sources import *
import subprocess
import os

default_prompt = """You are Jarvis, a helpful AI assistant with read-only access to the user's calendar, tasks, and email.
You should use the provided data sources to give accurate and helpful responses. You can only directly remember up to 10 messages.
When referencing information from data sources, be specific about where the information came from.
If you don't have enough information to answer completely, say so."""

def clear_screen():
    if os.name == 'nt':  # For Windows
        _ = os.system('cls')
    else:  # For Unix/Linux/macOS
        _ = os.system('clear')


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
                    print("\nthinking...")
                    self.agent.process_query(trigger['prompt'])
                else:
                    # print(f"Trigger '{trigger['name']}' condition not met")  # Debug
                    pass
            await asyncio.sleep(60)


class CommandHandler:
    def __init__(self, agent: "Agent"):
        self.agent = agent

        self.flags = {
            "amnesia": False,

        }
    
        self.commands = [
            "quit",
            "clear",
            "llm-info",
            "help",
            "commands",
            "reset",
            "enable",
            "disable",
            "flags"
        ]

    def match(self, partial: str):
        matches = [command for command in self.commands if command.startswith(partial)]
        if len(matches) > 1:
            print("Possible matches: "+", ".join(matches))
            raise ValueError("Must specify a unique command name, more than one match found.")
            return
        if matches == []:
            print(f"'{partial}' identified no commands")
            return None
        if matches[0] != partial:
            print(matches[0])
        return matches[0]
    
    def run(self, command: str, args: list[str]):
        match command:
            case "clear":
                clear_screen()
            case "llm-info":
                interface = self.agent.llm_interface
                if interface is None:
                    print("No LLM interface is loaded. ")
                else:
                    print("\n".join([
                        "API_TYPE = "+interface.api_type,
                        "API_URL = "+interface.api_url,
                        "MODEL = "+interface.model
                        # ,"API_KEY omitted. Type '/print api-key' to view." # Not implemented yet
                    ]))
            case "help":
                if args == []:
                    print("\n".join([
                        "This chat interface provides several commands for convenience.",
                        "Every command begins with '/', and may take further parameters separated by spaces.",
                        "For example the '/help' command displays this body of text with general information about",
                        "command use, but '/help commandname' will display more specific information about any given command.",
                        "\nAdditionally, you need only give so many consequtive characters in the command name,",
                        "starting with the first, that the command processor can uniquely identify which command you are referring to.",
                        "For example, '/h' will also display this message."
                        "\nTo see available commands, type '/commands'"
                    ]))
                else:
                    match args[0]:
                        case "help":
                            print("Bravo. You are either creative or stupid.")
                        case "commands":
                            print("Lists all available commands.")
                        case "llm-info":
                            print("Displays metadata about the currently loaded LLM API. Will not print the API_KEY.")
                        case "clear":
                            print("Clear the terminal.")
                        case "quit":
                            print("Quit Jarvis.")
                        case "reset":
                            print("Reset Jarvis' conversation memory.")
                        case "enable" | "disable":
                            print("The enable and disable commands both take one parameter: the name of a boolean setting/flag to set.")
                            print("For example,\n'/enable amnesia' would enable the 'amnesia' flag.")
                            print("These commands are really just aliases to the 'set' command provided for convenience.")
                            print("\nFor example, '/set amnesia True' is equivalent to the example above.")
                            print("Likewise, '/set amnesia False' is equivalent to '/disable amnesia'")
                        case "set":
                            print("The 'set' command takes two parameters, a setting name, and a new value.")
            case "commands":
                print("\n".join(self.commands))
            case "reset":
                global default_prompt
                self.agent.conversation = Conversation(default_prompt)
            case "enable":
                try:
                    self.flags[args[0]] # Create a KeyError for an invalid flag
                    self.flags[args[0]] = True
                    print(f"{args[0]} enabled")
                except KeyError as e:
                    print(f"No flag '{args[0]}'")
            case "disable":
                try:
                    self.flags[args[0]] # Create a KeyError for an invalid flag
                    self.flags[args[0]] = False
                    print(f"{args[0]} disabled")
                except KeyError as e:
                    print(f"No flag '{args[0]}'")

class Agent:
    def __init__(self, data_sources: list[DataSource], memory = None):
        self.data_sources = [source() for source in data_sources]
        self.llm_interface = LLMInterface()
        global default_prompt
        self.conversation = Conversation(
            default_prompt
        )
        self.proactive = ProactiveTriggerHandler(self)
        self.command = CommandHandler(self)


    def get_context(self):
        context = "Current date/time: " + get_formatted_datetime() + "\n"
        for source in self.data_sources:
            context += source.get_data()
        return context

    def print_user_prompt(self):
        print("\n> ", end="")

    def process_query(self, user_input: str, conversation_effect: bool = True, use_context: bool = True):
        
        context = ""

        if use_context:
            context += f"Current data sources:\n{self.get_context()}"

        if conversation_effect and self.command.flags["amnesia"]:
            global default_prompt
            amnesia_convo = Conversation(default_prompt)
            amnesia_convo.add_interaction("user", context + user_input)
            messages = amnesia_convo.get_messages()
        else:
            self.conversation.add_interaction("user", context + user_input)
            messages = self.conversation.get_message()
        
        response = self.llm_interface.get_response(messages)

        if conversation_effect:
            self.conversation.add_interaction("assistant", response)
            # {datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")}
            columns, lines = os.get_terminal_size()
            print("-" * columns)
            print(f"\n{datetime.now().strftime("%H:%M:%S")} Jarvis: {response}")
            self.print_user_prompt()

        return response
    

    async def run(self):
        """Run both interactive and proactive features concurrently"""
        self.print_user_prompt()
        
        async def input_loop():

            def handle_command() -> bool:
                """
                processes the user input as a command
                returns a boolean value indicating if
                the session should end
                """
                nonlocal user_input
                user_input = user_input.split()
                command, args = user_input[0][1:].lower(), user_input[1:]

                try:
                    command = self.command.match(command)
                except ValueError as e:
                    print(e)
                    return False
                
                if command == "quit":
                    return True
                
                if command is not None:
                    self.command.run(command, args)

                return False

            while True:
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, input
                )

                if user_input.startswith("/"):
                    if handle_command():
                        return
                    self.print_user_prompt()
                else:
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
