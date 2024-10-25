from datetime import datetime
from llm_interface import LLMInterface
from data_sources import (
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

class MainProgram:
    def __init__(self):
        self.llm_interface = LLMInterface()
        self.data_manager = DataSourceManager()
        self.conversation = ConversationHistory()
    
    def process_query(self, user_input):
        # Include conversation history in source classification
        chat_context = self.conversation.get_context()
        sources = self.llm_interface.classify_sources(user_input, chat_context)
        
        # Gather context from identified sources
        data_context = self.data_manager.get_context(sources)
        
        # Combine all context
        full_context = f"{chat_context}\n{data_context}"
        
        # Get LLM response with full context
        final_response = self.llm_interface.get_response(user_input, full_context)
        
        # Save interaction to history
        self.conversation.add_interaction(user_input, final_response)
        
        return final_response
