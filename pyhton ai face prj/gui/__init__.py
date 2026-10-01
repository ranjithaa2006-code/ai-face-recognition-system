"""
GUI Package
Provides the graphical user interface for the face recognition system.
"""

from gui.main_window import MainWindow
from gui.dashboard import DashboardFrame
from gui.live_recognition import LiveRecognitionFrame
from gui.register_face import RegisterFaceFrame
from gui.face_database import FaceDatabaseFrame
from gui.image_recognition import ImageRecognitionFrame
from gui.analytics import AnalyticsFrame
from gui.settings import SettingsFrame
from gui.about import AboutFrame

__all__ = [
    'MainWindow',
    'DashboardFrame',
    'LiveRecognitionFrame',
    'RegisterFaceFrame',
    'FaceDatabaseFrame',
    'ImageRecognitionFrame',
    'AnalyticsFrame',
    'SettingsFrame',
    'AboutFrame'
]
