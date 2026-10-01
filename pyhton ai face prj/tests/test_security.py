"""
Security Tests
Tests for security functions including password hashing and admin authentication.
"""

import pytest
import tempfile
import os
from utils.security import SecurityManager, AdminAuth


class TestSecurityManager:
    """Tests for security manager operations."""
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = SecurityManager.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        hashed = SecurityManager.hash_password(password)
        
        is_valid = SecurityManager.verify_password(password, hashed)
        assert is_valid is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = SecurityManager.hash_password(password)
        
        is_valid = SecurityManager.verify_password(wrong_password, hashed)
        assert is_valid is False
    
    def test_generate_secure_token(self):
        """Test secure token generation."""
        token = SecurityManager.generate_secure_token()
        
        assert token is not None
        assert len(token) == 64  # 32 bytes = 64 hex characters
    
    def test_generate_random_password(self):
        """Test random password generation."""
        password = SecurityManager.generate_random_password()
        
        assert password is not None
        assert len(password) == 12
    
    def test_validate_password_strength_strong(self):
        """Test password strength validation for strong password."""
        is_valid, message = SecurityManager.validate_password_strength("StrongPass123!")
        assert is_valid is True
    
    def test_validate_password_strength_weak(self):
        """Test password strength validation for weak password."""
        is_valid, message = SecurityManager.validate_password_strength("weak")
        assert is_valid is False
    
    def test_validate_password_strength_no_uppercase(self):
        """Test password strength without uppercase."""
        is_valid, message = SecurityManager.validate_password_strength("lowercase123!")
        assert is_valid is False
    
    def test_validate_password_strength_no_lowercase(self):
        """Test password strength without lowercase."""
        is_valid, message = SecurityManager.validate_password_strength("UPPERCASE123!")
        assert is_valid is False
    
    def test_validate_password_strength_no_digit(self):
        """Test password strength without digit."""
        is_valid, message = SecurityManager.validate_password_strength("NoDigits!")
        assert is_valid is False
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test normal input
        sanitized = SecurityManager.sanitize_input("Hello World")
        assert sanitized == "Hello World"
        
        # Test input with null bytes
        sanitized = SecurityManager.sanitize_input("Hello\x00World")
        assert "\x00" not in sanitized
        
        # Test input truncation
        long_input = "A" * 2000
        sanitized = SecurityManager.sanitize_input(long_input, max_length=100)
        assert len(sanitized) == 100


class TestAdminAuth:
    """Tests for admin authentication operations."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def admin_auth(self, temp_db):
        """Create admin auth instance."""
        return AdminAuth(temp_db)
    
    def test_create_admin(self, admin_auth):
        """Test creating an admin user."""
        result = admin_auth.create_admin("testuser", "testpass123")
        assert result is True
    
    def test_create_duplicate_admin(self, admin_auth):
        """Test creating duplicate admin user."""
        admin_auth.create_admin("testuser", "testpass123")
        
        # Try to create same username again
        result = admin_auth.create_admin("testuser", "differentpass")
        assert result is False
    
    def test_verify_admin_correct(self, admin_auth):
        """Test admin verification with correct credentials."""
        admin_auth.create_admin("testuser", "testpass123")
        
        is_valid = admin_auth.verify_admin("testuser", "testpass123")
        assert is_valid is True
    
    def test_verify_admin_incorrect_password(self, admin_auth):
        """Test admin verification with incorrect password."""
        admin_auth.create_admin("testuser", "testpass123")
        
        is_valid = admin_auth.verify_admin("testuser", "wrongpass")
        assert is_valid is False
    
    def test_verify_admin_nonexistent(self, admin_auth):
        """Test admin verification for nonexistent user."""
        is_valid = admin_auth.verify_admin("nonexistent", "anypass")
        assert is_valid is False
    
    def test_admin_exists(self, admin_auth):
        """Test checking if admin exists."""
        assert admin_auth.admin_exists() is False
        
        admin_auth.create_admin("testuser", "testpass123")
        assert admin_auth.admin_exists() is True
    
    def test_change_admin_password(self, admin_auth):
        """Test changing admin password."""
        admin_auth.create_admin("testuser", "oldpass123")
        
        result = admin_auth.change_admin_password("testuser", "oldpass123", "newpass456")
        assert result is True
        
        # Verify new password works
        is_valid = admin_auth.verify_admin("testuser", "newpass456")
        assert is_valid is True
        
        # Verify old password doesn't work
        is_valid = admin_auth.verify_admin("testuser", "oldpass123")
        assert is_valid is False
    
    def test_change_admin_password_wrong_old(self, admin_auth):
        """Test changing password with wrong old password."""
        admin_auth.create_admin("testuser", "oldpass123")
        
        result = admin_auth.change_admin_password("testuser", "wrongpass", "newpass456")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
