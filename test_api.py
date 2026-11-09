"""
Simple test script for the Exercise Posture Analysis API
Run this after starting the server to test the API endpoints
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"


def test_health_check():
    """Test health check endpoint"""
    print("Testing health check endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_supported_exercises():
    """Test supported exercises endpoint"""
    print("Testing supported exercises endpoint...")
    response = requests.get(f"{BASE_URL}/supported-exercises")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()


def test_analyze_posture(image_path, exercise_type=None):
    """
    Test posture analysis endpoint
    
    Args:
        image_path: Path to the image file
        exercise_type: Optional exercise type
    """
    print(f"Testing posture analysis with image: {image_path}")
    if exercise_type:
        print(f"Exercise type: {exercise_type}")
    
    url = f"{BASE_URL}/analyze"
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if exercise_type:
                data['exercise_type'] = exercise_type
            
            response = requests.post(url, files=files, data=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()


if __name__ == "__main__":
    print("=" * 50)
    print("Exercise Posture Analysis API Test")
    print("=" * 50)
    print()
    
    # Test health check
    try:
        test_health_check()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.")
        print("Start the server with: python main.py")
        exit(1)
    
    # Test supported exercises
    test_supported_exercises()
    
    # Test posture analysis (uncomment and provide image path)
    # test_analyze_posture("path/to/your/exercise_image.jpg", exercise_type="squat")
    
    print("=" * 50)
    print("Test completed!")
    print("=" * 50)
    print()
    print("To test with an actual image, uncomment the test_analyze_posture line")
    print("and provide the path to your exercise image.")

