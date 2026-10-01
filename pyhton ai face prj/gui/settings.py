"""
Settings GUI Module
Manages application settings and configuration.
"""

import customtkinter as ctk
from typing import Dict, Any
from database.database import get_database
from utils.validators import Validators


class SettingsFrame(ctk.CTkFrame):
    """Settings frame for application configuration."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        self._setup_layout()
        self._create_widgets()
        self._load_settings()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create settings widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Settings container
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        settings_frame.grid_rowconfigure(6, weight=1)
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # Recognition settings
        self._create_recognition_settings(settings_frame)
        
        # Camera settings
        self._create_camera_settings(settings_frame)
        
        # Display settings
        self._create_display_settings(settings_frame)
        
        # Save button
        save_button = ctk.CTkButton(
            settings_frame,
            text="Save Settings",
            command=self._save_settings,
            height=40,
            fg_color="green"
        )
        save_button.grid(row=6, column=0, padx=20, pady=(15, 20), sticky="ew")
        
        # Reset button
        reset_button = ctk.CTkButton(
            settings_frame,
            text="Reset to Defaults",
            command=self._reset_settings,
            height=35
        )
        reset_button.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="ew")
    
    def _create_recognition_settings(self, parent: ctk.CTkFrame):
        """Create recognition settings section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text="Recognition Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # Recognition threshold
        self._create_setting_row(
            section_frame,
            "Recognition Threshold",
            "Lower = stricter matching (0.3-0.8)",
            "recognition_threshold_slider",
            1,
            "slider",
            0.3,
            0.8,
            0.6
        )
        
        # Detection frequency
        self._create_setting_row(
            section_frame,
            "Detection Frequency",
            "Frames between detections (1-30)",
            "detection_frequency_slider",
            2,
            "slider",
            1,
            30,
            5
        )
        
        # Minimum face size
        self._create_setting_row(
            section_frame,
            "Minimum Face Size",
            "Minimum face size in pixels (50-500)",
            "min_face_size_slider",
            3,
            "slider",
            50,
            500,
            100
        )
    
    def _create_camera_settings(self, parent: ctk.CTkFrame):
        """Create camera settings section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text="Camera Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # Camera index
        self._create_setting_row(
            section_frame,
            "Camera Index",
            "Webcam camera index (0-10)",
            "camera_index_entry",
            1,
            "entry",
            default_value="0"
        )
        
        # Frame scaling
        self._create_setting_row(
            section_frame,
            "Frame Scaling",
            "Frame resize factor for performance (0.1-1.0)",
            "frame_scaling_slider",
            2,
            "slider",
            0.1,
            1.0,
            0.5
        )
    
    def _create_display_settings(self, parent: ctk.CTkFrame):
        """Create display settings section."""
        section_frame = ctk.CTkFrame(parent)
        section_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        section_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        title_label = ctk.CTkLabel(
            section_frame,
            text="Display Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # FPS display
        self._create_setting_row(
            section_frame,
            "Show FPS",
            "Display frames per second",
            "fps_display_switch",
            1,
            "switch",
            default_value=True
        )
        
        # Application theme
        self._create_setting_row(
            section_frame,
            "Application Theme",
            "Application color theme",
            "theme_option",
            2,
            "option",
            options=["dark", "light", "system"],
            default_value="dark"
        )
        
        # Unknown face behavior
        self._create_setting_row(
            section_frame,
            "Unknown Face Behavior",
            "How to handle unknown faces",
            "unknown_face_option",
            3,
            "option",
            options=["alert", "ignore", "log"],
            default_value="alert"
        )
    
    def _create_setting_row(self, parent: ctk.CTkFrame, label: str, description: str,
                           widget_name: str, row: int, widget_type: str,
                           min_value: float = None, max_value: float = None,
                           default_value: Any = None, options: list = None):
        """Create a settings row."""
        # Label
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=row, column=0, padx=15, pady=(10, 5), sticky="w")
        
        # Description
        desc_widget = ctk.CTkLabel(
            parent,
            text=description,
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        )
        desc_widget.grid(row=row + 1, column=0, padx=15, pady=(0, 5), sticky="w")
        
        # Create widget based on type
        if widget_type == "slider":
            widget = ctk.CTkSlider(
                parent,
                from_=min_value,
                to=max_value,
                number_of_steps=int((max_value - min_value) * 10)
            )
            widget.set(default_value)
            
            # Value label
            value_label = ctk.CTkLabel(parent, text=str(default_value))
            value_label.grid(row=row, column=1, padx=15, pady=10, sticky="e")
            
            # Update value label on change
            def on_slider_change(value):
                value_label.configure(text=f"{value:.2f}")
            
            widget.configure(command=on_slider_change)
            
        elif widget_type == "entry":
            widget = ctk.CTkEntry(parent, height=35)
            widget.insert(0, str(default_value))
            
        elif widget_type == "switch":
            widget = ctk.CTkSwitch(parent)
            widget.set(default_value)
            
        elif widget_type == "option":
            widget = ctk.CTkOptionMenu(parent, values=options)
            widget.set(default_value)
        
        widget.grid(row=row + 1, column=1, padx=15, pady=5, sticky="ew")
        
        # Store reference
        setattr(self, widget_name, widget)
    
    def _load_settings(self):
        """Load settings from database."""
        try:
            settings_manager = self.db.get_settings_manager()
            
            # Recognition threshold
            threshold = float(settings_manager.get_setting('recognition_threshold', '0.6'))
            self.recognition_threshold_slider.set(threshold)
            
            # Detection frequency
            frequency = int(settings_manager.get_setting('detection_frequency', '5'))
            self.detection_frequency_slider.set(frequency)
            
            # Minimum face size
            min_face = int(settings_manager.get_setting('minimum_face_size', '100'))
            self.min_face_size_slider.set(min_face)
            
            # Camera index
            camera_idx = settings_manager.get_setting('camera_index', '0')
            self.camera_index_entry.delete(0, ctk.END)
            self.camera_index_entry.insert(0, camera_idx)
            
            # Frame scaling
            scaling = float(settings_manager.get_setting('frame_scaling', '0.5'))
            self.frame_scaling_slider.set(scaling)
            
            # FPS display
            fps_display = settings_manager.get_setting('fps_display', 'true').lower() == 'true'
            self.fps_display_switch.set(fps_display)
            
            # Theme
            theme = settings_manager.get_setting('application_theme', 'dark')
            self.theme_option.set(theme)
            
            # Unknown face behavior
            unknown_behavior = settings_manager.get_setting('unknown_face_behavior', 'alert')
            self.unknown_face_option.set(unknown_behavior)
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _save_settings(self):
        """Save settings to database."""
        try:
            settings_manager = self.db.get_settings_manager()
            
            # Get values from widgets
            threshold = self.recognition_threshold_slider.get()
            frequency = int(self.detection_frequency_slider.get())
            min_face = int(self.min_face_size_slider.get())
            camera_idx = self.camera_index_entry.get()
            scaling = self.frame_scaling_slider.get()
            fps_display = self.fps_display_switch.get()
            theme = self.theme_option.get()
            unknown_behavior = self.unknown_face_option.get()
            
            # Validate values
            is_valid, message = Validators.validate_recognition_threshold(threshold)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
            
            is_valid, message = Validators.validate_camera_index(int(camera_idx))
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
            
            is_valid, message = Validators.validate_detection_frequency(frequency)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
            
            is_valid, message = Validators.validate_frame_scaling(scaling)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
            
            is_valid, message = Validators.validate_minimum_face_size(min_face)
            if not is_valid:
                self.parent.show_message("Validation Error", message, "error")
                return
            
            # Save to database
            settings_manager.set_setting('recognition_threshold', str(threshold))
            settings_manager.set_setting('detection_frequency', str(frequency))
            settings_manager.set_setting('minimum_face_size', str(min_face))
            settings_manager.set_setting('camera_index', camera_idx)
            settings_manager.set_setting('frame_scaling', str(scaling))
            settings_manager.set_setting('fps_display', str(fps_display).lower())
            settings_manager.set_setting('application_theme', theme)
            settings_manager.set_setting('unknown_face_behavior', unknown_behavior)
            
            self.parent.show_message("Success", "Settings saved successfully!", "info")
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            self.parent.show_message("Error", f"Error saving settings: {e}", "error")
    
    def _reset_settings(self):
        """Reset settings to default values."""
        confirmed = self.parent.show_confirmation(
            "Reset Settings",
            "Are you sure you want to reset all settings to default values?"
        )
        
        if not confirmed:
            return
        
        try:
            settings_manager = self.db.get_settings_manager()
            
            # Reset to defaults
            settings_manager.set_setting('recognition_threshold', '0.6')
            settings_manager.set_setting('detection_frequency', '5')
            settings_manager.set_setting('minimum_face_size', '100')
            settings_manager.set_setting('camera_index', '0')
            settings_manager.set_setting('frame_scaling', '0.5')
            settings_manager.set_setting('fps_display', 'true')
            settings_manager.set_setting('application_theme', 'dark')
            settings_manager.set_setting('unknown_face_behavior', 'alert')
            
            # Reload settings
            self._load_settings()
            
            self.parent.show_message("Success", "Settings reset to defaults!", "info")
            
        except Exception as e:
            print(f"Error resetting settings: {e}")
            self.parent.show_message("Error", f"Error resetting settings: {e}", "error")


if __name__ == "__main__":
    # Test settings frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    settings = SettingsFrame(app)
    settings.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
