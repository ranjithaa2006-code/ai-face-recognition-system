"""
Face Encoding Module
Handles generation of face embeddings (encodings) from face images.
"""

import numpy as np
import face_recognition
from typing import List, Optional, Tuple
from utils.image_utils import ImageUtils


class FaceEncoder:
    """Generates face encodings (embeddings) from face images."""
    
    def __init__(self, num_jitters: int = 1):
        """
        Initialize the face encoder.
        
        Args:
            num_jitters: Number of times to resample the face when encoding
        """
        self.num_jitters = num_jitters
        self.encoding_count = 0
    
    def encode_face(self, image: np.ndarray, 
                   face_location: Optional[Tuple[int, int, int, int]] = None,
                   num_jitters: Optional[int] = None) -> Optional[np.ndarray]:
        """
        Generate face encoding for a single face.
        
        Args:
            image: Image as numpy array (RGB)
            face_location: Specific face location to encode
            num_jitters: Number of jitters (overrides default)
            
        Returns:
            Face encoding as numpy array or None if encoding fails
        """
        try:
            if image is None or len(image.shape) != 3:
                return None
            
            jitters = num_jitters if num_jitters is not None else self.num_jitters
            
            if face_location:
                # Encode specific face
                face_encodings = face_recognition.face_encodings(
                    image,
                    known_face_locations=[face_location],
                    num_jitters=jitters
                )
            else:
                # Encode all faces and return first
                face_encodings = face_recognition.face_encodings(
                    image,
                    num_jitters=jitters
                )
            
            if face_encodings:
                self.encoding_count += 1
                return face_encodings[0]
            
            return None
            
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    def encode_multiple_faces(self, image: np.ndarray,
                             face_locations: List[Tuple[int, int, int, int]],
                             num_jitters: Optional[int] = None) -> List[Optional[np.ndarray]]:
        """
        Generate face encodings for multiple faces.
        
        Args:
            image: Image as numpy array (RGB)
            face_locations: List of face locations
            num_jitters: Number of jitters (overrides default)
            
        Returns:
            List of face encodings (None for failed encodings)
        """
        try:
            if not face_locations:
                return []
            
            jitters = num_jitters if num_jitters is not None else self.num_jitters
            
            face_encodings = face_recognition.face_encodings(
                image,
                known_face_locations=face_locations,
                num_jitters=jitters
            )
            
            self.encoding_count += len(face_encodings)
            
            # Ensure we return same number of encodings as locations
            encodings = []
            for i in range(len(face_locations)):
                if i < len(face_encodings):
                    encodings.append(face_encodings[i])
                else:
                    encodings.append(None)
            
            return encodings
            
        except Exception as e:
            print(f"Error encoding multiple faces: {e}")
            return [None] * len(face_locations)
    
    def encode_from_file(self, image_path: str) -> Optional[np.ndarray]:
        """
        Load an image and generate face encoding.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Face encoding or None if encoding fails
        """
        try:
            image = ImageUtils.load_image(image_path)
            if image is None:
                return None
            
            return self.encode_face(image)
            
        except Exception as e:
            print(f"Error encoding from file: {e}")
            return None
    
    def generate_average_encoding(self, encodings: List[np.ndarray]) -> Optional[np.ndarray]:
        """
        Generate an average encoding from multiple encodings of the same person.
        
        Args:
            encodings: List of face encodings for the same person
            
        Returns:
            Average encoding or None if input is empty
        """
        try:
            if not encodings:
                return None
            
            # Filter out None values
            valid_encodings = [e for e in encodings if e is not None]
            
            if not valid_encodings:
                return None
            
            # Calculate average
            average_encoding = np.mean(valid_encodings, axis=0)
            
            return average_encoding
            
        except Exception as e:
            print(f"Error generating average encoding: {e}")
            return None
    
    def normalize_encoding(self, encoding: np.ndarray) -> np.ndarray:
        """
        Normalize a face encoding.
        
        Args:
            encoding: Face encoding to normalize
            
        Returns:
            Normalized encoding
        """
        try:
            norm = np.linalg.norm(encoding)
            if norm > 0:
                return encoding / norm
            return encoding
        except Exception as e:
            print(f"Error normalizing encoding: {e}")
            return encoding
    
    def compare_encodings(self, encoding1: np.ndarray, 
                         encoding2: np.ndarray) -> float:
        """
        Compare two face encodings and return the distance.
        
        Args:
            encoding1: First face encoding
            encoding2: Second face encoding
            
        Returns:
            Euclidean distance between encodings
        """
        try:
            if encoding1 is None or encoding2 is None:
                return float('inf')
            
            return np.linalg.norm(encoding1 - encoding2)
            
        except Exception as e:
            print(f"Error comparing encodings: {e}")
            return float('inf')
    
    def set_num_jitters(self, num_jitters: int) -> None:
        """
        Set the number of jitters for encoding.
        
        Args:
            num_jitters: Number of jitters (1-10)
        """
        self.num_jitters = max(1, min(10, num_jitters))
    
    def get_statistics(self) -> dict:
        """
        Get encoder statistics.
        
        Returns:
            Dictionary with encoder statistics
        """
        return {
            'num_jitters': self.num_jitters,
            'total_encodings': self.encoding_count
        }
    
    def reset_statistics(self) -> None:
        """Reset encoder statistics."""
        self.encoding_count = 0


if __name__ == "__main__":
    # Test face encoder
    encoder = FaceEncoder()
    
    # Create a test image
    test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    
    # Test encoding
    encoding = encoder.encode_face(test_image)
    print(f"Encoding shape: {encoding.shape if encoding is not None else 'None'}")
    
    # Test encoding from file (will fail but test the method)
    encoding = encoder.encode_from_file("nonexistent.jpg")
    print(f"Encoding from file: {encoding}")
    
    # Get statistics
    stats = encoder.get_statistics()
    print(f"Encoder statistics: {stats}")
