"""
Helper utilities for the Face Recognition System
Provides general utility functions used across the application.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading


class Helpers:
    """General helper functions for the application."""
    
    @staticmethod
    def get_project_root() -> Path:
        """
        Get the project root directory.
        
        Returns:
            Path to project root
        """
        return Path(__file__).parent.parent
    
    @staticmethod
    def ensure_directory(directory_path: str) -> None:
        """
        Ensure a directory exists, create if it doesn't.
        
        Args:
            directory_path: Path to the directory
        """
        Path(directory_path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Get current timestamp as a formatted string.
        
        Returns:
            Timestamp string
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_timestamp_filename() -> str:
        """
        Get timestamp suitable for filenames.
        
        Returns:
            Timestamp string for filenames
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to human-readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 1:
            return f"{seconds * 1000:.1f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    @staticmethod
    def calculate_similarity(distance: float, threshold: float = 0.6) -> float:
        """
        Convert face distance to similarity percentage.
        
        Args:
            distance: Face distance from face_recognition
            threshold: Recognition threshold
            
        Returns:
            Similarity percentage (0-100)
        """
        # Clamp distance to reasonable range
        distance = max(0, min(distance, 1.0))
        
        # Convert to similarity percentage
        # Lower distance = higher similarity
        similarity = (1 - distance) * 100
        
        # Adjust based on threshold
        if distance < threshold:
            # Boost similarity for matches below threshold
            similarity = similarity + (threshold - distance) * 50
        
        return max(0, min(100, similarity))
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in bytes to human-readable string.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted file size string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Load a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary with JSON data or None if loading fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return None
    
    @staticmethod
    def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            data: Data to save
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Helpers.ensure_directory(str(Path(file_path).parent))
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON file: {e}")
            return False
    
    @staticmethod
    def get_unique_filename(base_path: str, extension: str = "") -> str:
        """
        Generate a unique filename by appending timestamp if file exists.
        
        Args:
            base_path: Base file path
            extension: File extension (with or without dot)
            
        Returns:
            Unique file path
        """
        if not extension.startswith('.'):
            extension = '.' + extension if extension else ''
        
        path = Path(base_path + extension)
        
        if not path.exists():
            return str(path)
        
        timestamp = Helpers.get_timestamp_filename()
        new_path = path.parent / f"{path.stem}_{timestamp}{path.suffix}"
        return str(new_path)
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean a filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Cleaned filename
        """
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255 - len(ext)] + ext
        
        return filename or "unnamed"
    
    @staticmethod
    def get_file_hash(file_path: str) -> Optional[str]:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string or None if calculation fails
        """
        import hashlib
        
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"Error calculating file hash: {e}")
            return None
    
    @staticmethod
    def copy_file_with_progress(source: str, destination: str, 
                                progress_callback=None) -> bool:
        """
        Copy a file with optional progress callback.
        
        Args:
            source: Source file path
            destination: Destination file path
            progress_callback: Optional callback function for progress
            
        Returns:
            True if successful, False otherwise
        """
        try:
            Helpers.ensure_directory(str(Path(destination).parent))
            
            file_size = os.path.getsize(source)
            copied = 0
            
            with open(source, 'rb') as src, open(destination, 'wb') as dst:
                while True:
                    chunk = src.read(4096)
                    if not chunk:
                        break
                    dst.write(chunk)
                    copied += len(chunk)
                    
                    if progress_callback:
                        progress = (copied / file_size) * 100
                        progress_callback(progress)
            
            return True
        except Exception as e:
            print(f"Error copying file: {e}")
            return False
    
    @staticmethod
    def delete_file_safely(file_path: str) -> bool:
        """
        Safely delete a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    @staticmethod
    def get_available_cameras(max_cameras: int = 5) -> List[int]:
        """
        Get list of available camera indices.
        
        Args:
            max_cameras: Maximum number of cameras to check
            
        Returns:
            List of available camera indices
        """
        import cv2
        
        available_cameras = []
        
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        
        return available_cameras
    
    @staticmethod
    def is_camera_available(camera_index: int) -> bool:
        """
        Check if a camera is available.
        
        Args:
            camera_index: Camera index to check
            
        Returns:
            True if camera is available, False otherwise
        """
        import cv2
        
        try:
            cap = cv2.VideoCapture(camera_index)
            available = cap.isOpened()
            cap.release()
            return available
        except Exception:
            return False


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, operation_name: str = "Operation"):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        print(f"{self.operation_name} took {Helpers.format_duration(self.duration)}")
    
    def get_duration(self) -> float:
        """Get the duration in seconds."""
        if self.duration is not None:
            return self.duration
        elif self.start_time is not None:
            return time.time() - self.start_time
        return 0.0


class ThreadSafeCounter:
    """Thread-safe counter for tracking statistics."""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        """Increment the counter and return new value."""
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """Decrement the counter and return new value."""
        with self._lock:
            self._value -= amount
            return self._value
    
    def get(self) -> int:
        """Get the current value."""
        with self._lock:
            return self._value
    
    def set(self, value: int) -> None:
        """Set the counter to a specific value."""
        with self._lock:
            self._value = value
    
    def reset(self) -> int:
        """Reset counter to zero and return old value."""
        with self._lock:
            old_value = self._value
            self._value = 0
            return old_value


class RateLimiter:
    """Rate limiter for controlling operation frequency."""
    
    def __init__(self, max_calls: int, time_window: float):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self._lock = threading.Lock()
    
    def allow(self) -> bool:
        """Check if a call is allowed under the rate limit."""
        with self._lock:
            now = time.time()
            
            # Remove old calls outside the time window
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            # Check if we can make a new call
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        with self._lock:
            self.calls = []


class ConfigManager:
    """Manages application configuration from JSON files."""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if Path(self.config_path).exists():
            return Helpers.load_json_file(self.config_path) or {}
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        Helpers.save_json_file(self.config, self.config_path)
    
    def save(self) -> None:
        """Explicitly save configuration."""
        self._save_config()


if __name__ == "__main__":
    # Test helper functions
    print("Testing Helpers...")
    
    # Test timestamp
    print(f"Timestamp: {Helpers.get_timestamp()}")
    
    # Test duration formatting
    print(f"Duration (0.5s): {Helpers.format_duration(0.5)}")
    print(f"Duration (65s): {Helpers.format_duration(65)}")
    
    # Test similarity calculation
    similarity = Helpers.calculate_similarity(0.3, 0.6)
    print(f"Similarity (distance=0.3): {similarity:.1f}%")
    
    # Test file size formatting
    print(f"File size (1024): {Helpers.format_file_size(1024)}")
    print(f"File size (1048576): {Helpers.format_file_size(1048576)}")
    
    # Test performance timer
    with PerformanceTimer("Test operation"):
        time.sleep(0.1)
    
    # Test thread-safe counter
    counter = ThreadSafeCounter()
    print(f"Counter initial: {counter.get()}")
    counter.increment()
    print(f"Counter after increment: {counter.get()}")
    
    # Test rate limiter
    limiter = RateLimiter(max_calls=3, time_window=1.0)
    print(f"Rate limiter calls: {[limiter.allow() for _ in range(5)]}")
