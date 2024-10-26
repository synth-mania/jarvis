from .base_source import BaseDataSource
from datetime import datetime, timedelta
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

class GoogleCalendarSource(BaseDataSource):
    def __init__(self):
        super().__init__()
        self.SCOPES = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/tasks.readonly'
        ]
        self.service = self._initialize_service()
        
    def _initialize_service(self):
        """Initialize and return the Calendar service."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, 'token_calendar.pickle')
        credentials_path = os.path.join(current_dir, 'credentials.json')

        creds = None
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

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

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('calendar', 'v3', credentials=creds)

    def _fetch_data(self) -> List[Dict]:
        """Fetch upcoming calendar events."""
        try:
            # Get the start of today and end of next week
            now = datetime.utcnow()
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=14)

            # Format timestamps for Google Calendar API
            start_str = start.isoformat() + 'Z'
            end_str = end.isoformat() + 'Z'

            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_str,
                timeMax=end_str,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Process events into a consistent format
            processed_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                # Convert string timestamps to datetime objects
                if 'T' in start:  # This is a datetime
                    start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
                else:  # This is a date
                    start_time = datetime.fromisoformat(start)
                    end_time = datetime.fromisoformat(end)

                processed_events.append({
                    'summary': event.get('summary', 'Untitled Event'),
                    'start': start_time,
                    'end': end_time,
                    'location': event.get('location', ''),
                    'description': event.get('description', ''),
                    'attendees': [
                        attendee.get('email', '')
                        for attendee in event.get('attendees', [])
                    ]
                })
            
            return processed_events

        except Exception as e:
            print(f"Error fetching calendar events: {e}")
            return []

    def _format_data(self, events: List[Dict]) -> str:
        """Format calendar events into a readable string."""
        if not events:
            return "No upcoming events found."

        formatted = "Upcoming Events:\n"
        current_date = None

        for event in events:
            event_date = event['start'].date()
            
            # Add date header if this is a new date
            if current_date != event_date:
                current_date = event_date
                formatted += f"\n{event_date.strftime('%A, %B %d')}:\n"

            # Format time
            if isinstance(event['start'], datetime):
                start_time = event['start'].strftime("%I:%M %p")
                end_time = event['end'].strftime("%I:%M %p")
                time_str = f"{start_time} - {end_time}"
            else:
                time_str = "All Day"

            # Add event details
            formatted += f"  - {event['summary']} ({time_str})\n"
            
            if event['location']:
                formatted += f"    Location: {event['location']}\n"
                
            if event['attendees']:
                formatted += f"    Attendees: {', '.join(event['attendees'])}\n"
                
            if event['description']:
                desc_preview = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                formatted += f"    Description: {desc_preview}\n"

        return formatted

    def get_events_for_date(self, target_date: datetime) -> List[Dict]:
        """Get events for a specific date."""
        events = self._fetch_data()
        return [
            event for event in events 
            if event['start'].date() == target_date.date()
        ]

    def get_next_event(self) -> Dict:
        """Get the next upcoming event."""
        events = self._fetch_data()
        if not events:
            return None
        
        now = datetime.now()
        future_events = [
            event for event in events 
            if event['start'] > now
        ]
        
        return future_events[0] if future_events else None
