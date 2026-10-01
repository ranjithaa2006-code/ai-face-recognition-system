"""
Face Detection Module
Handles face detection in images and video frames.
"""

import cv2
import numpy as np
import face_recognition
from typing import List, Tuple, Optional
from utils.image_utils import ImageUtils


class FaceDetector:
    """Detects faces in images using face_recognition library."""
    
    def __init__(self, model: str = 'hog', min_face_size: int = 100):
        """
        Initialize the face detector.
        
        Args:
            model: Detection model ('hog' for CPU, 'cnn' for GPU)
            min_face_size: Minimum face size in pixels
        """
        self.model = model
        self.min_face_size = min_face_size
        self.detection_count = 0
    
    def detect_faces(self, image: np.ndarray, 
                    upscale: int = 1) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.
        
        Args:
            image: Image as numpy array (RGB)
            upscale: Number of times to upscale the image
            
        Returns:
            List of face locations as (top, right, bottom, left)
        """
        try:
            if image is None or len(image.shape) != 3:
                return []
            
            # Resize image for faster detection if large
            height, width = image.shape[:2]
            if width > 800 or height > 800:
                scale_factor = 800 / max(width, height)
                small_image = ImageUtils.resize_image(image, scale_factor=scale_factor)
                
                # Detect faces in resized image
                face_locations = face_recognition.face_locations(
                    small_image, 
                    model=self.model,
                    number_of_times_to_upsample=upscale
                )
                
                # Scale locations back to original size
                scale_back = 1.0 / scale_factor
                scaled_locations = [
                    (int(top * scale_back), int(right * scale_back), 
                     int(bottom * scale_back), int(left * scale_back))
                    for top, right, bottom, left in face_locations
                ]
            else:
                # Detect faces in original image
                face_locations = face_recognition.face_locations(
                    image, 
                    model=self.model,
                    number_of_times_to_upsample=upscale
                )
                scaled_locations = face_locations
            
            # Filter by minimum face size
            filtered_locations = []
            for top, right, bottom, left in scaled_locations:
                face_height = bottom - top
                face_width = right - left
                if face_height >= self.min_face_size and face_width >= self.min_face_size:
                    filtered_locations.append((top, right, bottom, left))
            
            self.detection_count += len(filtered_locations)
            return filtered_locations
            
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    def detect_single_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect a single face in an image.
        
        Args:
            image: Image as numpy array (RGB)
            
        Returns:
            Single face location or None if no face/multiple faces detected
        """
        faces = self.detect_faces(image)
        
        if len(faces) == 1:
            return faces[0]
        elif len(faces) == 0:
            return None
        else:
            # Multiple faces detected, return the largest one
            faces_with_size = [
                (face, (face[2] - face[0]) * (face[1] - face[3]))
                for face in faces
            ]
            faces_with_size.sort(key=lambda x: x[1], reverse=True)
            return faces_with_size[0][0]
    
    def get_face_count(self, image: np.ndarray) -> int:
        """
        Get the number of faces in an image.
        
        Args:
            image: Image as numpy array (RGB)
            
        Returns:
            Number of faces detected
        """
        return len(self.detect_faces(image))
    
    def set_model(self, model: str) -> None:
        """
        Set the detection model.
        
        Args:
            model: Detection model ('hog' or 'cnn')
        """
        if model in ['hog', 'cnn']:
            self.model = model
    
    def set_min_face_size(self, size: int) -> None:
        """
        Set the minimum face size.
        
        Args:
            size: Minimum face size in pixels
        """
        self.min_face_size = max(50, min(500, size))
    
    def get_statistics(self) -> dict:
        """
        Get detector statistics.
        
        Returns:
            Dictionary with detector statistics
        """
        return {
            'model': self.model,
            'min_face_size': self.min_face_size,
            'total_detections': self.detection_count
        }
    
    def reset_statistics(self) -> None:
        """Reset detector statistics."""
        self.detection_count = 0


if __name__ == "__main__":
    # Test face detector
    detector = FaceDetector()
    
    # Create a test image
    test_image = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Test detection
    faces = detector.detect_faces(test_image)
    print(f"Detected {len(faces)} faces in test image")
    
    # Test single face detection
    single_face = detector.detect_single_face(test_image)
    print(f"Single face detection: {single_face}")
    
    # Get statistics
    stats = detector.get_statistics()
    print(f"Detector statistics: {stats}")
