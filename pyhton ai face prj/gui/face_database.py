"""
Face Database GUI Module
Manages and displays registered face profiles.
"""

import customtkinter as ctk
from typing import List, Optional
from pathlib import Path
from database.database import get_database
from database.models import Person
from PIL import Image, ImageTk
from utils.image_utils import ImageUtils


class FaceDatabaseFrame(ctk.CTkFrame):
    """Face database frame for managing registered profiles."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        self.current_person = None
        self.persons_list = []
        
        self._setup_layout()
        self._create_widgets()
        self._load_persons()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)  # Search and list
        self.grid_columnconfigure(1, weight=1)  # Details panel
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create face database widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Face Database",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Left panel - Search and list
        self._create_left_panel()
        
        # Right panel - Details
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Create the left panel with search and person list."""
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        left_panel.grid_rowconfigure(2, weight=1)
        left_panel.grid_columnconfigure(0, weight=1)
        
        # Search section
        search_frame = ctk.CTkFrame(left_panel)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_columnconfigure(1, weight=0)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by name, ID, or category")
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self._search_persons,
            width=80
        )
        self.search_button.grid(row=0, column=1, padx=(0, 10), pady=10)
        
        # Search type
        self.search_type = ctk.CTkOptionMenu(
            search_frame,
            values=["Name", "ID", "Category"],
            command=self._on_search_type_change
        )
        self.search_type.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")
        self.search_type.set("Name")
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            left_panel,
            text="Refresh List",
            command=self._load_persons,
            height=35
        )
        refresh_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Persons list
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        self.persons_scroll = ctk.CTkScrollableFrame(list_frame)
        self.persons_scroll.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    def _create_right_panel(self):
        """Create the right panel with person details."""
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        right_panel.grid_rowconfigure(5, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Person details section
        self._create_person_details(right_panel)
        
        # Action buttons
        self._create_action_buttons(right_panel)
    
    def _create_person_details(self, parent: ctk.CTkFrame):
        """Create person details display."""
        details_frame = ctk.CTkFrame(parent)
        details_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        details_frame.grid_rowconfigure(4, weight=1)
        details_frame.grid_columnconfigure(0, weight=1)
        
        # Profile image
        self.profile_image_label = ctk.CTkLabel(
            details_frame,
            text="No person selected",
            font=ctk.CTkFont(size=14),
            width=200,
            height=200
        )
        self.profile_image_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Person information
        info_frame = ctk.CTkFrame(details_frame)
        info_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        self._create_info_row(info_frame, "Person ID:", "person_id_label", 0)
        self._create_info_row(info_frame, "Full Name:", "full_name_label", 1)
        self._create_info_row(info_frame, "Email:", "email_label", 2)
        self._create_info_row(info_frame, "Phone:", "phone_label", 3)
        self._create_info_row(info_frame, "Category:", "category_label", 4)
        self._create_info_row(info_frame, "Registration Date:", "registration_date_label", 5)
        self._create_info_row(info_frame, "Face Data:", "face_data_label", 6)
    
    def _create_info_row(self, parent: ctk.CTkFrame, label: str, widget_name: str, row: int):
        """Create an information row."""
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        label_widget.grid(row=row, column=0, padx=10, pady=5, sticky="w")
        
        value_widget = ctk.CTkLabel(
            parent,
            text="-",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        value_widget.grid(row=row, column=1, padx=10, pady=5, sticky="w")
        
        setattr(self, widget_name, value_widget)
    
    def _create_action_buttons(self, parent: ctk.CTkFrame):
        """Create action buttons for person management."""
        button_frame = ctk.CTkFrame(parent)
        button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        self.edit_button = ctk.CTkButton(
            button_frame,
            text="Edit",
            command=self._edit_person,
            height=35,
            state="disabled"
        )
        self.edit_button.grid(row=0, column=0, padx=5, pady=10)
        
        self.update_face_button = ctk.CTkButton(
            button_frame,
            text="Update Face",
            command=self._update_face,
            height=35,
            state="disabled"
        )
        self.update_face_button.grid(row=0, column=1, padx=5, pady=10)
        
        self.delete_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            command=self._delete_person,
            height=35,
            fg_color="red",
            state="disabled"
        )
        self.delete_button.grid(row=0, column=2, padx=5, pady=10)
    
    def _load_persons(self):
        """Load all persons from database."""
        try:
            person_manager = self.db.get_person_manager()
            self.persons_list = person_manager.get_all_persons()
            
            self._update_persons_list()
            
        except Exception as e:
            print(f"Error loading persons: {e}")
            self.parent.show_message("Error", f"Error loading persons: {e}", "error")
    
    def _update_persons_list(self):
        """Update the persons list display."""
        # Clear existing widgets
        for widget in self.persons_scroll.winfo_children():
            widget.destroy()
        
        # Add person items
        for person in self.persons_list:
            person_item = self._create_person_item(person)
            person_item.pack(fill="x", padx=5, pady=5)
    
    def _create_person_item(self, person: Person) -> ctk.CTkFrame:
        """Create a person item for the list."""
        item_frame = ctk.CTkFrame(self.persons_scroll)
        
        # Name and ID
        name_label = ctk.CTkLabel(
            item_frame,
            text=person.full_name,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(side="left", padx=10, pady=10)
        
        id_label = ctk.CTkLabel(
            item_frame,
            text=f"ID: {person.person_id}",
            font=ctk.CTkFont(size=11)
        )
        id_label.pack(side="left", padx=10, pady=10)
        
        # Category if available
        if person.category:
            category_label = ctk.CTkLabel(
                item_frame,
                text=person.category,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            category_label.pack(side="right", padx=10, pady=10)
        
        # Click event
        item_frame.bind("<Button-1>", lambda e, p=person: self._select_person(p))
        name_label.bind("<Button-1>", lambda e, p=person: self._select_person(p))
        id_label.bind("<Button-1>", lambda e, p=person: self._select_person(p))
        
        return item_frame
    
    def _select_person(self, person: Person):
        """Select a person and display their details."""
        self.current_person = person
        
        # Enable buttons
        self.edit_button.configure(state="normal")
        self.update_face_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        
        # Update details
        self.person_id_label.configure(text=person.person_id)
        self.full_name_label.configure(text=person.full_name)
        self.email_label.configure(text=person.email or "-")
        self.phone_label.configure(text=person.phone or "-")
        self.category_label.configure(text=person.category or "-")
        self.registration_date_label.configure(text=person.registration_date)
        
        # Face data status
        has_face = person.face_embeddings is not None
        self.face_data_label.configure(
            text="Available" if has_face else "Not Available",
            text_color="green" if has_face else "red"
        )
        
        # Load profile image
        if person.profile_image_path and Path(person.profile_image_path).exists():
            try:
                image = ImageUtils.load_image(person.profile_image_path)
                if image is not None:
                    # Resize for display
                    display_image = ImageUtils.resize_image(image, target_size=(200, 200))
                    photo_image = ImageUtils.convert_to_photoimage(display_image)
                    if photo_image:
                        self.profile_image_label.configure(image=photo_image, text="")
                        self.profile_image_label.image = photo_image
            except Exception as e:
                print(f"Error loading profile image: {e}")
                self.profile_image_label.configure(image="", text="No image")
        else:
            self.profile_image_label.configure(image="", text="No image")
    
    def _search_persons(self):
        """Search persons based on search criteria."""
        search_term = self.search_entry.get().strip()
        search_type = self.search_type.get().lower()
        
        if not search_term:
            self._load_persons()
            return
        
        try:
            person_manager = self.db.get_person_manager()
            
            search_by_map = {
                'name': 'name',
                'id': 'id',
                'category': 'category'
            }
            
            self.persons_list = person_manager.search_persons(
                search_term,
                search_by=search_by_map.get(search_type, 'name')
            )
            
            self._update_persons_list()
            
        except Exception as e:
            print(f"Error searching persons: {e}")
            self.parent.show_message("Error", f"Error searching: {e}", "error")
    
    def _on_search_type_change(self, value):
        """Handle search type change."""
        pass
    
    def _edit_person(self):
        """Edit the selected person's information."""
        if not self.current_person:
            return
        
        # For simplicity, show a message dialog
        # In a full implementation, this would open an edit dialog
        self.parent.show_message(
            "Edit Person",
            f"Edit functionality for {self.current_person.full_name} would be implemented here.",
            "info"
        )
    
    def _update_face(self):
        """Update the selected person's face data."""
        if not self.current_person:
            return
        
        # For simplicity, show a message dialog
        # In a full implementation, this would open a face update dialog
        self.parent.show_message(
            "Update Face",
            f"Face update functionality for {self.current_person.full_name} would be implemented here.",
            "info"
        )
    
    def _delete_person(self):
        """Delete the selected person."""
        if not self.current_person:
            return
        
        # Confirm deletion
        confirmed = self.parent.show_confirmation(
            "Confirm Deletion",
            f"Are you sure you want to delete {self.current_person.full_name}? This action cannot be undone."
        )
        
        if not confirmed:
            return
        
        try:
            person_manager = self.db.get_person_manager()
            
            if person_manager.delete_person(self.current_person.person_id):
                self.parent.show_message("Success", "Person deleted successfully", "info")
                self._clear_selection()
                self._load_persons()
            else:
                self.parent.show_message("Error", "Could not delete person", "error")
                
        except Exception as e:
            print(f"Error deleting person: {e}")
            self.parent.show_message("Error", f"Error: {e}", "error")
    
    def _clear_selection(self):
        """Clear the current selection."""
        self.current_person = None
        
        # Disable buttons
        self.edit_button.configure(state="disabled")
        self.update_face_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        
        # Clear details
        self.person_id_label.configure(text="-")
        self.full_name_label.configure(text="-")
        self.email_label.configure(text="-")
        self.phone_label.configure(text="-")
        self.category_label.configure(text="-")
        self.registration_date_label.configure(text="-")
        self.face_data_label.configure(text="-")
        
        self.profile_image_label.configure(image="", text="No person selected")
        self.profile_image_label.image = None


if __name__ == "__main__":
    # Test face database frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    face_database = FaceDatabaseFrame(app)
    face_database.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
