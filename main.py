"""
FastAPI Backend for Exercise Posture Analysis
Analyzes physical exercise photos and determines if posture is correct
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
from io import BytesIO
from PIL import Image
import numpy as np

from models.pose_detector import PoseDetector
from models.posture_analyzer import PostureAnalyzer
from utils.image_processor import ImageProcessor

app = FastAPI(
    title="Exercise Posture Analysis API",
    description="API for analyzing exercise posture from images",
    version="1.0.0"
)

# CORS middleware to allow frontend connections later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
pose_detector = PoseDetector()
posture_analyzer = PostureAnalyzer()
image_processor = ImageProcessor()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Exercise Posture Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "posture-analysis"}


@app.post("/analyze")
async def analyze_posture(
    file: UploadFile = File(...),
    exercise_type: Optional[str] = None
):
    """
    Analyze exercise posture from uploaded image
    
    Args:
        file: Image file (JPEG, PNG, etc.)
        exercise_type: Optional exercise type (squat, pushup, plank, etc.)
    
    Returns:
        JSON response with posture analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        # Read image
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_array = np.array(image)
        
        # Ensure we have a 3-channel image
        if len(image_array.shape) == 2:
            # Grayscale - convert to RGB
            image_array = np.stack([image_array] * 3, axis=-1)
        elif len(image_array.shape) == 3 and image_array.shape[2] == 4:
            # RGBA - convert to RGB
            image_array = image_array[:, :, :3]
        elif len(image_array.shape) != 3:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image format"
            )
        
        # Detect pose
        pose_results = pose_detector.detect(image_array)
        
        if not pose_results or not pose_results.pose_landmarks:
            return JSONResponse(
                status_code=200,
                content={
                    "success": False,
                    "error": "No person detected in the image. Please ensure the image contains a clear view of a person performing an exercise.",
                    "detected": False
                }
            )
        
        # Analyze posture
        analysis_result = posture_analyzer.analyze(
            pose_results=pose_results,
            exercise_type=exercise_type,
            image_shape=image_array.shape
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "detected": True,
                "exercise_type": analysis_result.get("exercise_type", "unknown"),
                "posture_correct": analysis_result.get("is_correct", False),
                "confidence": analysis_result.get("confidence", 0.0),
                "feedback": analysis_result.get("feedback", []),
                "keypoints_detected": analysis_result.get("keypoints_detected", False),
                "angles": analysis_result.get("angles", {}),
                "issues": analysis_result.get("issues", []),
                "recommendations": analysis_result.get("recommendations", [])
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = str(e)
        # Log the full traceback for debugging
        print(f"Error processing image: {error_details}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": f"Error processing image: {error_details}",
                "detected": False
            }
        )


@app.get("/supported-exercises")
async def get_supported_exercises():
    """Get list of supported exercise types"""
    return {
        "supported_exercises": posture_analyzer.get_supported_exercises(),
        "default": "auto-detect"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

