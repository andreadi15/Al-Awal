

class SessionManager:   
    _instance = None
    _data = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance
    
    def set(self, key, value):
        """Save data to session"""
        self._data[key] = value
    
    def get(self, key, default=None):
        """Get data from session"""
        return self._data.get(key, default)
    
    def clear(self, key=None):
        """Clear specific key or all data"""
        if key:
            self._data.pop(key, None)
        else:
            self._data.clear()
    
    def has(self, key):
        """Check if key exists"""
        return key in self._data

session = SessionManager()