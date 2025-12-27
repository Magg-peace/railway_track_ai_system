"""
RailTrack - Railway Track Segmentation Module
Detects railway tracks and classifies zones (on-track, near-track, safe)
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
import yaml


class TrackSegmentation:
    """Detects railway tracks and defines safety zones"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize track segmentation
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.track_config = self.config.get('track', {})
        
        # Track boundaries (as percentage of frame)
        self.left_rail_x = self.track_config.get('left_rail_x', 0.35)
        self.right_rail_x = self.track_config.get('right_rail_x', 0.65)
        self.track_top_y = self.track_config.get('track_top_y', 0.4)
        self.track_bottom_y = self.track_config.get('track_bottom_y', 0.95)
        
        # Zone configurations
        zones = self.track_config.get('zones', {})
        self.critical_zone_width = zones.get('critical_zone_width', 0.25)
        self.warning_zone_width = zones.get('warning_zone_width', 0.40)
        self.safe_zone_threshold = zones.get('safe_zone_threshold', 0.50)
        
        self.frame_width = None
        self.frame_height = None
        self.track_mask = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def initialize_frame_dimensions(self, frame: np.ndarray):
        """
        Initialize frame dimensions and create track mask
        
        Args:
            frame: Input frame
        """
        self.frame_height, self.frame_width = frame.shape[:2]
        self.track_mask = self._create_track_mask()
    
    def _create_track_mask(self) -> np.ndarray:
        """
        Create a mask representing the railway track region
        
        Returns:
            Binary mask of track region
        """
        mask = np.zeros((self.frame_height, self.frame_width), dtype=np.uint8)
        
        # Define track region as trapezoid (perspective view)
        pts = np.array([
            [int(self.frame_width * self.left_rail_x), 
             int(self.frame_height * self.track_top_y)],
            [int(self.frame_width * self.right_rail_x), 
             int(self.frame_height * self.track_top_y)],
            [int(self.frame_width * 0.75), 
             int(self.frame_height * self.track_bottom_y)],
            [int(self.frame_width * 0.25), 
             int(self.frame_height * self.track_bottom_y)]
        ], np.int32)
        
        cv2.fillPoly(mask, [pts], 255)
        return mask
    
    def detect_track_lines(self, frame: np.ndarray) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Detect railway track lines using edge detection
        
        Args:
            frame: Input frame
            
        Returns:
            Tuple of (left_line, right_line) or (None, None)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Apply track mask
        if self.track_mask is None:
            self.initialize_frame_dimensions(frame)
        
        masked_edges = cv2.bitwise_and(edges, self.track_mask)
        
        # Detect lines using Hough Transform
        lines = cv2.HoughLinesP(
            masked_edges,
            rho=1,
            theta=np.pi/180,
            threshold=50,
            minLineLength=100,
            maxLineGap=50
        )
        
        if lines is None:
            return None, None
        
        # Separate left and right rail lines
        left_lines = []
        right_lines = []
        
        frame_center = self.frame_width // 2
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Calculate line center
            line_center_x = (x1 + x2) / 2
            
            if line_center_x < frame_center:
                left_lines.append(line[0])
            else:
                right_lines.append(line[0])
        
        # Average lines
        left_line = self._average_lines(left_lines) if left_lines else None
        right_line = self._average_lines(right_lines) if right_lines else None
        
        return left_line, right_line
    
    def _average_lines(self, lines: List[np.ndarray]) -> np.ndarray:
        """
        Average multiple lines into single line
        
        Args:
            lines: List of line coordinates
            
        Returns:
            Averaged line
        """
        if not lines:
            return None
        
        lines = np.array(lines)
        avg_line = np.mean(lines, axis=0).astype(int)
        return avg_line
    
    def classify_zone(self, bbox: Tuple[int, int, int, int]) -> str:
        """
        Classify which zone a bounding box falls into
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
            
        Returns:
            Zone classification: 'critical', 'warning', or 'safe'
        """
        x1, y1, x2, y2 = bbox
        
        # Calculate center point of bounding box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # Normalize to 0-1 range
        norm_x = center_x / self.frame_width
        norm_y = center_y / self.frame_height
        
        # Check if in track region (vertically)
        if norm_y < self.track_top_y or norm_y > self.track_bottom_y:
            return 'safe'
        
        # Calculate track center
        track_center = 0.5
        distance_from_center = abs(norm_x - track_center)
        
        # Classify based on distance from track center
        if distance_from_center <= self.critical_zone_width / 2:
            return 'critical'
        elif distance_from_center <= self.warning_zone_width / 2:
            return 'warning'
        else:
            return 'safe'
    
    def get_zone_coordinates(self) -> dict:
        """
        Get pixel coordinates of different zones
        
        Returns:
            Dictionary with zone coordinates
        """
        if self.frame_width is None or self.frame_height is None:
            return {}
        
        center_x = self.frame_width // 2
        
        critical_left = int(center_x - (self.frame_width * self.critical_zone_width / 2))
        critical_right = int(center_x + (self.frame_width * self.critical_zone_width / 2))
        
        warning_left = int(center_x - (self.frame_width * self.warning_zone_width / 2))
        warning_right = int(center_x + (self.frame_width * self.warning_zone_width / 2))
        
        top_y = int(self.frame_height * self.track_top_y)
        bottom_y = int(self.frame_height * self.track_bottom_y)
        
        return {
            'critical': {
                'x1': critical_left,
                'x2': critical_right,
                'y1': top_y,
                'y2': bottom_y
            },
            'warning': {
                'x1': warning_left,
                'x2': warning_right,
                'y1': top_y,
                'y2': bottom_y
            }
        }
    
    def draw_zones(self, frame: np.ndarray, alpha: float = 0.3) -> np.ndarray:
        """
        Draw zone overlays on frame
        
        Args:
            frame: Input frame
            alpha: Transparency of overlay
            
        Returns:
            Frame with zone overlays
        """
        if self.frame_width is None or self.frame_height is None:
            self.initialize_frame_dimensions(frame)
        
        overlay = frame.copy()
        zones = self.get_zone_coordinates()
        
        # Draw critical zone (red)
        if 'critical' in zones:
            crit = zones['critical']
            cv2.rectangle(overlay, 
                         (crit['x1'], crit['y1']), 
                         (crit['x2'], crit['y2']), 
                         (0, 0, 255), -1)
        
        # Draw warning zone (yellow)
        if 'warning' in zones:
            warn = zones['warning']
            cv2.rectangle(overlay, 
                         (warn['x1'], warn['y1']), 
                         (warn['x2'], warn['y2']), 
                         (0, 255, 255), -1)
        
        # Blend overlay with original frame
        result = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        # Draw zone labels
        cv2.putText(result, "CRITICAL ZONE", 
                   (zones['critical']['x1'] + 10, zones['critical']['y1'] + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.putText(result, "WARNING ZONE", 
                   (zones['warning']['x1'] + 10, zones['warning']['y1'] + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return result
    
    def is_on_track(self, bbox: Tuple[int, int, int, int]) -> bool:
        """
        Check if bounding box overlaps with track region
        
        Args:
            bbox: Bounding box (x1, y1, x2, y2)
            
        Returns:
            True if on track, False otherwise
        """
        if self.track_mask is None:
            return False
        
        x1, y1, x2, y2 = bbox
        
        # Create bbox mask
        bbox_mask = np.zeros_like(self.track_mask)
        cv2.rectangle(bbox_mask, (x1, y1), (x2, y2), 255, -1)
        
        # Calculate overlap
        overlap = cv2.bitwise_and(bbox_mask, self.track_mask)
        overlap_area = np.sum(overlap > 0)
        bbox_area = (x2 - x1) * (y2 - y1)
        
        # If more than 30% overlap, consider it on track
        overlap_ratio = overlap_area / bbox_area if bbox_area > 0 else 0
        
        return overlap_ratio > 0.3


if __name__ == "__main__":
    # Test track segmentation
    print("Testing Track Segmentation Module...")
    
    # Create dummy frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    tracker = TrackSegmentation()
    tracker.initialize_frame_dimensions(frame)
    
    # Test zone classification
    test_bbox = (300, 300, 350, 400)  # Center of frame
    zone = tracker.classify_zone(test_bbox)
    print(f"Test bbox zone: {zone}")
    
    # Test visualization
    vis_frame = tracker.draw_zones(frame)
    print(f"Visualization created: {vis_frame.shape}")
    
    print("Track segmentation test complete")
