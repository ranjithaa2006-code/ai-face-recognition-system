"""
Face Engine Tests
Tests for face detection, encoding, recognition, matching, and tracking.
"""

import pytest
import numpy as np
from face_engine.detector import FaceDetector
from face_engine.encoder import FaceEncoder
from face_engine.matcher import FaceMatcher
from face_engine.recognizer import FaceRecognizer, FaceRecognitionResult
from face_engine.tracker import FaceTracker


class TestFaceDetector:
    """Tests for face detector operations."""
    
    @pytest.fixture
    def detector(self):
        """Create face detector."""
        return FaceDetector(model='hog', min_face_size=100)
    
    def test_detector_initialization(self, detector):
        """Test detector initialization."""
        assert detector.model == 'hog'
        assert detector.min_face_size == 100
    
    def test_detect_faces_empty_image(self, detector):
        """Test face detection on empty/random image."""
        # Create a random image (no real faces)
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        faces = detector.detect_faces(test_image)
        # Random image shouldn't have detectable faces
        assert isinstance(faces, list)
    
    def test_detect_faces_none_image(self, detector):
        """Test face detection with None image."""
        faces = detector.detect_faces(None)
        assert faces == []
    
    def test_detect_single_face(self, detector):
        """Test single face detection."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        single_face = detector.detect_single_face(test_image)
        # Should return None if no face detected
        assert single_face is None or isinstance(single_face, tuple)
    
    def test_get_face_count(self, detector):
        """Test getting face count."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        count = detector.get_face_count(test_image)
        assert isinstance(count, int)
        assert count >= 0
    
    def test_set_model(self, detector):
        """Test setting detection model."""
        detector.set_model('cnn')
        assert detector.model == 'cnn'
    
    def test_set_min_face_size(self, detector):
        """Test setting minimum face size."""
        detector.set_min_face_size(150)
        assert detector.min_face_size == 150
    
    def test_get_statistics(self, detector):
        """Test getting detector statistics."""
        stats = detector.get_statistics()
        assert 'model' in stats
        assert 'min_face_size' in stats
        assert 'total_detections' in stats


class TestFaceEncoder:
    """Tests for face encoder operations."""
    
    @pytest.fixture
    def encoder(self):
        """Create face encoder."""
        return FaceEncoder(num_jitters=1)
    
    def test_encoder_initialization(self, encoder):
        """Test encoder initialization."""
        assert encoder.num_jitters == 1
    
    def test_encode_face_none_image(self, encoder):
        """Test face encoding with None image."""
        encoding = encoder.encode_face(None)
        assert encoding is None
    
    def test_encode_face_random_image(self, encoder):
        """Test face encoding on random image."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        encoding = encoder.encode_face(test_image)
        # Random image might not produce valid encoding
        # Just test that it doesn't crash
        assert encoding is None or isinstance(encoding, np.ndarray)
    
    def test_encode_multiple_faces(self, encoder):
        """Test encoding multiple faces."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        face_locations = [(50, 100, 150, 100)]
        
        encodings = encoder.encode_multiple_faces(test_image, face_locations)
        assert isinstance(encodings, list)
        assert len(encodings) == 1
    
    def test_generate_average_encoding(self, encoder):
        """Test generating average encoding."""
        encoding1 = np.random.rand(128)
        encoding2 = np.random.rand(128)
        
        average = encoder.generate_average_encoding([encoding1, encoding2])
        assert average is not None
        assert isinstance(average, np.ndarray)
        assert average.shape == (128,)
    
    def test_generate_average_encoding_empty(self, encoder):
        """Test generating average encoding with empty list."""
        average = encoder.generate_average_encoding([])
        assert average is None
    
    def test_normalize_encoding(self, encoder):
        """Test encoding normalization."""
        encoding = np.random.rand(128)
        
        normalized = encoder.normalize_encoding(encoding)
        assert isinstance(normalized, np.ndarray)
        assert normalized.shape == encoding.shape
    
    def test_compare_encodings(self, encoder):
        """Test comparing two encodings."""
        encoding1 = np.random.rand(128)
        encoding2 = np.random.rand(128)
        
        distance = encoder.compare_encodings(encoding1, encoding2)
        assert isinstance(distance, float)
        assert distance >= 0
    
    def test_compare_encodings_none(self, encoder):
        """Test comparing with None encoding."""
        encoding = np.random.rand(128)
        
        distance = encoder.compare_encodings(encoding, None)
        assert distance == float('inf')
    
    def test_set_num_jitters(self, encoder):
        """Test setting number of jitters."""
        encoder.set_num_jitters(5)
        assert encoder.num_jitters == 5


class TestFaceMatcher:
    """Tests for face matcher operations."""
    
    @pytest.fixture
    def matcher(self):
        """Create face matcher."""
        return FaceMatcher(threshold=0.6)
    
    def test_matcher_initialization(self, matcher):
        """Test matcher initialization."""
        assert matcher.threshold == 0.6
    
    def test_find_best_match_empty_known_faces(self, matcher):
        """Test finding best match with empty known faces."""
        test_encoding = np.random.rand(128)
        
        result = matcher.find_best_match(test_encoding, {})
        assert result['matched'] is False
        assert result['person_id'] is None
    
    def test_find_best_match_none_encoding(self, matcher):
        """Test finding best match with None encoding."""
        known_faces = {'PERSON001': np.random.rand(128)}
        
        result = matcher.find_best_match(None, known_faces)
        assert result['matched'] is False
    
    def test_compare_faces(self, matcher):
        """Test comparing two faces."""
        encoding1 = np.random.rand(128)
        encoding2 = np.random.rand(128)
        
        distance = matcher.compare_faces(encoding1, encoding2)
        assert isinstance(distance, float)
        assert distance >= 0
    
    def test_batch_compare(self, matcher):
        """Test batch comparison."""
        test_encoding = np.random.rand(128)
        known_faces = {
            'PERSON001': np.random.rand(128),
            'PERSON002': np.random.rand(128)
        }
        
        distances = matcher.batch_compare(test_encoding, known_faces)
        assert isinstance(distances, dict)
        assert len(distances) == 2
    
    def test_find_all_matches(self, matcher):
        """Test finding all matches."""
        test_encoding = np.random.rand(128)
        known_faces = {
            'PERSON001': np.random.rand(128),
            'PERSON002': np.random.rand(128),
            'PERSON003': np.random.rand(128)
        }
        
        matches = matcher.find_all_matches(test_encoding, known_faces, max_results=2)
        assert isinstance(matches, list)
        assert len(matches) <= 2
    
    def test_verify_match(self, matcher):
        """Test verifying a match."""
        encoding1 = np.random.rand(128)
        encoding2 = np.random.rand(128)
        
        # Random encodings likely won't match within threshold
        result = matcher.verify_match(encoding1, encoding2)
        assert isinstance(result, bool)
    
    def test_set_threshold(self, matcher):
        """Test setting recognition threshold."""
        matcher.set_threshold(0.5)
        assert matcher.threshold == 0.5
    
    def test_get_statistics(self, matcher):
        """Test getting matcher statistics."""
        stats = matcher.get_statistics()
        assert 'threshold' in stats
        assert 'total_matches' in stats
        assert 'total_comparisons' in stats


class TestFaceRecognizer:
    """Tests for face recognizer operations."""
    
    @pytest.fixture
    def recognizer(self):
        """Create face recognizer."""
        return FaceRecognizer(recognition_threshold=0.6)
    
    def test_recognizer_initialization(self, recognizer):
        """Test recognizer initialization."""
        assert recognizer.recognition_threshold == 0.6
    
    def test_recognize_faces_none_image(self, recognizer):
        """Test face recognition with None image."""
        results = recognizer.recognize_faces(None, {})
        assert results == []
    
    def test_recognize_faces_empty_known_faces(self, recognizer):
        """Test face recognition with empty known faces."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        results = recognizer.recognize_faces(test_image, {})
        assert isinstance(results, list)
    
    def test_recognize_single_face(self, recognizer):
        """Test single face recognition."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        result = recognizer.recognize_single_face(test_image, {})
        assert result is None or isinstance(result, FaceRecognitionResult)
    
    def test_register_face_none_image(self, recognizer):
        """Test face registration with None image."""
        encoding = recognizer.register_face(None, "TEST001")
        assert encoding is None
    
    def test_register_face_random_image(self, recognizer):
        """Test face registration with random image."""
        test_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        
        encoding = recognizer.register_face(test_image, "TEST001")
        # Random image might not produce valid encoding
        assert encoding is None or isinstance(encoding, np.ndarray)
    
    def test_register_face_from_multiple_images(self, recognizer):
        """Test face registration from multiple images."""
        images = [
            np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
            for _ in range(3)
        ]
        
        encoding = recognizer.register_face_from_multiple_images(images, "TEST001")
        # Random images might not produce valid encoding
        assert encoding is None or isinstance(encoding, np.ndarray)
    
    def test_set_recognition_threshold(self, recognizer):
        """Test setting recognition threshold."""
        recognizer.set_recognition_threshold(0.5)
        assert recognizer.recognition_threshold == 0.5
    
    def test_get_statistics(self, recognizer):
        """Test getting recognizer statistics."""
        stats = recognizer.get_statistics()
        assert 'recognition_threshold' in stats
        assert 'total_recognitions' in stats
        assert 'total_unknown' in stats


class TestFaceTracker:
    """Tests for face tracker operations."""
    
    @pytest.fixture
    def tracker(self):
        """Create face tracker."""
        return FaceTracker(max_distance=100.0, max_frames_lost=10)
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initialization."""
        assert tracker.max_distance == 100.0
        assert tracker.max_frames_lost == 10
    
    def test_update_empty_faces(self, tracker):
        """Test tracker update with empty faces."""
        results = tracker.update([])
        assert isinstance(results, list)
    
    def test_update_with_faces(self, tracker):
        """Test tracker update with face detections."""
        current_faces = [
            {
                'face_location': (100, 200, 300, 200),
                'person_id': 'PERSON001',
                'person_name': 'John Doe',
                'confidence': 95.0,
                'distance': 0.3,
                'is_known': True
            }
        ]
        
        results = tracker.update(current_faces)
        assert isinstance(results, list)
        assert len(results) >= 1
    
    def test_reset(self, tracker):
        """Test tracker reset."""
        tracker.reset()
        assert len(tracker.tracked_faces) == 0
        assert tracker.next_face_id == 1
    
    def test_get_statistics(self, tracker):
        """Test getting tracker statistics."""
        stats = tracker.get_statistics()
        assert 'total_tracked_faces' in stats
        assert 'stable_faces' in stats
        assert 'frame_count' in stats
    
    def test_set_max_distance(self, tracker):
        """Test setting max distance."""
        tracker.set_max_distance(150.0)
        assert tracker.max_distance == 150.0
    
    def test_set_max_frames_lost(self, tracker):
        """Test setting max frames lost."""
        tracker.set_max_frames_lost(15)
        assert tracker.max_frames_lost == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
