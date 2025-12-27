"""
RailTrack - Image Processor
Process single images for obstacle detection
"""

import cv2
import numpy as np
from typing import Dict, Optional
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.track_segmentation import TrackSegmentation
from src.obstacle_detection import ObstacleDetector
from src.distance_ttc import CollisionRiskAssessor
from src.severity_classification import SeverityClassifier, IncidentReporter


class ImageProcessor:
    """Process single images for obstacle detection"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize image processor
        
        Args:
            config_path: Path to configuration file
        """
        print("🖼️ Initializing Image Processor...")
        
        # Initialize modules
        self.track_segmentation = TrackSegmentation(config_path)
        self.obstacle_detector = ObstacleDetector(config_path)
        self.collision_risk_assessor = CollisionRiskAssessor(config_path)
        self.severity_classifier = SeverityClassifier(config_path)
        self.incident_reporter = IncidentReporter()
        
        print("✅ Image Processor ready\n")
    
    def process_image(self, image_path: str, show_result: bool = True) -> Dict:
        """
        Process a single image
        
        Args:
            image_path: Path to image file
            show_result: Whether to display result
            
        Returns:
            Processing results dictionary
        """
        print(f"📸 Processing image: {image_path}")
        
        # Load image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"❌ Error: Could not load image from {image_path}")
            return None
        
        print(f"   Image size: {image.shape[1]}x{image.shape[0]}")
        
        # Initialize track segmentation
        if self.track_segmentation.frame_width is None:
            self.track_segmentation.initialize_frame_dimensions(image)
        
        # Detect obstacles
        print("   🔍 Detecting obstacles...")
        detections = self.obstacle_detector.detect(image)
        print(f"   Found {len(detections)} detections")
        
        # Process each detection
        incidents = []
        for det in detections:
            # Classify zone
            zone = self.track_segmentation.classify_zone(det['bbox'])
            det['zone'] = zone
            
            # Assess risk
            risk = self.collision_risk_assessor.assess_risk(det, zone)
            
            # Classify severity
            incident_data = {
                'obstacle_class': det['class'],
                'zone': zone,
                'ttc': risk['ttc_seconds'],
                'distance': risk['distance_m'],
                'is_static': True,  # Image = static
                'confidence': det['confidence'],
                'bbox': det['bbox']
            }
            
            severity = self.severity_classifier.classify(incident_data)
            
            if severity in ['critical', 'high', 'medium']:
                report = self.incident_reporter.generate_report(incident_data)
                incidents.append(report)
                
                print(f"   ⚠️ {det['class'].upper()} detected - Severity: {severity.upper()}")
                print(f"      Zone: {zone}, Distance: {risk['distance_m']:.1f}m")
        
        # Create visualization
        result_image = self._visualize(image, detections, incidents)
        
        # Display result
        if show_result:
            self._display_result(result_image, image_path)
        
        results = {
            'image_path': image_path,
            'detections': detections,
            'incidents': incidents,
            'result_image': result_image
        }
        
        return results
    
    def _visualize(self, image: np.ndarray, detections: list, incidents: list) -> np.ndarray:
        """Create visualization with detections and zones"""
        vis_image = image.copy()
        
        # Draw track zones
        vis_image = self.track_segmentation.draw_zones(vis_image, alpha=0.2)
        
        # Draw detections
        vis_image = self.obstacle_detector.draw_detections(vis_image, detections)
        
        # Draw incident highlights
        for incident in incidents:
            bbox = incident.get('bbox') or incident.get('obstacle', {}).get('bbox')
            if bbox:
                x1, y1, x2, y2 = bbox
                severity = incident.get('severity', 'low')
                color = self.severity_classifier.get_severity_color(severity)
                
                # Draw thick border
                cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 4)
                
                # Draw severity label
                label = f"⚠️ {severity.upper()}"
                cv2.putText(vis_image, label, (x1, y1 - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Add title
        cv2.putText(vis_image, "RAILTRACK - IMAGE ANALYSIS", (20, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
        
        return vis_image
    
    def _display_result(self, result_image: np.ndarray, image_path: str):
        """Display result image"""
        window_name = f"RailTrack Analysis - {Path(image_path).name}"
        
        # Resize if too large
        height, width = result_image.shape[:2]
        max_width = 1920
        max_height = 1080
        
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            result_image = cv2.resize(result_image, (new_width, new_height))
        
        cv2.imshow(window_name, result_image)
        print("\n   Press any key to close, 's' to save...")
        
        key = cv2.waitKey(0)
        
        # Save if 's' pressed
        if key == ord('s'):
            output_path = f"logs/analyzed_{Path(image_path).name}"
            cv2.imwrite(output_path, result_image)
            print(f"   💾 Saved to: {output_path}")
        
        cv2.destroyWindow(window_name)
    
    def save_result(self, result_image: np.ndarray, output_path: str):
        """Save result image"""
        cv2.imwrite(output_path, result_image)
        print(f"💾 Result saved to: {output_path}")


if __name__ == "__main__":
    # Test image processor
    print("Testing Image Processor...")
    
    from src.file_selector import select_image_file
    
    # Select image
    image_path = select_image_file()
    
    if image_path:
        processor = ImageProcessor()
        results = processor.process_image(image_path)
        
        if results:
            print(f"\n✅ Processing complete!")
            print(f"   Detections: {len(results['detections'])}")
            print(f"   Incidents: {len(results['incidents'])}")
    else:
        print("No image selected")
