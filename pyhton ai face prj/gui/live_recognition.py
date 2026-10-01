"""
Live Recognition GUI Module
Handles real-time face recognition from webcam.
"""

import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Optional, Dict, List
import threading
import time
from face_engine import FaceRecognizer, FaceTracker
from database.database import get_database
from utils.image_utils import ImageUtils
from utils.helpers import Helpers


class LiveRecognitionFrame(ctk.CTkFrame):
    """Live recognition frame with webcam integration."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        # Face recognition components
        self.recognizer = None
        self.tracker = FaceTracker()
        
        # Camera
        self.camera = None
        self.camera_index = 0
        self.is_running = False
        self.camera_thread = None
        
        # Settings
        self.detection_frequency = 5
        self.frame_scaling = 0.5
        self.recognition_threshold = 0.6
        
        # Statistics
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        self.detected_faces = 0
        self.recognized_faces = 0
        self.unknown_faces = 0
        
        # Known faces cache
        self.known_faces = {}
        self.known_names = {}
        
        self._setup_layout()
        self._create_widgets()
        self._load_settings()
        self._load_known_faces()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=2)  # Camera view
        self.grid_columnconfigure(1, weight=1)  # Info panel
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create live recognition widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Live Face Recognition",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Camera view frame
        self.camera_frame = ctk.CTkFrame(self)
        self.camera_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.camera_frame.grid_rowconfigure(0, weight=1)
        self.camera_frame.grid_columnconfigure(0, weight=1)
        
        # Camera label
        self.camera_label = ctk.CTkLabel(
            self.camera_frame,
            text="Camera not started",
            font=ctk.CTkFont(size=16)
        )
        self.camera_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Info panel frame
        self.info_panel = ctk.CTkFrame(self)
        self.info_panel.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.info_panel.grid_rowconfigure(4, weight=1)
        self.info_panel.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        self._create_control_buttons()
        
        # Statistics display
        self._create_statistics_display()
        
        # Detected faces list
        self._create_detected_faces_list()
    
    def _create_control_buttons(self):
        """Create control buttons."""
        button_frame = ctk.CTkFrame(self.info_panel)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Camera",
            command=self.start_camera,
            height=40
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Stop Camera",
            command=self.stop_camera,
            height=40,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
    
    def _create_statistics_display(self):
        """Create statistics display."""
        stats_frame = ctk.CTkFrame(self.info_panel)
        stats_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self._create_stat_item(stats_frame, "FPS", "0", 0, 0)
        self._create_stat_item(stats_frame, "Detected", "0", 0, 1)
        self._create_stat_item(stats_frame, "Recognized", "0", 1, 0)
        self._create_stat_item(stats_frame, "Unknown", "0", 1, 1)
    
    def _create_stat_item(self, parent: ctk.CTkFrame, label: str, value: str, row: int, col: int):
        """Create a statistics item."""
        item_frame = ctk.CTkFrame(parent)
        item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        label_widget = ctk.CTkLabel(
            item_frame,
            text=label,
            font=ctk.CTkFont(size=10)
        )
        label_widget.grid(row=0, column=0, padx=8, pady=(8, 4))
        
        value_widget = ctk.CTkLabel(
            item_frame,
            text=value,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        value_widget.grid(row=1, column=0, padx=8, pady=(0, 8))
        
        # Store reference
        setattr(self, f"{label.lower()}_stat", value_widget)
    
    def _create_detected_faces_list(self):
        """Create the detected faces list."""
        list_frame = ctk.CTkFrame(self.info_panel)
        list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        list_title = ctk.CTkLabel(
            list_frame,
            text="Detected Faces",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Scrollable frame
        self.detected_faces_scroll = ctk.CTkScrollableFrame(list_frame)
        self.detected_faces_scroll.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
    
    def _load_settings(self):
        """Load settings from database."""
        try:
            settings_manager = self.db.get_settings_manager()
            
            self.camera_index = int(settings_manager.get_setting('camera_index', '0'))
            self.detection_frequency = int(settings_manager.get_setting('detection_frequency', '5'))
            self.frame_scaling = float(settings_manager.get_setting('frame_scaling', '0.5'))
            self.recognition_threshold = float(settings_manager.get_setting('recognition_threshold', '0.6'))
            
            # Initialize recognizer with settings
            self.recognizer = FaceRecognizer(
                recognition_threshold=self.recognition_threshold,
                detection_model='hog',
                min_face_size=100
            )
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _load_known_faces(self):
        """Load known faces from database."""
        try:
            person_manager = self.db.get_person_manager()
            persons = person_manager.get_persons_with_embeddings()
            
            self.known_faces = {}
            self.known_names = {}
            
            for person in persons:
                if person.face_embeddings is not None:
                    self.known_faces[person.person_id] = person.face_embeddings
                    self.known_names[person.person_id] = person.full_name
            
            print(f"Loaded {len(self.known_faces)} known faces")
            
        except Exception as e:
            print(f"Error loading known faces: {e}")
    
    def start_camera(self):
        """Start the camera and recognition."""
        if self.is_running:
            return
        
        try:
            # Initialize camera
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                self.parent.show_message("Camera Error", "Could not open camera", "error")
                return
            
            self.is_running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            
            # Start camera thread
            self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
            self.camera_thread.start()
            
            # Reset statistics
            self.frame_count = 0
            self.start_time = time.time()
            self.detected_faces = 0
            self.recognized_faces = 0
            self.unknown_faces = 0
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            self.parent.show_message("Camera Error", f"Error starting camera: {e}", "error")
    
    def stop_camera(self):
        """Stop the camera and recognition."""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        
        # Reset camera label
        self.camera_label.configure(text="Camera stopped")
        
        # Clear detected faces list
        for widget in self.detected_faces_scroll.winfo_children():
            widget.destroy()
    
    def _camera_loop(self):
        """Main camera loop running in separate thread."""
        frame_counter = 0
        
        while self.is_running and self.camera:
            try:
                # Read frame
                ret, frame = self.camera.read()
                
                if not ret:
                    break
                
                frame_counter += 1
                
                # Process frame at specified frequency
                if frame_counter % self.detection_frequency == 0:
                    self._process_frame(frame)
                
                # Update FPS
                self.frame_count += 1
                elapsed = time.time() - self.start_time
                if elapsed > 0:
                    self.fps = self.frame_count / elapsed
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Error in camera loop: {e}")
                break
        
        # Clean up
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _process_frame(self, frame: np.ndarray):
        """Process a single frame for face recognition."""
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame for faster processing
            if self.frame_scaling < 1.0:
                frame_rgb = ImageUtils.resize_image(frame_rgb, scale_factor=self.frame_scaling)
            
            # Recognize faces
            results = self.recognizer.recognize_faces(
                frame_rgb,
                self.known_faces,
                self.known_names
            )
            
            # Update tracker
            tracked_results = self.tracker.update([result.to_dict() for result in results])
            
            # Draw results on frame
            frame_with_boxes = self._draw_results(frame_rgb, tracked_results)
            
            # Update UI (must be done on main thread)
            self.after(0, self._update_ui, frame_with_boxes, tracked_results)
            
        except Exception as e:
            print(f"Error processing frame: {e}")
    
    def _draw_results(self, frame: np.ndarray, results: List[Dict]) -> np.ndarray:
        """Draw recognition results on frame."""
        try:
            frame_copy = frame.copy()
            
            for result in results:
                location = result.get('face_location')
                if not location:
                    continue
                
                is_known = result.get('is_known', False)
                person_name = result.get('person_name', 'UNKNOWN')
                confidence = result.get('confidence', 0.0)
                
                # Choose color based on recognition
                if is_known:
                    color = (0, 255, 0)  # Green for known
                else:
                    color = (255, 0, 0)  # Red for unknown
                
                # Draw face box
                frame_copy = ImageUtils.draw_face_box(
                    frame_copy,
                    location,
                    label=person_name,
                    color=color,
                    confidence=confidence
                )
            
            return frame_copy
            
        except Exception as e:
            print(f"Error drawing results: {e}")
            return frame
    
    def _update_ui(self, frame: np.ndarray, results: List[Dict]):
        """Update the UI with processed frame and results."""
        try:
            # Update camera view
            if frame is not None:
                # Convert to PhotoImage
                photo_image = ImageUtils.convert_to_photoimage(frame)
                if photo_image:
                    self.camera_label.configure(image=photo_image, text="")
                    self.camera_label.image = photo_image
            
            # Update statistics
            self.fps_stat.configure(text=f"{self.fps:.1f}")
            self.detected_stat.configure(text=str(len(results)))
            
            recognized = sum(1 for r in results if r.get('is_known', False))
            unknown = len(results) - recognized
            
            self.recognized_stat.configure(text=str(recognized))
            self.unknown_stat.configure(text=str(unknown))
            
            # Update detected faces list
            self._update_detected_faces_list(results)
            
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def _update_detected_faces_list(self, results: List[Dict]):
        """Update the detected faces list."""
        try:
            # Clear existing widgets
            for widget in self.detected_faces_scroll.winfo_children():
                widget.destroy()
            
            # Add new widgets for each detected face
            for result in results:
                person_name = result.get('person_name', 'UNKNOWN')
                confidence = result.get('confidence', 0.0)
                is_known = result.get('is_known', False)
                
                # Create face item
                face_item = ctk.CTkFrame(self.detected_faces_scroll)
                face_item.pack(fill="x", padx=5, pady=5)
                
                # Name label
                name_label = ctk.CTkLabel(
                    face_item,
                    text=person_name,
                    font=ctk.CTkFont(size=12, weight="bold" if is_known else "normal")
                )
                name_label.pack(side="left", padx=10, pady=5)
                
                # Confidence label
                conf_label = ctk.CTkLabel(
                    face_item,
                    text=f"{confidence:.1f}%",
                    font=ctk.CTkFont(size=10)
                )
                conf_label.pack(side="right", padx=10, pady=5)
                
                # Status indicator
                status_color = "green" if is_known else "red"
                status_label = ctk.CTkLabel(
                    face_item,
                    text="●",
                    text_color=status_color,
                    font=ctk.CTkFont(size=12)
                )
                status_label.pack(side="right", padx=5, pady=5)
            
        except Exception as e:
            print(f"Error updating detected faces list: {e}")
    
    def refresh_known_faces(self):
        """Refresh the known faces from database."""
        self._load_known_faces()
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_camera()
        if self.camera_thread and self.camera_thread.is_alive():
            self.camera_thread.join(timeout=1.0)


if __name__ == "__main__":
    # Test live recognition frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    live_recognition = LiveRecognitionFrame(app)
    live_recognition.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
