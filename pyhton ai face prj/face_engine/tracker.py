"""
Face Tracking Module
Handles tracking of faces across consecutive video frames to prevent flickering.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from utils.helpers import Helpers


@dataclass
class TrackedFace:
    """Represents a tracked face across frames."""
    face_id: int
    person_id: Optional[str]
    person_name: Optional[str]
    last_location: Tuple[int, int, int, int]
    confidence: float
    distance: float
    frames_seen: int
    frames_lost: int
    is_stable: bool


class FaceTracker:
    """Tracks faces across consecutive frames to provide stable recognition."""
    
    def __init__(self, max_distance: float = 100.0,
                 max_frames_lost: int = 10,
                 min_frames_for_stability: int = 3):
        """
        Initialize the face tracker.
        
        Args:
            max_distance: Maximum pixel distance for face matching across frames
            max_frames_lost: Maximum frames a face can be lost before being removed
            min_frames_for_stability: Minimum frames before a face is considered stable
        """
        self.max_distance = max_distance
        self.max_frames_lost = max_frames_lost
        self.min_frames_for_stability = min_frames_for_stability
        
        self.tracked_faces: Dict[int, TrackedFace] = {}
        self.next_face_id = 1
        self.frame_count = 0
    
    def update(self, current_faces: List[Dict]) -> List[Dict]:
        """
        Update tracked faces with current frame detections.
        
        Args:
            current_faces: List of current face detection results
            
        Returns:
            List of tracked face results with stable information
        """
        self.frame_count += 1
        
        if not current_faces:
            # No faces detected, increment lost frames for all tracked faces
            self._increment_lost_frames()
            return self._get_active_tracked_faces()
        
        # Match current faces to tracked faces
        matched_pairs = self._match_faces(current_faces)
        
        # Update matched faces
        for tracked_id, current_face in matched_pairs:
            self._update_tracked_face(tracked_id, current_face)
        
        # Create new tracked faces for unmatched current faces
        unmatched_current = self._get_unmatched_current(current_faces, matched_pairs)
        for current_face in unmatched_current:
            self._create_new_tracked_face(current_face)
        
        # Remove faces that have been lost too long
        self._remove_lost_faces()
        
        return self._get_active_tracked_faces()
    
    def _match_faces(self, current_faces: List[Dict]) -> List[Tuple[int, Dict]]:
        """
        Match current faces to tracked faces based on location.
        
        Args:
            current_faces: List of current face detection results
            
        Returns:
            List of (tracked_face_id, current_face) tuples
        """
        matched_pairs = []
        used_current_indices = set()
        
        for tracked_id, tracked_face in self.tracked_faces.items():
            if tracked_face.frames_lost > 0:
                continue  # Skip faces that were lost
            
            best_match_idx = None
            best_distance = float('inf')
            
            for i, current_face in enumerate(current_faces):
                if i in used_current_indices:
                    continue
                
                current_location = current_face.get('face_location')
                if current_location is None:
                    continue
                
                distance = self._calculate_location_distance(
                    tracked_face.last_location,
                    current_location
                )
                
                if distance < best_distance and distance <= self.max_distance:
                    best_distance = distance
                    best_match_idx = i
            
            if best_match_idx is not None:
                matched_pairs.append((tracked_id, current_faces[best_match_idx]))
                used_current_indices.add(best_match_idx)
        
        return matched_pairs
    
    def _calculate_location_distance(self, loc1: Tuple[int, int, int, int],
                                     loc2: Tuple[int, int, int, int]) -> float:
        """
        Calculate distance between two face locations (center points).
        
        Args:
            loc1: First face location (top, right, bottom, left)
            loc2: Second face location (top, right, bottom, left)
            
        Returns:
            Euclidean distance between center points
        """
        center1 = ((loc1[1] + loc1[3]) / 2, (loc1[0] + loc1[2]) / 2)
        center2 = ((loc2[1] + loc2[3]) / 2, (loc2[0] + loc2[2]) / 2)
        
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def _update_tracked_face(self, tracked_id: int, current_face: Dict) -> None:
        """
        Update an existing tracked face with new information.
        
        Args:
            tracked_id: ID of the tracked face
            current_face: Current face detection result
        """
        if tracked_id not in self.tracked_faces:
            return
        
        tracked_face = self.tracked_faces[tracked_id]
        
        # Update location
        tracked_face.last_location = current_face.get('face_location', tracked_face.last_location)
        
        # Update recognition information if provided
        if current_face.get('is_known'):
            tracked_face.person_id = current_face.get('person_id')
            tracked_face.person_name = current_face.get('person_name')
            tracked_face.confidence = current_face.get('confidence', 0.0)
            tracked_face.distance = current_face.get('distance', float('inf'))
        
        # Update frame counters
        tracked_face.frames_seen += 1
        tracked_face.frames_lost = 0
        
        # Check stability
        tracked_face.is_stable = tracked_face.frames_seen >= self.min_frames_for_stability
    
    def _create_new_tracked_face(self, current_face: Dict) -> None:
        """
        Create a new tracked face from current detection.
        
        Args:
            current_face: Current face detection result
        """
        tracked_face = TrackedFace(
            face_id=self.next_face_id,
            person_id=current_face.get('person_id'),
            person_name=current_face.get('person_name'),
            last_location=current_face.get('face_location'),
            confidence=current_face.get('confidence', 0.0),
            distance=current_face.get('distance', float('inf')),
            frames_seen=1,
            frames_lost=0,
            is_stable=False
        )
        
        self.tracked_faces[self.next_face_id] = tracked_face
        self.next_face_id += 1
    
    def _increment_lost_frames(self) -> None:
        """Increment lost frames counter for all tracked faces."""
        for tracked_face in self.tracked_faces.values():
            tracked_face.frames_lost += 1
    
    def _remove_lost_faces(self) -> None:
        """Remove faces that have been lost too long."""
        to_remove = [
            face_id for face_id, tracked_face in self.tracked_faces.items()
            if tracked_face.frames_lost > self.max_frames_lost
        ]
        
        for face_id in to_remove:
            del self.tracked_faces[face_id]
    
    def _get_unmatched_current(self, current_faces: List[Dict],
                             matched_pairs: List[Tuple[int, Dict]]) -> List[Dict]:
        """
        Get current faces that were not matched to any tracked face.
        
        Args:
            current_faces: List of current face detection results
            matched_pairs: List of matched (tracked_id, current_face) pairs
            
        Returns:
            List of unmatched current faces
        """
        matched_current = [pair[1] for pair in matched_pairs]
        unmatched = []
        
        for current_face in current_faces:
            if current_face not in matched_current:
                unmatched.append(current_face)
        
        return unmatched
    
    def _get_active_tracked_faces(self) -> List[Dict]:
        """
        Get all active tracked faces as dictionaries.
        
        Returns:
            List of tracked face dictionaries
        """
        active_faces = []
        
        for tracked_face in self.tracked_faces.values():
            if tracked_face.frames_lost <= self.max_frames_lost:
                face_dict = {
                    'face_id': tracked_face.face_id,
                    'face_location': tracked_face.last_location,
                    'person_id': tracked_face.person_id,
                    'person_name': tracked_face.person_name,
                    'confidence': tracked_face.confidence,
                    'distance': tracked_face.distance,
                    'is_known': tracked_face.person_id is not None,
                    'is_stable': tracked_face.is_stable,
                    'frames_seen': tracked_face.frames_seen
                }
                active_faces.append(face_dict)
        
        return active_faces
    
    def reset(self) -> None:
        """Reset the tracker, clearing all tracked faces."""
        self.tracked_faces.clear()
        self.next_face_id = 1
        self.frame_count = 0
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get tracker statistics.
        
        Returns:
            Dictionary with tracker statistics
        """
        stable_faces = sum(1 for f in self.tracked_faces.values() if f.is_stable)
        known_faces = sum(1 for f in self.tracked_faces.values() if f.person_id is not None)
        
        return {
            'total_tracked_faces': len(self.tracked_faces),
            'stable_faces': stable_faces,
            'known_faces': known_faces,
            'frame_count': self.frame_count,
            'max_distance': self.max_distance,
            'max_frames_lost': self.max_frames_lost,
            'min_frames_for_stability': self.min_frames_for_stability
        }
    
    def set_max_distance(self, distance: float) -> None:
        """
        Set the maximum distance for face matching.
        
        Args:
            distance: Maximum pixel distance
        """
        self.max_distance = max(50.0, min(500.0, distance))
    
    def set_max_frames_lost(self, frames: int) -> None:
        """
        Set the maximum frames before a face is removed.
        
        Args:
            frames: Maximum frames
        """
        self.max_frames_lost = max(5, min(30, frames))
    
    def set_min_frames_for_stability(self, frames: int) -> None:
        """
        Set the minimum frames for stability.
        
        Args:
            frames: Minimum frames
        """
        self.min_frames_for_stability = max(1, min(10, frames))


if __name__ == "__main__":
    # Test face tracker
    tracker = FaceTracker()
    
    # Simulate face detections across frames
    frame1_faces = [
        {
            'face_location': (100, 200, 300, 200),
            'person_id': 'PERSON001',
            'person_name': 'John Doe',
            'confidence': 95.0,
            'distance': 0.3,
            'is_known': True
        }
    ]
    
    frame2_faces = [
        {
            'face_location': (105, 205, 305, 205),  # Slightly moved
            'person_id': 'PERSON001',
            'person_name': 'John Doe',
            'confidence': 94.0,
            'distance': 0.31,
            'is_known': True
        }
    ]
    
    # Update tracker
    tracked1 = tracker.update(frame1_faces)
    print(f"Frame 1 tracked faces: {len(tracked1)}")
    
    tracked2 = tracker.update(frame2_faces)
    print(f"Frame 2 tracked faces: {len(tracked2)}")
    
    # Get statistics
    stats = tracker.get_statistics()
    print(f"Tracker statistics: {stats}")
