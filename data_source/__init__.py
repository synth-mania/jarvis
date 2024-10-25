# Import the classes we want to make available when importing the package
from .base_source import BaseDataSource
from .calendar_source import GoogleCalendarSource
from .tasks_source import GoogleTasksSource
from .email_source import GmailSource

# This allows you to do: from data_sources import GoogleCalendarSource
# Instead of: from data_sources.calendar_source import GoogleCalendarSource
