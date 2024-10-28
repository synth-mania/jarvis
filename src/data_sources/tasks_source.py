from .data_source import DataSource
from datetime import datetime, timedelta
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

class GoogleTasksSource(DataSource):
    def __init__(self):
        super().__init__()
        self.SCOPES = [
            'https://www.googleapis.com/auth/tasks.readonly',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
        self.creds = None
        self.service = self._initialize_service()
        
    def _initialize_service(self):
        """Initialize and return the Google Tasks service."""
        """Initialize and return the Google Tasks service."""
        # Update paths to be relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token_tasks.pickle')
        credentials_path = os.path.join(current_dir, 'credentials.json')

        # Load existing credentials if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no valid credentials available, authenticate
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        "credentials.json not found. Download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return build('tasks', 'v1', credentials=self.creds)

    def _fetch_data(self) -> List[Dict]:
        """Fetch tasks from Google Tasks API."""
        try:
            # First, get all task lists
            tasklists_result = self.service.tasklists().list().execute()
            tasklists = tasklists_result.get('items', [])
            
            all_tasks = []
            
            # Get tasks from each task list
            for tasklist in tasklists:
                tasklist_id = tasklist['id']
                tasklist_title = tasklist['title']
                
                # Get tasks from this list
                tasks_result = self.service.tasks().list(
                    tasklist=tasklist_id,
                    showCompleted=True,
                    showHidden=False
                ).execute()
                
                tasks = tasks_result.get('items', [])
                
                # Add task list title to each task
                for task in tasks:
                    task['tasklistTitle'] = tasklist_title
                    
                all_tasks.extend(tasks)
            
            # Sort tasks by due date if available
            all_tasks.sort(
                key=lambda x: x.get('due', '9999-12-31'),
                reverse=False
            )
            
            return all_tasks

        except Exception as e:
            print(f"Error fetching tasks: {e}")
            return []
    

    def _format_data(self, tasks: List[Dict]) -> str:
        """Format tasks into a readable string."""
        if not tasks:
            return "No tasks found."
        
        formatted = "Tasks:\n"
        
        # Group tasks by task list
        tasks_by_list = {}
        for task in tasks:
            list_title = task.get('tasklistTitle', 'Default')
            if list_title not in tasks_by_list:
                tasks_by_list[list_title] = []
            tasks_by_list[list_title].append(task)
        
        # Format tasks by list
        for list_title, list_tasks in tasks_by_list.items():
            formatted += f"\n{list_title}:\n"
            for task in list_tasks:
                # Get task details
                title = task.get('title', 'Untitled Task')
                due_date = task.get('due', 'No due date')
                if due_date != 'No due date':
                    # Convert Google's datetime format to more readable form
                    try:
                        due_dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        due_date = due_dt.strftime('%Y-%m-%d')
                    except ValueError:
                        pass  # Keep original format if parsing fails
                
                status = task.get('status', 'unknown')
                notes = task.get('notes', '')
                
                # Format the task line
                task_line = f"  - {title}"
                if due_date != 'No due date':
                    task_line += f" (Due: {due_date})"
                if status == 'completed':
                    task_line += " ✓"
                task_line += "\n"
                
                # Add notes if they exist
                if notes:
                    task_line += f"    Notes: {notes}\n"
                
                formatted += task_line
        
        return formatted

    def get_completed_tasks(self) -> List[Dict]:
        """Get only completed tasks."""
        tasks = self._fetch_data()
        return [task for task in tasks if task.get('status') == 'completed']

    def get_pending_tasks(self) -> List[Dict]:
        """Get only pending tasks."""
        tasks = self._fetch_data()
        return [task for task in tasks if task.get('status') != 'completed']

    def get_tasks_due_soon(self, days: int = 7) -> List[Dict]:
        """Get tasks due within the specified number of days."""
        tasks = self._fetch_data()
        cutoff_date = datetime.now() + timedelta(days=days)
        
        due_soon = []
        for task in tasks:
            due_date = task.get('due')
            if due_date:
                try:
                    task_due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    if task_due <= cutoff_date and task.get('status') != 'completed':
                        due_soon.append(task)
                except ValueError:
                    continue
        
        return due_soon
