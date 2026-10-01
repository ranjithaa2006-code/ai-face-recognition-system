"""
Input validation utilities for the Face Recognition System
Validates user inputs, data formats, and business rules.
"""

import re
from typing import Tuple, List, Optional
from datetime import datetime
from pathlib import Path


class Validators:
    """Utility class for validating various inputs and data."""
    
    @staticmethod
    def validate_person_id(person_id: str) -> Tuple[bool, str]:
        """
        Validate person ID format.
        
        Args:
            person_id: Person ID to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not person_id:
            return False, "Person ID cannot be empty"
        
        if len(person_id) < 3:
            return False, "Person ID must be at least 3 characters"
        
        if len(person_id) > 50:
            return False, "Person ID must not exceed 50 characters"
        
        # Allow alphanumeric, underscore, and hyphen
        if not re.match(r'^[a-zA-Z0-9_-]+$', person_id):
            return False, "Person ID can only contain letters, numbers, underscores, and hyphens"
        
        return True, "Person ID is valid"
    
    @staticmethod
    def validate_full_name(full_name: str) -> Tuple[bool, str]:
        """
        Validate full name format.
        
        Args:
            full_name: Full name to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not full_name:
            return False, "Full name cannot be empty"
        
        if len(full_name) < 2:
            return False, "Full name must be at least 2 characters"
        
        if len(full_name) > 100:
            return False, "Full name must not exceed 100 characters"
        
        # Allow letters, spaces, and common name characters
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', full_name):
            return False, "Full name contains invalid characters"
        
        return True, "Full name is valid"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not email:
            return True, "Email is optional"
        
        if len(email) > 100:
            return False, "Email must not exceed 100 characters"
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"
        
        return True, "Email is valid"
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not phone:
            return True, "Phone number is optional"
        
        if len(phone) > 20:
            return False, "Phone number must not exceed 20 characters"
        
        # Allow digits, spaces, +, -, (, )
        phone_pattern = r'^[\d\s\+\-\(\)]+$'
        if not re.match(phone_pattern, phone):
            return False, "Phone number contains invalid characters"
        
        # Check if there are at least some digits
        if not re.search(r'\d', phone):
            return False, "Phone number must contain at least one digit"
        
        return True, "Phone number is valid"
    
    @staticmethod
    def validate_category(category: str) -> Tuple[bool, str]:
        """
        Validate category/department format.
        
        Args:
            category: Category to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not category:
            return True, "Category is optional"
        
        if len(category) > 50:
            return False, "Category must not exceed 50 characters"
        
        # Allow letters, numbers, spaces, and common separators
        if not re.match(r'^[a-zA-Z0-9\s\-_\/]+$', category):
            return False, "Category contains invalid characters"
        
        return True, "Category is valid"
    
    @staticmethod
    def validate_file_path(file_path: str, must_exist: bool = False) -> Tuple[bool, str]:
        """
        Validate file path.
        
        Args:
            file_path: File path to validate
            must_exist: Whether the file must exist
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not file_path:
            return False, "File path cannot be empty"
        
        try:
            path = Path(file_path)
            
            # Check for invalid characters
            if any(char in str(path) for char in '<>:"|?*'):
                return False, "File path contains invalid characters"
            
            if must_exist:
                if not path.exists():
                    return False, "File does not exist"
                if not path.is_file():
                    return False, "Path is not a file"
            
            return True, "File path is valid"
        except Exception as e:
            return False, f"Error validating file path: {e}"
    
    @staticmethod
    def validate_image_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate that a file is a valid image.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            Tuple of (is_valid, message)
        """
        # First validate file path
        is_valid, message = Validators.validate_file_path(file_path, must_exist=True)
        if not is_valid:
            return is_valid, message
        
        try:
            path = Path(file_path)
            
            # Check file extension
            valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
            if path.suffix.lower() not in valid_extensions:
                return False, f"Invalid image format. Supported: {', '.join(valid_extensions)}"
            
            # Check file size (max 10MB)
            file_size = path.stat().st_size
            if file_size > 10 * 1024 * 1024:
                return False, "Image file is too large (maximum 10MB)"
            
            if file_size == 0:
                return False, "Image file is empty"
            
            return True, "Image file is valid"
        except Exception as e:
            return False, f"Error validating image file: {e}"
    
    @staticmethod
    def validate_recognition_threshold(threshold: float) -> Tuple[bool, str]:
        """
        Validate recognition threshold value.
        
        Args:
            threshold: Recognition threshold (0.0 to 1.0)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(threshold, (int, float)):
            return False, "Threshold must be a number"
        
        if threshold < 0.0:
            return False, "Threshold cannot be negative"
        
        if threshold > 1.0:
            return False, "Threshold cannot exceed 1.0"
        
        # Recommended range for face_recognition library
        if threshold < 0.3:
            return False, "Threshold is too low (minimum 0.3)"
        
        if threshold > 0.8:
            return False, "Threshold is too high (maximum 0.8)"
        
        return True, "Threshold is valid"
    
    @staticmethod
    def validate_camera_index(camera_index: int) -> Tuple[bool, str]:
        """
        Validate camera index.
        
        Args:
            camera_index: Camera index
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(camera_index, int):
            return False, "Camera index must be an integer"
        
        if camera_index < 0:
            return False, "Camera index cannot be negative"
        
        if camera_index > 10:
            return False, "Camera index is too high (maximum 10)"
        
        return True, "Camera index is valid"
    
    @staticmethod
    def validate_detection_frequency(frequency: int) -> Tuple[bool, str]:
        """
        Validate detection frequency (frames between detections).
        
        Args:
            frequency: Detection frequency in frames
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(frequency, int):
            return False, "Detection frequency must be an integer"
        
        if frequency < 1:
            return False, "Detection frequency must be at least 1"
        
        if frequency > 30:
            return False, "Detection frequency is too high (maximum 30)"
        
        return True, "Detection frequency is valid"
    
    @staticmethod
    def validate_frame_scaling(scale: float) -> Tuple[bool, str]:
        """
        Validate frame scaling factor.
        
        Args:
            scale: Scaling factor (e.g., 0.5 for half size)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(scale, (int, float)):
            return False, "Frame scaling must be a number"
        
        if scale <= 0:
            return False, "Frame scaling must be positive"
        
        if scale > 1.0:
            return False, "Frame scaling cannot exceed 1.0"
        
        if scale < 0.1:
            return False, "Frame scaling is too small (minimum 0.1)"
        
        return True, "Frame scaling is valid"
    
    @staticmethod
    def validate_minimum_face_size(size: int) -> Tuple[bool, str]:
        """
        Validate minimum face size in pixels.
        
        Args:
            size: Minimum face size
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not isinstance(size, int):
            return False, "Minimum face size must be an integer"
        
        if size < 50:
            return False, "Minimum face size is too small (minimum 50 pixels)"
        
        if size > 500:
            return False, "Minimum face size is too large (maximum 500 pixels)"
        
        return True, "Minimum face size is valid"
    
    @staticmethod
    def validate_registration_data(data: dict) -> Tuple[bool, List[str]]:
        """
        Validate complete registration data.
        
        Args:
            data: Dictionary containing registration data
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate required fields
        if 'person_id' not in data or not data['person_id']:
            errors.append("Person ID is required")
        else:
            is_valid, message = Validators.validate_person_id(data['person_id'])
            if not is_valid:
                errors.append(message)
        
        if 'full_name' not in data or not data['full_name']:
            errors.append("Full name is required")
        else:
            is_valid, message = Validators.validate_full_name(data['full_name'])
            if not is_valid:
                errors.append(message)
        
        # Validate optional fields
        if 'email' in data and data['email']:
            is_valid, message = Validators.validate_email(data['email'])
            if not is_valid:
                errors.append(message)
        
        if 'phone' in data and data['phone']:
            is_valid, message = Validators.validate_phone(data['phone'])
            if not is_valid:
                errors.append(message)
        
        if 'category' in data and data['category']:
            is_valid, message = Validators.validate_category(data['category'])
            if not is_valid:
                errors.append(message)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 100) -> str:
        """
        Sanitize a string input.
        
        Args:
            input_string: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not input_string:
            return ""
        
        # Remove null bytes and trim
        sanitized = input_string.replace('\x00', '').strip()
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_face_count(face_count: int, max_faces: int = 1) -> Tuple[bool, str]:
        """
        Validate number of faces detected.
        
        Args:
            face_count: Number of faces detected
            max_faces: Maximum allowed faces
            
        Returns:
            Tuple of (is_valid, message)
        """
        if face_count == 0:
            return False, "No face detected in the image"
        
        if face_count > max_faces:
            return False, f"Multiple faces detected ({face_count}). Please provide an image with only one face for registration."
        
        return True, f"Valid face count: {face_count}"


if __name__ == "__main__":
    # Test validators
    print("Testing Validators...")
    
    # Test person ID validation
    is_valid, message = Validators.validate_person_id("USER001")
    print(f"Person ID validation: {is_valid}, {message}")
    
    # Test email validation
    is_valid, message = Validators.validate_email("test@example.com")
    print(f"Email validation: {is_valid}, {message}")
    
    # Test registration data validation
    data = {
        'person_id': 'USER001',
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1234567890',
        'category': 'Engineering'
    }
    is_valid, errors = Validators.validate_registration_data(data)
    print(f"Registration data validation: {is_valid}, errors: {errors}")
    
    # Test threshold validation
    is_valid, message = Validators.validate_recognition_threshold(0.6)
    print(f"Threshold validation: {is_valid}, {message}")
