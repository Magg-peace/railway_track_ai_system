"""
RailTrack - Multi-Frame Confirmation System
Reduces false alerts by confirming obstacles across multiple frames
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, deque
import time


class MultiFrameConfirmation:
    """Confirms obstacles across multiple frames to reduce false positives"""
    
    def __init__(self, 
                 min_consecutive_frames: int = 5,
                 max_frame_gap: int = 3,
                 movement_threshold: int = 50):
        """
        Initialize multi-frame confirmation system
        
        Args:
            min_consecutive_frames: Minimum frames obstacle must appear
            max_frame_gap: Maximum frames obstacle can disappear
            movement_threshold: Pixel threshold for stationary detection
        """
        self.min_consecutive_frames = min_consecutive_frames
        self.max_frame_gap = max_frame_gap
        self.movement_threshold = movement_threshold
        
        # Track obstacle history
        self.obstacle_history = defaultdict(lambda: {
            'detections': deque(maxlen=min_consecutive_frames + max_frame_gap),
            'first_seen': None,
            'last_seen': None,
            'confirmed': False,
            'positions': deque(maxlen=10),
            'is_static': False
        })
        
        self.confirmed_obstacles = {}
        self.frame_count = 0
    
    def update(self, detections: List[Dict], tracked_objects: Dict[int, Dict]) -> List[Dict]:
        """
        Update confirmation system with new detections
        
        Args:
            detections: List of current detections
            tracked_objects: Dictionary of tracked objects from ObstacleTracker
            
        Returns:
            List of confirmed obstacles
        """
        self.frame_count += 1
        current_time = time.time()
        
        confirmed = []
        
        # Process tracked objects
        for obj_id, detection in tracked_objects.items():
            history = self.obstacle_history[obj_id]
            
            # Add detection to history
            history['detections'].append({
                'detection': detection,
                'frame': self.frame_count,
                'timestamp': current_time
            })
            
            # Update timestamps
            if history['first_seen'] is None:
                history['first_seen'] = current_time
            history['last_seen'] = current_time
            
            # Track positions
            bbox = detection['bbox']
            center = self._get_center(bbox)
            history['positions'].append(center)
            
            # Check if static
            if len(history['positions']) >= 3:
                history['is_static'] = self._is_static(list(history['positions']))
            
            # Check confirmation criteria
            if self._should_confirm(obj_id):
                if not history['confirmed']:
                    history['confirmed'] = True
                    self.confirmed_obstacles[obj_id] = detection
                
                confirmed.append({
                    **detection,
                    'object_id': obj_id,
                    'duration': current_time - history['first_seen'],
                    'is_static': history['is_static'],
                    'frame_count': len(history['detections'])
                })
        
        # Clean up old obstacles
        self._cleanup_old_obstacles(current_time)
        
        return confirmed
    
    def _should_confirm(self, obj_id: int) -> bool:
        """
        Check if obstacle should be confirmed
        
        Args:
            obj_id: Object ID
            
        Returns:
            True if should be confirmed
        """
        history = self.obstacle_history[obj_id]
        detections = history['detections']
        
        if len(detections) < self.min_consecutive_frames:
            return False
        
        # Check for consecutive appearances
        recent_frames = [d['frame'] for d in list(detections)[-self.min_consecutive_frames:]]
        
        # Calculate frame gaps
        gaps = [recent_frames[i+1] - recent_frames[i] - 1 
                for i in range(len(recent_frames) - 1)]
        
        # All gaps must be within threshold
        return all(gap <= self.max_frame_gap for gap in gaps)
    
    def _is_static(self, positions: List[Tuple[float, float]]) -> bool:
        """
        Check if obstacle is stationary
        
        Args:
            positions: List of (x, y) positions
            
        Returns:
            True if stationary
        """
        if len(positions) < 2:
            return True
        
        # Calculate maximum displacement
        positions_array = np.array(positions)
        displacements = np.linalg.norm(
            positions_array[1:] - positions_array[:-1], 
            axis=1
        )
        
        max_displacement = np.max(displacements)
        
        return max_displacement < self.movement_threshold
    
    def _get_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
        """Get center point of bounding box"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _cleanup_old_obstacles(self, current_time: float, timeout: float = 10.0):
        """
        Remove obstacles not seen recently
        
        Args:
            current_time: Current timestamp
            timeout: Seconds before removing obstacle
        """
        to_remove = []
        
        for obj_id, history in self.obstacle_history.items():
            if history['last_seen'] and (current_time - history['last_seen']) > timeout:
                to_remove.append(obj_id)
        
        for obj_id in to_remove:
            del self.obstacle_history[obj_id]
            if obj_id in self.confirmed_obstacles:
                del self.confirmed_obstacles[obj_id]
    
    def get_obstacle_info(self, obj_id: int) -> Optional[Dict]:
        """
        Get detailed information about an obstacle
        
        Args:
            obj_id: Object ID
            
        Returns:
            Dictionary with obstacle information
        """
        if obj_id not in self.obstacle_history:
            return None
        
        history = self.obstacle_history[obj_id]
        
        return {
            'object_id': obj_id,
            'first_seen': history['first_seen'],
            'last_seen': history['last_seen'],
            'duration': history['last_seen'] - history['first_seen'] if history['first_seen'] else 0,
            'detection_count': len(history['detections']),
            'confirmed': history['confirmed'],
            'is_static': history['is_static'],
            'positions': list(history['positions'])
        }
    
    def get_all_confirmed(self) -> List[Dict]:
        """
        Get all currently confirmed obstacles
        
        Returns:
            List of confirmed obstacles with metadata
        """
        confirmed = []
        
        for obj_id, detection in self.confirmed_obstacles.items():
            info = self.get_obstacle_info(obj_id)
            if info:
                confirmed.append({
                    **detection,
                    **info
                })
        
        return confirmed
    
    def reset(self):
        """Reset confirmation system"""
        self.obstacle_history.clear()
        self.confirmed_obstacles.clear()
        self.frame_count = 0
    
    def get_stats(self) -> Dict:
        """
        Get statistics about confirmation system
        
        Returns:
            Dictionary with statistics
        """
        total_tracked = len(self.obstacle_history)
        total_confirmed = len(self.confirmed_obstacles)
        
        static_count = sum(1 for h in self.obstacle_history.values() if h['is_static'])
        
        return {
            'frame_count': self.frame_count,
            'total_tracked': total_tracked,
            'total_confirmed': total_confirmed,
            'confirmation_rate': total_confirmed / total_tracked if total_tracked > 0 else 0,
            'static_obstacles': static_count
        }


class FalseAlertFilter:
    """Additional filtering to reduce false alerts"""
    
    def __init__(self):
        """Initialize false alert filter"""
        self.alert_history = deque(maxlen=100)
        self.suppressed_count = 0
    
    def filter(self, obstacles: List[Dict], min_size: int = 1000) -> List[Dict]:
        """
        Filter out likely false alerts
        
        Args:
            obstacles: List of detected obstacles
            min_size: Minimum bounding box area
            
        Returns:
            Filtered list of obstacles
        """
        filtered = []
        
        for obstacle in obstacles:
            # Size filter
            bbox = obstacle['bbox']
            area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            
            if area < min_size:
                self.suppressed_count += 1
                continue
            
            # Aspect ratio filter (eliminate very thin detections)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            aspect_ratio = max(width, height) / min(width, height) if min(width, height) > 0 else 0
            
            if aspect_ratio > 10:  # Too elongated
                self.suppressed_count += 1
                continue
            
            # Confidence filter for specific classes
            if obstacle['class'] == 'debris' and obstacle['confidence'] < 0.6:
                self.suppressed_count += 1
                continue
            
            filtered.append(obstacle)
        
        return filtered
    
    def is_duplicate_alert(self, obstacle: Dict, time_window: float = 30.0) -> bool:
        """
        Check if this is a duplicate alert
        
        Args:
            obstacle: Obstacle detection
            time_window: Time window in seconds to check for duplicates
            
        Returns:
            True if duplicate
        """
        current_time = time.time()
        
        # Check recent alerts
        for past_alert in self.alert_history:
            if current_time - past_alert['timestamp'] > time_window:
                continue
            
            # Check if same type and similar location
            if (past_alert['class'] == obstacle['class'] and
                self._is_similar_location(past_alert['bbox'], obstacle['bbox'])):
                return True
        
        # Add to history
        self.alert_history.append({
            'timestamp': current_time,
            'class': obstacle['class'],
            'bbox': obstacle['bbox']
        })
        
        return False
    
    def _is_similar_location(self, bbox1: Tuple, bbox2: Tuple, threshold: int = 50) -> bool:
        """Check if two bounding boxes are in similar locations"""
        center1 = ((bbox1[0] + bbox1[2]) / 2, (bbox1[1] + bbox1[3]) / 2)
        center2 = ((bbox2[0] + bbox2[2]) / 2, (bbox2[1] + bbox2[3]) / 2)
        
        distance = np.linalg.norm(np.array(center1) - np.array(center2))
        return distance < threshold


if __name__ == "__main__":
    # Test multi-frame confirmation
    print("Testing Multi-Frame Confirmation Module...")
    
    mfc = MultiFrameConfirmation(min_consecutive_frames=3)
    
    # Simulate detections
    test_detection = {
        'class': 'human',
        'confidence': 0.95,
        'bbox': (100, 100, 150, 200),
        'class_id': 0
    }
    
    # Simulate tracking
    test_tracked = {1: test_detection}
    
    # Run updates
    for i in range(5):
        confirmed = mfc.update([test_detection], test_tracked)
        print(f"Frame {i+1}: Confirmed = {len(confirmed)}")
    
    stats = mfc.get_stats()
    print(f"Stats: {stats}")
    
    print("Multi-frame confirmation test complete")
