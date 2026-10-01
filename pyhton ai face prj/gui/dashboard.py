"""
Dashboard GUI Module
Displays system overview and statistics cards.
"""

import customtkinter as ctk
from typing import Dict, Any
from database.database import get_database


class DashboardFrame(ctk.CTkFrame):
    """Dashboard frame showing system overview and statistics."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        self._setup_layout()
        self._create_widgets()
        self._load_data()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
    
    def _create_widgets(self):
        """Create dashboard widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="w")
        
        # Statistics cards
        self._create_stat_card("Total Registered People", "0", "👥", 1, 0)
        self._create_stat_card("Total Face Profiles", "0", "👤", 1, 1)
        self._create_stat_card("Camera Status", "Ready", "📹", 1, 2)
        
        # System status section
        self._create_system_status_section()
    
    def _create_stat_card(self, title: str, value: str, icon: str, row: int, col: int):
        """Create a statistics card."""
        card_frame = ctk.CTkFrame(self)
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Icon and value
        icon_label = ctk.CTkLabel(
            card_frame,
            text=icon,
            font=ctk.CTkFont(size=32)
        )
        icon_label.grid(row=0, column=0, padx=15, pady=15)
        
        value_label = ctk.CTkLabel(
            card_frame,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        value_label.grid(row=0, column=1, padx=15, pady=15)
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(size=12)
        )
        title_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15))
        
        # Store reference
        setattr(self, f"{title.lower().replace(' ', '_')}_card", card_frame)
        setattr(self, f"{title.lower().replace(' ', '_')}_value", value_label)
    
    def _create_system_status_section(self):
        """Create the system status section."""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)
        
        # Section title
        section_title = ctk.CTkLabel(
            status_frame,
            text="System Status",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        section_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Status grid
        status_grid = ctk.CTkFrame(status_frame)
        status_grid.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        status_grid.grid_columnconfigure(0, weight=1)
        status_grid.grid_columnconfigure(1, weight=1)
        status_grid.grid_columnconfigure(2, weight=1)
        
        # Status items
        self._create_status_item(status_grid, "Recognition Engine", "Ready", 0, 0)
        self._create_status_item(status_grid, "Database", "Connected", 0, 1)
        self._create_status_item(status_grid, "Face Models", "Loaded", 0, 2)
        self._create_status_item(status_grid, "Currently Detected", "0", 1, 0)
        self._create_status_item(status_grid, "Recognized Faces", "0", 1, 1)
        self._create_status_item(status_grid, "Unknown Faces", "0", 1, 2)
    
    def _create_status_item(self, parent: ctk.CTkFrame, label: str, value: str, row: int, col: int):
        """Create a status item."""
        item_frame = ctk.CTkFrame(parent)
        item_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        label_widget = ctk.CTkLabel(
            item_frame,
            text=label,
            font=ctk.CTkFont(size=12)
        )
        label_widget.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        value_widget = ctk.CTkLabel(
            item_frame,
            text=value,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        value_widget.grid(row=1, column=0, padx=10, pady=(0, 10))
        
        # Store reference
        setattr(self, f"{label.lower().replace(' ', '_')}_status", value_widget)
    
    def _load_data(self):
        """Load data from database and update display."""
        try:
            # Get statistics
            person_manager = self.db.get_person_manager()
            stats = person_manager.get_statistics()
            
            # Update statistics cards
            self.total_registered_people_value.configure(text=str(stats['total_persons']))
            self.total_face_profiles_value.configure(text=str(stats['persons_with_faces']))
            
            # Check camera availability
            from utils.helpers import Helpers
            cameras = Helpers.get_available_cameras(max_cameras=1)
            camera_status = "Available" if cameras else "Not Available"
            self.camera_status_value.configure(text=camera_status)
            
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
    
    def refresh(self):
        """Refresh the dashboard data."""
        self._load_data()


if __name__ == "__main__":
    # Test dashboard frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    dashboard = DashboardFrame(app)
    dashboard.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
