"""
Database Package
Provides database schema, models, and management for the face recognition system.
"""

from database.schema import DatabaseSchema, initialize_database
from database.models import DatabaseManager, Person, SettingsManager, AnalyticsManager
from database.database import Database, get_database

__all__ = [
    'DatabaseSchema',
    'initialize_database',
    'DatabaseManager',
    'Person',
    'SettingsManager',
    'AnalyticsManager',
    'Database',
    'get_database'
]
