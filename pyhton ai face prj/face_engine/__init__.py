"""
Face Engine Package
Provides face detection, encoding, recognition, matching, and tracking capabilities.
"""

from face_engine.detector import FaceDetector
from face_engine.encoder import FaceEncoder
from face_engine.recognizer import FaceRecognizer, FaceRecognitionResult
from face_engine.matcher import FaceMatcher
from face_engine.tracker import FaceTracker, TrackedFace

__all__ = [
    'FaceDetector',
    'FaceEncoder',
    'FaceRecognizer',
    'FaceRecognitionResult',
    'FaceMatcher',
    'FaceTracker',
    'TrackedFace'
]
