"""
Database Schema Definition for Face Recognition System
Defines the structure and relationships for storing face data and user information.
"""

import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseSchema:
    """Handles database schema creation and initialization."""
    
    def __init__(self, db_path: str = "data/database/face_recognition.db"):
        self.db_path = db_path
        self.ensure_database_directory()
    
    def ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def create_schema(self) -> None:
        """Create all database tables and indexes."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create persons table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    category TEXT,
                    profile_image_path TEXT,
                    face_embeddings BLOB,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Create analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persons_person_id 
                ON persons(person_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persons_full_name 
                ON persons(full_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persons_category 
                ON persons(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analytics_metric_name 
                ON analytics(metric_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analytics_timestamp 
                ON analytics(timestamp)
            """)
            
            # Insert default settings
            self._insert_default_settings(cursor)
            
            conn.commit()
    
    def _insert_default_settings(self, cursor) -> None:
        """Insert default application settings."""
        default_settings = {
            'recognition_threshold': '0.6',
            'camera_index': '0',
            'detection_frequency': '5',
            'frame_scaling': '0.5',
            'minimum_face_size': '100',
            'application_theme': 'dark',
            'fps_display': 'true',
            'unknown_face_behavior': 'alert'
        }
        
        for key, value in default_settings.items():
            cursor.execute("""
                INSERT OR IGNORE INTO settings (key, value)
                VALUES (?, ?)
            """, (key, value))
    
    def drop_all_tables(self) -> None:
        """Drop all tables (use with caution)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS analytics")
            cursor.execute("DROP TABLE IF EXISTS settings")
            cursor.execute("DROP TABLE IF EXISTS persons")
            conn.commit()
    
    def get_schema_info(self) -> dict:
        """Get information about the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            schema_info = {'tables': {}}
            
            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                schema_info['tables'][table] = [
                    {'name': col[1], 'type': col[2], 'not_null': bool(col[3]), 
                     'primary_key': bool(col[5])}
                    for col in columns
                ]
            
            return schema_info


def initialize_database(db_path: str = "data/database/face_recognition.db") -> None:
    """Initialize the database with schema."""
    schema = DatabaseSchema(db_path)
    schema.create_schema()
    print(f"Database initialized at {db_path}")


if __name__ == "__main__":
    initialize_database()
