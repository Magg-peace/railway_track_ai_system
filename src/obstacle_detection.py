"""
RailTrack - Obstacle Detection Module using YOLOv8
Detects humans, animals, vehicles, and debris on railway tracks
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple, Optional
import yaml
from pathlib import Path


class ObstacleDetector:
    """YOLOv8-based obstacle detection system"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize obstacle detector
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.yolo_config = self.config.get('yolo', {})
        
        self.model = None
        self.device = self.yolo_config.get('device', 'cpu')
        self.conf_threshold = self.yolo_config.get('confidence_threshold', 0.5)
        self.iou_threshold = self.yolo_config.get('iou_threshold', 0.45)
        
        # Class mappings
        self.class_mappings = {
            'human': self.yolo_config.get('classes', {}).get('human', 0),
            'vehicle': self.yolo_config.get('classes', {}).get('vehicle', [2, 3, 5, 7]),
            'animal': self.yolo_config.get('classes', {}).get('animal', list(range(15, 24))),
            'debris': self.yolo_config.get('classes', {}).get('debris', list(range(24, 28)))
        }
        
        self._initialize_model()
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _initialize_model(self):
        """Initialize YOLOv8 model"""
        try:
            from ultralytics import YOLO
            
            model_path = self.yolo_config.get('model_path', 'models/yolov8n.pt')
            
            # Check if model exists, if not download default
            if not Path(model_path).exists():
                print(f"Model not found at {model_path}, downloading YOLOv8n...")
                model_path = 'yolov8n.pt'
            
            self.model = YOLO(model_path)
            
            # Move to appropriate device
            if self.device == 'cuda':
                try:
                    import torch
                    if torch.cuda.is_available():
                        self.model.to('cuda')
                        print("Model loaded on GPU")
                    else:
                        print("CUDA not available, using CPU")
                        self.device = 'cpu'
                except ImportError:
                    print("PyTorch not available, using CPU")
                    self.device = 'cpu'
            
            print(f"YOLOv8 model initialized successfully on {self.device}")
            
        except ImportError:
            print("Error: Ultralytics YOLO not installed. Install with: pip install ultralytics")
            self.model = None
        except Exception as e:
            print(f"Error initializing YOLO model: {e}")
            self.model = None
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect obstacles in frame
        
        Args:
            frame: Input frame
            
        Returns:
            List of detections with format:
            [{'class': str, 'confidence': float, 'bbox': (x1, y1, x2, y2), 'class_id': int}]
        """
        if self.model is None:
            print("Model not initialized")
            return []
        
        try:
            # Run inference
            results = self.model.predict(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            detections = []
            
            # Process results
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Extract box data
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    # Get class name
                    class_name = self._get_obstacle_class(class_id)
                    
                    if class_name:
                        detection = {
                            'class': class_name,
                            'confidence': confidence,
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'class_id': class_id
                        }
                        detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Error during detection: {e}")
            return []
    
    def _get_obstacle_class(self, class_id: int) -> Optional[str]:
        """
        Map YOLO class ID to obstacle category
        
        Args:
            class_id: YOLO class ID
            
        Returns:
            Obstacle class name or None
        """
        # Check human
        if class_id == self.class_mappings['human']:
            return 'human'
        
        # Check vehicle
        vehicle_ids = self.class_mappings['vehicle']
        if isinstance(vehicle_ids, list) and class_id in vehicle_ids:
            return 'vehicle'
        elif class_id == vehicle_ids:
            return 'vehicle'
        
        # Check animal
        animal_ids = self.class_mappings['animal']
        if isinstance(animal_ids, list) and class_id in animal_ids:
            return 'animal'
        elif class_id == animal_ids:
            return 'animal'
        
        # Check debris
        debris_ids = self.class_mappings['debris']
        if isinstance(debris_ids, list) and class_id in debris_ids:
            return 'debris'
        elif class_id == debris_ids:
            return 'debris'
        
        return None
    
    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection bounding boxes on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with drawn detections
        """
        output = frame.copy()
        
        # Color mapping
        colors = {
            'human': (0, 0, 255),      # Red
            'vehicle': (255, 0, 0),    # Blue
            'animal': (0, 255, 0),     # Green
            'debris': (0, 165, 255)    # Orange
        }
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            class_name = det['class']
            confidence = det['confidence']
            
            # Get color
            color = colors.get(class_name, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name.upper()}: {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # Draw label background
            cv2.rectangle(output, 
                         (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), 
                         color, -1)
            
            # Draw label text
            cv2.putText(output, label, 
                       (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, 
                       (255, 255, 255), 1)
        
        return output
    
    def filter_by_confidence(self, detections: List[Dict], min_confidence: float) -> List[Dict]:
        """
        Filter detections by minimum confidence
        
        Args:
            detections: List of detections
            min_confidence: Minimum confidence threshold
            
        Returns:
            Filtered detections
        """
        return [det for det in detections if det['confidence'] >= min_confidence]
    
    def filter_by_class(self, detections: List[Dict], classes: List[str]) -> List[Dict]:
        """
        Filter detections by class
        
        Args:
            detections: List of detections
            classes: List of class names to keep
            
        Returns:
            Filtered detections
        """
        return [det for det in detections if det['class'] in classes]
    
    def get_detection_stats(self, detections: List[Dict]) -> Dict:
        """
        Get statistics about detections
        
        Args:
            detections: List of detections
            
        Returns:
            Dictionary with detection statistics
        """
        stats = {
            'total': len(detections),
            'by_class': {
                'human': 0,
                'vehicle': 0,
                'animal': 0,
                'debris': 0
            },
            'avg_confidence': 0.0
        }
        
        if not detections:
            return stats
        
        # Count by class
        for det in detections:
            class_name = det['class']
            if class_name in stats['by_class']:
                stats['by_class'][class_name] += 1
        
        # Calculate average confidence
        stats['avg_confidence'] = sum(d['confidence'] for d in detections) / len(detections)
        
        return stats


class ObstacleTracker:
    """Track obstacles across multiple frames"""
    
    def __init__(self, max_disappeared: int = 5):
        """
        Initialize obstacle tracker
        
        Args:
            max_disappeared: Maximum frames an object can disappear before being removed
        """
        self.next_object_id = 0
        self.objects = {}  # {id: detection}
        self.disappeared = {}  # {id: frame_count}
        self.max_disappeared = max_disappeared
    
    def register(self, detection: Dict) -> int:
        """
        Register new obstacle
        
        Args:
            detection: Detection dictionary
            
        Returns:
            Object ID
        """
        self.objects[self.next_object_id] = detection
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
        return self.next_object_id - 1
    
    def deregister(self, object_id: int):
        """
        Remove obstacle from tracking
        
        Args:
            object_id: ID of object to remove
        """
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections: List[Dict]) -> Dict[int, Dict]:
        """
        Update tracked objects with new detections
        
        Args:
            detections: List of current frame detections
            
        Returns:
            Dictionary of tracked objects {id: detection}
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                # Deregister if disappeared too long
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            return self.objects
        
        # If no existing objects, register all detections
        if len(self.objects) == 0:
            for detection in detections:
                self.register(detection)
        else:
            # Match detections to existing objects
            object_ids = list(self.objects.keys())
            
            # Simple centroid-based matching
            for detection in detections:
                best_match = None
                min_distance = float('inf')
                
                det_center = self._get_center(detection['bbox'])
                
                for object_id in object_ids:
                    obj_center = self._get_center(self.objects[object_id]['bbox'])
                    distance = np.linalg.norm(np.array(det_center) - np.array(obj_center))
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match = object_id
                
                # If close enough, update; otherwise register new
                if best_match is not None and min_distance < 100:
                    self.objects[best_match] = detection
                    self.disappeared[best_match] = 0
                    object_ids.remove(best_match)
                else:
                    self.register(detection)
            
            # Mark remaining objects as disappeared
            for object_id in object_ids:
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
        
        return self.objects
    
    def _get_center(self, bbox: Tuple[int, int, int, int]) -> Tuple[float, float]:
        """Get center point of bounding box"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)


if __name__ == "__main__":
    # Test obstacle detector
    print("Testing Obstacle Detection Module...")
    
    detector = ObstacleDetector()
    
    if detector.model is not None:
        print("Model initialized successfully")
        
        # Create test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test detection (will return empty on blank frame)
        detections = detector.detect(test_frame)
        print(f"Detections: {len(detections)}")
        
        stats = detector.get_detection_stats(detections)
        print(f"Detection stats: {stats}")
    else:
        print("Model initialization failed")
    
    print("Obstacle detection test complete")
