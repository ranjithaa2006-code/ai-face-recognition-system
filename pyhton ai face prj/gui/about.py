"""
About GUI Module
Displays information about the application.
"""

import customtkinter as ctk


class AboutFrame(ctk.CTkFrame):
    """About frame displaying application information."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        
        self._setup_layout()
        self._create_widgets()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create about widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="About",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Content frame
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Scrollable content
        scrollable_frame = ctk.CTkScrollableFrame(content_frame)
        scrollable_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Application information
        self._create_app_info(scrollable_frame)
        
        # Features section
        self._create_features_section(scrollable_frame)
        
        # Technologies section
        self._create_technologies_section(scrollable_frame)
        
        # Privacy notice
        self._create_privacy_notice(scrollable_frame)
        
        # Disclaimer
        self._create_disclaimer(scrollable_frame)
    
    def _create_app_info(self, parent: ctk.CTkFrame):
        """Create application information section."""
        # App name and version
        app_name_label = ctk.CTkLabel(
            parent,
            text="AI Face Recognition System",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        app_name_label.pack(pady=(0, 5))
        
        version_label = ctk.CTkLabel(
            parent,
            text="Version 1.0.0",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(
            parent,
            text=(
                "A professional AI-based face recognition system for real-time face detection, "
                "recognition, and identity management. Built for educational and portfolio purposes, "
                "this system provides advanced face recognition capabilities using modern computer "
                "vision techniques."
            ),
            font=ctk.CTkFont(size=12),
            wraplength=800,
            justify="left"
        )
        desc_label.pack(pady=(0, 20), padx=10, anchor="w")
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2)
        separator.pack(fill="x", pady=10)
    
    def _create_features_section(self, parent: ctk.CTkFrame):
        """Create features section."""
        features_title = ctk.CTkLabel(
            parent,
            text="Key Features",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        features_title.pack(pady=(10, 10), anchor="w")
        
        features = [
            "• Real-time face recognition via webcam",
            "• Multiple face detection and recognition",
            "• Face profile registration and management",
            "• Image-based face recognition",
            "• Face database with search and filtering",
            "• Performance analytics and statistics",
            "• Configurable recognition settings",
            "• Local data storage (no cloud dependencies)",
            "• Modern, professional GUI interface",
            "• Privacy-focused design"
        ]
        
        for feature in features:
            feature_label = ctk.CTkLabel(
                parent,
                text=feature,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            feature_label.pack(pady=2, padx=10, anchor="w")
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2)
        separator.pack(fill="x", pady=10)
    
    def _create_technologies_section(self, parent: ctk.CTkFrame):
        """Create technologies section."""
        tech_title = ctk.CTkLabel(
            parent,
            text="Technologies Used",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tech_title.pack(pady=(10, 10), anchor="w")
        
        technologies = [
            "• Python 3.11+",
            "• OpenCV (Computer Vision)",
            "• face_recognition (Face embeddings)",
            "• CustomTkinter (Modern GUI)",
            "• NumPy (Numerical computing)",
            "• Pillow (Image processing)",
            "• SQLite (Local database)",
            "• Pandas (Data management)",
            "• Matplotlib (Analytics visualization)",
            "• bcrypt (Password security)"
        ]
        
        for tech in technologies:
            tech_label = ctk.CTkLabel(
                parent,
                text=tech,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            tech_label.pack(pady=2, padx=10, anchor="w")
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2)
        separator.pack(fill="x", pady=10)
    
    def _create_privacy_notice(self, parent: ctk.CTkFrame):
        """Create privacy notice section."""
        privacy_title = ctk.CTkLabel(
            parent,
            text="Privacy Notice",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        privacy_title.pack(pady=(10, 10), anchor="w")
        
        privacy_text = (
            "This system processes biometric data (face embeddings) for face recognition purposes. "
            "All data is stored locally on your device and is never transmitted to external servers. "
            "Face embeddings should only be collected and processed with appropriate user consent. "
            "Users have the right to delete their biometric data at any time through the Face Database section."
        )
        
        privacy_label = ctk.CTkLabel(
            parent,
            text=privacy_text,
            font=ctk.CTkFont(size=12),
            wraplength=800,
            justify="left"
        )
        privacy_label.pack(pady=(0, 20), padx=10, anchor="w")
        
        # Separator
        separator = ctk.CTkFrame(parent, height=2)
        separator.pack(fill="x", pady=10)
    
    def _create_disclaimer(self, parent: ctk.CTkFrame):
        """Create disclaimer section."""
        disclaimer_title = ctk.CTkLabel(
            parent,
            text="Disclaimer",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        disclaimer_title.pack(pady=(10, 10), anchor="w")
        
        disclaimer_text = (
            "This face recognition system is provided for educational and portfolio purposes. "
            "It does not provide perfect identification or security guarantees. Recognition accuracy "
            "depends on various factors including lighting conditions, camera quality, face pose, "
            "image quality, and the configured recognition threshold. This system should not be "
            "relied upon for security-critical applications without proper testing and validation."
        )
        
        disclaimer_label = ctk.CTkLabel(
            parent,
            text=disclaimer_text,
            font=ctk.CTkFont(size=12),
            wraplength=800,
            justify="left"
        )
        disclaimer_label.pack(pady=(0, 20), padx=10, anchor="w")
        
        # Footer
        footer_label = ctk.CTkLabel(
            parent,
            text="© 2024 AI Face Recognition System. All rights reserved.",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        footer_label.pack(pady=(20, 10))


if __name__ == "__main__":
    # Test about frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    about = AboutFrame(app)
    about.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
