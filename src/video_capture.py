"""
RailTrack - Video Capture and Preprocessing Module
Handles camera input, frame enhancement, and preprocessing
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import yaml
from pathlib import Path


class VideoCapture:
    """Manages video capture from camera or file with preprocessing capabilities"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize video capture system
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.cap = None
        self.frame_count = 0
        self.is_running = False
        
        # Extract config parameters
        self.camera_config = self.config['camera']
        self.video_config = self.config['video']
        
        # Initialize CLAHE for contrast enhancement
        if self.video_config.get('clahe_enabled', True):
            self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        else:
            self.clahe = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            # Return default config
            return {
                'camera': {'source': 0, 'resolution': {'width': 1920, 'height': 1080}},
                'video': {'resize_width': 640, 'resize_height': 480, 'clahe_enabled': True}
            }
    
    def start(self) -> bool:
        """
        Start video capture
        
        Returns:
            True if successful, False otherwise
        """
        try:
            source = self.camera_config['source']
            self.cap = cv2.VideoCapture(source)
            
            if not self.cap.isOpened():
                print(f"Error: Could not open video source {source}")
                return False
            
            # Set camera resolution
            if isinstance(source, int):  # Only for camera devices
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 
                           self.camera_config['resolution']['width'])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 
                           self.camera_config['resolution']['height'])
                self.cap.set(cv2.CAP_PROP_FPS, self.camera_config.get('fps', 30))
            
            self.is_running = True
            print(f"Video capture started from source: {source}")
            return True
            
        except Exception as e:
            print(f"Error starting video capture: {e}")
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read and preprocess a frame
        
        Returns:
            Tuple of (success, processed_frame)
        """
        if not self.is_running or self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        
        if not ret:
            return False, None
        
        self.frame_count += 1
        
        # Apply preprocessing
        processed_frame = self._preprocess_frame(frame)
        
        return True, processed_frame
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing to frame
        
        Args:
            frame: Input frame
            
        Returns:
            Preprocessed frame
        """
        # Resize frame
        resized = cv2.resize(
            frame,
            (self.video_config['resize_width'], 
             self.video_config['resize_height'])
        )
        
        # Low-light enhancement
        if self.camera_config.get('night_vision_enabled', True):
            resized = self._enhance_low_light(resized)
        
        # Denoising
        if self.video_config.get('denoise_enabled', True):
            resized = cv2.fastNlMeansDenoisingColored(resized, None, 10, 10, 7, 21)
        
        return resized
    
    def _enhance_low_light(self, frame: np.ndarray) -> np.ndarray:
        """
        Enhance frame for low-light conditions
        
        Args:
            frame: Input frame
            
        Returns:
            Enhanced frame
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        if self.clahe is not None:
            l = self.clahe.apply(l)
        
        # Merge channels
        enhanced_lab = cv2.merge([l, a, b])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def apply_gamma_correction(self, frame: np.ndarray, gamma: float = 1.5) -> np.ndarray:
        """
        Apply gamma correction for brightness adjustment
        
        Args:
            frame: Input frame
            gamma: Gamma value (>1 brightens, <1 darkens)
            
        Returns:
            Gamma corrected frame
        """
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 
                         for i in range(256)]).astype("uint8")
        return cv2.LUT(frame, table)
    
    def get_frame_info(self) -> dict:
        """
        Get information about current video stream
        
        Returns:
            Dictionary with frame information
        """
        if self.cap is None:
            return {}
        
        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'frame_count': self.frame_count,
            'is_running': self.is_running
        }
    
    def stop(self):
        """Stop video capture and release resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_running = False
            print("Video capture stopped")
    
    def __del__(self):
        """Destructor to ensure resources are released"""
        self.stop()


class FrameBuffer:
    """Buffer for storing recent frames for multi-frame analysis"""
    
    def __init__(self, max_size: int = 10):
        """
        Initialize frame buffer
        
        Args:
            max_size: Maximum number of frames to store
        """
        self.max_size = max_size
        self.frames = []
        self.timestamps = []
    
    def add_frame(self, frame: np.ndarray, timestamp: float):
        """
        Add frame to buffer
        
        Args:
            frame: Frame to add
            timestamp: Timestamp of frame
        """
        self.frames.append(frame)
        self.timestamps.append(timestamp)
        
        # Remove oldest frame if buffer is full
        if len(self.frames) > self.max_size:
            self.frames.pop(0)
            self.timestamps.pop(0)
    
    def get_frames(self, n: int = None) -> list:
        """
        Get last n frames
        
        Args:
            n: Number of frames to retrieve (None for all)
            
        Returns:
            List of frames
        """
        if n is None:
            return self.frames
        return self.frames[-n:]
    
    def get_frame_at(self, index: int) -> Optional[np.ndarray]:
        """
        Get frame at specific index
        
        Args:
            index: Index of frame
            
        Returns:
            Frame or None
        """
        if 0 <= index < len(self.frames):
            return self.frames[index]
        return None
    
    def clear(self):
        """Clear all frames from buffer"""
        self.frames.clear()
        self.timestamps.clear()
    
    def __len__(self):
        """Return number of frames in buffer"""
        return len(self.frames)


if __name__ == "__main__":
    # Test video capture
    print("Testing Video Capture Module...")
    
    capture = VideoCapture()
    
    if capture.start():
        print("Video capture initialized successfully")
        print(f"Frame info: {capture.get_frame_info()}")
        
        # Test frame reading
        for i in range(5):
            ret, frame = capture.read_frame()
            if ret:
                print(f"Frame {i+1}: Shape = {frame.shape}")
            else:
                print(f"Failed to read frame {i+1}")
                break
        
        capture.stop()
    else:
        print("Failed to initialize video capture")
