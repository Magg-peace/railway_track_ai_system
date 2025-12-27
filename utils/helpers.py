"""
RailTrack - Utility Functions
Common helper functions used across the system
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from datetime import datetime
import os


def save_image(image: np.ndarray, 
               directory: str = "logs/images",
               prefix: str = "image",
               timestamp: bool = True) -> str:
    """
    Save image to file
    
    Args:
        image: Image to save
        directory: Directory to save to
        prefix: Filename prefix
        timestamp: Include timestamp in filename
        
    Returns:
        Path to saved image
    """
    os.makedirs(directory, exist_ok=True)
    
    if timestamp:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{ts}.jpg"
    else:
        filename = f"{prefix}.jpg"
    
    filepath = os.path.join(directory, filename)
    cv2.imwrite(filepath, image)
    
    return filepath


def calculate_iou(bbox1: Tuple[int, int, int, int], 
                  bbox2: Tuple[int, int, int, int]) -> float:
    """
    Calculate Intersection over Union (IoU) between two bounding boxes
    
    Args:
        bbox1: First bounding box (x1, y1, x2, y2)
        bbox2: Second bounding box (x1, y1, x2, y2)
        
    Returns:
        IoU value (0-1)
    """
    x1_1, y1_1, x2_1, y2_1 = bbox1
    x1_2, y1_2, x2_2, y2_2 = bbox2
    
    # Calculate intersection
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    intersection = (x2_i - x1_i) * (y2_i - y1_i)
    
    # Calculate union
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    if union == 0:
        return 0.0
    
    return intersection / union


def resize_with_aspect_ratio(image: np.ndarray, 
                             width: Optional[int] = None,
                             height: Optional[int] = None) -> np.ndarray:
    """
    Resize image while maintaining aspect ratio
    
    Args:
        image: Input image
        width: Target width (optional)
        height: Target height (optional)
        
    Returns:
        Resized image
    """
    h, w = image.shape[:2]
    
    if width is None and height is None:
        return image
    
    if width is None:
        ratio = height / h
        width = int(w * ratio)
    elif height is None:
        ratio = width / w
        height = int(h * ratio)
    
    return cv2.resize(image, (width, height))


def draw_text_with_background(image: np.ndarray,
                              text: str,
                              position: Tuple[int, int],
                              font_scale: float = 0.6,
                              color: Tuple[int, int, int] = (255, 255, 255),
                              bg_color: Tuple[int, int, int] = (0, 0, 0),
                              thickness: int = 1,
                              padding: int = 5):
    """
    Draw text with background rectangle
    
    Args:
        image: Image to draw on
        text: Text to draw
        position: (x, y) position
        font_scale: Font scale
        color: Text color
        bg_color: Background color
        thickness: Text thickness
        padding: Padding around text
    """
    x, y = position
    
    # Get text size
    (text_width, text_height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    
    # Draw background
    cv2.rectangle(
        image,
        (x - padding, y - text_height - padding),
        (x + text_width + padding, y + baseline + padding),
        bg_color,
        -1
    )
    
    # Draw text
    cv2.putText(
        image,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness
    )


def format_time(seconds: float) -> str:
    """
    Format seconds to human-readable time
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def calculate_distance_2d(point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points
    
    Args:
        point1: First point (x, y)
        point2: Second point (x, y)
        
    Returns:
        Distance
    """
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def get_bbox_center(bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
    """
    Get center point of bounding box
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        
    Returns:
        Center point (x, y)
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def get_bbox_area(bbox: Tuple[int, int, int, int]) -> int:
    """
    Calculate area of bounding box
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        
    Returns:
        Area in pixels
    """
    x1, y1, x2, y2 = bbox
    return (x2 - x1) * (y2 - y1)


def clip_bbox(bbox: Tuple[int, int, int, int], 
              image_shape: Tuple[int, int]) -> Tuple[int, int, int, int]:
    """
    Clip bounding box to image boundaries
    
    Args:
        bbox: Bounding box (x1, y1, x2, y2)
        image_shape: Image shape (height, width)
        
    Returns:
        Clipped bounding box
    """
    height, width = image_shape[:2]
    x1, y1, x2, y2 = bbox
    
    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width - 1))
    y2 = max(0, min(y2, height - 1))
    
    return (x1, y1, x2, y2)


def create_color_map(num_classes: int) -> dict:
    """
    Create color map for different classes
    
    Args:
        num_classes: Number of classes
        
    Returns:
        Dictionary mapping class index to RGB color
    """
    np.random.seed(42)  # For reproducibility
    colors = {}
    
    for i in range(num_classes):
        colors[i] = tuple(np.random.randint(0, 255, 3).tolist())
    
    return colors


if __name__ == "__main__":
    # Test utilities
    print("Testing utility functions...")
    
    # Test IoU
    bbox1 = (100, 100, 200, 200)
    bbox2 = (150, 150, 250, 250)
    iou = calculate_iou(bbox1, bbox2)
    print(f"IoU: {iou:.3f}")
    
    # Test center calculation
    center = get_bbox_center(bbox1)
    print(f"Center: {center}")
    
    # Test area calculation
    area = get_bbox_area(bbox1)
    print(f"Area: {area}")
    
    # Test distance calculation
    distance = calculate_distance_2d((0, 0), (3, 4))
    print(f"Distance: {distance}")
    
    # Test time formatting
    print(f"Time: {format_time(125)}")
    
    print("Utility tests complete")
