from typing import List
import requests
import os
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
        
        if os.getenv("DEBUG") == "enabled":
            print(f"---\nDEBUG - API call:\n{messages}\n---\n")


        try:
            response = requests.post(self.api_url, headers=self.headers, json=data)
            response.raise_for_status()
            cleaned_response = response.json()['choices'][0]['message']['content'].strip()

            if os.getenv("DEBUG") == "enabled":
                print(f"---\nDEBUG - API response:\n{response.json()['choices'][0]['message']['content'].strip()}\n---")

            return cleaned_response
        except Exception as e:
            print(f"API error: {e}")
            raise
        
    def get_response(self, messages: list[dict]):
        try:
            return self._make_api_call(messages)
        except Exception as e:
            print(f"API error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
