"""
RailTrack - Example Usage Script
Demonstrates different ways to use the RailTrack system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from main import RailTrackSystem


def example_basic():
    """Basic usage example"""
    print("Example 1: Basic Usage\n")
    
    # Create system
    system = RailTrackSystem()
    
    # Run system (will use default camera)
    system.run()


def example_video_file():
    """Process video file example"""
    print("Example 2: Process Video File\n")
    
    # Create system
    system = RailTrackSystem()
    
    # Modify video source
    system.video_capture.camera_config['source'] = "path/to/video.mp4"
    
    # Run system
    system.run()


def example_headless():
    """Headless mode (no visualization)"""
    print("Example 3: Headless Mode\n")
    
    # Create system
    system = RailTrackSystem()
    
    # Disable visualization
    system.show_visualization = False
    
    # Run system
    system.run()


def example_custom_processing():
    """Custom frame processing example"""
    print("Example 4: Custom Processing\n")
    
    import cv2
    from src.video_capture import VideoCapture
    from src.obstacle_detection import ObstacleDetector
    
    # Initialize modules
    capture = VideoCapture()
    detector = ObstacleDetector()
    
    # Start capture
    if capture.start():
        frame_count = 0
        
        while frame_count < 100:  # Process 100 frames
            ret, frame = capture.read_frame()
            
            if ret:
                # Detect obstacles
                detections = detector.detect(frame)
                
                # Process detections
                for det in detections:
                    print(f"Detected: {det['class']} at {det['bbox']}")
                
                frame_count += 1
            else:
                break
        
        capture.stop()
        print(f"Processed {frame_count} frames")


def example_analytics():
    """Analytics example"""
    print("Example 5: Analytics\n")
    
    from src.incident_logging import IncidentLogger, AnalyticsEngine
    from datetime import datetime, timedelta
    
    # Initialize logger
    logger = IncidentLogger()
    analytics = AnalyticsEngine(logger)
    
    # Generate daily report
    report = analytics.generate_daily_report()
    print(f"Daily Report:")
    print(f"  Total Incidents: {report['total_incidents']}")
    print(f"  By Severity: {report['by_severity']}")
    print(f"  By Type: {report['by_type']}")
    
    # Identify high-risk locations
    high_risk = analytics.identify_high_risk_locations(days=30)
    print(f"\nHigh-Risk Locations: {len(high_risk)}")
    for loc in high_risk[:5]:
        print(f"  Location: {loc['location']}")
        print(f"  Incidents: {loc['incident_count']}")
    
    logger.close()


def example_alert_testing():
    """Test alert system"""
    print("Example 6: Alert Testing\n")
    
    from src.alert_system import AlertManager
    from datetime import datetime
    
    # Initialize alert manager
    alert_mgr = AlertManager()
    
    # Create test incident
    test_incident = {
        'incident_id': 'TEST_001',
        'timestamp': datetime.now().isoformat(),
        'severity': 'high',
        'explanation': 'Test alert for system verification',
        'obstacle': {'type': 'human'},
        'location': {'zone': 'warning'},
        'risk_assessment': {
            'distance_meters': 500,
            'ttc_seconds': 30
        },
        'recommended_action': 'Test action'
    }
    
    # Send alert
    result = alert_mgr.send_alert(test_incident)
    print(f"Alert sent: {result}")
    
    # Get statistics
    stats = alert_mgr.get_alert_statistics()
    print(f"Alert Statistics: {stats}")


if __name__ == "__main__":
    print("="*60)
    print("🚆 RAILTRACK EXAMPLES")
    print("="*60)
    
    examples = {
        '1': ('Basic Usage', example_basic),
        '2': ('Video File Processing', example_video_file),
        '3': ('Headless Mode', example_headless),
        '4': ('Custom Processing', example_custom_processing),
        '5': ('Analytics', example_analytics),
        '6': ('Alert Testing', example_alert_testing)
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-6, or 'all'): ").strip()
    
    if choice == 'all':
        for key, (name, func) in examples.items():
            print(f"\n{'='*60}")
            print(f"Running: {name}")
            print('='*60)
            try:
                func()
            except KeyboardInterrupt:
                print("\nSkipped by user")
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
    elif choice in examples:
        name, func = examples[choice]
        print(f"\n{'='*60}")
        print(f"Running: {name}")
        print('='*60)
        func()
    else:
        print("Invalid choice")
