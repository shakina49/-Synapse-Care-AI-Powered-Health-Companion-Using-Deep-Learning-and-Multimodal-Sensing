"""
Image Processing Utilities
Helper functions for image preprocessing
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional


class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def resize_image(image: np.ndarray, max_size: int = 1920) -> np.ndarray:
        """
        Resize image while maintaining aspect ratio
        
        Args:
            image: Input image as numpy array
            max_size: Maximum dimension size
        
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if max(height, width) <= max_size:
            return image
        
        if height > width:
            new_height = max_size
            new_width = int(width * (max_size / height))
        else:
            new_width = max_size
            new_height = int(height * (max_size / width))
        
        pil_image = Image.fromarray(image)
        resized = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return np.array(resized)
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalize image values to 0-1 range
        
        Args:
            image: Input image
        
        Returns:
            Normalized image
        """
        if image.dtype == np.uint8:
            return image.astype(np.float32) / 255.0
        return image
    
    @staticmethod
    def preprocess_for_pose(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for pose detection
        
        Args:
            image: Input image
        
        Returns:
            Preprocessed image
        """
        # Resize if too large
        image = ImageProcessor.resize_image(image, max_size=1920)
        
        # Ensure RGB format
        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)
        elif image.shape[2] == 4:
            image = image[:, :, :3]
        
        return image

