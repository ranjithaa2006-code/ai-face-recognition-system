"""
Main Window Module
Creates the main application window with sidebar navigation.
"""

import customtkinter as ctk
from typing import Optional, Callable
import tkinter as tk
from tkinter import messagebox
from gui.dashboard import DashboardFrame
from gui.live_recognition import LiveRecognitionFrame
from gui.register_face import RegisterFaceFrame
from gui.face_database import FaceDatabaseFrame
from gui.image_recognition import ImageRecognitionFrame
from gui.analytics import AnalyticsFrame
from gui.settings import SettingsFrame
from gui.about import AboutFrame


class MainWindow(ctk.CTk):
    """Main application window with sidebar navigation."""
    
    def __init__(self, title: str = "AI Face Recognition System"):
        super().__init__()
        
        self.title(title)
        self.geometry("1280x720")
        self.minsize(1024, 600)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize theme
        self._setup_theme()
        
        # Create sidebar
        self._create_sidebar()
        
        # Create main content area
        self._create_main_content()
        
        # Track current frame
        self.current_frame = None
        self.frame_map = {}
        
        # Initialize all frames
        self._initialize_frames()
    
    def _setup_theme(self):
        """Setup the application theme."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
    
    def _create_sidebar(self):
        """Create the sidebar with navigation buttons."""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # Spacer
        
        # App title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="AI Face Recognition",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self._create_nav_button("Dashboard", "📊", 1, self._show_dashboard)
        self._create_nav_button("Live Recognition", "📹", 2, self._show_live_recognition)
        self._create_nav_button("Register Face", "👤", 3, self._show_register_face)
        self._create_nav_button("Face Database", "🗂️", 4, self._show_face_database)
        self._create_nav_button("Image Recognition", "🖼️", 5, self._show_image_recognition)
        self._create_nav_button("Analytics", "📈", 6, self._show_analytics)
        self._create_nav_button("Settings", "⚙️", 7, self._show_settings)
        self._create_nav_button("About", "ℹ️", 8, self._show_about)
        
        # Appearance mode switch
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar,
            text="Appearance Mode:",
            anchor="w"
        )
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["System", "Dark", "Light"],
            command=self._change_appearance_mode_event
        )
        self.appearance_mode_menu.grid(row=10, column=0, padx=20, pady=(10, 20))
    
    def _create_nav_button(self, text: str, icon: str, row: int, command: Callable):
        """Create a navigation button."""
        button = ctk.CTkButton(
            self.sidebar,
            text=f"{icon} {text}",
            font=ctk.CTkFont(size=14),
            height=40,
            anchor="w",
            command=command
        )
        button.grid(row=row, column=0, padx=20, pady=5)
        return button
    
    def _create_main_content(self):
        """Create the main content area."""
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)
    
    def _initialize_frames(self):
        """Initialize all application frames."""
        self.frame_map['dashboard'] = DashboardFrame(self.main_content)
        self.frame_map['live_recognition'] = LiveRecognitionFrame(self.main_content)
        self.frame_map['register_face'] = RegisterFaceFrame(self.main_content)
        self.frame_map['face_database'] = FaceDatabaseFrame(self.main_content)
        self.frame_map['image_recognition'] = ImageRecognitionFrame(self.main_content)
        self.frame_map['analytics'] = AnalyticsFrame(self.main_content)
        self.frame_map['settings'] = SettingsFrame(self.main_content)
        self.frame_map['about'] = AboutFrame(self.main_content)
    
    def _change_appearance_mode_event(self, new_appearance_mode: str):
        """Change the appearance mode."""
        ctk.set_appearance_mode(new_appearance_mode.lower())
    
    def _show_dashboard(self):
        """Show the dashboard frame."""
        self._show_frame("dashboard")
    
    def _show_live_recognition(self):
        """Show the live recognition frame."""
        self._show_frame("live_recognition")
    
    def _show_register_face(self):
        """Show the register face frame."""
        self._show_frame("register_face")
    
    def _show_face_database(self):
        """Show the face database frame."""
        self._show_frame("face_database")
    
    def _show_image_recognition(self):
        """Show the image recognition frame."""
        self._show_frame("image_recognition")
    
    def _show_analytics(self):
        """Show the analytics frame."""
        self._show_frame("analytics")
    
    def _show_settings(self):
        """Show the settings frame."""
        self._show_frame("settings")
    
    def _show_about(self):
        """Show the about frame."""
        self._show_frame("about")
    
    def _show_frame(self, frame_name: str):
        """Show a specific frame in the main content area."""
        # Hide current frame
        if self.current_frame:
            self.current_frame.grid_forget()
        
        # Show the requested frame
        if frame_name in self.frame_map:
            self.current_frame = self.frame_map[frame_name]
            self.current_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        else:
            print(f"Frame {frame_name} not found")
    
    def register_frame(self, frame_name: str, frame: ctk.CTkFrame):
        """
        Register a custom frame for a specific name.
        
        Args:
            frame_name: Name to register the frame under
            frame: The frame to register
        """
        self.frame_map[frame_name] = frame
    
    def show_frame(self, frame_name: str):
        """
        Show a registered frame by name.
        
        Args:
            frame_name: Name of the frame to show
        """
        self._show_frame(frame_name)
    
    def show_message(self, title: str, message: str, message_type: str = "info"):
        """
        Show a message dialog.
        
        Args:
            title: Dialog title
            message: Dialog message
            message_type: Type of message ("info", "warning", "error")
        """
        if message_type == "info":
            messagebox.showinfo(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        elif message_type == "error":
            messagebox.showerror(title, message)
    
    def show_confirmation(self, title: str, message: str) -> bool:
        """
        Show a confirmation dialog.
        
        Args:
            title: Dialog title
            message: Dialog message
            
        Returns:
            True if user confirms, False otherwise
        """
        return messagebox.askyesno(title, message)
    
    def cleanup(self):
        """Clean up resources before closing."""
        # Cleanup live recognition frame
        if 'live_recognition' in self.frame_map:
            self.frame_map['live_recognition'].cleanup()
        
        # Cleanup register face frame
        if 'register_face' in self.frame_map:
            self.frame_map['register_face'].cleanup()
    
    def on_close(self):
        """Handle window close event."""
        self.cleanup()
        self.destroy()


if __name__ == "__main__":
    # Test main window
    app = MainWindow()
    app.mainloop()
