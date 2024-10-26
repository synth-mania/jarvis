from typing import List
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",  # Your site URL
            "Content-Type": "application/json"
        }
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
    def classify_sources(self, query: str, context: str) -> List[str]:
        """Determine which data sources are relevant to the query."""
        prompt = f"""Given the following user query and conversation context, 
        determine which data sources are needed to answer the query.
        Reply with only a Python list of strings, choosing from: 'calendar', 'tasks', 'email'.
        
        Context:
        {context}
        
        Query: {query}
        
        Required sources:"""
        
        data = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that determines which data sources are needed to answer queries."},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            sources = eval(response.json()['choices'][0]['message']['content'].strip())
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
        
        data = {
            "model": "anthropic/claude-3.5-sonnet",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant named Jarvis with read-only access to the user's calendar, tasks, and email."},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
