"""
Face Recognition Module
Handles the complete face recognition pipeline.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from face_engine.detector import FaceDetector
from face_engine.encoder import FaceEncoder
from face_engine.matcher import FaceMatcher
from utils.helpers import Helpers


class FaceRecognitionResult:
    """Represents the result of face recognition for a single face."""
    
    def __init__(self, face_location: Tuple[int, int, int, int],
                 person_id: Optional[str] = None,
                 person_name: Optional[str] = None,
                 confidence: float = 0.0,
                 distance: float = float('inf'),
                 is_known: bool = False):
        self.face_location = face_location
        self.person_id = person_id
        self.person_name = person_name
        self.confidence = confidence
        self.distance = distance
        self.is_known = is_known
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'face_location': self.face_location,
            'person_id': self.person_id,
            'person_name': self.person_name,
            'confidence': self.confidence,
            'distance': self.distance,
            'is_known': self.is_known
        }


class FaceRecognizer:
    """Complete face recognition pipeline combining detection, encoding, and matching."""
    
    def __init__(self, recognition_threshold: float = 0.6,
                 detection_model: str = 'hog',
                 min_face_size: int = 100):
        """
        Initialize the face recognizer.
        
        Args:
            recognition_threshold: Threshold for face recognition (lower = stricter)
            detection_model: Face detection model ('hog' or 'cnn')
            min_face_size: Minimum face size in pixels
        """
        self.detector = FaceDetector(model=detection_model, min_face_size=min_face_size)
        self.encoder = FaceEncoder()
        self.matcher = FaceMatcher(threshold=recognition_threshold)
        
        self.recognition_threshold = recognition_threshold
        self.recognition_count = 0
        self.unknown_count = 0
    
    def recognize_faces(self, image: np.ndarray,
                       known_faces: Dict[str, np.ndarray],
                       known_names: Dict[str, str] = None) -> List[FaceRecognitionResult]:
        """
        Recognize faces in an image.
        
        Args:
            image: Image as numpy array (RGB)
            known_faces: Dictionary mapping person_id to face encoding
            known_names: Optional dictionary mapping person_id to person name
            
        Returns:
            List of FaceRecognitionResult objects
        """
        try:
            if image is None:
                return []
            
            # Detect faces
            face_locations = self.detector.detect_faces(image)
            
            if not face_locations:
                return []
            
            # Encode faces
            face_encodings = self.encoder.encode_multiple_faces(
                image,
                face_locations
            )
            
            # Match faces
            results = []
            for i, (location, encoding) in enumerate(zip(face_locations, face_encodings)):
                if encoding is None:
                    # Failed to encode
                    results.append(FaceRecognitionResult(
                        face_location=location,
                        is_known=False,
                        confidence=0.0,
                        distance=float('inf')
                    ))
                    continue
                
                # Find best match
                match_result = self.matcher.find_best_match(encoding, known_faces)
                
                if match_result['matched']:
                    self.recognition_count += 1
                    person_id = match_result['person_id']
                    person_name = known_names.get(person_id, person_id) if known_names else person_id
                    
                    results.append(FaceRecognitionResult(
                        face_location=location,
                        person_id=person_id,
                        person_name=person_name,
                        confidence=match_result['confidence'],
                        distance=match_result['distance'],
                        is_known=True
                    ))
                else:
                    self.unknown_count += 1
                    results.append(FaceRecognitionResult(
                        face_location=location,
                        person_id=None,
                        person_name="UNKNOWN",
                        confidence=match_result['confidence'],
                        distance=match_result['distance'],
                        is_known=False
                    ))
            
            return results
            
        except Exception as e:
            print(f"Error recognizing faces: {e}")
            return []
    
    def recognize_single_face(self, image: np.ndarray,
                             known_faces: Dict[str, np.ndarray],
                             known_names: Dict[str, str] = None) -> Optional[FaceRecognitionResult]:
        """
        Recognize a single face in an image.
        
        Args:
            image: Image as numpy array (RGB)
            known_faces: Dictionary mapping person_id to face encoding
            known_names: Optional dictionary mapping person_id to person name
            
        Returns:
            FaceRecognitionResult or None if no face detected
        """
        results = self.recognize_faces(image, known_faces, known_names)
        
        if results:
            return results[0]
        return None
    
    def recognize_from_file(self, image_path: str,
                           known_faces: Dict[str, np.ndarray],
                           known_names: Dict[str, str] = None) -> List[FaceRecognitionResult]:
        """
        Recognize faces in an image file.
        
        Args:
            image_path: Path to the image file
            known_faces: Dictionary mapping person_id to face encoding
            known_names: Optional dictionary mapping person_id to person name
            
        Returns:
            List of FaceRecognitionResult objects
        """
        from utils.image_utils import ImageUtils
        
        try:
            image = ImageUtils.load_image(image_path)
            if image is None:
                return []
            
            return self.recognize_faces(image, known_faces, known_names)
            
        except Exception as e:
            print(f"Error recognizing from file: {e}")
            return []
    
    def register_face(self, image: np.ndarray,
                     person_id: str,
                     existing_encoding: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        """
        Register a face by generating its encoding.
        
        Args:
            image: Image as numpy array (RGB)
            person_id: Person ID for the face
            existing_encoding: Existing encoding to average with (optional)
            
        Returns:
            Face encoding or None if registration fails
        """
        try:
            # Detect single face
            face_location = self.detector.detect_single_face(image)
            
            if face_location is None:
                return None
            
            # Encode face
            encoding = self.encoder.encode_face(image, face_location)
            
            if encoding is None:
                return None
            
            # Average with existing encoding if provided
            if existing_encoding is not None:
                encoding = self.encoder.generate_average_encoding([encoding, existing_encoding])
            
            return encoding
            
        except Exception as e:
            print(f"Error registering face: {e}")
            return None
    
    def register_face_from_multiple_images(self, images: List[np.ndarray],
                                         person_id: str) -> Optional[np.ndarray]:
        """
        Register a face from multiple images for better accuracy.
        
        Args:
            images: List of images as numpy arrays (RGB)
            person_id: Person ID for the face
            
        Returns:
            Average face encoding or None if registration fails
        """
        try:
            encodings = []
            
            for image in images:
                encoding = self.register_face(image, person_id)
                if encoding is not None:
                    encodings.append(encoding)
            
            if not encodings:
                return None
            
            # Generate average encoding
            average_encoding = self.encoder.generate_average_encoding(encodings)
            
            return average_encoding
            
        except Exception as e:
            print(f"Error registering face from multiple images: {e}")
            return None
    
    def set_recognition_threshold(self, threshold: float) -> None:
        """
        Set the recognition threshold.
        
        Args:
            threshold: Recognition threshold (0.0 to 1.0)
        """
        from utils.validators import Validators
        
        is_valid, _ = Validators.validate_recognition_threshold(threshold)
        if is_valid:
            self.recognition_threshold = threshold
            self.matcher.set_threshold(threshold)
    
    def set_detection_model(self, model: str) -> None:
        """
        Set the detection model.
        
        Args:
            model: Detection model ('hog' or 'cnn')
        """
        self.detector.set_model(model)
    
    def set_min_face_size(self, size: int) -> None:
        """
        Set the minimum face size.
        
        Args:
            size: Minimum face size in pixels
        """
        self.detector.set_min_face_size(size)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get recognizer statistics.
        
        Returns:
            Dictionary with recognizer statistics
        """
        detector_stats = self.detector.get_statistics()
        encoder_stats = self.encoder.get_statistics()
        matcher_stats = self.matcher.get_statistics()
        
        return {
            'recognition_threshold': self.recognition_threshold,
            'total_recognitions': self.recognition_count,
            'total_unknown': self.unknown_count,
            'detector': detector_stats,
            'encoder': encoder_stats,
            'matcher': matcher_stats
        }
    
    def reset_statistics(self) -> None:
        """Reset recognizer statistics."""
        self.recognition_count = 0
        self.unknown_count = 0
        self.detector.reset_statistics()
        self.encoder.reset_statistics()
        self.matcher.reset_statistics()


if __name__ == "__main__":
    # Test face recognizer
    recognizer = FaceRecognizer()
    
    # Create a test image
    test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    
    # Test recognition with empty known faces
    results = recognizer.recognize_faces(test_image, {})
    print(f"Recognition results: {len(results)} faces")
    
    # Get statistics
    stats = recognizer.get_statistics()
    print(f"Recognizer statistics: {stats}")
