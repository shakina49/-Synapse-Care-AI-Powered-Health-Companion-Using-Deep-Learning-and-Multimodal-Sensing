"""
Posture Analysis Module
Analyzes detected poses and compares with reference postures
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy.spatial.distance import cosine
import math
from models.posture_model import PostureClassifier

# MediaPipe Pose landmark indices
LANDMARKS = {
    'NOSE': 0,
    'LEFT_EYE_INNER': 1,
    'LEFT_EYE': 2,
    'LEFT_EYE_OUTER': 3,
    'RIGHT_EYE_INNER': 4,
    'RIGHT_EYE': 5,
    'RIGHT_EYE_OUTER': 6,
    'LEFT_EAR': 7,
    'RIGHT_EAR': 8,
    'MOUTH_LEFT': 9,
    'MOUTH_RIGHT': 10,
    'LEFT_SHOULDER': 11,
    'RIGHT_SHOULDER': 12,
    'LEFT_ELBOW': 13,
    'RIGHT_ELBOW': 14,
    'LEFT_WRIST': 15,
    'RIGHT_WRIST': 16,
    'LEFT_PINKY': 17,
    'RIGHT_PINKY': 18,
    'LEFT_INDEX': 19,
    'RIGHT_INDEX': 20,
    'LEFT_THUMB': 21,
    'RIGHT_THUMB': 22,
    'LEFT_HIP': 23,
    'RIGHT_HIP': 24,
    'LEFT_KNEE': 25,
    'RIGHT_KNEE': 26,
    'LEFT_ANKLE': 27,
    'RIGHT_ANKLE': 28,
    'LEFT_HEEL': 29,
    'RIGHT_HEEL': 30,
    'LEFT_FOOT_INDEX': 31,
    'RIGHT_FOOT_INDEX': 32
}


class PostureAnalyzer:
    """Analyzes exercise posture and determines correctness"""
    
    def __init__(self):
        """Initialize posture analyzer with reference data"""
        self.reference_data = self._load_reference_data()
        self.supported_exercises = list(self.reference_data.keys())
        self.classifier = PostureClassifier()
        try:
            self.classifier.ensure_model()
        except Exception as e:
            # If training/loading fails, continue with rule-based logic
            print(f"Warning: posture classifier unavailable ({e})")
    
    def _load_reference_data(self) -> Dict:
        """
        Load reference posture data from multiple sources
        This includes ideal angles, alignments, and keypoint relationships
        """
        return {
            'squat': {
                'name': 'Squat',
                'key_angles': {
                    # More forgiving ranges for real-world photos
                    'knee_angle': {'min': 70, 'max': 140, 'ideal': 95},
                    'hip_angle': {'min': 60, 'max': 130, 'ideal': 90},
                    'torso_angle': {'min': 50, 'max': 120, 'ideal': 85}
                },
                'alignments': {
                    'knees_over_toes': True,
                    'spine_neutral': True,  # approximated by torso angle
                    'feet_shoulder_width': True,
                    'hip_shoulder_stack': True
                },
                'common_issues': [
                    'knee_valgus',  # Knees caving in
                    'forward_lean',  # Too much forward lean
                    'incomplete_depth',  # Not going low enough
                    'heel_lift'  # Heels coming off ground
                ]
            },
            'pushup': {
                'name': 'Push-up',
                'key_angles': {
                    'elbow_angle': {'min': 70, 'max': 135, 'ideal': 95},
                    'shoulder_angle': {'min': 150, 'max': 195, 'ideal': 175},
                    'hip_angle': {'min': 155, 'max': 195, 'ideal': 180}
                },
                'alignments': {
                    'body_straight': True,
                    'hands_shoulder_width': True,
                    'head_neutral': True,
                    'shoulders_over_wrists': True
                },
                'common_issues': [
                    'sagging_hips',
                    'raised_hips',
                    'head_dropping',
                    'incomplete_range'
                ]
            },
            'plank': {
                'name': 'Plank',
                'key_angles': {
                    'shoulder_angle': {'min': 155, 'max': 195, 'ideal': 178},
                    'hip_angle': {'min': 155, 'max': 195, 'ideal': 178},
                    'knee_angle': {'min': 155, 'max': 195, 'ideal': 178}
                },
                'alignments': {
                    'body_straight': True,
                    'head_neutral': True,
                    'shoulders_over_wrists': True
                },
                'common_issues': [
                    'sagging_hips',
                    'raised_hips',
                    'head_position',
                    'shoulder_alignment'
                ]
            },
            'lunge': {
                'name': 'Lunge',
                'key_angles': {
                    'front_knee_angle': {'min': 70, 'max': 120, 'ideal': 95},
                    'back_knee_angle': {'min': 70, 'max': 130, 'ideal': 95},
                    'torso_angle': {'min': 70, 'max': 120, 'ideal': 90}
                },
                'alignments': {
                    'front_knee_over_ankle': True,
                    'torso_upright': True,
                    'hips_square': True,
                    'hip_shoulder_stack': True
                },
                'common_issues': [
                    'knee_overextension',
                    'forward_lean',
                    'hip_rotation',
                    'back_knee_touching_ground'
                ]
            },
            'deadlift': {
                'name': 'Deadlift',
                'key_angles': {
                    'knee_angle': {'min': 120, 'max': 180, 'ideal': 155},
                    'hip_angle': {'min': 45, 'max': 110, 'ideal': 75},
                    'torso_angle': {'min': 30, 'max': 95, 'ideal': 60}
                },
                'alignments': {
                    'spine_neutral': True,
                    'shoulders_over_bar': True,
                    'bar_path_straight': True
                },
                'common_issues': [
                    'rounded_back',
                    'hyperextended_back',
                    'bar_away_from_body',
                    'knee_collapse'
                ]
            }
        }
    
    def get_supported_exercises(self) -> List[str]:
        """Get list of supported exercise types"""
        return self.supported_exercises
    
    def analyze(
        self,
        pose_results,
        exercise_type: Optional[str] = None,
        image_shape: Optional[Tuple] = None
    ) -> Dict:
        """
        Analyze posture from pose detection results
        
        Args:
            pose_results: MediaPipe pose detection results
            exercise_type: Type of exercise (optional, will auto-detect if None)
            image_shape: Shape of the original image
        
        Returns:
            Dictionary with analysis results
        """
        if not pose_results or not pose_results.pose_landmarks:
            return {
                "is_correct": False,
                "confidence": 0.0,
                "feedback": ["No pose detected"],
                "keypoints_detected": False
            }
        
        # Extract landmarks
        landmarks = self._extract_landmarks(pose_results.pose_landmarks)

        # Visibility / quality guard
        if not self._has_minimum_visibility(landmarks, threshold=0.5):
            return {
                "is_correct": False,
                "confidence": 0.0,
                "feedback": ["Pose detected but landmarks are too low-confidence. Try a clearer photo with full body in frame."],
                "keypoints_detected": False
            }
        
        # Auto-detect exercise type if not provided
        if not exercise_type:
            exercise_type = self._auto_detect_exercise(landmarks)
        
        # Get reference data for this exercise
        if exercise_type not in self.reference_data:
            exercise_type = 'squat'  # Default fallback
        
        reference = self.reference_data[exercise_type]

        # Ensure required landmarks are visible for the chosen exercise
        if not self._validate_landmarks_for_exercise(exercise_type, landmarks):
            return {
                "is_correct": False,
                "confidence": 0.0,
                "feedback": [f"Key landmarks for {exercise_type} are not clearly visible. Please ensure the full body is in frame and well-lit."],
                "keypoints_detected": False
            }
        
        # Calculate key angles
        angles = self._calculate_angles(landmarks)

        # ML-assisted suggestion (after angles are calculated)
        ml_label, ml_conf = self.classifier.predict(angles)
        if not exercise_type and ml_label:
            exercise_type = ml_label
            # Update reference if exercise type changed
            if exercise_type in self.reference_data:
                reference = self.reference_data[exercise_type]
        
        # Check alignments
        alignments = self._check_alignments(landmarks, reference)
        
        # Detect issues
        issues = self._detect_issues(landmarks, angles, reference, exercise_type, alignments)
        
        # Calculate correctness score
        correctness_score, confidence = self._calculate_correctness(
            angles, alignments, issues, reference
        )

        # Boost score if ML agrees with selected exercise
        if ml_label and ml_label == exercise_type:
            correctness_score = min(1.0, correctness_score + (0.15 * ml_conf))
            confidence = min(1.0, max(confidence, ml_conf))
        
        # Generate feedback and recommendations
        feedback = self._generate_feedback(issues, angles, reference)
        recommendations = self._generate_recommendations(issues, exercise_type)
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy_types(obj):
            """Recursively convert numpy types to native Python types"""
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            else:
                return obj
        
        # More lenient correctness determination
        # Consider correct if score is decent and not too many critical issues
        is_correct = bool(correctness_score >= 0.45 and len(issues) <= 5)

        result = {
            "exercise_type": exercise_type,
            "is_correct": is_correct,
            "confidence": float(confidence),
            "feedback": feedback,
            "keypoints_detected": True,
            "angles": convert_numpy_types(angles),
            "alignments": convert_numpy_types(alignments),
            "issues": issues,
            "recommendations": recommendations
        }
        
        return result
    
    def _extract_landmarks(self, pose_landmarks) -> Dict:
        """Extract landmark coordinates"""
        landmarks = {}
        for idx, landmark in enumerate(pose_landmarks.landmark):
            landmarks[idx] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        return landmarks

    def _has_minimum_visibility(self, landmarks: Dict, threshold: float = 0.5) -> bool:
        """Check if we have enough visible keypoints to trust analysis"""
        visible_count = sum(1 for lm in landmarks.values() if lm.get('visibility', 0) >= threshold)
        return visible_count >= 10  # require majority of keypoints visible

    def _validate_landmarks_for_exercise(self, exercise_type: str, landmarks: Dict) -> bool:
        """Ensure key landmarks for an exercise are reasonably visible"""
        required = {
            'squat': ['LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_ANKLE', 'RIGHT_ANKLE', 'LEFT_SHOULDER', 'RIGHT_SHOULDER'],
            'pushup': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW', 'LEFT_WRIST', 'RIGHT_WRIST', 'LEFT_HIP', 'RIGHT_HIP'],
            'plank': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_HIP', 'RIGHT_HIP', 'LEFT_ANKLE', 'RIGHT_ANKLE'],
            'lunge': ['LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_ANKLE', 'RIGHT_ANKLE'],
            'deadlift': ['LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE', 'LEFT_ANKLE', 'RIGHT_ANKLE'],
        }
        names = required.get(exercise_type, [])
        for name in names:
            idx = LANDMARKS.get(name)
            lm = landmarks.get(idx)
            if not lm or lm.get('visibility', 0) < 0.5:
                return False
        return True
    
    def _calculate_angle(self, point1: Dict, point2: Dict, point3: Dict) -> float:
        """
        Calculate angle between three points (point2 is the vertex)
        
        Args:
            point1: First point (x, y)
            point2: Vertex point (x, y)
            point3: Third point (x, y)
        
        Returns:
            Angle in degrees
        """
        # Convert to numpy arrays for easier calculation
        p1 = np.array([point1['x'], point1['y']])
        p2 = np.array([point2['x'], point2['y']])
        p3 = np.array([point3['x'], point3['y']])
        
        # Calculate vectors
        v1 = p1 - p2
        v2 = p3 - p2
        
        # Calculate angle using dot product
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        
        return float(np.degrees(angle))
    
    def _calculate_angles(self, landmarks: Dict) -> Dict:
        """Calculate all relevant angles for posture analysis"""
        angles = {}
        
        # Helper function to get landmark
        def get_landmark(name):
            idx = LANDMARKS[name]
            return landmarks.get(idx)

        def all_visible(points):
            return all(p and p.get('visibility', 0) > 0.5 for p in points)
        
        # Left knee angle (hip-knee-ankle)
        left_hip = get_landmark('LEFT_HIP')
        left_knee = get_landmark('LEFT_KNEE')
        left_ankle = get_landmark('LEFT_ANKLE')
        if all_visible([left_hip, left_knee, left_ankle]):
            angles['left_knee'] = self._calculate_angle(left_hip, left_knee, left_ankle)
        
        # Right knee angle
        right_hip = get_landmark('RIGHT_HIP')
        right_knee = get_landmark('RIGHT_KNEE')
        right_ankle = get_landmark('RIGHT_ANKLE')
        if all_visible([right_hip, right_knee, right_ankle]):
            angles['right_knee'] = self._calculate_angle(right_hip, right_knee, right_ankle)
        
        # Average knee angle
        if 'left_knee' in angles and 'right_knee' in angles:
            angles['knee_angle'] = float((angles['left_knee'] + angles['right_knee']) / 2)
        elif 'left_knee' in angles:
            angles['knee_angle'] = float(angles['left_knee'])
        elif 'right_knee' in angles:
            angles['knee_angle'] = float(angles['right_knee'])
        
        # Left hip angle (shoulder-hip-knee)
        left_shoulder = get_landmark('LEFT_SHOULDER')
        if all_visible([left_shoulder, left_hip, left_knee]):
            angles['left_hip'] = self._calculate_angle(left_shoulder, left_hip, left_knee)
        
        # Right hip angle
        right_shoulder = get_landmark('RIGHT_SHOULDER')
        if all_visible([right_shoulder, right_hip, right_knee]):
            angles['right_hip'] = self._calculate_angle(right_shoulder, right_hip, right_knee)
        
        # Average hip angle
        if 'left_hip' in angles and 'right_hip' in angles:
            angles['hip_angle'] = float((angles['left_hip'] + angles['right_hip']) / 2)
        elif 'left_hip' in angles:
            angles['hip_angle'] = float(angles['left_hip'])
        elif 'right_hip' in angles:
            angles['hip_angle'] = float(angles['right_hip'])
        
        # Left elbow angle (shoulder-elbow-wrist)
        left_elbow = get_landmark('LEFT_ELBOW')
        left_wrist = get_landmark('LEFT_WRIST')
        if all_visible([left_shoulder, left_elbow, left_wrist]):
            angles['left_elbow'] = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
        
        # Right elbow angle
        right_elbow = get_landmark('RIGHT_ELBOW')
        right_wrist = get_landmark('RIGHT_WRIST')
        if all_visible([right_shoulder, right_elbow, right_wrist]):
            angles['right_elbow'] = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Average elbow angle
        if 'left_elbow' in angles and 'right_elbow' in angles:
            angles['elbow_angle'] = float((angles['left_elbow'] + angles['right_elbow']) / 2)
        elif 'left_elbow' in angles:
            angles['elbow_angle'] = float(angles['left_elbow'])
        elif 'right_elbow' in angles:
            angles['elbow_angle'] = float(angles['right_elbow'])
        
        # Torso angle (shoulder-hip vertical)
        if all_visible([left_shoulder, right_shoulder, left_hip, right_hip]):
            shoulder_center = {
                'x': (left_shoulder['x'] + right_shoulder['x']) / 2,
                'y': (left_shoulder['y'] + right_shoulder['y']) / 2,
                'visibility': min(left_shoulder['visibility'], right_shoulder['visibility'])
            }
            hip_center = {
                'x': (left_hip['x'] + right_hip['x']) / 2,
                'y': (left_hip['y'] + right_hip['y']) / 2,
                'visibility': min(left_hip['visibility'], right_hip['visibility'])
            }
            # Vertical reference point (above shoulder)
            vertical_ref = {
                'x': shoulder_center['x'],
                'y': shoulder_center['y'] - 0.1,
                'visibility': 1.0
            }
            angles['torso_angle'] = self._calculate_angle(vertical_ref, shoulder_center, hip_center)
        
        return angles
    
    def _check_alignments(self, landmarks: Dict, reference: Dict) -> Dict:
        """Check body alignments"""
        alignments = {}
        
        def get_landmark(name):
            idx = LANDMARKS[name]
            return landmarks.get(idx)

        def vis(p):
            return p and p.get('visibility', 0) > 0.5
        
        # Check if body is relatively straight (for plank, pushup)
        if 'body_straight' in reference.get('alignments', {}):
            left_shoulder = get_landmark('LEFT_SHOULDER')
            right_shoulder = get_landmark('RIGHT_SHOULDER')
            left_hip = get_landmark('LEFT_HIP')
            right_hip = get_landmark('RIGHT_HIP')
            left_ankle = get_landmark('LEFT_ANKLE')
            right_ankle = get_landmark('RIGHT_ANKLE')
            
            if all(map(vis, [left_shoulder, right_shoulder, left_hip, right_hip, left_ankle, right_ankle])):
                shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
                hip_y = (left_hip['y'] + right_hip['y']) / 2
                ankle_y = (left_ankle['y'] + right_ankle['y']) / 2
                
                # Check if points are roughly aligned
                shoulder_hip_diff = abs(shoulder_y - hip_y)
                hip_ankle_diff = abs(hip_y - ankle_y)
                total_height = abs(shoulder_y - ankle_y)
                
                if total_height > 0:
                    alignment_score = 1 - (shoulder_hip_diff + hip_ankle_diff) / (2 * total_height)
                    alignments['body_straight'] = bool(alignment_score > 0.85)
        
        # Check knee alignment (knees over toes for squat)
        if 'knees_over_toes' in reference.get('alignments', {}):
            left_knee = get_landmark('LEFT_KNEE')
            left_ankle = get_landmark('LEFT_ANKLE')
            right_knee = get_landmark('RIGHT_KNEE')
            right_ankle = get_landmark('RIGHT_ANKLE')
            
            if all(map(vis, [left_knee, left_ankle, right_knee, right_ankle])):
                left_aligned = abs(left_knee['x'] - left_ankle['x']) < 0.05
                right_aligned = abs(right_knee['x'] - right_ankle['x']) < 0.05
                alignments['knees_over_toes'] = bool(left_aligned and right_aligned)

        # Head neutral (nose roughly aligned vertically with shoulders/hips)
        if 'head_neutral' in reference.get('alignments', {}):
            nose = get_landmark('NOSE')
            left_shoulder = get_landmark('LEFT_SHOULDER')
            right_shoulder = get_landmark('RIGHT_SHOULDER')
            if all(map(vis, [nose, left_shoulder, right_shoulder])):
                shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
                head_offset = abs(nose['x'] - shoulder_center_x)
                alignments['head_neutral'] = bool(head_offset < 0.08)

        # Shoulders over wrists (for plank/pushup)
        if 'shoulders_over_wrists' in reference.get('alignments', {}):
            left_shoulder = get_landmark('LEFT_SHOULDER')
            right_shoulder = get_landmark('RIGHT_SHOULDER')
            left_wrist = get_landmark('LEFT_WRIST')
            right_wrist = get_landmark('RIGHT_WRIST')
            if all(map(vis, [left_shoulder, right_shoulder, left_wrist, right_wrist])):
                left_offset = abs(left_shoulder['x'] - left_wrist['x'])
                right_offset = abs(right_shoulder['x'] - right_wrist['x'])
                alignments['shoulders_over_wrists'] = bool((left_offset + right_offset) / 2 < 0.1)

        # Hip-shoulder vertical stacking (useful for squat/lunge)
        if 'hip_shoulder_stack' in reference.get('alignments', {}):
            left_shoulder = get_landmark('LEFT_SHOULDER')
            right_shoulder = get_landmark('RIGHT_SHOULDER')
            left_hip = get_landmark('LEFT_HIP')
            right_hip = get_landmark('RIGHT_HIP')
            if all(map(vis, [left_shoulder, right_shoulder, left_hip, right_hip])):
                shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
                hip_center_x = (left_hip['x'] + right_hip['x']) / 2
                alignments['hip_shoulder_stack'] = bool(abs(shoulder_center_x - hip_center_x) < 0.08)
        
        return alignments
    
    def _detect_issues(self, landmarks: Dict, angles: Dict, reference: Dict, exercise_type: str, alignments: Dict) -> List[str]:
        """Detect posture issues"""
        issues = []
        
        # Only report major angle violations (not minor ones)
        key_angles = reference.get('key_angles', {})
        for angle_name, angle_value in angles.items():
            if angle_name in key_angles:
                ref_range = key_angles[angle_name]
                # Add buffer zone - only flag if significantly out of range
                buffer = 10  # 10 degree buffer
                if angle_value < (ref_range['min'] - buffer) or angle_value > (ref_range['max'] + buffer):
                    issues.append(f"{angle_name} out of optimal range ({angle_value:.1f}°)")
        
        # Exercise-specific issue detection - more lenient thresholds
        if exercise_type == 'squat':
            if 'knee_angle' in angles and angles['knee_angle'] > 145:
                issues.append("Squat depth could be improved")
            if 'knee_angle' in angles and angles['knee_angle'] < 55:
                issues.append("Squat depth might be too deep for some")
            if 'hip_angle' in angles and angles['hip_angle'] > 135:
                issues.append("Try sitting back a bit more")
            if 'torso_angle' in angles and angles['torso_angle'] < 45:
                issues.append("Try keeping chest up a bit more")
        
        elif exercise_type == 'pushup':
            if 'elbow_angle' in angles and angles['elbow_angle'] > 140:
                issues.append("Push-up depth could be improved")
            if 'hip_angle' in angles and angles['hip_angle'] < 150:
                issues.append("Try maintaining a straighter body line")
            if 'shoulder_angle' in angles and angles['shoulder_angle'] < 145:
                issues.append("Keep shoulders stable")
        
        elif exercise_type == 'plank':
            if 'hip_angle' in angles and angles['hip_angle'] < 150:
                issues.append("Try raising hips slightly")
            if 'hip_angle' in angles and angles['hip_angle'] > 200:
                issues.append("Try lowering hips slightly")
        
        elif exercise_type == 'lunge':
            if 'front_knee_angle' in angles and (angles['front_knee_angle'] < 65 or angles['front_knee_angle'] > 125):
                issues.append("Front knee angle could be adjusted")
            if 'back_knee_angle' in angles and angles['back_knee_angle'] < 60:
                issues.append("Back knee position could be higher")

        elif exercise_type == 'deadlift':
            if 'torso_angle' in angles and angles['torso_angle'] < 25:
                issues.append("Try keeping chest up more")
            if 'hip_angle' in angles and angles['hip_angle'] > 115:
                issues.append("Try pushing hips back more")

        # Only report alignment issues if they're clearly wrong
        # Don't report every minor alignment issue
        return issues
    
    def _calculate_correctness(self, angles: Dict, alignments: Dict, issues: List, reference: Dict) -> Tuple[float, float]:
        """Calculate overall correctness score"""
        score = 1.0
        angle_checks = 0
        
        # Check angles
        key_angles = reference.get('key_angles', {})
        for angle_name, angle_value in angles.items():
            if angle_name in key_angles:
                angle_checks += 1
                ref_range = key_angles[angle_name]
                ideal = ref_range.get('ideal', (ref_range['min'] + ref_range['max']) / 2)
                
                # Calculate deviation from ideal
                if angle_value < ref_range['min'] or angle_value > ref_range['max']:
                    score -= 0.15  # Reduced penalty for out of range
                else:
                    # Smaller penalty for deviation from ideal
                    deviation = abs(angle_value - ideal)
                    max_deviation = max(ideal - ref_range['min'], ref_range['max'] - ideal)
                    if max_deviation > 0:
                        score -= 0.03 * (deviation / max_deviation)
        
        # Check alignments - reduced penalty
        for alignment_name, alignment_value in alignments.items():
            if not alignment_value:
                score -= 0.05  # Reduced from 0.1
        
        # Smaller penalty for issues
        score -= len(issues) * 0.03  # Reduced from 0.05
        
        # Normalize score
        score = max(0.0, min(1.0, score))
        
        # Calculate confidence based on number of detected angles (more forgiving)
        confidence = min(1.0, (angle_checks + 1.0) / max(1, len(key_angles)))
        
        return score, confidence
    
    def _generate_feedback(self, issues: List, angles: Dict, reference: Dict) -> List[str]:
        """Generate feedback messages"""
        feedback = []
        
        if not issues:
            feedback.append("Great form! Your posture looks correct.")
        else:
            feedback.append(f"Found {len(issues)} issue(s) with your posture:")
            feedback.extend(issues)
        
        # Add angle information
        if angles:
            feedback.append("\nDetected angles:")
            for angle_name, angle_value in angles.items():
                feedback.append(f"  {angle_name}: {angle_value:.1f}°")
        
        return feedback
    
    def _generate_recommendations(self, issues: List, exercise_type: str) -> List[str]:
        """Generate recommendations based on issues"""
        recommendations = []
        
        if not issues:
            recommendations.append("Keep up the good work! Maintain this form.")
            return recommendations
        
        # General recommendations
        if any('knee' in issue.lower() for issue in issues):
            recommendations.append("Focus on proper knee alignment and depth")
        
        if any('hip' in issue.lower() for issue in issues):
            recommendations.append("Pay attention to hip position and alignment")
        
        if any('spine' in issue.lower() or 'back' in issue.lower() for issue in issues):
            recommendations.append("Maintain a neutral spine throughout the movement")
        
        # Exercise-specific recommendations
        if exercise_type == 'squat':
            recommendations.append("Keep your chest up and core engaged")
            recommendations.append("Ensure knees track over toes, not caving inward")
            recommendations.append("Keep weight mid-foot and avoid heels lifting")
        
        elif exercise_type == 'pushup':
            recommendations.append("Keep your body in a straight line from head to heels")
            recommendations.append("Lower your body until chest nearly touches the ground")
            recommendations.append("Place hands slightly wider than shoulders, elbows ~45° from body")
        
        elif exercise_type == 'plank':
            recommendations.append("Engage your core to keep hips level with shoulders")
            recommendations.append("Keep your head in a neutral position")
            recommendations.append("Press the floor away to keep shoulders stable")

        elif exercise_type == 'lunge':
            recommendations.append("Keep front knee stacked over ankle")
            recommendations.append("Lower straight down, not forward")
            recommendations.append("Keep hips square and torso tall")

        elif exercise_type == 'deadlift':
            recommendations.append("Push hips back, keep bar close to the body")
            recommendations.append("Brace core and keep spine neutral")
            recommendations.append("Drive through heels and keep shoulders over mid-foot")
        
        return recommendations
    
    def _auto_detect_exercise(self, landmarks: Dict) -> str:
        """
        Auto-detect exercise type based on pose
        Simple heuristic-based detection
        """
        def get_landmark(name):
            idx = LANDMARKS[name]
            return landmarks.get(idx)
        
        def vis(p):
            return p and p.get('visibility', 0) > 0.5

        # Calculate key angles for detection
        left_hip = get_landmark('LEFT_HIP')
        left_knee = get_landmark('LEFT_KNEE')
        left_ankle = get_landmark('LEFT_ANKLE')
        left_shoulder = get_landmark('LEFT_SHOULDER')
        left_elbow = get_landmark('LEFT_ELBOW')
        left_wrist = get_landmark('LEFT_WRIST')
        
        # Check if person is horizontal (plank/pushup)
        if vis(left_shoulder) and vis(left_hip) and vis(left_ankle):
            shoulder_y = left_shoulder['y']
            hip_y = left_hip['y']
            ankle_y = left_ankle['y']
            
            # If body is relatively horizontal
            if abs(shoulder_y - ankle_y) < 0.2:
                # Check if arms are bent (pushup) or straight (plank)
                if vis(left_elbow) and vis(left_wrist):
                    elbow_angle = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
                    if elbow_angle < 150:
                        return 'pushup'
                    else:
                        return 'plank'
        
        # Check if person is in squat position
        if vis(left_hip) and vis(left_knee) and vis(left_ankle):
            knee_angle = self._calculate_angle(left_hip, left_knee, left_ankle)
            if 60 < knee_angle < 120:
                return 'squat'
        
        # Default to squat if uncertain
        return 'squat'

