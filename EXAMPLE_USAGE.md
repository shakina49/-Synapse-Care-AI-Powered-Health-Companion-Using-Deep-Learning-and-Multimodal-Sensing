# Example Usage Guide

This guide shows practical examples of using the Exercise Posture Analysis API.

---

## 🌐 Example 1: Using the Web Interface

1. **Start the server**:
   ```bash
   python main.py
   ```

2. **Open the test page**:
   - Open `test_upload.html` in your web browser
   - You should see "✓ Server is online and ready"

3. **Upload an image**:
   - Click the upload area or drag and drop an exercise photo
   - Select exercise type (or leave as "Auto-detect")
   - Click "Analyze Posture"

4. **View results**:
   - Posture Status: ✓ Correct or ✗ Incorrect
   - Confidence score
   - Detected angles
   - Issues and recommendations

---

## 🐍 Example 2: Python Script

### Basic Usage

```python
import requests

# API endpoint
url = "http://localhost:8000/analyze"

# Upload image with auto-detection
with open("squat_photo.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    
result = response.json()

if result["success"]:
    print(f"Exercise: {result['exercise_type']}")
    print(f"Posture Correct: {result['posture_correct']}")
    print(f"Confidence: {result['confidence']:.1%}")
    
    if result["issues"]:
        print("\nIssues found:")
        for issue in result["issues"]:
            print(f"  - {issue}")
    
    print("\nRecommendations:")
    for rec in result["recommendations"]:
        print(f"  - {rec}")
```

### Specify Exercise Type

```python
import requests

url = "http://localhost:8000/analyze"

with open("pushup_photo.jpg", "rb") as f:
    files = {"file": f}
    data = {"exercise_type": "pushup"}  # Specify exercise type
    response = requests.post(url, files=files, data=data)

result = response.json()
print(result)
```

### Handle Errors Gracefully

```python
import requests

def analyze_posture(image_path, exercise_type=None):
    """Analyze exercise posture from image"""
    url = "http://localhost:8000/analyze"
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {}
            if exercise_type:
                data["exercise_type"] = exercise_type
            
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                return result
            else:
                print(f"Error: {result.get('error', 'Unknown error')}")
                return None
                
    except FileNotFoundError:
        print(f"Error: File '{image_path}' not found")
        return None
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to API. Is the server running?")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Usage
result = analyze_posture("exercise.jpg", "squat")
if result:
    print(f"Posture is {'correct' if result['posture_correct'] else 'incorrect'}")
```

### Batch Processing Multiple Images

```python
import requests
import os
from pathlib import Path

def batch_analyze(image_dir, exercise_type=None):
    """Analyze multiple images in a directory"""
    url = "http://localhost:8000/analyze"
    results = []
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = [
        f for f in Path(image_dir).iterdir() 
        if f.suffix.lower() in image_extensions
    ]
    
    print(f"Found {len(image_files)} images to analyze\n")
    
    for image_path in image_files:
        print(f"Analyzing {image_path.name}...")
        
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {}
            if exercise_type:
                data["exercise_type"] = exercise_type
            
            try:
                response = requests.post(url, files=files, data=data)
                result = response.json()
                
                if result.get("success"):
                    results.append({
                        "filename": image_path.name,
                        "exercise": result["exercise_type"],
                        "correct": result["posture_correct"],
                        "confidence": result["confidence"]
                    })
                    
                    status = "✓" if result["posture_correct"] else "✗"
                    print(f"  {status} {result['exercise_type']} - "
                          f"{result['confidence']:.1%} confidence")
                else:
                    print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
        
        print()
    
    # Summary
    correct_count = sum(1 for r in results if r["correct"])
    print(f"\nSummary: {correct_count}/{len(results)} with correct posture")
    
    return results

# Usage
results = batch_analyze("./exercise_photos", exercise_type="squat")
```

---

## 🌐 Example 3: cURL (Command Line)

### Basic Request

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@exercise_photo.jpg"
```

### With Exercise Type

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@squat.jpg" \
  -F "exercise_type=squat"
```

### Pretty Print JSON

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@exercise_photo.jpg" \
  -F "exercise_type=pushup" \
  | python -m json.tool
```

### Save Response to File

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@exercise_photo.jpg" \
  -o result.json
```

---

## 🔍 Example 4: Understanding the Response

### Successful Analysis Response

```json
{
  "success": true,
  "detected": true,
  "exercise_type": "squat",
  "posture_correct": true,
  "confidence": 0.89,
  "feedback": [
    "Great form! Your posture looks correct.",
    "\nDetected angles:",
    "  knee_angle: 95.3°",
    "  hip_angle: 88.7°",
    "  torso_angle: 85.1°"
  ],
  "keypoints_detected": true,
  "angles": {
    "left_knee": 94.2,
    "right_knee": 96.4,
    "knee_angle": 95.3,
    "left_hip": 87.5,
    "right_hip": 89.9,
    "hip_angle": 88.7,
    "torso_angle": 85.1
  },
  "issues": [],
  "recommendations": [
    "Keep up the good work! Maintain this form."
  ]
}
```

### Incorrect Posture Response

```json
{
  "success": true,
  "detected": true,
  "exercise_type": "squat",
  "posture_correct": false,
  "confidence": 0.82,
  "feedback": [
    "Found 2 issue(s) with your posture:",
    "knee_angle out of range (125.3°)",
    "Squat depth insufficient",
    "\nDetected angles:",
    "  knee_angle: 125.3°",
    "  hip_angle: 115.2°",
    "  torso_angle: 78.5°"
  ],
  "keypoints_detected": true,
  "angles": {
    "knee_angle": 125.3,
    "hip_angle": 115.2,
    "torso_angle": 78.5
  },
  "issues": [
    "knee_angle out of range (125.3°)",
    "Squat depth insufficient"
  ],
  "recommendations": [
    "Focus on proper knee alignment and depth",
    "Keep your chest up and core engaged",
    "Ensure knees track over toes, not caving inward"
  ]
}
```

### No Person Detected Response

```json
{
  "success": false,
  "error": "No person detected in the image. Please ensure the image contains a clear view of a person performing an exercise.",
  "detected": false
}
```

---

## 🧪 Example 5: Integration with Flask App

```python
from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)
POSTURE_API = "http://localhost:8000/analyze"

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    exercise_type = request.form.get('exercise_type')
    
    # Forward to posture analysis API
    files = {'file': file}
    data = {}
    if exercise_type:
        data['exercise_type'] = exercise_type
    
    response = requests.post(POSTURE_API, files=files, data=data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 📱 Example 6: JavaScript/Fetch API

```javascript
async function analyzePosture(imageFile, exerciseType = null) {
    const formData = new FormData();
    formData.append('file', imageFile);
    
    if (exerciseType) {
        formData.append('exercise_type', exerciseType);
    }
    
    try {
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Exercise:', result.exercise_type);
            console.log('Correct:', result.posture_correct);
            console.log('Confidence:', result.confidence);
            
            if (result.issues.length > 0) {
                console.log('Issues:', result.issues);
            }
            
            console.log('Recommendations:', result.recommendations);
            
            return result;
        } else {
            console.error('Error:', result.error);
            return null;
        }
    } catch (error) {
        console.error('Request failed:', error);
        return null;
    }
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    const exerciseType = document.getElementById('exerciseType').value;
    
    const result = await analyzePosture(file, exerciseType);
    if (result) {
        displayResults(result);
    }
});
```

---

## 🎯 Example 7: Specific Exercise Analysis

### Squat Analysis
```python
import requests

def analyze_squat(image_path):
    url = "http://localhost:8000/analyze"
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {"exercise_type": "squat"}
        response = requests.post(url, files=files, data=data)
    
    result = response.json()
    
    if result.get("success") and result.get("posture_correct"):
        angles = result["angles"]
        print(f"✓ Great squat form!")
        print(f"  Knee angle: {angles.get('knee_angle', 'N/A'):.1f}°")
        print(f"  Hip angle: {angles.get('hip_angle', 'N/A'):.1f}°")
        print(f"  Torso angle: {angles.get('torso_angle', 'N/A'):.1f}°")
    else:
        print(f"✗ Squat needs improvement")
        for issue in result.get("issues", []):
            print(f"  - {issue}")

analyze_squat("my_squat.jpg")
```

### Push-up Analysis
```python
def analyze_pushup(image_path):
    url = "http://localhost:8000/analyze"
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {"exercise_type": "pushup"}
        response = requests.post(url, files=files, data=data)
    
    result = response.json()
    
    if result.get("success"):
        print(f"Push-up Form: {'✓ Correct' if result['posture_correct'] else '✗ Incorrect'}")
        print(f"Confidence: {result['confidence']:.1%}")
        
        if "elbow_angle" in result.get("angles", {}):
            print(f"Elbow angle: {result['angles']['elbow_angle']:.1f}°")
        
        for rec in result.get("recommendations", []):
            print(f"💡 {rec}")

analyze_pushup("my_pushup.jpg")
```

---

## 🔄 Example 8: Real-time Analysis (Continuous)

```python
import requests
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ImageAnalyzer(FileSystemEventHandler):
    def __init__(self, api_url):
        self.api_url = api_url
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if event.src_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"\n📸 New image detected: {event.src_path}")
            time.sleep(1)  # Wait for file to be fully written
            
            with open(event.src_path, "rb") as f:
                files = {"file": f}
                response = requests.post(self.api_url, files=files)
            
            result = response.json()
            
            if result.get("success"):
                status = "✓" if result["posture_correct"] else "✗"
                print(f"{status} {result['exercise_type'].upper()}: "
                      f"{'Correct' if result['posture_correct'] else 'Incorrect'}")
                print(f"   Confidence: {result['confidence']:.1%}")

# Watch a directory for new images
if __name__ == "__main__":
    api_url = "http://localhost:8000/analyze"
    watch_dir = "./incoming_images"
    
    event_handler = ImageAnalyzer(api_url)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    
    print(f"👀 Watching {watch_dir} for new images...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()
```

---

## 📊 Example Response Scenarios

### Scenario 1: Perfect Squat
- `posture_correct`: `true`
- `confidence`: `0.92`
- `issues`: `[]`
- Angles within ideal ranges

### Scenario 2: Shallow Squat
- `posture_correct`: `false`
- `issues`: `["Squat depth insufficient", "knee_angle out of range (135.2°)"]`
- Recommendations focus on depth

### Scenario 3: Forward Lean
- `posture_correct`: `false`
- `issues`: `["Torso leaning too far forward - keep chest up"]`
- `torso_angle`: Too low (< 60°)

### Scenario 4: Auto-Detected Exercise
- User doesn't specify exercise type
- System detects: `"exercise_type": "pushup"`
- Analysis proceeds automatically

---

## 🎓 Best Practices

1. **Always check `success` field first**
   ```python
   if result.get("success"):
       # Process result
   else:
       # Handle error
   ```

2. **Validate file before upload**
   ```python
   if file.content_type.startswith('image/'):
       # Upload
   ```

3. **Handle network errors**
   ```python
   try:
       response = requests.post(url, files=files, timeout=10)
   except requests.exceptions.Timeout:
       print("Request timed out")
   ```

4. **Use appropriate exercise types**
   - Specify when known
   - Use auto-detect for mixed sets

5. **Check confidence scores**
   - High confidence (> 0.8): Very reliable
   - Medium confidence (0.6-0.8): Mostly reliable
   - Low confidence (< 0.6): Review issues

---

Happy analyzing! 💪
