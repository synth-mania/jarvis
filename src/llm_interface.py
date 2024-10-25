import os
import requests
from typing import Optional, List
from datetime import datetime

class LLMInterface:
    def __init__(self, api_key: Optional[str] = None, model: str = "anthropic/claude-2"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided. Set OPENROUTER_API_KEY environment variable or pass api_key to constructor.")
        self.model = model
        self.api_base = "https://openrouter.ai/api/v1"
        
    def classify_sources(self, user_input: str, chat_context: str = "") -> List[str]:
        classification_prompt = f"""
        Given the following user query and conversation context, determine which data sources would be relevant.
        Available sources: calendar, tasks, email

        IMPORTANT: Your response must follow this EXACT format:
        SOURCES: source1,source2
        REASONING: Your explanation here
        
        If no sources are needed, respond with:
        SOURCES: none
        REASONING: Your explanation here

        Examples:
        SOURCES: calendar,tasks
        REASONING: Query involves both schedule and todo items

        SOURCES: none
        REASONING: Query doesn't require any external data

        SOURCES: email
        REASONING: Query only requires email content

        Conversation context:
        {chat_context}

        User query: {user_input}

        Provide your response in the specified format:
        """
        
        response = self._call_api(classification_prompt)
        
        try:
            lines = response.strip().split('\n')
            sources_line = next(line for line in lines if line.startswith('SOURCES:'))
            sources = sources_line.replace('SOURCES:', '').strip()
            
            if sources.lower() == 'none':
                return []
                
            return [s.strip() for s in sources.split(',') if s.strip()]
            
        except Exception as e:
            print(f"Error parsing LLM response: {response}")
            print(f"Error details: {e}")
            return []
    
    def get_response(self, user_input: str, context: str) -> str:
        response_prompt = f"""
        Context information:
        {context}

        User query: {user_input}

        Provide a helpful response using the context provided above.
        """
        
        return self._call_api(response_prompt)
    
    def _call_api(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",  # Required by OpenRouter
            "X-Title": "Jarvis Assistant",  # Optional, but good practice
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()  # Raise exception for bad status codes
            
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.RequestException as e:
            print(f"API call error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return "I apologize, but I encountered an error processing your request."
        except Exception as e:
            print(f"Unexpected error: {e}")
            return "I apologize, but an unexpected error occurred."

