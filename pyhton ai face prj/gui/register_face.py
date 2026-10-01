"""
Register Face GUI Module
Handles face registration with webcam or image upload.
"""

import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
from typing import Optional, List
from pathlib import Path
from face_engine import FaceRecognizer
from database.database import get_database
from database.models import Person
from utils.image_utils import ImageUtils
from utils.validators import Validators
from utils.helpers import Helpers


class RegisterFaceFrame(ctk.CTkFrame):
    """Face registration frame with webcam and image upload support."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        # Face recognition
        self.recognizer = FaceRecognizer()
        
        # Camera
        self.camera = None
        self.camera_index = 0
        self.is_camera_running = False
        
        # Registration state
        self.current_image = None
        self.captured_images = []
        self.current_encoding = None
        
        self._setup_layout()
        self._create_widgets()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)  # Form
        self.grid_columnconfigure(1, weight=1)  # Camera/Image preview
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create registration widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Register New Face",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Form frame
        self._create_form_frame()
        
        # Camera/Image frame
        self._create_camera_frame()
    
    def _create_form_frame(self):
        """Create the registration form."""
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        form_frame.grid_rowconfigure(9, weight=1)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Person ID
        self._create_form_field(form_frame, "Person ID *", "person_id_entry", 0)
        
        # Full Name
        self._create_form_field(form_frame, "Full Name *", "full_name_entry", 1)
        
        # Email
        self._create_form_field(form_frame, "Email", "email_entry", 2)
        
        # Phone
        self._create_form_field(form_frame, "Phone", "phone_entry", 3)
        
        # Category
        self._create_form_field(form_frame, "Category/Department", "category_entry", 4)
        
        # Profile image path
        self._create_form_field(form_frame, "Profile Image", "profile_image_entry", 5)
        
        # Upload button
        upload_button = ctk.CTkButton(
            form_frame,
            text="Upload Image",
            command=self._upload_image,
            height=35
        )
        upload_button.grid(row=6, column=0, padx=20, pady=5, sticky="ew")
        
        # Capture from camera button
        capture_button = ctk.CTkButton(
            form_frame,
            text="Capture from Camera",
            command=self._toggle_camera,
            height=35
        )
        capture_button.grid(row=7, column=0, padx=20, pady=5, sticky="ew")
        
        # Register button
        register_button = ctk.CTkButton(
            form_frame,
            text="Register Face",
            command=self._register_face,
            height=40,
            fg_color="green"
        )
        register_button.grid(row=8, column=0, padx=20, pady=(15, 10), sticky="ew")
        
        # Clear button
        clear_button = ctk.CTkButton(
            form_frame,
            text="Clear Form",
            command=self._clear_form,
            height=35
        )
        clear_button.grid(row=9, column=0, padx=20, pady=(0, 20), sticky="ew")
    
    def _create_form_field(self, parent: ctk.CTkFrame, label: str, entry_name: str, row: int):
        """Create a form field with label and entry."""
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        label_widget.grid(row=row, column=0, padx=20, pady=(10, 5), sticky="w")
        
        entry_widget = ctk.CTkEntry(parent, height=35)
        entry_widget.grid(row=row + 1, column=0, padx=20, pady=(0, 5), sticky="ew")
        
        setattr(self, entry_name, entry_widget)
    
    def _create_camera_frame(self):
        """Create the camera/image preview frame."""
        camera_frame = ctk.CTkFrame(self)
        camera_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        camera_frame.grid_rowconfigure(0, weight=1)
        camera_frame.grid_columnconfigure(0, weight=1)
        
        # Preview label
        self.preview_label = ctk.CTkLabel(
            camera_frame,
            text="No image loaded",
            font=ctk.CTkFont(size=16)
        )
        self.preview_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Info label
        self.info_label = ctk.CTkLabel(
            camera_frame,
            text="Upload an image or capture from camera",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.grid(row=1, column=0, padx=20, pady=(0, 20))
    
    def _upload_image(self):
        """Upload an image file."""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Validate image
        is_valid, message = Validators.validate_image_file(file_path)
        if not is_valid:
            self.parent.show_message("Invalid Image", message, "error")
            return
        
        # Load image
        image = ImageUtils.load_image(file_path)
        if image is None:
            self.parent.show_message("Error", "Could not load image", "error")
            return
        
        # Validate face count
        face_count = self.recognizer.detector.get_face_count(image)
        is_valid, message = Validators.validate_face_count(face_count, max_faces=1)
        if not is_valid:
            self.parent.show_message("Face Detection Error", message, "error")
            return
        
        # Store image and update preview
        self.current_image = image
        self.profile_image_entry.delete(0, ctk.END)
        self.profile_image_entry.insert(0, file_path)
        
        # Update preview
        self._update_preview(image)
        self.info_label.configure(text=f"Image loaded successfully - {face_count} face detected")
    
    def _toggle_camera(self):
        """Toggle camera on/off."""
        if self.is_camera_running:
            self._stop_camera()
        else:
            self._start_camera()
    
    def _start_camera(self):
        """Start the camera for capture."""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                self.parent.show_message("Camera Error", "Could not open camera", "error")
                return
            
            self.is_camera_running = True
            self._camera_loop()
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            self.parent.show_message("Camera Error", f"Error: {e}", "error")
    
    def _stop_camera(self):
        """Stop the camera."""
        self.is_camera_running = False
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _camera_loop(self):
        """Camera loop for preview."""
        while self.is_camera_running and self.camera:
            try:
                ret, frame = self.camera.read()
                
                if not ret:
                    break
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                face_locations = self.recognizer.detector.detect_faces(frame_rgb)
                
                # Draw face boxes
                for location in face_locations:
                    frame_rgb = ImageUtils.draw_face_box(
                        frame_rgb,
                        location,
                        label="Face",
                        color=(0, 255, 0)
                    )
                
                # Update preview
                self._update_preview(frame_rgb)
                
                # Small delay
                import time
                time.sleep(0.03)
                
            except Exception as e:
                print(f"Error in camera loop: {e}")
                break
        
        self._stop_camera()
    
    def _capture_image(self):
        """Capture current frame from camera."""
        if not self.camera or not self.camera.isOpened():
            return
        
        ret, frame = self.camera.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_image = frame_rgb
            
            # Validate face count
            face_count = self.recognizer.detector.get_face_count(frame_rgb)
            is_valid, message = Validators.validate_face_count(face_count, max_faces=1)
            if not is_valid:
                self.parent.show_message("Face Detection Error", message, "error")
                return
            
            # Stop camera after capture
            self._stop_camera()
            
            # Save captured image
            timestamp = Helpers.get_timestamp_filename()
            filename = f"captured_{timestamp}.jpg"
            save_path = f"data/faces/{filename}"
            
            if ImageUtils.save_image(frame_rgb, save_path):
                self.profile_image_entry.delete(0, ctk.END)
                self.profile_image_entry.insert(0, save_path)
                self.info_label.configure(text=f"Image captured successfully - {face_count} face detected")
    
    def _update_preview(self, image: np.ndarray):
        """Update the preview image."""
        try:
            # Resize for display
            display_image = ImageUtils.resize_image(image, target_size=(400, 300))
            
            # Convert to PhotoImage
            photo_image = ImageUtils.convert_to_photoimage(display_image)
            if photo_image:
                self.preview_label.configure(image=photo_image, text="")
                self.preview_label.image = photo_image
            
        except Exception as e:
            print(f"Error updating preview: {e}")
    
    def _register_face(self):
        """Register the face with the provided information."""
        # Get form data
        person_id = self.person_id_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        category = self.category_entry.get().strip()
        profile_image_path = self.profile_image_entry.get().strip()
        
        # Validate required fields
        if not person_id or not full_name:
            self.parent.show_message("Validation Error", "Person ID and Full Name are required", "error")
            return
        
        # Validate person ID
        is_valid, message = Validators.validate_person_id(person_id)
        if not is_valid:
            self.parent.show_message("Validation Error", message, "error")
            return
        
        # Validate full name
        is_valid, message = Validators.validate_full_name(full_name)
        if not is_valid:
            self.parent.show_message("Validation Error", message, "error")
            return
        
        # Validate optional fields
        if email:
            is_valid, message = Validators.validate_email(email)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
        
        if phone:
            is_valid, message = Validators.validate_phone(phone)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
        
        if category:
            is_valid, message = Validators.validate_category(category)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
        
        # Check if person ID already exists
        person_manager = self.db.get_person_manager()
        if person_manager.person_id_exists(person_id):
            self.parent.show_message("Registration Error", "Person ID already exists", "error")
            return
        
        # Check if image is provided
        if not self.current_image:
            self.parent.show_message("Registration Error", "Please provide an image", "error")
            return
        
        # Generate face encoding
        try:
            encoding = self.recognizer.register_face(self.current_image, person_id)
            if encoding is None:
                self.parent.show_message("Registration Error", "Could not generate face encoding", "error")
                return
            
            self.current_encoding = encoding
            
        except Exception as e:
            print(f"Error generating encoding: {e}")
            self.parent.show_message("Registration Error", f"Error generating encoding: {e}", "error")
            return
        
        # Save profile image if not already saved
        if not profile_image_path or not Path(profile_image_path).exists():
            timestamp = Helpers.get_timestamp_filename()
            filename = f"{person_id}_{timestamp}.jpg"
            profile_image_path = f"data/faces/{filename}"
            
            if not ImageUtils.save_image(self.current_image, profile_image_path):
                self.parent.show_message("Registration Error", "Could not save profile image", "error")
                return
        
        # Create person object
        person = Person(
            person_id=person_id,
            full_name=full_name,
            email=email if email else None,
            phone=phone if phone else None,
            category=category if category else None,
            profile_image_path=profile_image_path,
            face_encoding=encoding
        )
        
        # Save to database
        try:
            if person_manager.add_person(person):
                self.parent.show_message("Success", "Face registered successfully!", "info")
                self._clear_form()
            else:
                self.parent.show_message("Registration Error", "Could not save to database", "error")
                
        except Exception as e:
            print(f"Error saving to database: {e}")
            self.parent.show_message("Registration Error", f"Error: {e}", "error")
    
    def _clear_form(self):
        """Clear the registration form."""
        self.person_id_entry.delete(0, ctk.END)
        self.full_name_entry.delete(0, ctk.END)
        self.email_entry.delete(0, ctk.END)
        self.phone_entry.delete(0, ctk.END)
        self.category_entry.delete(0, ctk.END)
        self.profile_image_entry.delete(0, ctk.END)
        
        self.current_image = None
        self.current_encoding = None
        self.captured_images = []
        
        self.preview_label.configure(image="", text="No image loaded")
        self.preview_label.image = None
        self.info_label.configure(text="Upload an image or capture from camera")
        
        self._stop_camera()
    
    def cleanup(self):
        """Clean up resources."""
        self._stop_camera()


if __name__ == "__main__":
    # Test register face frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    register_face = RegisterFaceFrame(app)
    register_face.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
