"""
Main Database Interface for Face Recognition System
Provides a unified interface for all database operations.
"""

from database.models import DatabaseManager, Person, SettingsManager, AnalyticsManager
from database.schema import DatabaseSchema, initialize_database


class Database:
    """Unified database interface for the face recognition system."""
    
    def __init__(self, db_path: str = "data/database/face_recognition.db"):
        self.db_path = db_path
        self.schema = DatabaseSchema(db_path)
        self.person_manager = DatabaseManager(db_path)
        self.settings_manager = SettingsManager(db_path)
        self.analytics_manager = AnalyticsManager(db_path)
    
    def initialize(self) -> None:
        """Initialize the database with schema."""
        self.schema.create_schema()
    
    def get_person_manager(self) -> DatabaseManager:
        """Get the person manager."""
        return self.person_manager
    
    def get_settings_manager(self) -> SettingsManager:
        """Get the settings manager."""
        return self.settings_manager
    
    def get_analytics_manager(self) -> AnalyticsManager:
        """Get the analytics manager."""
        return self.analytics_manager


# Global database instance
_database_instance = None


def get_database(db_path: str = "data/database/face_recognition.db") -> Database:
    """Get the global database instance."""
    global _database_instance
    if _database_instance is None:
        _database_instance = Database(db_path)
        _database_instance.initialize()
    return _database_instance


if __name__ == "__main__":
    # Test the database interface
    db = get_database()
    
    # Test person operations
    person_manager = db.get_person_manager()
    stats = person_manager.get_statistics()
    print(f"Database statistics: {stats}")
    
    # Test settings
    settings_manager = db.get_settings_manager()
    all_settings = settings_manager.get_all_settings()
    print(f"Current settings: {all_settings}")
