from typing import List
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self):
        load_dotenv()
        
        # Load API configuration from environment
        self.api_type = os.getenv('LLM_API_TYPE', 'openrouter')  # default to openrouter if not specified
        
        if self.api_type == 'openrouter':
            self.api_key = os.getenv('OPENROUTER_API_KEY')
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "Content-Type": "application/json"
            }
            self.model = "anthropic/claude-3.5-sonnet"
        else:  # local API
            self.api_key = os.getenv('LOCAL_API_KEY')
            self.api_url = os.getenv('LOCAL_API_URL', 'http://localhost:1234/v1/chat/completions')
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.model = os.getenv('LOCAL_MODEL_NAME', 'local-model')
        
        if not self.api_key:
            raise ValueError(f"API key not found for {self.api_type}")
        
    def _make_api_call(self, messages: List[dict]) -> str:
        """Make API call with appropriate formatting for the selected API."""
        data = {
            "model": self.model,
            "messages": messages
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"API error: {e}")
            raise
        
    def classify_sources(self, query: str, context: str) -> List[str]:
        """Determine which data sources are relevant to the query."""
        prompt = f"""Given the following user query and conversation context, 
        determine which data sources are needed to answer the query.
        Reply with only a Python list of strings, choosing from: 'calendar', 'tasks', 'email'.
        
        Context:
        {context}
        
        Query: {query}
        
        Required sources:"""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that determines which data sources are needed to answer queries."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._make_api_call(messages)
            sources = eval(response)
            valid_sources = ['calendar', 'tasks', 'email']
            return [s for s in sources if s in valid_sources]
        except Exception as e:
            print(f"API error: {e}")
            return ['calendar', 'tasks', 'email']
    
    def get_response(self, query: str, context: str) -> str:
        """Generate a response to the user's query using the provided context."""
        current_time = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
    
        prompt = f"""Using the following context and conversation history, 
        provide a helpful response to the user's query.
        
        Current Time: {current_time}
        
        Context:
        {context}
        
        Query: {query}"""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant named Jarvis with read-only access to the user's calendar, tasks, and email."},
            {"role": "user", "content": prompt}
        ]
        
        
        try:
            return self._make_api_call(messages)
        except Exception as e:
            print(f"API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
