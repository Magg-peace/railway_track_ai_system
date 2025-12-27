"""
RailTrack - Main Application
AI-Based Intelligent Railway Track Obstacle Detection & Collision Prevention System
"""

import cv2
import numpy as np
from typing import Dict, List, Optional
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules
from src.video_capture import VideoCapture, FrameBuffer
from src.track_segmentation import TrackSegmentation
from src.obstacle_detection import ObstacleDetector, ObstacleTracker
from src.multi_frame_confirmation import MultiFrameConfirmation, FalseAlertFilter
from src.distance_ttc import DistanceEstimator, CollisionRiskAssessor
from src.severity_classification import SeverityClassifier, IncidentReporter
from src.alert_system import AlertManager
from src.incident_logging import IncidentLogger, AnalyticsEngine


class RailTrackSystem:
    """Main RailTrack obstacle detection and collision prevention system"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize RailTrack system
        
        Args:
            config_path: Path to configuration file
        """
        print("🚆 Initializing RailTrack AI Safety System...")
        
        self.config_path = config_path
        
        # Initialize all modules
        print("📹 Initializing video capture...")
        self.video_capture = VideoCapture(config_path)
        
        print("🛤️ Initializing track segmentation...")
        self.track_segmentation = TrackSegmentation(config_path)
        
        print("🤖 Initializing obstacle detector...")
        self.obstacle_detector = ObstacleDetector(config_path)
        
        print("📊 Initializing tracking and confirmation...")
        self.obstacle_tracker = ObstacleTracker(max_disappeared=5)
        self.multi_frame_confirmation = MultiFrameConfirmation(
            min_consecutive_frames=5,
            max_frame_gap=3,
            movement_threshold=50
        )
        self.false_alert_filter = FalseAlertFilter()
        
        print("📏 Initializing distance estimation...")
        self.distance_estimator = DistanceEstimator(config_path)
        self.collision_risk_assessor = CollisionRiskAssessor(config_path)
        
        print("⚠️ Initializing severity classification...")
        self.severity_classifier = SeverityClassifier(config_path)
        self.incident_reporter = IncidentReporter()
        
        print("📢 Initializing alert system...")
        self.alert_manager = AlertManager(config_path)
        
        print("💾 Initializing incident logging...")
        self.incident_logger = IncidentLogger(config_path)
        self.analytics_engine = AnalyticsEngine(self.incident_logger)
        
        # Frame buffer for temporal analysis
        self.frame_buffer = FrameBuffer(max_size=10)
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'detections_count': 0,
            'confirmed_obstacles': 0,
            'alerts_sent': 0,
            'start_time': time.time()
        }
        
        # Control flags
        self.running = False
        self.show_visualization = True
        
        print("✅ RailTrack system initialized successfully!\n")
    
    def start(self):
        """Start the RailTrack system"""
        print("🚀 Starting RailTrack system...")
        
        # Start video capture
        if not self.video_capture.start():
            print("❌ Failed to start video capture")
            return False
        
        self.running = True
        print("✅ System is now running and monitoring railway tracks\n")
        print("Press 'q' to quit, 's' to save screenshot, 'r' for report\n")
        
        return True
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process a single frame through the pipeline
        
        Args:
            frame: Input frame
            
        Returns:
            Processing results dictionary
        """
        self.stats['frames_processed'] += 1
        
        # Initialize track segmentation if needed
        if self.track_segmentation.frame_width is None:
            self.track_segmentation.initialize_frame_dimensions(frame)
        
        # Step 1: Detect obstacles
        detections = self.obstacle_detector.detect(frame)
        self.stats['detections_count'] += len(detections)
        
        # Step 2: Track obstacles
        tracked_objects = self.obstacle_tracker.update(detections)
        
        # Step 3: Multi-frame confirmation
        confirmed_obstacles = self.multi_frame_confirmation.update(detections, tracked_objects)
        
        # Step 4: Filter false alerts
        filtered_obstacles = self.false_alert_filter.filter(confirmed_obstacles)
        
        # Step 5: Classify track zones
        obstacles_with_zones = []
        for obstacle in filtered_obstacles:
            zone = self.track_segmentation.classify_zone(obstacle['bbox'])
            obstacle['zone'] = zone
            obstacles_with_zones.append(obstacle)
        
        # Step 6: Distance estimation and risk assessment
        incidents = []
        for obstacle in obstacles_with_zones:
            # Assess collision risk
            risk = self.collision_risk_assessor.assess_risk(obstacle, obstacle['zone'])
            
            # Create incident data
            incident = {
                'obstacle_class': obstacle['class'],
                'zone': obstacle['zone'],
                'ttc': risk['ttc_seconds'],
                'distance': risk['distance_m'],
                'is_static': obstacle.get('is_static', False),
                'confidence': obstacle['confidence'],
                'bbox': obstacle['bbox']
            }
            
            # Classify severity
            severity = self.severity_classifier.classify(incident)
            
            # Generate report if high severity
            if severity in ['critical', 'high']:
                report = self.incident_reporter.generate_report(incident)
                
                # Send alert
                self.alert_manager.send_alert(report)
                self.stats['alerts_sent'] += 1
                
                # Log incident
                self.incident_logger.log_incident(report)
                
                incidents.append(report)
        
        self.stats['confirmed_obstacles'] += len(confirmed_obstacles)
        
        return {
            'detections': detections,
            'confirmed_obstacles': confirmed_obstacles,
            'filtered_obstacles': filtered_obstacles,
            'incidents': incidents,
            'stats': self.stats.copy()
        }
    
    def visualize(self, frame: np.ndarray, results: Dict) -> np.ndarray:
        """
        Create visualization of detection results
        
        Args:
            frame: Input frame
            results: Processing results
            
        Returns:
            Annotated frame
        """
        vis_frame = frame.copy()
        
        # Draw track zones
        vis_frame = self.track_segmentation.draw_zones(vis_frame, alpha=0.2)
        
        # Draw detections
        vis_frame = self.obstacle_detector.draw_detections(
            vis_frame, 
            results.get('detections', [])
        )
        
        # Draw incidents with severity
        for incident in results.get('incidents', []):
            bbox = incident.get('obstacle', {}).get('bbox') or incident.get('bbox')
            if bbox:
                x1, y1, x2, y2 = bbox
                severity = incident.get('severity', 'low')
                color = self.severity_classifier.get_severity_color(severity)
                
                # Draw thick border for incidents
                cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 4)
                
                # Draw severity label
                label = f"{severity.upper()}"
                cv2.putText(vis_frame, label, (x1, y1 - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Draw statistics
        self._draw_stats(vis_frame, results['stats'])
        
        return vis_frame
    
    def _draw_stats(self, frame: np.ndarray, stats: Dict):
        """Draw statistics overlay on frame"""
        height, width = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (300, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Draw text
        y_offset = 30
        text_color = (255, 255, 255)
        
        runtime = time.time() - stats['start_time']
        fps = stats['frames_processed'] / runtime if runtime > 0 else 0
        
        cv2.putText(frame, "RAILTRACK AI SYSTEM", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 25
        
        cv2.putText(frame, f"FPS: {fps:.1f}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        y_offset += 20
        
        cv2.putText(frame, f"Frames: {stats['frames_processed']}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        y_offset += 20
        
        cv2.putText(frame, f"Detections: {stats['detections_count']}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        y_offset += 20
        
        cv2.putText(frame, f"Confirmed: {stats['confirmed_obstacles']}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 1)
        y_offset += 20
        
        cv2.putText(frame, f"Alerts: {stats['alerts_sent']}", (20, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    def run(self):
        """Main processing loop"""
        if not self.start():
            return
        
        try:
            while self.running:
                # Read frame
                ret, frame = self.video_capture.read_frame()
                
                if not ret:
                    print("❌ Failed to read frame")
                    break
                
                # Add to buffer
                self.frame_buffer.add_frame(frame, time.time())
                
                # Process frame
                results = self.process_frame(frame)
                
                # Visualize if enabled
                if self.show_visualization:
                    vis_frame = self.visualize(frame, results)
                    cv2.imshow('RailTrack AI Safety System', vis_frame)
                    
                    # Handle keyboard input
                    key = cv2.waitKey(1) & 0xFF
                    
                    if key == ord('q'):
                        print("\n🛑 Stopping system...")
                        break
                    elif key == ord('s'):
                        # Save screenshot
                        timestamp = time.strftime('%Y%m%d_%H%M%S')
                        filename = f"logs/screenshot_{timestamp}.jpg"
                        cv2.imwrite(filename, vis_frame)
                        print(f"📸 Screenshot saved: {filename}")
                    elif key == ord('r'):
                        # Print report
                        self.print_report()
                
                # Small delay to prevent CPU overload
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            self.stop()
    
    def print_report(self):
        """Print system report"""
        print("\n" + "="*60)
        print("📊 RAILTRACK SYSTEM REPORT")
        print("="*60)
        
        runtime = time.time() - self.stats['start_time']
        fps = self.stats['frames_processed'] / runtime if runtime > 0 else 0
        
        print(f"Runtime: {runtime:.1f} seconds")
        print(f"Average FPS: {fps:.1f}")
        print(f"Frames Processed: {self.stats['frames_processed']}")
        print(f"Total Detections: {self.stats['detections_count']}")
        print(f"Confirmed Obstacles: {self.stats['confirmed_obstacles']}")
        print(f"Alerts Sent: {self.stats['alerts_sent']}")
        
        # Get alert statistics
        alert_stats = self.alert_manager.get_alert_statistics()
        print(f"\nAlerts by Severity: {alert_stats.get('by_severity', {})}")
        print(f"Alerts by Type: {alert_stats.get('by_type', {})}")
        
        print("="*60 + "\n")
    
    def stop(self):
        """Stop the system and cleanup"""
        print("\n🛑 Shutting down RailTrack system...")
        
        self.running = False
        
        # Print final report
        self.print_report()
        
        # Stop video capture
        self.video_capture.stop()
        
        # Close database
        self.incident_logger.close()
        
        # Close windows
        cv2.destroyAllWindows()
        
        print("✅ System shutdown complete")


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚆 RAILTRACK - AI RAILWAY SAFETY SYSTEM")
    print("="*60)
    print("AI-Based Intelligent Railway Track Obstacle Detection")
    print("& Collision Prevention System")
    print("="*60 + "\n")
    
    # Create and run system
    system = RailTrackSystem()
    system.run()


if __name__ == "__main__":
    main()
