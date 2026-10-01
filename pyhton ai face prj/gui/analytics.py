"""
Analytics GUI Module
Displays system performance analytics and statistics.
"""

import customtkinter as ctk
from typing import Dict, Any
from database.database import get_database
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkinter
import numpy as np


class AnalyticsFrame(ctk.CTkFrame):
    """Analytics frame showing system performance statistics."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.parent = parent
        self.db = get_database()
        
        self._setup_layout()
        self._create_widgets()
        self._load_analytics()
    
    def _setup_layout(self):
        """Setup the grid layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
    
    def _create_widgets(self):
        """Create analytics widgets."""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Analytics",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="w")
        
        # Statistics cards
        self._create_statistics_cards()
        
        # Charts section
        self._create_charts_section()
    
    def _create_statistics_cards(self):
        """Create statistics cards."""
        stats_frame = ctk.CTkFrame(self)
        stats_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        stats_frame.grid_rowconfigure(0, weight=1)
        
        self._create_stat_card(stats_frame, "Recognition Attempts", "0", "🔍", 0, 0)
        self._create_stat_card(stats_frame, "Successful Matches", "0", "✅", 0, 1)
        self._create_stat_card(stats_frame, "Unknown Faces", "0", "❓", 0, 2)
        self._create_stat_card(stats_frame, "Avg Processing Time", "0ms", "⏱️", 0, 3)
    
    def _create_stat_card(self, parent: ctk.CTkFrame, title: str, value: str, icon: str, row: int, col: int):
        """Create a statistics card."""
        card_frame = ctk.CTkFrame(parent)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Icon
        icon_label = ctk.CTkLabel(
            card_frame,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Value
        value_label = ctk.CTkLabel(
            card_frame,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        value_label.grid(row=1, column=0, padx=10, pady=(0, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(size=10)
        )
        title_label.grid(row=2, column=0, padx=10, pady=(0, 10))
        
        # Store reference
        setattr(self, f"{title.lower().replace(' ', '_')}_card", card_frame)
        setattr(self, f"{title.lower().replace(' ', '_')}_value", value_label)
    
    def _create_charts_section(self):
        """Create the charts section."""
        charts_frame = ctk.CTkFrame(self)
        charts_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(0, weight=1)
        
        # Charts title
        charts_title = ctk.CTkLabel(
            charts_frame,
            text="Performance Metrics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        charts_title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")
        
        # Chart area
        self.chart_frame = ctk.CTkFrame(charts_frame)
        self.chart_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder for chart
        self.chart_label = ctk.CTkLabel(
            self.chart_frame,
            text="Charts will be displayed here",
            font=ctk.CTkFont(size=14)
        )
        self.chart_label.grid(row=0, column=0, padx=20, pady=20)
    
    def _load_analytics(self):
        """Load analytics data from database."""
        try:
            analytics_manager = self.db.get_analytics_manager()
            
            # Get metrics summary
            summary = analytics_manager.get_all_metrics_summary()
            
            # Update statistics cards
            self._update_statistics_cards(summary)
            
            # Create charts
            self._create_charts(summary)
            
        except Exception as e:
            print(f"Error loading analytics: {e}")
    
    def _update_statistics_cards(self, summary: Dict[str, Dict[str, Any]]):
        """Update statistics cards with data."""
        try:
            # Recognition attempts
            recognition_attempts = summary.get('recognition_attempts', {}).get('count', 0)
            self.recognition_attempts_value.configure(text=str(recognition_attempts))
            
            # Successful matches
            successful_matches = summary.get('successful_matches', {}).get('count', 0)
            self.successful_matches_value.configure(text=str(successful_matches))
            
            # Unknown faces
            unknown_faces = summary.get('unknown_faces', {}).get('count', 0)
            self.unknown_faces_value.configure(text=str(unknown_faces))
            
            # Average processing time
            avg_processing_time = summary.get('processing_time', {}).get('average', 0)
            self.avg_processing_time_value.configure(text=f"{avg_processing_time:.1f}ms")
            
        except Exception as e:
            print(f"Error updating statistics cards: {e}")
    
    def _create_charts(self, summary: Dict[str, Dict[str, Any]]):
        """Create charts with analytics data."""
        try:
            # Clear previous chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()
            
            # Create matplotlib figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            fig.patch.set_facecolor('#2b2b2b')
            
            # Chart 1: Recognition performance
            metrics = ['Attempts', 'Matches', 'Unknown']
            values = [
                summary.get('recognition_attempts', {}).get('count', 0),
                summary.get('successful_matches', {}).get('count', 0),
                summary.get('unknown_faces', {}).get('count', 0)
            ]
            
            colors = ['#3498db', '#2ecc71', '#e74c3c']
            ax1.bar(metrics, values, color=colors)
            ax1.set_title('Recognition Performance', color='white')
            ax1.set_ylabel('Count', color='white')
            ax1.tick_params(axis='x', colors='white')
            ax1.tick_params(axis='y', colors='white')
            ax1.spines['bottom'].set_color('white')
            ax1.spines['left'].set_color('white')
            ax1.spines['top'].set_color('#2b2b2b')
            ax1.spines['right'].set_color('#2b2b2b')
            
            # Chart 2: Processing time distribution
            processing_times = summary.get('processing_time', {})
            if processing_times.get('count', 0) > 0:
                avg_time = processing_times.get('average', 0)
                min_time = processing_times.get('min', 0)
                max_time = processing_times.get('max', 0)
                
                time_metrics = ['Average', 'Min', 'Max']
                time_values = [avg_time, min_time, max_time]
                
                ax2.bar(time_metrics, time_values, color='#9b59b6')
                ax2.set_title('Processing Time (ms)', color='white')
                ax2.set_ylabel('Time (ms)', color='white')
                ax2.tick_params(axis='x', colors='white')
                ax2.tick_params(axis='y', colors='white')
                ax2.spines['bottom'].set_color('white')
                ax2.spines['left'].set_color('white')
                ax2.spines['top'].set_color('#2b2b2b')
                ax2.spines['right'].set_color('#2b2b2b')
            else:
                ax2.text(0.5, 0.5, 'No processing time data', 
                        ha='center', va='center', color='white', transform=ax2.transAxes)
            
            plt.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkinter(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            print(f"Error creating charts: {e}")
            self.chart_label.configure(text="Error creating charts")
    
    def refresh(self):
        """Refresh the analytics data."""
        self._load_analytics()


if __name__ == "__main__":
    # Test analytics frame
    app = ctk.CTk()
    app.geometry("1280x720")
    
    analytics = AnalyticsFrame(app)
    analytics.pack(fill="both", expand=True, padx=10, pady=10)
    
    app.mainloop()
