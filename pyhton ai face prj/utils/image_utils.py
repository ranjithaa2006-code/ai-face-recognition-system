"""
Image processing utilities for the Face Recognition System
Handles image loading, processing, conversion, and face-related operations.
"""

import cv2
import numpy as np
from PIL import Image, ImageTk
import face_recognition
from pathlib import Path
from typing import Optional, Tuple, List
import io


class ImageUtils:
    """Utility class for image processing operations."""
    
    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        """
        Load an image from file.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image as numpy array or None if loading fails
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return None
            return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str) -> bool:
        """
        Save an image to file.
        
        Args:
            image: Image as numpy array
            output_path: Path where to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert RGB to BGR for OpenCV
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = image
            
            return cv2.imwrite(output_path, image_bgr)
        except Exception as e:
            print(f"Error saving image: {e}")
            return False
    
    @staticmethod
    def resize_image(image: np.ndarray, target_size: Tuple[int, int] = None, 
                    scale_factor: float = None) -> np.ndarray:
        """
        Resize an image.
        
        Args:
            image: Image as numpy array
            target_size: Target size as (width, height)
            scale_factor: Scale factor (e.g., 0.5 for half size)
            
        Returns:
            Resized image
        """
        try:
            if target_size:
                return cv2.resize(image, target_size)
            elif scale_factor:
                width = int(image.shape[1] * scale_factor)
                height = int(image.shape[0] * scale_factor)
                return cv2.resize(image, (width, height))
            else:
                return image
        except Exception as e:
            print(f"Error resizing image: {e}")
            return image
    
    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Grayscale image
        """
        try:
            if len(image.shape) == 3:
                return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            return image
        except Exception as e:
            print(f"Error converting to grayscale: {e}")
            return image
    
    @staticmethod
    def convert_color_space(image: np.ndarray, from_space: str = 'RGB', 
                           to_space: str = 'BGR') -> np.ndarray:
        """
        Convert image between color spaces.
        
        Args:
            image: Image as numpy array
            from_space: Source color space (RGB, BGR, GRAY)
            to_space: Target color space (RGB, BGR, GRAY)
            
        Returns:
            Converted image
        """
        try:
            if from_space == to_space:
                return image
            
            conversion_map = {
                ('RGB', 'BGR'): cv2.COLOR_RGB2BGR,
                ('BGR', 'RGB'): cv2.COLOR_BGR2RGB,
                ('RGB', 'GRAY'): cv2.COLOR_RGB2GRAY,
                ('BGR', 'GRAY'): cv2.COLOR_BGR2GRAY,
                ('GRAY', 'RGB'): cv2.COLOR_GRAY2RGB,
                ('GRAY', 'BGR'): cv2.COLOR_GRAY2BGR
            }
            
            conversion_code = conversion_map.get((from_space, to_space))
            if conversion_code:
                return cv2.cvtColor(image, conversion_code)
            
            return image
        except Exception as e:
            print(f"Error converting color space: {e}")
            return image
    
    @staticmethod
    def detect_faces(image: np.ndarray, model: str = 'hog', 
                    min_face_size: int = 100) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces in an image.
        
        Args:
            image: Image as numpy array (RGB)
            model: Detection model ('hog' or 'cnn')
            min_face_size: Minimum face size in pixels
            
        Returns:
            List of face locations as (top, right, bottom, left)
        """
        try:
            # Resize image for faster detection if needed
            small_image = ImageUtils.resize_image(image, scale_factor=0.25)
            
            # Detect faces
            face_locations = face_recognition.face_locations(
                small_image, 
                model=model
            )
            
            # Scale face locations back to original image size
            scale_factor = 4
            scaled_locations = [
                (int(top * scale_factor), int(right * scale_factor), 
                 int(bottom * scale_factor), int(left * scale_factor))
                for top, right, bottom, left in face_locations
            ]
            
            # Filter by minimum face size
            filtered_locations = []
            for top, right, bottom, left in scaled_locations:
                height = bottom - top
                width = right - left
                if height >= min_face_size and width >= min_face_size:
                    filtered_locations.append((top, right, bottom, left))
            
            return filtered_locations
        except Exception as e:
            print(f"Error detecting faces: {e}")
            return []
    
    @staticmethod
    def encode_face(image: np.ndarray, 
                   face_location: Tuple[int, int, int, int] = None) -> Optional[np.ndarray]:
        """
        Generate face encoding (embedding) from an image.
        
        Args:
            image: Image as numpy array (RGB)
            face_location: Specific face location to encode
            
        Returns:
            Face encoding as numpy array or None if encoding fails
        """
        try:
            if face_location:
                face_encodings = face_recognition.face_encodings(
                    image, 
                    known_face_locations=[face_location]
                )
            else:
                face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                return face_encodings[0]
            return None
        except Exception as e:
            print(f"Error encoding face: {e}")
            return None
    
    @staticmethod
    def draw_face_box(image: np.ndarray, face_location: Tuple[int, int, int, int],
                     label: str = "", color: Tuple[int, int, int] = (0, 255, 0),
                     confidence: float = None) -> np.ndarray:
        """
        Draw a bounding box around a face with label.
        
        Args:
            image: Image as numpy array
            face_location: Face location as (top, right, bottom, left)
            label: Label to display above the face
            color: Box color as (R, G, B)
            confidence: Confidence score to display
            
        Returns:
            Image with drawn box and label
        """
        try:
            image_copy = image.copy()
            top, right, bottom, left = face_location
            
            # Draw rectangle
            cv2.rectangle(image_copy, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            if label:
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 0.6
                thickness = 1
                
                # Build label text
                label_text = label
                if confidence is not None:
                    label_text += f" ({confidence:.1f}%)"
                
                # Get text size
                (text_width, text_height), baseline = cv2.getTextSize(
                    label_text, font, font_scale, thickness
                )
                
                # Draw label background
                cv2.rectangle(
                    image_copy,
                    (left, top - text_height - 10),
                    (left + text_width + 10, top),
                    color,
                    -1
                )
                
                # Draw label text
                cv2.putText(
                    image_copy,
                    label_text,
                    (left + 5, top - 5),
                    font,
                    font_scale,
                    (255, 255, 255),
                    thickness
                )
            
            return image_copy
        except Exception as e:
            print(f"Error drawing face box: {e}")
            return image
    
    @staticmethod
    def extract_face(image: np.ndarray, 
                    face_location: Tuple[int, int, int, int],
                    padding: int = 0) -> np.ndarray:
        """
        Extract face region from image.
        
        Args:
            image: Image as numpy array
            face_location: Face location as (top, right, bottom, left)
            padding: Padding around the face
            
        Returns:
            Extracted face image
        """
        try:
            top, right, bottom, left = face_location
            
            # Add padding
            top = max(0, top - padding)
            left = max(0, left - padding)
            bottom = min(image.shape[0], bottom + padding)
            right = min(image.shape[1], right + padding)
            
            return image[top:bottom, left:right]
        except Exception as e:
            print(f"Error extracting face: {e}")
            return image
    
    @staticmethod
    def convert_to_pil_image(image: np.ndarray) -> Image.Image:
        """
        Convert numpy array to PIL Image.
        
        Args:
            image: Image as numpy array (RGB)
            
        Returns:
            PIL Image
        """
        try:
            return Image.fromarray(image)
        except Exception as e:
            print(f"Error converting to PIL Image: {e}")
            return Image.new('RGB', (100, 100))
    
    @staticmethod
    def convert_to_photoimage(image: np.ndarray) -> ImageTk.PhotoImage:
        """
        Convert numpy array to PhotoImage for Tkinter.
        
        Args:
            image: Image as numpy array (RGB)
            
        Returns:
            PhotoImage for use in Tkinter
        """
        try:
            pil_image = ImageUtils.convert_to_pil_image(image)
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print(f"Error converting to PhotoImage: {e}")
            return None
    
    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality using basic techniques.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Enhanced image
        """
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            
            # Split channels
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            lab = cv2.merge([l, a, b])
            
            # Convert back to RGB
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            return enhanced
        except Exception as e:
            print(f"Error enhancing image: {e}")
            return image
    
    @staticmethod
    def validate_image(image: np.ndarray) -> Tuple[bool, str]:
        """
        Validate an image for face recognition.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if image is None:
                return False, "Image is None"
            
            if len(image.shape) != 3:
                return False, "Image must be 3-dimensional (RGB)"
            
            if image.shape[2] != 3:
                return False, "Image must have 3 color channels (RGB)"
            
            if image.shape[0] < 100 or image.shape[1] < 100:
                return False, "Image is too small (minimum 100x100)"
            
            return True, "Image is valid"
        except Exception as e:
            return False, f"Error validating image: {e}"
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """
        Get information about an image.
        
        Args:
            image: Image as numpy array
            
        Returns:
            Dictionary with image information
        """
        try:
            return {
                'height': image.shape[0],
                'width': image.shape[1],
                'channels': image.shape[2] if len(image.shape) == 3 else 1,
                'dtype': str(image.dtype),
                'size': image.size
            }
        except Exception as e:
            print(f"Error getting image info: {e}")
            return {}


if __name__ == "__main__":
    # Test image utilities
    print("ImageUtils class loaded successfully")
    
    # Test validation
    test_image = np.zeros((200, 200, 3), dtype=np.uint8)
    is_valid, message = ImageUtils.validate_image(test_image)
    print(f"Image validation: {is_valid}, {message}")
    
    # Test image info
    info = ImageUtils.get_image_info(test_image)
    print(f"Image info: {info}")
