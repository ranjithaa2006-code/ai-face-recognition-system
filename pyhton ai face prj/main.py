"""
AI Face Recognition System - Main Entry Point
Launches the face recognition application with GUI.
"""

import sys
import customtkinter as ctk
from gui.main_window import MainWindow
from database.database import get_database
from utils.security import initialize_default_admin


def main():
    """Main function to launch the application."""
    try:
        # Initialize database
        print("Initializing database...")
        db = get_database()
        db.initialize()
        print("Database initialized successfully")
        
        # Initialize default admin user
        print("Initializing default admin...")
        initialize_default_admin(username="admin", password="admin123")
        print("Default admin initialized")
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create and launch main window
        print("Launching application...")
        app = MainWindow(title="AI Face Recognition System")
        
        # Handle window close event
        app.protocol("WM_DELETE_WINDOW", app.on_close)
        
        # Start the application
        app.mainloop()
        
        print("Application closed successfully")
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
