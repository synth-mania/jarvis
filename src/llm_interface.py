class LLMInterface:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        
    def classify_sources(self, user_input, chat_context=""):
        # Prompt to determine which sources are relevant
        classification_prompt = f"""
        Given the following user query and conversation context, determine which data sources would be relevant.
        Available sources: calendar, tasks, email
        
        Conversation context:
        {chat_context}
        
        User query: {user_input}
        
        Return only a comma-separated list of relevant sources, or 'none' if no sources are needed.
        """
        
        # Call LLM API and parse response
        response = self._call_api(classification_prompt)
        # Split response into list and clean whitespace
        sources = [s.strip() for s in response.lower().split(',')]
        return sources if 'none' not in sources else []
    
    def get_response(self, user_input, context):
        # Prompt for final response including context
        response_prompt = f"""
        Context information:
        {context}
        
        User query: {user_input}
        
        Provide a helpful response using the context provided above.
        """
        
        return self._call_api(response_prompt)
    
    def _call_api(self, prompt):
        # Implement your specific LLM API call here
        # This is a placeholder for OpenAI-style API
        try:
            # Your API implementation here
            pass
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return "I apologize, but I encountered an error processing your request."
