"""
Database Models for Face Recognition System
Provides data models and database operations for managing persons and settings.
"""

import sqlite3
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np


class Person:
    """Data model for a person in the face recognition system."""
    
    def __init__(self, person_id: str, full_name: str, email: Optional[str] = None,
                 phone: Optional[str] = None, category: Optional[str] = None,
                 profile_image_path: Optional[str] = None, 
                 face_embeddings: Optional[np.ndarray] = None,
                 registration_date: Optional[str] = None,
                 last_updated: Optional[str] = None,
                 db_id: Optional[int] = None):
        self.db_id = db_id
        self.person_id = person_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.category = category
        self.profile_image_path = profile_image_path
        self.face_embeddings = face_embeddings
        self.registration_date = registration_date or datetime.now().isoformat()
        self.last_updated = last_updated or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert person to dictionary."""
        return {
            'db_id': self.db_id,
            'person_id': self.person_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'category': self.category,
            'profile_image_path': self.profile_image_path,
            'face_embeddings': self.face_embeddings.tolist() if self.face_embeddings is not None else None,
            'registration_date': self.registration_date,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Person':
        """Create person from dictionary."""
        embeddings = None
        if data.get('face_embeddings') is not None:
            embeddings = np.array(data['face_embeddings'])
        
        return cls(
            db_id=data.get('db_id'),
            person_id=data['person_id'],
            full_name=data['full_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            category=data.get('category'),
            profile_image_path=data.get('profile_image_path'),
            face_embeddings=embeddings,
            registration_date=data.get('registration_date'),
            last_updated=data.get('last_updated')
        )


class DatabaseManager:
    """Manages database operations for the face recognition system."""
    
    def __init__(self, db_path: str = "data/database/face_recognition.db"):
        self.db_path = db_path
        self.ensure_database_directory()
    
    def ensure_database_directory(self):
        """Ensure the database directory exists."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def add_person(self, person: Person) -> bool:
        """Add a new person to the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                embeddings_blob = None
                if person.face_embeddings is not None:
                    embeddings_blob = pickle.dumps(person.face_embeddings)
                
                cursor.execute("""
                    INSERT INTO persons 
                    (person_id, full_name, email, phone, category, profile_image_path, 
                     face_embeddings, registration_date, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    person.person_id,
                    person.full_name,
                    person.email,
                    person.phone,
                    person.category,
                    person.profile_image_path,
                    embeddings_blob,
                    person.registration_date,
                    person.last_updated
                ))
                
                conn.commit()
                person.db_id = cursor.lastrowid
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error adding person: {e}")
            return False
    
    def get_person_by_id(self, person_id: str) -> Optional[Person]:
        """Get a person by their person_id."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM persons WHERE person_id = ?
                """, (person_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_person(row)
                return None
        except Exception as e:
            print(f"Error getting person: {e}")
            return None
    
    def get_person_by_db_id(self, db_id: int) -> Optional[Person]:
        """Get a person by their database ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM persons WHERE id = ?
                """, (db_id,))
                
                row = cursor.fetchone()
                if row:
                    return self._row_to_person(row)
                return None
        except Exception as e:
            print(f"Error getting person: {e}")
            return None
    
    def get_all_persons(self) -> List[Person]:
        """Get all persons from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM persons ORDER BY full_name")
                
                rows = cursor.fetchall()
                return [self._row_to_person(row) for row in rows]
        except Exception as e:
            print(f"Error getting all persons: {e}")
            return []
    
    def search_persons(self, search_term: str, search_by: str = 'name') -> List[Person]:
        """Search persons by name, ID, or category."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if search_by == 'name':
                    cursor.execute("""
                        SELECT * FROM persons 
                        WHERE full_name LIKE ? 
                        ORDER BY full_name
                    """, (f'%{search_term}%',))
                elif search_by == 'id':
                    cursor.execute("""
                        SELECT * FROM persons 
                        WHERE person_id LIKE ? 
                        ORDER BY person_id
                    """, (f'%{search_term}%',))
                elif search_by == 'category':
                    cursor.execute("""
                        SELECT * FROM persons 
                        WHERE category LIKE ? 
                        ORDER BY category, full_name
                    """, (f'%{search_term}%',))
                else:
                    return []
                
                rows = cursor.fetchall()
                return [self._row_to_person(row) for row in rows]
        except Exception as e:
            print(f"Error searching persons: {e}")
            return []
    
    def update_person(self, person: Person) -> bool:
        """Update an existing person in the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                embeddings_blob = None
                if person.face_embeddings is not None:
                    embeddings_blob = pickle.dumps(person.face_embeddings)
                
                person.last_updated = datetime.now().isoformat()
                
                cursor.execute("""
                    UPDATE persons 
                    SET full_name = ?, email = ?, phone = ?, category = ?, 
                        profile_image_path = ?, face_embeddings = ?, last_updated = ?
                    WHERE person_id = ?
                """, (
                    person.full_name,
                    person.email,
                    person.phone,
                    person.category,
                    person.profile_image_path,
                    embeddings_blob,
                    person.last_updated,
                    person.person_id
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating person: {e}")
            return False
    
    def delete_person(self, person_id: str) -> bool:
        """Delete a person from the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get person info to delete profile image
                person = self.get_person_by_id(person_id)
                if person and person.profile_image_path:
                    try:
                        Path(person.profile_image_path).unlink(missing_ok=True)
                    except Exception as e:
                        print(f"Error deleting profile image: {e}")
                
                cursor.execute("""
                    DELETE FROM persons WHERE person_id = ?
                """, (person_id,))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting person: {e}")
            return False
    
    def get_persons_with_embeddings(self) -> List[Person]:
        """Get all persons that have face embeddings."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM persons 
                    WHERE face_embeddings IS NOT NULL 
                    ORDER BY full_name
                """)
                
                rows = cursor.fetchall()
                return [self._row_to_person(row) for row in rows]
        except Exception as e:
            print(f"Error getting persons with embeddings: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM persons")
                total_persons = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM persons WHERE face_embeddings IS NOT NULL")
                persons_with_faces = cursor.fetchone()[0]
                
                cursor.execute("SELECT DISTINCT category FROM persons WHERE category IS NOT NULL")
                categories = [row[0] for row in cursor.fetchall()]
                
                return {
                    'total_persons': total_persons,
                    'persons_with_faces': persons_with_faces,
                    'categories': categories
                }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {'total_persons': 0, 'persons_with_faces': 0, 'categories': []}
    
    def _row_to_person(self, row: sqlite3.Row) -> Person:
        """Convert a database row to a Person object."""
        embeddings = None
        if row['face_embeddings'] is not None:
            try:
                embeddings = pickle.loads(row['face_embeddings'])
            except Exception as e:
                print(f"Error loading embeddings: {e}")
        
        return Person(
            db_id=row['id'],
            person_id=row['person_id'],
            full_name=row['full_name'],
            email=row['email'],
            phone=row['phone'],
            category=row['category'],
            profile_image_path=row['profile_image_path'],
            face_embeddings=embeddings,
            registration_date=row['registration_date'],
            last_updated=row['last_updated']
        )
    
    def person_id_exists(self, person_id: str) -> bool:
        """Check if a person_id already exists."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM persons WHERE person_id = ?
                """, (person_id,))
                return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Error checking person_id existence: {e}")
            return False


class SettingsManager:
    """Manages application settings."""
    
    def __init__(self, db_path: str = "data/database/face_recognition.db"):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get a setting value."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT value FROM settings WHERE key = ?
                """, (key,))
                
                row = cursor.fetchone()
                if row:
                    return row['value']
                return default
        except Exception as e:
            print(f"Error getting setting: {e}")
            return default
    
    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO settings (key, value)
                    VALUES (?, ?)
                """, (key, value))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error setting setting: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, str]:
        """Get all settings."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM settings")
                
                return {row['key']: row['value'] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error getting all settings: {e}")
            return {}


class AnalyticsManager:
    """Manages analytics data."""
    
    def __init__(self, db_path: str = "data/database/face_recognition.db"):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def record_metric(self, metric_name: str, metric_value: float) -> bool:
        """Record an analytics metric."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO analytics (metric_name, metric_value)
                    VALUES (?, ?)
                """, (metric_name, metric_value))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording metric: {e}")
            return False
    
    def get_metric_statistics(self, metric_name: str, limit: int = 100) -> Dict[str, Any]:
        """Get statistics for a specific metric."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT metric_value, timestamp 
                    FROM analytics 
                    WHERE metric_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (metric_name, limit))
                
                rows = cursor.fetchall()
                values = [row['metric_value'] for row in rows]
                
                if not values:
                    return {'count': 0, 'average': 0, 'min': 0, 'max': 0}
                
                return {
                    'count': len(values),
                    'average': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        except Exception as e:
            print(f"Error getting metric statistics: {e}")
            return {'count': 0, 'average': 0, 'min': 0, 'max': 0}
    
    def get_all_metrics_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics for all metrics."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT metric_name FROM analytics
                """)
                
                metric_names = [row[0] for row in cursor.fetchall()]
                
                summary = {}
                for metric_name in metric_names:
                    summary[metric_name] = self.get_metric_statistics(metric_name)
                
                return summary
        except Exception as e:
            print(f"Error getting all metrics summary: {e}")
            return {}
    
    def clear_old_metrics(self, days: int = 30) -> bool:
        """Clear metrics older than specified days."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM analytics 
                    WHERE timestamp < datetime('now', '-' || ? || ' days')
                """, (days,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error clearing old metrics: {e}")
            return False


if __name__ == "__main__":
    # Test the database models
    from database.schema import DatabaseSchema
    
    # Initialize database
    schema = DatabaseSchema()
    schema.create_schema()
    
    # Test database manager
    db_manager = DatabaseManager()
    
    # Create a test person
    test_person = Person(
        person_id="TEST001",
        full_name="Test User",
        email="test@example.com",
        category="Test"
    )
    
    # Add person
    if db_manager.add_person(test_person):
        print("Person added successfully")
    
    # Get person
    retrieved_person = db_manager.get_person_by_id("TEST001")
    if retrieved_person:
        print(f"Retrieved person: {retrieved_person.full_name}")
    
    # Get statistics
    stats = db_manager.get_statistics()
    print(f"Database statistics: {stats}")
