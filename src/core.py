import asyncio
from datetime import datetime
from .llm_interface import LLMInterface
from .data_sources import (
    GoogleCalendarSource,
    GoogleTasksSource,
    GmailSource
)


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
            }
            # Add more triggers here
        ]

    def _is_time(self, target_time: time, tolerance_minutes: int = 1) -> bool:
        now = datetime.now().time()
        target_minutes = target_time.hour * 60 + target_time.minute
        current_minutes = now.hour * 60 + now.minute
        return abs(current_minutes - target_minutes) <= tolerance_minutes

    async def check_triggers(self):
        while True:
            for trigger in self.triggers:
                if trigger['condition']():
                    # Use existing MainProgram methods to handle the trigger
                    response = self.main_program.process_query(trigger['prompt'])
                    print(f"\n[Jarvis Proactive]: {response}")
            await asyncio.sleep(60)


class MainProgram:
    def __init__(self):
        self.llm_interface = LLMInterface()
        self.data_manager = DataSourceManager()
        self.conversation = ConversationHistory()
    
    def process_query(self, user_input: str):
        # Use chat context for classification but keep data separate
        chat_context = self.conversation.get_context()
        sources = self.llm_interface.classify_sources(user_input, chat_context)
        
        # Get fresh data from sources
        data_context = self.data_manager.get_context(sources)
        
        # Combine contexts for the final response
        full_context = f"""
Conversation History:
{chat_context}

Current Data from Sources:
{data_context}
"""
        
        # Get LLM response
        final_response = self.llm_interface.get_response(user_input, full_context)
        
        # Save only the interaction, not the data context
        self.conversation.add_interaction(user_input, final_response)
        
        return final_response