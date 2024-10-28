from .data_source import DataSource
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from email.utils import parsedate_to_datetime

class GmailSource(DataSource):
    def __init__(self):
        super().__init__()
        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/tasks.readonly'
        ]
        self.max_emails = 20  # Only fetch last 20 emails for context (used to be 5)
        self.service = self._initialize_service()
    
    def _initialize_service(self):
        """Initialize and return the Gmail service."""
        # Token file stores the user's access and refresh tokens
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token_gmail.pickle')
        credentials_path = os.path.join(current_dir, 'credentials.json')

        creds = None
        # Load existing credentials if available
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no valid credentials available, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        "credentials.json not found. Download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def _parse_email_message(self, message) -> Dict:
        """Parse Gmail message into a more usable format."""
        try:
            payload = message['payload']
            headers = payload.get('headers', [])
            
            # Extract basic info from headers
            email_data = {
                'id': message['id'],
                'from': next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown'),
                'subject': next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject'),
                'date': next((h['value'] for h in headers if h['name'].lower() == 'date'), None),
                'snippet': message.get('snippet', '')
            }
            
            # # Convert date string to datetime
            # if email_data['date']:
            #     try:
            #         email_data['date'] = parsedate_to_datetime(email_data['date'])
            #     except Exception:
            #         email_data['date'] = datetime.now()
            
            
             # Convert date string to timezone-aware datetime
            if email_data['date']:
                try:
                    # parsedate_to_datetime already returns timezone-aware datetime
                    email_data['date'] = parsedate_to_datetime(email_data['date'])
                except Exception:
                    # Ensure fallback datetime is timezone-aware
                    email_data['date'] = datetime.now(timezone.utc)
            else:
                # Ensure default datetime is timezone-aware
                email_data['date'] = datetime.now(timezone.utc)
            
            return email_data
            
        except Exception as e:
            print(f"Error parsing email message: {e}")
            return {
                'from': 'Error parsing email',
                'subject': 'Parse error',
                'date': datetime.now(timezone.utc),
                'snippet': 'Error occurred while parsing this email'
            }
    
    def _fetch_data(self) -> List[Dict]:
        """Fetch emails from Gmail API."""
        try:
            # Get list of recent messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=self.max_emails,
                q='in:inbox is:unread'
            ).execute()
            
            messages = results.get('messages', [])
            detailed_messages = []
            
            # Get detailed information for each message
            for msg in messages:
                message_detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                
                parsed_message = self._parse_email_message(message_detail)
                detailed_messages.append(parsed_message)
            
            # Sort by date, newest first
            # detailed_messages.sort(
            #     key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.now(timezone.utc),
            #     reverse=True
            # )
            def get_aware_date(msg):
                date = msg['date']
                if isinstance(date, datetime):
                    if date.tzinfo is None:  # if naive
                        return date.replace(tzinfo=timezone.utc)  # make it UTC aware
                    return date
                return datetime.now(timezone.utc)
            
            detailed_messages.sort(
                key=get_aware_date,
                reverse=True
            )

            
            return detailed_messages
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def _format_data(self, emails: List[Dict]) -> str:
        if not emails:
            return "No recent emails found."
        
        formatted = "Recent Unread Emails:\n"
        for email in emails:
            date_str = email['date'].strftime("%Y-%m-%d %H:%M") if isinstance(email['date'], datetime) else 'Unknown date'
            formatted += f"- From: {email['from']}\n"
            formatted += f"  Subject: {email['subject']}\n"
            formatted += f"  Date: {date_str}\n"
            formatted += f"  Preview: {email['snippet']}\n\n"
        
        return formatted

    def get_unread_count(self) -> int:
        """Get count of unread emails."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='in:inbox is:unread'
            ).execute()
            return len(results.get('messages', []))
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0

    def get_recent_from(self, sender: str) -> List[Dict]:
        """Get recent emails from a specific sender."""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=f'from:{sender}'
            ).execute()
            
            messages = results.get('messages', [])[:self.max_emails]
            detailed_messages = []
            
            for msg in messages:
                message_detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id']
                ).execute()
                parsed_message = self._parse_email_message(message_detail)
                detailed_messages.append(parsed_message)
                
            return detailed_messages
            
        except Exception as e:
            print(f"Error fetching emails from {sender}: {e}")
            return []
