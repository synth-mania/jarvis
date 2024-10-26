from datetime import datetime

from datetime import datetime
from typing import Any, Optional

class BaseDataSource:
    """Base class for all data sources (Calendar, Email, Tasks)."""
    
    def __init__(self):
        self.last_updated: Optional[datetime] = None
        
    def get_data(self) -> str:
        """
        Fetch and format data from the source.
        Returns formatted string representation of the data.
        """
        data = self._fetch_data()
        self.last_updated = datetime.now()
        return self._format_data(data)
    
    def _fetch_data(self) -> Any:
        """
        Fetch raw data from the source.
        Must be implemented by child classes.
        """
        raise NotImplementedError
    
    def _format_data(self, data: Any) -> str:
        """
        Format raw data into a readable string.
        Can be overridden by child classes.
        """
        return str(data)
