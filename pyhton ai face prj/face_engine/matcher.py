"""
Face Matching Module
Handles comparison of face encodings and matching against known faces.
"""

import numpy as np
from typing import Dict, Optional, Tuple, List
from utils.helpers import Helpers


class FaceMatcher:
    """Matches face encodings against known face database."""
    
    def __init__(self, threshold: float = 0.6):
        """
        Initialize the face matcher.
        
        Args:
            threshold: Recognition threshold (lower = stricter matching)
        """
        self.threshold = threshold
        self.match_count = 0
        self.comparison_count = 0
    
    def find_best_match(self, face_encoding: np.ndarray,
                      known_faces: Dict[str, np.ndarray]) -> Dict[str, any]:
        """
        Find the best matching person for a face encoding.
        
        Args:
            face_encoding: Face encoding to match
            known_faces: Dictionary mapping person_id to face encoding
            
        Returns:
            Dictionary with match results
        """
        try:
            if face_encoding is None or not known_faces:
                return {
                    'matched': False,
                    'person_id': None,
                    'distance': float('inf'),
                    'confidence': 0.0
                }
            
            best_person_id = None
            best_distance = float('inf')
            
            # Compare against all known faces
            for person_id, known_encoding in known_faces.items():
                if known_encoding is None:
                    continue
                
                distance = self.compare_faces(face_encoding, known_encoding)
                
                if distance < best_distance:
                    best_distance = distance
                    best_person_id = person_id
            
            # Check if best match is within threshold
            if best_distance <= self.threshold:
                self.match_count += 1
                confidence = Helpers.calculate_similarity(best_distance, self.threshold)
                
                return {
                    'matched': True,
                    'person_id': best_person_id,
                    'distance': best_distance,
                    'confidence': confidence
                }
            else:
                # Calculate confidence even for unknown faces
                confidence = Helpers.calculate_similarity(best_distance, self.threshold)
                
                return {
                    'matched': False,
                    'person_id': None,
                    'distance': best_distance,
                    'confidence': confidence
                }
            
        except Exception as e:
            print(f"Error finding best match: {e}")
            return {
                'matched': False,
                'person_id': None,
                'distance': float('inf'),
                'confidence': 0.0
            }
    
    def compare_faces(self, encoding1: np.ndarray, encoding2: np.ndarray) -> float:
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
            
            self.comparison_count += 1
            return np.linalg.norm(encoding1 - encoding2)
            
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return float('inf')
    
    def batch_compare(self, face_encoding: np.ndarray,
                     known_faces: Dict[str, np.ndarray]) -> Dict[str, float]:
        """
        Compare a face encoding against all known faces.
        
        Args:
            face_encoding: Face encoding to compare
            known_faces: Dictionary mapping person_id to face encoding
            
        Returns:
            Dictionary mapping person_id to distance
        """
        try:
            if face_encoding is None:
                return {}
            
            distances = {}
            
            for person_id, known_encoding in known_faces.items():
                if known_encoding is not None:
                    distance = self.compare_faces(face_encoding, known_encoding)
                    distances[person_id] = distance
            
            return distances
            
        except Exception as e:
            print(f"Error in batch comparison: {e}")
            return {}
    
    def find_all_matches(self, face_encoding: np.ndarray,
                        known_faces: Dict[str, np.ndarray],
                        max_results: int = 5) -> List[Tuple[str, float]]:
        """
        Find all potential matches sorted by distance.
        
        Args:
            face_encoding: Face encoding to match
            known_faces: Dictionary mapping person_id to face encoding
            max_results: Maximum number of results to return
            
        Returns:
            List of (person_id, distance) tuples sorted by distance
        """
        try:
            distances = self.batch_compare(face_encoding, known_faces)
            
            # Sort by distance
            sorted_distances = sorted(distances.items(), key=lambda x: x[1])
            
            return sorted_distances[:max_results]
            
        except Exception as e:
            print(f"Error finding all matches: {e}")
            return []
    
    def verify_match(self, face_encoding: np.ndarray,
                    known_encoding: np.ndarray) -> bool:
        """
        Verify if a face encoding matches a known encoding.
        
        Args:
            face_encoding: Face encoding to verify
            known_encoding: Known face encoding to compare against
            
        Returns:
            True if match is within threshold, False otherwise
        """
        distance = self.compare_faces(face_encoding, known_encoding)
        return distance <= self.threshold
    
    def set_threshold(self, threshold: float) -> None:
        """
        Set the recognition threshold.
        
        Args:
            threshold: Recognition threshold (0.0 to 1.0)
        """
        from utils.validators import Validators
        
        is_valid, _ = Validators.validate_recognition_threshold(threshold)
        if is_valid:
            self.threshold = threshold
    
    def get_threshold(self) -> float:
        """Get the current recognition threshold."""
        return self.threshold
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get matcher statistics.
        
        Returns:
            Dictionary with matcher statistics
        """
        return {
            'threshold': self.threshold,
            'total_matches': self.match_count,
            'total_comparisons': self.comparison_count,
            'match_rate': self.match_count / self.comparison_count if self.comparison_count > 0 else 0.0
        }
    
    def reset_statistics(self) -> None:
        """Reset matcher statistics."""
        self.match_count = 0
        self.comparison_count = 0


if __name__ == "__main__":
    # Test face matcher
    matcher = FaceMatcher(threshold=0.6)
    
    # Create test encodings
    encoding1 = np.random.rand(128)
    encoding2 = np.random.rand(128)
    encoding3 = np.random.rand(128)
    
    # Test comparison
    distance = matcher.compare_faces(encoding1, encoding2)
    print(f"Distance between encoding1 and encoding2: {distance:.4f}")
    
    # Test best match
    known_faces = {
        'PERSON001': encoding1,
        'PERSON002': encoding2
    }
    
    result = matcher.find_best_match(encoding3, known_faces)
    print(f"Best match result: {result}")
    
    # Test batch comparison
    distances = matcher.batch_compare(encoding3, known_faces)
    print(f"Batch comparison distances: {distances}")
    
    # Get statistics
    stats = matcher.get_statistics()
    print(f"Matcher statistics: {stats}")
