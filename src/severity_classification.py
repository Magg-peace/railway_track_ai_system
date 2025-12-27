"""
RailTrack - Severity Classification Engine
Classifies incident severity based on multiple factors
"""

import yaml
from typing import Dict, List, Optional
from datetime import datetime


class SeverityClassifier:
    """Classifies incident severity based on rules and conditions"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize severity classifier
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.severity_config = self.config.get('severity', {})
        self.rules = self.severity_config.get('rules', {})
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def classify(self, incident: Dict) -> str:
        """
        Classify incident severity
        
        Args:
            incident: Dictionary containing:
                - obstacle_class: Type of obstacle
                - zone: Track zone
                - ttc: Time-to-collision
                - distance: Distance to obstacle
                - is_static: Whether obstacle is stationary
                - confidence: Detection confidence
                
        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'
        """
        obstacle_class = incident.get('obstacle_class', 'unknown')
        zone = incident.get('zone', 'safe')
        ttc = incident.get('ttc', float('inf'))
        is_static = incident.get('is_static', False)
        distance = incident.get('distance', float('inf'))
        
        # Critical conditions
        if self._is_critical(obstacle_class, zone, ttc, is_static):
            return 'critical'
        
        # High severity conditions
        if self._is_high(obstacle_class, zone, ttc, is_static):
            return 'high'
        
        # Medium severity conditions
        if self._is_medium(obstacle_class, zone, ttc):
            return 'medium'
        
        # Default to low
        return 'low'
    
    def _is_critical(self, obstacle_class: str, zone: str, ttc: float, is_static: bool) -> bool:
        """Check if incident is critical"""
        critical_conditions = [
            # Human on track with low TTC
            obstacle_class == 'human' and zone == 'critical' and ttc < 20,
            
            # Vehicle on track with very low TTC
            obstacle_class == 'vehicle' and zone == 'critical' and ttc < 15,
            
            # Any static obstacle on track with low TTC
            is_static and zone == 'critical' and ttc < 25,
            
            # Human or vehicle on track with very close distance
            obstacle_class in ['human', 'vehicle'] and zone == 'critical' and ttc < 10
        ]
        
        return any(critical_conditions)
    
    def _is_high(self, obstacle_class: str, zone: str, ttc: float, is_static: bool) -> bool:
        """Check if incident is high severity"""
        high_conditions = [
            # Human near track with moderate TTC
            obstacle_class == 'human' and zone == 'warning' and ttc < 40,
            
            # Animal on critical track
            obstacle_class == 'animal' and zone == 'critical',
            
            # Large debris on track
            obstacle_class == 'debris' and zone == 'critical' and is_static,
            
            # Vehicle near track with low TTC
            obstacle_class == 'vehicle' and zone == 'warning' and ttc < 30,
            
            # Any obstacle on track with moderate TTC
            zone == 'critical' and ttc < 40
        ]
        
        return any(high_conditions)
    
    def _is_medium(self, obstacle_class: str, zone: str, ttc: float) -> bool:
        """Check if incident is medium severity"""
        medium_conditions = [
            # Animal near track
            obstacle_class == 'animal' and zone == 'warning',
            
            # Small debris on track
            obstacle_class == 'debris' and zone == 'critical',
            
            # Vehicle near track with higher TTC
            obstacle_class == 'vehicle' and zone == 'warning' and ttc < 60,
            
            # Human in safe zone but close TTC
            obstacle_class == 'human' and ttc < 60,
            
            # Any obstacle on track with high TTC
            zone == 'critical' and ttc < 60
        ]
        
        return any(medium_conditions)
    
    def get_severity_color(self, severity: str) -> tuple:
        """
        Get color code for severity level
        
        Args:
            severity: Severity level
            
        Returns:
            RGB color tuple
        """
        colors = {
            'critical': (0, 0, 255),    # Red
            'high': (0, 165, 255),      # Orange
            'medium': (0, 255, 255),    # Yellow
            'low': (0, 255, 0)          # Green
        }
        return colors.get(severity, (128, 128, 128))
    
    def get_severity_priority(self, severity: str) -> int:
        """
        Get numeric priority for severity level
        
        Args:
            severity: Severity level
            
        Returns:
            Priority number (higher = more severe)
        """
        priorities = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priorities.get(severity, 0)
    
    def classify_batch(self, incidents: List[Dict]) -> List[Dict]:
        """
        Classify multiple incidents
        
        Args:
            incidents: List of incident dictionaries
            
        Returns:
            List of incidents with severity classifications
        """
        classified = []
        
        for incident in incidents:
            severity = self.classify(incident)
            
            classified_incident = {
                **incident,
                'severity': severity,
                'severity_priority': self.get_severity_priority(severity),
                'severity_color': self.get_severity_color(severity),
                'timestamp': datetime.now().isoformat()
            }
            
            classified.append(classified_incident)
        
        # Sort by severity priority
        classified.sort(key=lambda x: x['severity_priority'], reverse=True)
        
        return classified
    
    def get_recommended_action(self, severity: str) -> str:
        """
        Get recommended action for severity level
        
        Args:
            severity: Severity level
            
        Returns:
            Recommended action string
        """
        actions = {
            'critical': "IMMEDIATE ACTION REQUIRED: Alert driver, activate emergency braking if available, notify control room",
            'high': "URGENT: Alert driver, reduce speed, notify control room and nearest station",
            'medium': "CAUTION: Monitor situation, notify control room, prepare for potential action",
            'low': "ADVISORY: Log incident, continue monitoring"
        }
        return actions.get(severity, "Monitor situation")


class IncidentReporter:
    """Generates detailed incident reports"""
    
    def __init__(self):
        """Initialize incident reporter"""
        self.severity_classifier = SeverityClassifier()
    
    def generate_report(self, incident: Dict) -> Dict:
        """
        Generate comprehensive incident report
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Detailed incident report
        """
        severity = self.severity_classifier.classify(incident)
        
        report = {
            'incident_id': self._generate_incident_id(),
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'severity_priority': self.severity_classifier.get_severity_priority(severity),
            'obstacle': {
                'type': incident.get('obstacle_class', 'unknown'),
                'confidence': incident.get('confidence', 0.0),
                'is_static': incident.get('is_static', False),
                'duration_seconds': incident.get('duration', 0)
            },
            'location': {
                'zone': incident.get('zone', 'unknown'),
                'bbox': incident.get('bbox', None),
                'gps': incident.get('gps_location', None)
            },
            'risk_assessment': {
                'distance_meters': incident.get('distance', None),
                'ttc_seconds': incident.get('ttc', None),
                'train_speed_kmh': incident.get('train_speed', None)
            },
            'recommended_action': self.severity_classifier.get_recommended_action(severity),
            'explanation': self._generate_explanation(incident, severity)
        }
        
        return report
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"INC_{timestamp}"
    
    def _generate_explanation(self, incident: Dict, severity: str) -> str:
        """
        Generate human-readable explanation
        
        Args:
            incident: Incident dictionary
            severity: Severity level
            
        Returns:
            Explanation string
        """
        obstacle_type = incident.get('obstacle_class', 'unknown')
        zone = incident.get('zone', 'unknown')
        ttc = incident.get('ttc', None)
        distance = incident.get('distance', None)
        is_static = incident.get('is_static', False)
        duration = incident.get('duration', 0)
        
        explanation_parts = []
        
        # Obstacle description
        if obstacle_type == 'human':
            explanation_parts.append("A human was detected")
        elif obstacle_type == 'vehicle':
            explanation_parts.append("A vehicle was detected")
        elif obstacle_type == 'animal':
            explanation_parts.append("An animal was detected")
        elif obstacle_type == 'debris':
            explanation_parts.append("Debris was detected")
        else:
            explanation_parts.append("An obstacle was detected")
        
        # Location
        if zone == 'critical':
            explanation_parts.append("on the railway track")
        elif zone == 'warning':
            explanation_parts.append("near the railway track")
        else:
            explanation_parts.append("in the vicinity")
        
        # Distance
        if distance is not None:
            explanation_parts.append(f"at approximately {distance:.1f} meters ahead")
        
        # Static/moving
        if is_static:
            explanation_parts.append(f"The obstacle remained stationary for {duration:.1f} seconds")
        
        # Time to collision
        if ttc is not None and ttc < 60:
            explanation_parts.append(f"Estimated collision time: {ttc:.1f} seconds")
        
        # Severity
        explanation_parts.append(f"Severity classified as {severity.upper()}")
        
        return ". ".join(explanation_parts) + "."
    
    def generate_summary_report(self, incidents: List[Dict]) -> Dict:
        """
        Generate summary report for multiple incidents
        
        Args:
            incidents: List of incidents
            
        Returns:
            Summary report dictionary
        """
        if not incidents:
            return {
                'total_incidents': 0,
                'by_severity': {},
                'by_type': {},
                'critical_incidents': []
            }
        
        # Classify all incidents
        classified = self.severity_classifier.classify_batch(incidents)
        
        # Count by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for inc in classified:
            severity = inc.get('severity', 'low')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by type
        type_counts = {}
        for inc in incidents:
            obs_type = inc.get('obstacle_class', 'unknown')
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        # Get critical incidents
        critical = [inc for inc in classified if inc.get('severity') == 'critical']
        
        return {
            'total_incidents': len(incidents),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'critical_incidents': critical[:5],  # Top 5 critical
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test severity classification
    print("Testing Severity Classification Module...")
    
    classifier = SeverityClassifier()
    
    # Test incidents
    test_incidents = [
        {
            'obstacle_class': 'human',
            'zone': 'critical',
            'ttc': 15,
            'distance': 250,
            'is_static': True,
            'confidence': 0.95
        },
        {
            'obstacle_class': 'animal',
            'zone': 'warning',
            'ttc': 45,
            'distance': 750,
            'is_static': False,
            'confidence': 0.87
        }
    ]
    
    for i, incident in enumerate(test_incidents, 1):
        severity = classifier.classify(incident)
        action = classifier.get_recommended_action(severity)
        print(f"\nIncident {i}:")
        print(f"  Severity: {severity}")
        print(f"  Action: {action}")
    
    # Test reporter
    reporter = IncidentReporter()
    report = reporter.generate_report(test_incidents[0])
    print(f"\nGenerated Report:")
    print(f"  ID: {report['incident_id']}")
    print(f"  Severity: {report['severity']}")
    print(f"  Explanation: {report['explanation']}")
    
    print("\nSeverity classification test complete")
