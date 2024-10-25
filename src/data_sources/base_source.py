from datetime import datetime

class BaseDataSource:
    def __init__(self):
        self.last_updated = None
        
    def get_data(self):
        data = self._fetch_data()
        self.last_updated = datetime.now()
        return self._format_data(data)
    
    def _fetch_data(self):
        raise NotImplementedError
    
    def _format_data(self, data):
        return str(data)
