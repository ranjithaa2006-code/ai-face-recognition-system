"""
Image Recognition GUI Module
Handles face recognition from uploaded images.
"""

import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Optional, List
from pathlib import Path
from tkinter import filedialog
from face_engine import FaceRecognizer
from database.database import get_database
from utils.image_utils import ImageUtils
from utils.validators import Validators


class ImageRecognitionFrame(ctk.CTkFrame):
    """Image recognition frame for processing uploaded images."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        # Face recognition
        self.recognizer = FaceRecognizer()
        
        # State
        self.current_image = None
        self.current_image_path = None
        self.processed_image = None
        self.recognition_results = []
        
        # Known faces cache
        self.known_faces = {}
        self.known_names = {}
        
        self._setup_layout()
        self._create_widgets()
        self._load_known_faces()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)  # Image display
        self.grid_columnconfigure(1, weight=1)  # Results panel
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create image recognition widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Image Recognition",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Image display frame
        self._create_image_display()
        
        # Results panel
        self._create_results_panel()
    
    def _create_image_display(self):
        """Create the image display area."""
        image_frame = ctk.CTkFrame(self)
        image_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        image_frame.grid_rowconfigure(1, weight=1)
        image_frame.grid_columnconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ctk.CTkFrame(image_frame)
        button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        self.upload_button = ctk.CTkButton(
            button_frame,
            text="Upload Image",
            command=self._upload_image,
            height=35
        )
        self.upload_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.process_button = ctk.CTkButton(
            button_frame,
            text="Process Image",
            command=self._process_image,
            height=35,
            state="disabled"
        )
        self.process_button.grid(row=0, column=1, padx=5, pady=5)
        
        self.save_button = ctk.CTkButton(
            button_frame,
            text="Save Result",
            command=self._save_result,
            height=35,
            state="disabled"
        )
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Image preview
        self.image_label = ctk.CTkLabel(
            image_frame,
            text="No image loaded",
            font=ctk.CTkFont(size=16)
        )
        self.image_label.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
    
    def _create_results_panel(self):
        """Create the results panel."""
        results_frame = ctk.CTkFrame(self)
        results_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        results_title = ctk.CTkLabel(
            results_frame,
            text="Recognition Results",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        results_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Results scroll
        self.results_scroll = ctk.CTkScrollableFrame(results_frame)
        self.results_scroll.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Summary
        self.summary_label = ctk.CTkLabel(
            results_frame,
            text="No results yet",
            font=ctk.CTkFont(size=12)
        )
        self.summary_label.grid(row=2, column=0, padx=20, pady=(0, 20))
    
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
    
    def _upload_image(self):
        """Upload an image file."""
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
        
        # Store image
        self.current_image = image
        self.current_image_path = file_path
        self.processed_image = None
        self.recognition_results = []
        
        # Update display
        self._update_image_display(image)
        
        # Enable process button
        self.process_button.configure(state="normal")
        self.save_button.configure(state="disabled")
        
        # Clear results
        self._clear_results()
        
        self.summary_label.configure(text="Image loaded. Click 'Process Image' to recognize faces.")
    
    def _process_image(self):
        """Process the current image for face recognition."""
        if self.current_image is None:
            return
        
        try:
            # Recognize faces
            results = self.recognizer.recognize_faces(
                self.current_image,
                self.known_faces,
                self.known_names
            )
            
            self.recognition_results = results
            
            # Draw results on image
            self.processed_image = self._draw_results(self.current_image, results)
            
            # Update display
            self._update_image_display(self.processed_image)
            
            # Update results panel
            self._update_results(results)
            
            # Enable save button
            self.save_button.configure(state="normal")
            
            # Update summary
            total = len(results)
            recognized = sum(1 for r in results if r.is_known)
            unknown = total - recognized
            
            self.summary_label.configure(
                text=f"Detected {total} faces: {recognized} recognized, {unknown} unknown"
            )
            
        except Exception as e:
            print(f"Error processing image: {e}")
            self.parent.show_message("Processing Error", f"Error: {e}", "error")
    
    def _draw_results(self, image, results: List) -> np.ndarray:
        """Draw recognition results on image."""
        try:
            image_copy = image.copy()
            
            for result in results:
                location = result.face_location
                if not location:
                    continue
                
                is_known = result.is_known
                person_name = result.person_name or "UNKNOWN"
                confidence = result.confidence
                
                # Choose color
                if is_known:
                    color = (0, 255, 0)  # Green
                else:
                    color = (255, 0, 0)  # Red
                
                # Draw face box
                image_copy = ImageUtils.draw_face_box(
                    image_copy,
                    location,
                    label=person_name,
                    color=color,
                    confidence=confidence
                )
            
            return image_copy
            
        except Exception as e:
            print(f"Error drawing results: {e}")
            return image
    
    def _update_image_display(self, image: np.ndarray):
        """Update the image display."""
        try:
            # Resize for display
            max_size = 600
            height, width = image.shape[:2]
            
            if max(height, width) > max_size:
                if height > width:
                    target_size = (int(width * max_size / height), max_size)
                else:
                    target_size = (max_size, int(height * max_size / width))
                display_image = ImageUtils.resize_image(image, target_size=target_size)
            else:
                display_image = image
            
            # Convert to PhotoImage
            photo_image = ImageUtils.convert_to_photoimage(display_image)
            if photo_image:
                self.image_label.configure(image=photo_image, text="")
                self.image_label.image = photo_image
            
        except Exception as e:
            print(f"Error updating image display: {e}")
    
    def _update_results(self, results: List):
        """Update the results panel."""
        # Clear existing widgets
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Add result items
        for i, result in enumerate(results):
            result_item = self._create_result_item(result, i + 1)
            result_item.pack(fill="x", padx=5, pady=5)
    
    def _create_result_item(self, result, index: int) -> ctk.CTkFrame:
        """Create a result item."""
        item_frame = ctk.CTkFrame(self.results_scroll)
        
        # Index
        index_label = ctk.CTkLabel(
            item_frame,
            text=f"#{index}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        index_label.pack(side="left", padx=10, pady=10)
        
        # Name
        name_label = ctk.CTkLabel(
            item_frame,
            text=result.person_name or "UNKNOWN",
            font=ctk.CTkFont(size=12, weight="bold" if result.is_known else "normal")
        )
        name_label.pack(side="left", padx=10, pady=10)
        
        # Confidence
        conf_label = ctk.CTkLabel(
            item_frame,
            text=f"{result.confidence:.1f}%",
            font=ctk.CTkFont(size=11)
        )
        conf_label.pack(side="right", padx=10, pady=10)
        
        # Status indicator
        status_color = "green" if result.is_known else "red"
        status_label = ctk.CTkLabel(
            item_frame,
            text="●",
            text_color=status_color,
            font=ctk.CTkFont(size=12)
        )
        status_label.pack(side="right", padx=5, pady=10)
        
        return item_frame
    
    def _clear_results(self):
        """Clear the results panel."""
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        self.summary_label.configure(text="No results yet")
    
    def _save_result(self):
        """Save the processed image."""
        if self.processed_image is None:
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=".jpg",
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            if ImageUtils.save_image(self.processed_image, file_path):
                self.parent.show_message("Success", "Image saved successfully", "info")
            else:
                self.parent.show_message("Error", "Could not save image", "error")
                
        except Exception as e:
            print(f"Error saving image: {e}")
            self.parent.show_message("Error", f"Error: {e}", "error")


if __name__ == "__main__":
    # Test image recognition frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    image_recognition = ImageRecognitionFrame(app)
    image_recognition.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
