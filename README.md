# Exercise Posture Analysis Backend

A FastAPI-based backend service that analyzes physical exercise photos and determines whether the posture is correct or not. The system uses MediaPipe Pose for pose detection and compares detected postures against reference data from multiple sources.

## Features

- **Pose Detection**: Uses MediaPipe Pose to detect human keypoints in images
- **Posture Analysis**: Analyzes exercise posture by calculating angles and checking alignments
- **Multiple Exercise Support**: Supports squat, push-up, plank, lunge, and deadlift exercises
- **Auto-Detection**: Automatically detects exercise type if not specified
- **Detailed Feedback**: Provides specific feedback on posture issues and recommendations
- **RESTful API**: Clean REST API with proper error handling

## Supported Exercises

- Squat
- Push-up
- Plank
- Lunge
- Deadlift

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Start the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### 1. Health Check
```
GET /health
```

#### 2. Analyze Posture
```
POST /analyze
Content-Type: multipart/form-data

Parameters:
- file: Image file (required)
- exercise_type: Optional exercise type (squat, pushup, plank, lunge, deadlift)
```

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@exercise_photo.jpg" \
  -F "exercise_type=squat"
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:8000/analyze"
files = {"file": open("exercise_photo.jpg", "rb")}
data = {"exercise_type": "squat"}  # Optional

response = requests.post(url, files=files, data=data)
print(response.json())
```

#### 3. Get Supported Exercises
```
GET /supported-exercises
```

### Response Format

```json
{
  "success": true,
  "detected": true,
  "exercise_type": "squat",
  "posture_correct": true,
  "confidence": 0.95,
  "feedback": [
    "Great form! Your posture looks correct.",
    "\nDetected angles:",
    "  knee_angle: 90.5°",
    "  hip_angle: 82.3°"
  ],
  "keypoints_detected": true,
  "angles": {
    "knee_angle": 90.5,
    "hip_angle": 82.3,
    "torso_angle": 85.2
  },
  "alignments": {
    "knees_over_toes": true,
    "body_straight": true
  },
  "issues": [],
  "recommendations": [
    "Keep up the good work! Maintain this form."
  ]
}
```

## How It Works

1. **Image Upload**: User uploads an exercise photo
2. **Pose Detection**: MediaPipe Pose detects 33 body keypoints
3. **Angle Calculation**: System calculates key joint angles (knee, hip, elbow, torso)
4. **Alignment Check**: Verifies body alignments (straight line, knee position, etc.)
5. **Comparison**: Compares detected angles and alignments against reference data
6. **Analysis**: Identifies issues and generates feedback
7. **Response**: Returns detailed analysis with correctness score and recommendations

## Reference Data Sources

The system uses reference data that includes:
- Ideal angle ranges for each exercise
- Alignment requirements
- Common posture issues
- Exercise-specific guidelines

This data is compiled from multiple fitness and biomechanics sources to ensure accuracy.

## Project Structure

```
f_project/
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── models/
│   ├── __init__.py
│   ├── pose_detector.py   # MediaPipe pose detection
│   └── posture_analyzer.py # Posture analysis logic
└── utils/
    ├── __init__.py
    └── image_processor.py  # Image preprocessing utilities
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Error Handling

The API handles various error cases:
- Invalid file types
- No person detected in image
- Missing keypoints
- Processing errors

## Future Enhancements

- Support for more exercise types
- Video analysis support
- Real-time feedback
- User profiles and progress tracking
- Machine learning model for improved accuracy

## License

This project is provided as-is for educational and development purposes.

