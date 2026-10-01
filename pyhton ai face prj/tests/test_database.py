"""
Database Tests
Tests for database operations including person management, settings, and analytics.
"""

import pytest
import sqlite3
import numpy as np
from pathlib import Path
import tempfile
import os

from database.models import DatabaseManager, Person, SettingsManager, AnalyticsManager
from database.schema import DatabaseSchema


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_schema(temp_db):
    """Create and initialize database schema."""
    schema = DatabaseSchema(temp_db)
    schema.create_schema()
    return schema


@pytest.fixture
def db_manager(temp_db):
    """Create database manager."""
    return DatabaseManager(temp_db)


@pytest.fixture
def sample_person():
    """Create a sample person for testing."""
    return Person(
        person_id="TEST001",
        full_name="Test User",
        email="test@example.com",
        phone="1234567890",
        category="Test"
    )


class TestDatabaseSchema:
    """Tests for database schema operations."""
    
    def test_schema_creation(self, db_schema):
        """Test that schema is created correctly."""
        schema_info = db_schema.get_schema_info()
        
        assert 'tables' in schema_info
        assert 'persons' in schema_info['tables']
        assert 'settings' in schema_info['tables']
        assert 'analytics' in schema_info['tables']
    
    def test_default_settings_inserted(self, db_schema):
        """Test that default settings are inserted."""
        with sqlite3.connect(db_schema.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM settings")
            count = cursor.fetchone()[0]
            assert count > 0


class TestDatabaseManager:
    """Tests for database manager operations."""
    
    def test_add_person(self, db_manager, sample_person):
        """Test adding a person to the database."""
        result = db_manager.add_person(sample_person)
        assert result is True
    
    def test_add_duplicate_person_id(self, db_manager, sample_person):
        """Test that duplicate person IDs are rejected."""
        db_manager.add_person(sample_person)
        
        # Try to add same person again
        result = db_manager.add_person(sample_person)
        assert result is False
    
    def test_get_person_by_id(self, db_manager, sample_person):
        """Test retrieving a person by ID."""
        db_manager.add_person(sample_person)
        
        retrieved = db_manager.get_person_by_id("TEST001")
        assert retrieved is not None
        assert retrieved.person_id == "TEST001"
        assert retrieved.full_name == "Test User"
    
    def test_get_person_by_db_id(self, db_manager, sample_person):
        """Test retrieving a person by database ID."""
        db_manager.add_person(sample_person)
        
        retrieved = db_manager.get_person_by_id("TEST001")
        assert retrieved is not None
        
        # Now test by db_id
        by_db_id = db_manager.get_person_by_db_id(retrieved.db_id)
        assert by_db_id is not None
        assert by_db_id.person_id == "TEST001"
    
    def test_get_all_persons(self, db_manager):
        """Test retrieving all persons."""
        person1 = Person(person_id="TEST001", full_name="User 1")
        person2 = Person(person_id="TEST002", full_name="User 2")
        
        db_manager.add_person(person1)
        db_manager.add_person(person2)
        
        all_persons = db_manager.get_all_persons()
        assert len(all_persons) == 2
    
    def test_search_persons_by_name(self, db_manager):
        """Test searching persons by name."""
        person1 = Person(person_id="TEST001", full_name="John Doe")
        person2 = Person(person_id="TEST002", full_name="Jane Smith")
        
        db_manager.add_person(person1)
        db_manager.add_person(person2)
        
        results = db_manager.search_persons("John", search_by='name')
        assert len(results) == 1
        assert results[0].full_name == "John Doe"
    
    def test_search_persons_by_id(self, db_manager):
        """Test searching persons by ID."""
        person1 = Person(person_id="TEST001", full_name="User 1")
        person2 = Person(person_id="TEST002", full_name="User 2")
        
        db_manager.add_person(person1)
        db_manager.add_person(person2)
        
        results = db_manager.search_persons("TEST001", search_by='id')
        assert len(results) == 1
        assert results[0].person_id == "TEST001"
    
    def test_update_person(self, db_manager, sample_person):
        """Test updating a person's information."""
        db_manager.add_person(sample_person)
        
        sample_person.full_name = "Updated Name"
        sample_person.email = "updated@example.com"
        
        result = db_manager.update_person(sample_person)
        assert result is True
        
        # Verify update
        retrieved = db_manager.get_person_by_id("TEST001")
        assert retrieved.full_name == "Updated Name"
        assert retrieved.email == "updated@example.com"
    
    def test_delete_person(self, db_manager, sample_person):
        """Test deleting a person."""
        db_manager.add_person(sample_person)
        
        result = db_manager.delete_person("TEST001")
        assert result is True
        
        # Verify deletion
        retrieved = db_manager.get_person_by_id("TEST001")
        assert retrieved is None
    
    def test_person_id_exists(self, db_manager, sample_person):
        """Test checking if person ID exists."""
        assert db_manager.person_id_exists("TEST001") is False
        
        db_manager.add_person(sample_person)
        assert db_manager.person_id_exists("TEST001") is True
    
    def test_get_statistics(self, db_manager):
        """Test getting database statistics."""
        person1 = Person(person_id="TEST001", full_name="User 1")
        person2 = Person(person_id="TEST002", full_name="User 2")
        
        db_manager.add_person(person1)
        db_manager.add_person(person2)
        
        stats = db_manager.get_statistics()
        assert stats['total_persons'] == 2
    
    def test_person_with_embeddings(self, db_manager):
        """Test storing and retrieving person with face embeddings."""
        embeddings = np.random.rand(128).astype(np.float32)
        person = Person(
            person_id="TEST001",
            full_name="Test User",
            face_embeddings=embeddings
        )
        
        db_manager.add_person(person)
        
        retrieved = db_manager.get_person_by_id("TEST001")
        assert retrieved.face_embeddings is not None
        assert np.allclose(retrieved.face_embeddings, embeddings)


class TestSettingsManager:
    """Tests for settings manager operations."""
    
    @pytest.fixture
    def settings_manager(self, temp_db):
        """Create settings manager."""
        return SettingsManager(temp_db)
    
    def test_get_setting(self, settings_manager):
        """Test getting a setting value."""
        value = settings_manager.get_setting('test_key', 'default')
        assert value == 'default'
    
    def test_set_setting(self, settings_manager):
        """Test setting a value."""
        result = settings_manager.set_setting('test_key', 'test_value')
        assert result is True
        
        value = settings_manager.get_setting('test_key')
        assert value == 'test_value'
    
    def test_get_all_settings(self, settings_manager):
        """Test getting all settings."""
        settings_manager.set_setting('key1', 'value1')
        settings_manager.set_setting('key2', 'value2')
        
        all_settings = settings_manager.get_all_settings()
        assert 'key1' in all_settings
        assert 'key2' in all_settings


class TestAnalyticsManager:
    """Tests for analytics manager operations."""
    
    @pytest.fixture
    def analytics_manager(self, temp_db):
        """Create analytics manager."""
        return AnalyticsManager(temp_db)
    
    def test_record_metric(self, analytics_manager):
        """Test recording a metric."""
        result = analytics_manager.record_metric('test_metric', 42.0)
        assert result is True
    
    def test_get_metric_statistics(self, analytics_manager):
        """Test getting metric statistics."""
        analytics_manager.record_metric('test_metric', 10.0)
        analytics_manager.record_metric('test_metric', 20.0)
        analytics_manager.record_metric('test_metric', 30.0)
        
        stats = analytics_manager.get_metric_statistics('test_metric')
        assert stats['count'] == 3
        assert stats['average'] == 20.0
        assert stats['min'] == 10.0
        assert stats['max'] == 30.0
    
    def test_get_all_metrics_summary(self, analytics_manager):
        """Test getting all metrics summary."""
        analytics_manager.record_metric('metric1', 10.0)
        analytics_manager.record_metric('metric2', 20.0)
        
        summary = analytics_manager.get_all_metrics_summary()
        assert 'metric1' in summary
        assert 'metric2' in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
