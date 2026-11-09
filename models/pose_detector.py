"""
Pose Detection Module using MediaPipe
Detects human pose keypoints from images
"""

import mediapipe as mp
import numpy as np
import cv2


class PoseDetector:
    """Detects human pose using MediaPipe Pose"""
    
    def __init__(self):
        """Initialize MediaPipe Pose model"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
    
    def detect(self, image: np.ndarray):
        """
        Detect pose in image
        
        Args:
            image: Input image as numpy array (RGB format expected)
        
        Returns:
            MediaPipe pose detection results
        """
        # Ensure image is in the correct format
        if len(image.shape) == 2:
            # Grayscale - convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            # RGBA - convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif image.shape[2] == 3:
            # Assume RGB (PIL images are RGB, OpenCV would be BGR)
            # MediaPipe expects RGB, so if image comes from PIL it's already RGB
            # If it comes from OpenCV, it would be BGR, but we're using PIL in main.py
            image_rgb = image
        else:
            image_rgb = image
        
        # Ensure uint8 format
        if image_rgb.dtype != np.uint8:
            if image_rgb.max() <= 1.0:
                image_rgb = (image_rgb * 255).astype(np.uint8)
            else:
                image_rgb = image_rgb.astype(np.uint8)
        
        # Process image
        results = self.pose.process(image_rgb)
        return results
    
    def get_landmarks(self, results):
        """
        Extract landmark coordinates from results
        
        Args:
            results: MediaPipe pose detection results
        
        Returns:
            Dictionary of landmark coordinates
        """
        if not results.pose_landmarks:
            return None
        
        landmarks = {}
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            landmarks[idx] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        
        return landmarks

