"""
data_sources package provides integrations with Google Calendar, Tasks, and Gmail APIs.
Requires proper Google OAuth2 credentials to function.
"""


# Import the classes we want to make available when importing the package
from .data_source import DataSource
from .calendar_source import GoogleCalendarSource
from .tasks_source import GoogleTasksSource
from .email_source import GmailSource

# This allows you to do: from data_sources import GoogleCalendarSource
# Instead of: from data_sources.calendar_source import GoogleCalendarSource
