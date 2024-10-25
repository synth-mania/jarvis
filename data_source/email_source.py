from .base_source import BaseDataSource
from datetime import datetime, timedelta
from typing import List, Dict

class GmailSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        # In a real implementation, you would initialize the Gmail API client here
        # from google.oauth2.credentials import Credentials
        # from googleapiclient.discovery import build
        # self.service = build('gmail', 'v1', credentials=credentials)
        self.max_emails = 5  # Only fetch last 5 emails for context
        
    def _fetch_data(self) -> List[Dict]:
        try:
            # This is where you'd make the actual API call
            # Example of what the real implementation would look like:
            # results = self.service.users().messages().list(
            #     userId='me',
            #     maxResults=self.max_emails,
            #     q='in:inbox is:unread'
            # ).execute()
            # messages = results.get('messages', [])
            # detailed_messages = []
            # for msg in messages:
            #     message_detail = self.service.users().messages().get(
            #         userId='me',
            #         id=msg['id']
            #     ).execute()
            #     detailed_messages.append(message_detail)
            # return detailed_messages
            
            # Placeholder data for demonstration
            return [
                {
                    'from': 'john.doe@example.com',
                    'subject': 'Project Update Meeting',
                    'date': datetime.now() - timedelta(hours=2),
                    'snippet': 'Let\'s discuss the progress on...'
                },
                {
                    'from': 'team@company.com',
                    'subject': 'Weekly Newsletter',
                    'date': datetime.now() - timedelta(hours=5),
                    'snippet': 'Here are this week\'s updates...'
                }
            ]
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _format_data(self, emails: List[Dict]) -> str:
        if not emails:
            return "No recent emails found."
        
        formatted = "Recent Emails:\n"
        for email in emails:
            date_str = email['date'].strftime("%Y-%m-%d %H:%M")
            formatted += f"- From: {email['from']}\n"
            formatted += f"  Subject: {email['subject']}\n"
            formatted += f"  Date: {date_str}\n"
            formatted += f"  Preview: {email['snippet']}\n\n"
        
        return formatted

    def get_data(self) -> str:
        """
        Override the base get_data method to add specific email filtering
        or processing logic if needed
        """
        emails = self._fetch_data()
        # Could add additional filtering or processing here
        return self._format_data(emails)
