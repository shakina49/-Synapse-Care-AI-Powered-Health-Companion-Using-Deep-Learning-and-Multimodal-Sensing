"""
Verification script to check if all components of the posture detection project are working correctly
"""

import sys
import os

def check_imports():
    """Check if all required packages can be imported"""
    print("=" * 60)
    print("Checking required packages...")
    print("=" * 60)
    
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('PIL', 'Pillow'),
        ('cv2', 'OpenCV'),
        ('mediapipe', 'MediaPipe'),
        ('numpy', 'NumPy'),
        ('scipy', 'SciPy'),
        ('sklearn', 'scikit-learn'),
        ('joblib', 'joblib'),
        ('pandas', 'Pandas')
    ]
    
    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name} is installed")
        except ImportError:
            print(f"✗ {name} is NOT installed")
            all_ok = False
    
    print()
    return all_ok

def check_files():
    """Check if all required files exist"""
    print("=" * 60)
    print("Checking required files...")
    print("=" * 60)
    
    required_files = [
        'main.py',
        'requirements.txt',
        'models/pose_detector.py',
        'models/posture_analyzer.py',
        'models/posture_model.py',
        'models/__init__.py',
        'utils/image_processor.py',
        'utils/__init__.py',
        'archive/angles.csv',
        'archive/labels.csv',
        'test_upload.html',
        'test_api.py'
    ]
    
    all_ok = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} is MISSING")
            all_ok = False
    
    print()
    return all_ok

def check_models():
    """Check if models can be initialized"""
    print("=" * 60)
    print("Checking model initialization...")
    print("=" * 60)
    
    try:
        from models.pose_detector import PoseDetector
        detector = PoseDetector()
        print("✓ PoseDetector initialized successfully")
    except Exception as e:
        print(f"✗ PoseDetector initialization failed: {e}")
        return False
    
    try:
        from models.posture_analyzer import PostureAnalyzer
        analyzer = PostureAnalyzer()
        print("✓ PostureAnalyzer initialized successfully")
    except Exception as e:
        print(f"✗ PostureAnalyzer initialization failed: {e}")
        return False
    
    try:
        from models.posture_model import PostureClassifier
        classifier = PostureClassifier()
        print("✓ PostureClassifier initialized successfully")
    except Exception as e:
        print(f"✗ PostureClassifier initialization failed: {e}")
        return False
    
    try:
        from utils.image_processor import ImageProcessor
        processor = ImageProcessor()
        print("✓ ImageProcessor initialized successfully")
    except Exception as e:
        print(f"✗ ImageProcessor initialization failed: {e}")
        return False
    
    print()
    return True

def check_data_files():
    """Check if training data files are valid"""
    print("=" * 60)
    print("Checking training data files...")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        angles_path = os.path.join("archive", "angles.csv")
        labels_path = os.path.join("archive", "labels.csv")
        
        if not os.path.exists(angles_path):
            print(f"✗ {angles_path} not found")
            return False
        
        if not os.path.exists(labels_path):
            print(f"✗ {labels_path} not found")
            return False
        
        angles_df = pd.read_csv(angles_path)
        labels_df = pd.read_csv(labels_path)
        
        print(f"✓ angles.csv loaded ({len(angles_df)} rows)")
        print(f"✓ labels.csv loaded ({len(labels_df)} rows)")
        
        # Check if files can be merged
        merged = angles_df.merge(labels_df, on="pose_id")
        print(f"✓ Data files can be merged ({len(merged)} rows)")
        
        # Check for pose labels
        if 'pose' in merged.columns:
            unique_poses = merged['pose'].unique()
            print(f"✓ Found {len(unique_poses)} unique poses: {list(unique_poses)}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Data file check failed: {e}")
        print()
        return False

def run_basic_test():
    """Run a basic functionality test"""
    print("=" * 60)
    print("Running basic functionality test...")
    print("=" * 60)
    
    try:
        import numpy as np
        from models.pose_detector import PoseDetector
        from models.posture_analyzer import PostureAnalyzer
        
        # Create a dummy image
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test pose detection
        detector = PoseDetector()
        results = detector.detect(dummy_image)
        print("✓ Pose detection runs without errors")
        
        # Test posture analysis (even with no pose detected)
        analyzer = PostureAnalyzer()
        analysis = analyzer.analyze(results, exercise_type='squat', image_shape=dummy_image.shape)
        print("✓ Posture analysis runs without errors")
        
        # Check response structure
        required_keys = ['is_correct', 'confidence', 'feedback', 'keypoints_detected']
        for key in required_keys:
            if key in analysis:
                print(f"✓ Response contains '{key}'")
            else:
                print(f"✗ Response missing '{key}'")
                return False
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False

def main():
    """Run all verification checks"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "POSTURE DETECTION PROJECT VERIFICATION" + " " * 9 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    results = []
    
    # Run all checks
    results.append(("Package Installation", check_imports()))
    results.append(("Required Files", check_files()))
    results.append(("Data Files", check_data_files()))
    results.append(("Model Initialization", check_models()))
    results.append(("Basic Functionality", run_basic_test()))
    
    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "✓ ALL CHECKS PASSED!" + " " * 22 + "║")
        print("║" + " " * 58 + "║")
        print("║  Your project is ready to use!                          ║")
        print("║  Start the server with: python main.py                  ║")
        print("║  Or use: start_server.bat                               ║")
        print("╚" + "═" * 58 + "╝")
        return 0
    else:
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 15 + "✗ SOME CHECKS FAILED" + " " * 22 + "║")
        print("║" + " " * 58 + "║")
        print("║  Please fix the issues above before running the server. ║")
        print("║  Install missing packages with:                         ║")
        print("║  pip install -r requirements.txt                        ║")
        print("╚" + "═" * 58 + "╝")
        return 1

if __name__ == "__main__":
    sys.exit(main())
