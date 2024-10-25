from .base_source import BaseDataSource
from datetime import datetime
from typing import List, Dict

class GoogleTasksSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        # In a real implementation, you would initialize the Google Tasks API client here
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build
        # self.service = build('tasks', 'v1', credentials=credentials)
        
    def _fetch_data(self) -> List[Dict]:
        try:
            # This is where you'd make the actual API call
            # Example of what the real implementation would look like:
            # results = self.service.tasks().list(tasklist='@default').execute()
            # return results.get('items', [])
            
            # Placeholder data for demonstration
            return [
                {
                    'title': 'Complete project documentation',
                    'due': '2024-02-20',
                    'status': 'needsAction'
                },
                {
                    'title': 'Review pull requests',
                    'due': '2024-02-19',
                    'status': 'needsAction'
                }
            ]
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []
    
    def _format_data(self, tasks: List[Dict]) -> str:
        if not tasks:
            return "No tasks found."
        
        formatted = "Tasks:\n"
        for task in tasks:
            due_date = task.get('due', 'No due date')
            status = task.get('status', 'unknown')
            formatted += f"- {task['title']} (Due: {due_date}, Status: {status})\n"
        
        return formatted
