# AI Face Recognition System

A professional, advanced AI-based face recognition system built with Python for real-time face detection, recognition, and identity management. This system is designed as a complete desktop application suitable for college final-year projects and portfolios.

## 🌟 Features

### Core Functionality
- **Real-time Face Recognition**: Live face detection and recognition via webcam
- **Multiple Face Detection**: Simultaneous detection and recognition of multiple faces
- **Face Profile Management**: Complete registration system for face profiles
- **Image-Based Recognition**: Upload and process images for face recognition
- **Face Database**: Search, view, update, and delete registered profiles
- **Performance Analytics**: Real-time statistics and performance metrics
- **Configurable Settings**: Customizable recognition parameters and system settings

### Advanced Features
- **Stable Recognition**: Face tracking to prevent flickering between frames
- **Confidence Scoring**: Display recognition confidence/similarity percentages
- **Unknown Face Detection**: Identifies and highlights unregistered faces
- **Multi-Angle Registration**: Support for multiple images per person for improved accuracy
- **Local Data Storage**: All data stored locally (no cloud dependencies)
- **Security Features**: Admin authentication, password hashing, secure data handling
- **Modern GUI**: Professional dark/light theme interface with CustomTkinter

## 🛠️ Technologies Used

- **Python 3.11+**: Core programming language
- **OpenCV**: Computer vision and image processing
- **face_recognition**: Face detection and embedding generation
- **CustomTkinter**: Modern GUI framework
- **NumPy**: Numerical computing and array operations
- **Pillow**: Image processing and manipulation
- **SQLite**: Local database storage
- **Pandas**: Data management and analysis
- **Matplotlib**: Analytics visualization
- **bcrypt**: Password security and hashing

## 📋 System Requirements

### Hardware Requirements
- **Processor**: Intel Core i5 or equivalent (recommended: i7 or better)
- **RAM**: 8GB minimum (recommended: 16GB)
- **Storage**: 500MB free space
- **Camera**: Webcam (USB or integrated)
- **OS**: Windows 10/11, macOS 10.14+, or Linux

### Software Requirements
- **Python**: 3.11 or higher
- **pip**: Python package manager
- **Git**: For cloning the repository (optional)

## 🚀 Installation Instructions

### 1. Clone or Download the Repository

```bash
git clone <repository-url>
cd pyhton-ai-face-prj
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Database

The database will be automatically initialized when you first run the application. However, you can manually initialize it:

```bash
python -c "from database.schema import initialize_database; initialize_database()"
```

### 5. Run the Application

```bash
python main.py
```

## 📖 Usage Instructions

### First-Time Setup

1. **Launch the Application**: Run `python main.py`
2. **Default Admin Login**: 
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ **Important**: Change the default password after first login

### Registering a Face

1. Navigate to **Register Face** from the sidebar
2. Fill in the required information:
   - **Person ID**: Unique identifier (e.g., EMP001)
   - **Full Name**: Person's full name
   - **Email**: Optional email address
   - **Phone**: Optional phone number
   - **Category/Department**: Optional category
3. **Add Face Image**:
   - Click **Upload Image** to select an existing photo
   - Or click **Capture from Camera** to take a live photo
4. Ensure only one face is visible in the image
5. Click **Register Face** to complete registration

### Live Face Recognition

1. Navigate to **Live Recognition** from the sidebar
2. Click **Start Camera** to begin
3. The system will:
   - Display live webcam feed
   - Detect faces in real-time
   - Recognize registered faces (green boxes)
   - Highlight unknown faces (red boxes)
   - Show recognition confidence percentages
4. Click **Stop Camera** to stop recognition

### Image Recognition

1. Navigate to **Image Recognition** from the sidebar
2. Click **Upload Image** to select an image file
3. Click **Process Image** to analyze the image
4. View recognition results:
   - Detected faces with bounding boxes
   - Person names and confidence scores
   - Unknown face indicators
5. Click **Save Result** to export the processed image

### Managing Face Database

1. Navigate to **Face Database** from the sidebar
2. **Search** for persons by name, ID, or category
3. **View** person details by clicking on a person in the list
4. **Edit** person information
5. **Update Face** data for existing profiles
6. **Delete** profiles (with confirmation)

### Configuring Settings

1. Navigate to **Settings** from the sidebar
2. **Recognition Settings**:
   - Recognition Threshold: Lower = stricter matching (0.3-0.8)
   - Detection Frequency: Frames between detections (1-30)
   - Minimum Face Size: Minimum face size in pixels (50-500)
3. **Camera Settings**:
   - Camera Index: Webcam camera index (0-10)
   - Frame Scaling: Resize factor for performance (0.1-1.0)
4. **Display Settings**:
   - Show FPS: Display frames per second
   - Application Theme: Dark, Light, or System
   - Unknown Face Behavior: Alert, Ignore, or Log
5. Click **Save Settings** to apply changes

### Viewing Analytics

1. Navigate to **Analytics** from the sidebar
2. View real-time statistics:
   - Recognition attempts
   - Successful matches
   - Unknown faces
   - Average processing time
3. View performance charts:
   - Recognition performance bar chart
   - Processing time distribution

## 🏗️ System Architecture

### Project Structure

```
pyhton-ai-face-prj/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── database/              # Database layer
│   ├── __init__.py
│   ├── database.py        # Database interface
│   ├── schema.py          # Database schema
│   └── models.py          # Data models
├── face_engine/           # Face recognition engine
│   ├── __init__.py
│   ├── detector.py        # Face detection
│   ├── encoder.py         # Face encoding
│   ├── recognizer.py      # Face recognition
│   ├── matcher.py         # Face matching
│   └── tracker.py         # Face tracking
├── gui/                   # Graphical user interface
│   ├── __init__.py
│   ├── main_window.py     # Main application window
│   ├── dashboard.py       # Dashboard view
│   ├── live_recognition.py # Live recognition view
│   ├── register_face.py    # Face registration view
│   ├── face_database.py   # Face database view
│   ├── image_recognition.py # Image recognition view
│   ├── analytics.py       # Analytics view
│   ├── settings.py        # Settings view
│   └── about.py          # About view
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── security.py        # Security functions
│   ├── image_utils.py     # Image processing utilities
│   ├── validators.py      # Input validation
│   └── helpers.py         # General helper functions
├── tests/                 # Automated tests
│   ├── __init__.py
│   ├── test_database.py   # Database tests
│   ├── test_validators.py # Validator tests
│   ├── test_security.py   # Security tests
│   └── test_face_engine.py # Face engine tests
├── data/                  # Data directory
│   ├── database/          # Database files
│   ├── faces/             # Face images
│   └── exports/           # Exported files
└── assets/                # Static assets
```

### Recognition Pipeline

The face recognition system follows this pipeline:

1. **Input**: Camera frame or uploaded image
2. **Face Detection**: Locate faces in the image using HOG or CNN model
3. **Face Localization**: Extract face regions with bounding boxes
4. **Face Encoding**: Generate 128-dimensional face embeddings
5. **Comparison**: Compare embeddings against known face database
6. **Distance Calculation**: Calculate Euclidean distance between embeddings
7. **Threshold Application**: Apply recognition threshold for classification
8. **Classification**: Classify as recognized or unknown
9. **Tracking**: Track faces across frames for stability
10. **Output**: Display results with bounding boxes and labels

### Database Design

#### Persons Table
- `id`: Primary key (auto-increment)
- `person_id`: Unique person identifier
- `full_name`: Person's full name
- `email`: Email address (optional)
- `phone`: Phone number (optional)
- `category`: Category/department (optional)
- `profile_image_path`: Path to profile image
- `face_embeddings`: Face embedding data (BLOB)
- `registration_date`: Registration timestamp
- `last_updated`: Last update timestamp

#### Settings Table
- `key`: Setting key (primary key)
- `value`: Setting value

#### Analytics Table
- `id`: Primary key (auto-increment)
- `metric_name`: Name of the metric
- `metric_value`: Metric value
- `timestamp`: Measurement timestamp

## 🔧 Troubleshooting

### Camera Not Working

**Problem**: Camera doesn't start or shows error

**Solutions**:
1. Check if camera is properly connected
2. Ensure no other application is using the camera
3. Try different camera index in Settings (0, 1, 2, etc.)
4. Check camera permissions in system settings
5. Update camera drivers

### Face Detection Not Working

**Problem**: Faces not being detected in images

**Solutions**:
1. Ensure adequate lighting
2. Check that faces are clearly visible and not obscured
3. Try adjusting minimum face size in Settings
4. Ensure image resolution is sufficient (at least 640x480)
5. Try with CNN model (slower but more accurate)

### Recognition Accuracy Issues

**Problem**: Low recognition accuracy or false positives

**Solutions**:
1. Adjust recognition threshold in Settings:
   - Lower threshold (0.4-0.5) for stricter matching
   - Higher threshold (0.6-0.7) for more lenient matching
2. Register multiple images of the same person from different angles
3. Ensure good quality registration images
4. Check lighting conditions during recognition
5. Verify face embeddings are properly stored

### Database Errors

**Problem**: Database connection or operation errors

**Solutions**:
1. Ensure data/database directory exists
2. Check file permissions for database directory
3. Verify SQLite is properly installed
4. Try deleting the database file and reinitializing
5. Check available disk space

### Import Errors

**Problem**: Module import errors when running the application

**Solutions**:
1. Ensure virtual environment is activated
2. Install all dependencies: `pip install -r requirements.txt`
3. Check Python version (3.11+ required)
4. Verify all package installations: `pip list`
5. Try reinstalling problematic packages

### Performance Issues

**Problem**: Application running slowly or lagging

**Solutions**:
1. Increase frame scaling in Settings (0.5-0.7)
2. Increase detection frequency (fewer detections per second)
3. Use HOG model instead of CNN (faster but less accurate)
4. Close other applications to free up resources
5. Reduce minimum face size to reduce processing
6. Check system resources (CPU, RAM usage)

## 🔒 Privacy and Security

### Privacy Notice

This system processes biometric data (face embeddings) for face recognition purposes. 

**Important Privacy Considerations**:
- All data is stored locally on your device
- No data is transmitted to external servers
- Face embeddings are mathematical representations, not actual images
- Users have the right to delete their biometric data at any time
- Face embeddings should only be collected with appropriate consent
- The system does not provide perfect identification or security guarantees

### Security Features

- **Password Hashing**: Admin passwords are hashed using bcrypt
- **Secure Database**: Parameterized queries prevent SQL injection
- **Input Validation**: All user inputs are validated and sanitized
- **Local Storage**: No cloud dependencies or external data transmission
- **Data Deletion**: Complete data deletion capability for user privacy

### Best Practices

1. **Change Default Password**: Immediately change the default admin password
2. **Secure Access**: Limit physical access to the system
3. **Regular Backups**: Backup the database regularly
4. **Data Minimization**: Only collect necessary biometric data
5. **User Consent**: Obtain explicit consent before registering faces
6. **Secure Storage**: Ensure the system runs on a secure device

## ⚠️ Limitations

### Recognition Accuracy

- Recognition accuracy depends on:
  - Lighting conditions
  - Camera quality
  - Face pose and angle
  - Image quality and resolution
  - Distance from camera
  - Facial expressions and accessories

### System Limitations

- **Not Security-Grade**: Not suitable for high-security applications
- **Lighting Dependent**: Performance degrades in poor lighting
- **Single-Person Registration**: Registration requires single-face images
- **Local Processing**: All processing happens locally (resource intensive)
- **No Cloud Backup**: No automatic cloud backup or sync
- **No Multi-Factor**: No additional authentication factors

### Environmental Factors

- Extreme lighting conditions (very bright or very dark)
- Partial face occlusion (masks, glasses, hats)
- Extreme face angles (profile views)
- Poor image quality or low resolution
- Multiple similar-looking individuals

## 🚀 Future Improvements

### Planned Features

1. **Multi-Face Registration**: Support for registering multiple faces in one image
2. **Anti-Spoofing**: Liveness detection to prevent photo/video attacks
3. **Face Clustering**: Automatic grouping of similar faces
4. **Emotion Recognition**: Detect facial expressions and emotions
5. **Age and Gender Estimation**: Demographic estimation
6. **Cloud Sync**: Optional cloud backup and synchronization
7. **Mobile App**: Cross-platform mobile application
8. **API Interface**: REST API for integration with other systems
9. **Advanced Analytics**: More detailed analytics and reporting
10. **Multi-Language Support**: Internationalization support

### Technical Improvements

1. **GPU Acceleration**: CUDA support for faster processing
2. **Deep Learning Models**: Integration with more advanced models
3. **Edge Deployment**: Optimization for edge devices
4. **Real-Time Video Processing**: Video file processing capabilities
5. **Batch Processing**: Process multiple images at once
6. **Export Options**: More export formats and options
7. **Theme Customization**: More theme and UI customization options
8. **Keyboard Shortcuts**: Keyboard shortcuts for common actions

## 📝 Academic Documentation

For academic purposes, this project includes comprehensive documentation covering:

- Abstract and Introduction
- Problem Statement and Objectives
- Existing System Analysis
- Proposed System Design
- System Requirements (Hardware/Software)
- System Architecture and Data Flow
- Database Design
- Methodology and Algorithm
- Face Recognition Algorithm Explanation
- Testing and Results
- Limitations and Future Scope
- Conclusion and References

See the separate academic documentation file for detailed academic content.

## 🧪 Testing

### Running Tests

The project includes comprehensive automated tests:

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_database.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=.
```

### Test Coverage

- **Database Operations**: CRUD operations, validation, statistics
- **Security Functions**: Password hashing, authentication, validation
- **Face Engine**: Detection, encoding, recognition, matching, tracking
- **Input Validation**: All input fields and validation rules

## 📄 License

This project is created for educational and portfolio purposes. Please ensure compliance with local regulations regarding biometric data collection and processing.

## 🤝 Contributing

This is a standalone project for educational purposes. For improvements or issues, please refer to the project documentation or contact the development team.

## 📞 Support

For issues, questions, or support:

1. Check the Troubleshooting section
2. Review the academic documentation
3. Verify system requirements and installation steps
4. Check for common issues in the Limitations section

## 🎓 Acknowledgments

This project utilizes several open-source libraries and frameworks:

- **face_recognition**: Face recognition library by Adam Geitgey
- **OpenCV**: Open Source Computer Vision Library
- **CustomTkinter**: Modern CustomTkinter library
- **dlib**: C++ toolkit containing machine learning algorithms

---

**Note**: This system is designed for educational and portfolio purposes. It should not be relied upon for security-critical applications without proper testing, validation, and professional assessment.
