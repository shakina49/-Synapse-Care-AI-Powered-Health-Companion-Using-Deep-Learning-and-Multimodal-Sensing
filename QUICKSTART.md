# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- FastAPI (web framework)
- MediaPipe (pose detection)
- OpenCV & Pillow (image processing)
- scikit-learn (ML model)
- And more...

### Step 2: Verify Setup

Run the verification script to ensure everything is working:

```bash
python verify_setup.py
```

This will check:
- ✓ All packages are installed
- ✓ All required files exist
- ✓ Models can be initialized
- ✓ Training data is valid
- ✓ Basic functionality works

### Step 3: Start the Server

**Option A - Using the batch file (Windows):**
```bash
start_server.bat
```

**Option B - Using Python directly:**
```bash
python main.py
```

**Option C - Using uvicorn:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at: **http://localhost:8000**

---

## 🧪 Testing the API

### Option 1: Web Interface (Easiest)

1. Open `test_upload.html` in your web browser
2. Upload an exercise photo
3. Select exercise type (or leave as auto-detect)
4. Click "Analyze Posture"
5. View the results!

### Option 2: API Documentation

Visit the interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Option 3: Python Script

Run the test script:
```bash
python test_api.py
```

Or use it programmatically:
```python
import requests

url = "http://localhost:8000/analyze"
files = {"file": open("exercise_photo.jpg", "rb")}
data = {"exercise_type": "squat"}  # Optional

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Option 4: cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@exercise_photo.jpg" \
  -F "exercise_type=squat"
```

---

## 📸 Supported Exercises

- **Squat** - Best with side view
- **Push-up** - Best with side view
- **Plank** - Best with side view
- **Lunge** - Best with side view
- **Deadlift** - Best with side view

---

## 💡 Tips for Best Results

1. **Full body in frame** - Ensure head, shoulders, hips, knees, and ankles are visible
2. **Good lighting** - Avoid heavy shadows
3. **Side view** - Works best for most exercises
4. **Single person** - Only the exercising person should be in frame
5. **Clear photo** - Avoid blurry or low-quality images

---

## 📊 Understanding the Response

The API returns a JSON response with:

```json
{
  "success": true,
  "detected": true,
  "exercise_type": "squat",
  "posture_correct": true,
  "confidence": 0.92,
  "feedback": ["Great form! Your posture looks correct."],
  "keypoints_detected": true,
  "angles": {
    "knee_angle": 95.2,
    "hip_angle": 88.5,
    "torso_angle": 85.3
  },
  "issues": [],
  "recommendations": ["Keep up the good work!"]
}
```

### Key Fields:
- **posture_correct**: `true` if posture is correct, `false` otherwise
- **confidence**: How confident the system is (0.0 to 1.0)
- **angles**: Detected joint angles in degrees
- **issues**: List of detected posture problems
- **recommendations**: Suggestions for improvement

---

## 🔧 Troubleshooting

### Server won't start?
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is already in use
- Try running on a different port: `uvicorn main:app --port 8080`

### "No person detected" error?
- Ensure the full body is visible in the photo
- Check lighting - avoid heavy shadows
- Try a different angle or clearer photo

### Low confidence scores?
- Use higher quality images
- Ensure proper lighting
- Make sure all key body parts are visible
- Try a side view instead of front view

### Import errors?
- Run `python verify_setup.py` to check what's missing
- Reinstall dependencies: `pip install -r requirements.txt`
- Make sure you're using Python 3.8 or higher

---

## 📁 Project Structure

```
f_project/
├── main.py                  # FastAPI application entry point
├── models/
│   ├── pose_detector.py     # MediaPipe pose detection
│   ├── posture_analyzer.py  # Posture analysis logic
│   └── posture_model.py     # ML classifier
├── utils/
│   └── image_processor.py   # Image preprocessing
├── archive/                 # Training data
│   ├── angles.csv
│   └── labels.csv
├── test_upload.html         # Web testing interface
├── test_api.py             # Python API test script
├── verify_setup.py         # Setup verification script
└── requirements.txt        # Python dependencies
```

---

## 🎯 Next Steps

1. Test with your own exercise photos
2. Try different exercise types
3. Integrate the API into your application
4. Explore the API documentation at http://localhost:8000/docs

---

## 📞 Need Help?

Check out:
- Full documentation in `README.md`
- API docs at http://localhost:8000/docs
- Run `python verify_setup.py` to diagnose issues

Happy exercising! 💪
