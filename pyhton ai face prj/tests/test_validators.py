"""
Validator Tests
Tests for input validation functions.
"""

import pytest
from utils.validators import Validators


class TestValidators:
    """Tests for validation functions."""
    
    def test_validate_person_id_valid(self):
        """Test validation of valid person ID."""
        is_valid, message = Validators.validate_person_id("USER001")
        assert is_valid is True
        assert "valid" in message.lower()
    
    def test_validate_person_id_empty(self):
        """Test validation of empty person ID."""
        is_valid, message = Validators.validate_person_id("")
        assert is_valid is False
        assert "empty" in message.lower()
    
    def test_validate_person_id_too_short(self):
        """Test validation of too short person ID."""
        is_valid, message = Validators.validate_person_id("AB")
        assert is_valid is False
        assert "at least 3" in message.lower()
    
    def test_validate_person_id_invalid_chars(self):
        """Test validation of person ID with invalid characters."""
        is_valid, message = Validators.validate_person_id("USER@001")
        assert is_valid is False
        assert "invalid" in message.lower()
    
    def test_validate_full_name_valid(self):
        """Test validation of valid full name."""
        is_valid, message = Validators.validate_full_name("John Doe")
        assert is_valid is True
    
    def test_validate_full_name_empty(self):
        """Test validation of empty full name."""
        is_valid, message = Validators.validate_full_name("")
        assert is_valid is False
    
    def test_validate_email_valid(self):
        """Test validation of valid email."""
        is_valid, message = Validators.validate_email("test@example.com")
        assert is_valid is True
    
    def test_validate_email_invalid(self):
        """Test validation of invalid email."""
        is_valid, message = Validators.validate_email("invalid-email")
        assert is_valid is False
    
    def test_validate_email_optional(self):
        """Test that email is optional."""
        is_valid, message = Validators.validate_email("")
        assert is_valid is True
        assert "optional" in message.lower()
    
    def test_validate_phone_valid(self):
        """Test validation of valid phone number."""
        is_valid, message = Validators.validate_phone("+1234567890")
        assert is_valid is True
    
    def test_validate_phone_invalid_chars(self):
        """Test validation of phone with invalid characters."""
        is_valid, message = Validators.validate_phone("123-ABC-789")
        assert is_valid is False
    
    def test_validate_phone_optional(self):
        """Test that phone is optional."""
        is_valid, message = Validators.validate_phone("")
        assert is_valid is True
    
    def test_validate_category_valid(self):
        """Test validation of valid category."""
        is_valid, message = Validators.validate_category("Engineering")
        assert is_valid is True
    
    def test_validate_category_optional(self):
        """Test that category is optional."""
        is_valid, message = Validators.validate_category("")
        assert is_valid is True
    
    def test_validate_recognition_threshold_valid(self):
        """Test validation of valid recognition threshold."""
        is_valid, message = Validators.validate_recognition_threshold(0.6)
        assert is_valid is True
    
    def test_validate_recognition_threshold_too_low(self):
        """Test validation of threshold that's too low."""
        is_valid, message = Validators.validate_recognition_threshold(0.1)
        assert is_valid is False
    
    def test_validate_recognition_threshold_too_high(self):
        """Test validation of threshold that's too high."""
        is_valid, message = Validators.validate_recognition_threshold(0.9)
        assert is_valid is False
    
    def test_validate_camera_index_valid(self):
        """Test validation of valid camera index."""
        is_valid, message = Validators.validate_camera_index(0)
        assert is_valid is True
    
    def test_validate_camera_index_negative(self):
        """Test validation of negative camera index."""
        is_valid, message = Validators.validate_camera_index(-1)
        assert is_valid is False
    
    def test_validate_detection_frequency_valid(self):
        """Test validation of valid detection frequency."""
        is_valid, message = Validators.validate_detection_frequency(5)
        assert is_valid is True
    
    def test_validate_detection_frequency_too_low(self):
        """Test validation of detection frequency that's too low."""
        is_valid, message = Validators.validate_detection_frequency(0)
        assert is_valid is False
    
    def test_validate_frame_scaling_valid(self):
        """Test validation of valid frame scaling."""
        is_valid, message = Validators.validate_frame_scaling(0.5)
        assert is_valid is True
    
    def test_validate_frame_scaling_invalid(self):
        """Test validation of invalid frame scaling."""
        is_valid, message = Validators.validate_frame_scaling(1.5)
        assert is_valid is False
    
    def test_validate_minimum_face_size_valid(self):
        """Test validation of valid minimum face size."""
        is_valid, message = Validators.validate_minimum_face_size(100)
        assert is_valid is True
    
    def test_validate_minimum_face_size_too_small(self):
        """Test validation of minimum face size that's too small."""
        is_valid, message = Validators.validate_minimum_face_size(30)
        assert is_valid is False
    
    def test_validate_registration_data_valid(self):
        """Test validation of complete valid registration data."""
        data = {
            'person_id': 'USER001',
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'category': 'Engineering'
        }
        is_valid, errors = Validators.validate_registration_data(data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_registration_data_missing_required(self):
        """Test validation with missing required fields."""
        data = {
            'person_id': '',
            'full_name': 'John Doe'
        }
        is_valid, errors = Validators.validate_registration_data(data)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_validate_face_count_valid(self):
        """Test validation of valid face count."""
        is_valid, message = Validators.validate_face_count(1, max_faces=1)
        assert is_valid is True
    
    def test_validate_face_count_no_faces(self):
        """Test validation when no faces detected."""
        is_valid, message = Validators.validate_face_count(0, max_faces=1)
        assert is_valid is False
        assert "no face" in message.lower()
    
    def test_validate_face_count_multiple_faces(self):
        """Test validation when multiple faces detected."""
        is_valid, message = Validators.validate_face_count(3, max_faces=1)
        assert is_valid is False
        assert "multiple" in message.lower()
    
    def test_sanitize_string(self):
        """Test string sanitization."""
        # Test normal string
        sanitized = Validators.sanitize_string("Hello World")
        assert sanitized == "Hello World"
        
        # Test string with null bytes
        sanitized = Validators.sanitize_string("Hello\x00World")
        assert "\x00" not in sanitized
        
        # Test string truncation
        long_string = "A" * 200
        sanitized = Validators.sanitize_string(long_string, max_length=50)
        assert len(sanitized) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
