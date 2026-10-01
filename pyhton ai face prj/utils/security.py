"""
Security utilities for the Face Recognition System
Handles password hashing, validation, and security-related operations.
"""

import bcrypt
import secrets
import string
from typing import Optional, Tuple


class SecurityManager:
    """Manages security operations including password hashing and validation."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password as a string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hashed password.
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.
        
        Args:
            length: Length of the token in bytes
            
        Returns:
            Hexadecimal string representation of the token
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """
        Generate a random secure password.
        
        Args:
            length: Length of the password
            
        Returns:
            Random password string
        """
        alphabet = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, "Password meets strength requirements"
    
    @staticmethod
    def sanitize_input(input_string: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_string: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not input_string:
            return ""
        
        # Truncate to max length
        sanitized = input_string[:max_length]
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized.strip()


class AdminAuth:
    """Handles administrator authentication."""
    
    def __init__(self, db_path: str = "data/database/face_recognition.db"):
        self.db_path = db_path
        self._ensure_admin_table()
    
    def _ensure_admin_table(self):
        """Ensure the admin table exists."""
        import sqlite3
        from pathlib import Path
        
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def create_admin(self, username: str, password: str) -> bool:
        """
        Create an admin user.
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            True if successful, False otherwise
        """
        import sqlite3
        
        try:
            hashed_password = SecurityManager.hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO admin_users (username, password_hash)
                    VALUES (?, ?)
                """, (username, hashed_password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            print(f"Error creating admin: {e}")
            return False
    
    def verify_admin(self, username: str, password: str) -> bool:
        """
        Verify admin credentials.
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            True if credentials are valid, False otherwise
        """
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT password_hash FROM admin_users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if row:
                    return SecurityManager.verify_password(password, row[0])
                return False
        except Exception as e:
            print(f"Error verifying admin: {e}")
            return False
    
    def admin_exists(self) -> bool:
        """Check if any admin user exists."""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM admin_users")
                return cursor.fetchone()[0] > 0
        except Exception as e:
            print(f"Error checking admin existence: {e}")
            return False
    
    def change_admin_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Change admin password.
        
        Args:
            username: Admin username
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        import sqlite3
        
        if not self.verify_admin(username, old_password):
            return False
        
        try:
            hashed_password = SecurityManager.hash_password(new_password)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE admin_users 
                    SET password_hash = ? 
                    WHERE username = ?
                """, (hashed_password, username))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error changing admin password: {e}")
            return False


def initialize_default_admin(username: str = "admin", password: str = "admin123") -> bool:
    """
    Initialize default admin user if none exists.
    
    Args:
        username: Default admin username
        password: Default admin password
        
    Returns:
        True if admin was created or already exists, False otherwise
    """
    auth = AdminAuth()
    
    if not auth.admin_exists():
        return auth.create_admin(username, password)
    
    return True


if __name__ == "__main__":
    # Test security functions
    security = SecurityManager()
    
    # Test password hashing
    password = "test_password_123"
    hashed = security.hash_password(password)
    print(f"Hashed password: {hashed}")
    
    # Test password verification
    is_valid = security.verify_password(password, hashed)
    print(f"Password verification: {is_valid}")
    
    # Test password strength
    is_strong, message = security.validate_password_strength("weak")
    print(f"Password strength (weak): {is_strong}, {message}")
    
    is_strong, message = security.validate_password_strength("StrongPass123!")
    print(f"Password strength (strong): {is_strong}, {message}")
    
    # Test token generation
    token = security.generate_secure_token()
    print(f"Generated token: {token}")
    
    # Test admin authentication
    auth = AdminAuth()
    if not auth.admin_exists():
        auth.create_admin("admin", "admin123")
        print("Default admin created")
    
    is_admin = auth.verify_admin("admin", "admin123")
    print(f"Admin verification: {is_admin}")
