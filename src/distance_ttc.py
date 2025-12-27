"""
RailTrack - Distance Estimation and Time-to-Collision Module
Estimates distance to obstacles and calculates time-to-collision
"""

import numpy as np
from typing import Dict, Tuple, Optional
import yaml


class DistanceEstimator:
    """Estimates distance to obstacles using camera calibration"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize distance estimator
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.distance_config = self.config.get('distance', {})
        
        # Camera parameters
        self.focal_length = self.distance_config.get('focal_length', 800)  # pixels
        
        # Known object heights (in meters)
        self.known_heights = self.distance_config.get('known_object_heights', {
            'human': 1.7,
            'vehicle': 1.5,
            'animal': 0.8,
            'debris': 0.3
        })
        
        # Train speed (km/h)
        self.train_speed = self.distance_config.get('default_train_speed', 60)
        self.gps_enabled = self.distance_config.get('gps_enabled', False)
        
        # TTC thresholds
        self.ttc_critical = self.distance_config.get('ttc_critical', 20)
        self.ttc_high = self.distance_config.get('ttc_high', 40)
        self.ttc_medium = self.distance_config.get('ttc_medium', 60)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def estimate_distance(self, obstacle: Dict) -> float:
        """
        Estimate distance to obstacle
        
        Args:
            obstacle: Detection dictionary with 'class' and 'bbox'
            
        Returns:
            Estimated distance in meters
        """
        obstacle_class = obstacle['class']
        bbox = obstacle['bbox']
        
        # Get known height for this class
        known_height = self.known_heights.get(obstacle_class, 1.0)
        
        # Calculate pixel height of bounding box
        pixel_height = bbox[3] - bbox[1]
        
        if pixel_height == 0:
            return float('inf')
        
        # Distance formula: D = (Known_Height * Focal_Length) / Pixel_Height
        distance = (known_height * self.focal_length) / pixel_height
        
        return max(0, distance)  # Ensure non-negative
    
    def calculate_ttc(self, distance: float, speed_kmh: Optional[float] = None) -> float:
        """
        Calculate time-to-collision
        
        Args:
            distance: Distance to obstacle in meters
            speed_kmh: Train speed in km/h (uses default if None)
            
        Returns:
            Time-to-collision in seconds
        """
        if speed_kmh is None:
            speed_kmh = self.train_speed
        
        if speed_kmh == 0:
            return float('inf')
        
        # Convert speed from km/h to m/s
        speed_ms = speed_kmh / 3.6
        
        # TTC = Distance / Speed
        ttc = distance / speed_ms
        
        return ttc
    
    def update_train_speed(self, speed_kmh: float):
        """
        Update train speed
        
        Args:
            speed_kmh: New train speed in km/h
        """
        self.train_speed = max(0, speed_kmh)
    
    def get_ttc_level(self, ttc: float) -> str:
        """
        Get TTC risk level
        
        Args:
            ttc: Time-to-collision in seconds
            
        Returns:
            Risk level: 'critical', 'high', 'medium', or 'low'
        """
        if ttc < self.ttc_critical:
            return 'critical'
        elif ttc < self.ttc_high:
            return 'high'
        elif ttc < self.ttc_medium:
            return 'medium'
        else:
            return 'low'
    
    def estimate_with_triangulation(self, 
                                    bbox1: Tuple[int, int, int, int], 
                                    bbox2: Tuple[int, int, int, int],
                                    baseline: float = 0.1) -> float:
        """
        Estimate distance using stereo triangulation (for dual camera setup)
        
        Args:
            bbox1: Bounding box from camera 1
            bbox2: Bounding box from camera 2
            baseline: Distance between cameras in meters
            
        Returns:
            Estimated distance in meters
        """
        # Calculate center x coordinates
        center1_x = (bbox1[0] + bbox1[2]) / 2
        center2_x = (bbox2[0] + bbox2[2]) / 2
        
        # Calculate disparity
        disparity = abs(center1_x - center2_x)
        
        if disparity == 0:
            return float('inf')
        
        # Distance = (Focal_Length * Baseline) / Disparity
        distance = (self.focal_length * baseline) / disparity
        
        return distance
    
    def calibrate_focal_length(self, 
                               known_distance: float,
                               known_height: float,
                               pixel_height: int) -> float:
        """
        Calibrate focal length using known measurements
        
        Args:
            known_distance: Known distance to object in meters
            known_height: Known height of object in meters
            pixel_height: Measured pixel height in image
            
        Returns:
            Calibrated focal length
        """
        # Focal_Length = (Pixel_Height * Distance) / Known_Height
        focal_length = (pixel_height * known_distance) / known_height
        
        self.focal_length = focal_length
        print(f"Focal length calibrated to: {focal_length:.2f} pixels")
        
        return focal_length


class CollisionRiskAssessor:
    """Assesses overall collision risk"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize collision risk assessor
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.distance_estimator = DistanceEstimator(config_path)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def assess_risk(self, obstacle: Dict, zone: str) -> Dict:
        """
        Assess collision risk for obstacle
        
        Args:
            obstacle: Detection dictionary
            zone: Track zone ('critical', 'warning', or 'safe')
            
        Returns:
            Risk assessment dictionary
        """
        # Estimate distance
        distance = self.distance_estimator.estimate_distance(obstacle)
        
        # Calculate TTC
        ttc = self.distance_estimator.calculate_ttc(distance)
        
        # Get TTC level
        ttc_level = self.distance_estimator.get_ttc_level(ttc)
        
        # Determine overall risk
        risk_score = self._calculate_risk_score(
            obstacle['class'],
            zone,
            ttc,
            obstacle.get('is_static', False)
        )
        
        return {
            'obstacle_class': obstacle['class'],
            'distance_m': round(distance, 2),
            'ttc_seconds': round(ttc, 2),
            'ttc_level': ttc_level,
            'zone': zone,
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'is_static': obstacle.get('is_static', False)
        }
    
    def _calculate_risk_score(self, 
                             obstacle_class: str,
                             zone: str,
                             ttc: float,
                             is_static: bool) -> float:
        """
        Calculate numerical risk score (0-100)
        
        Args:
            obstacle_class: Type of obstacle
            zone: Track zone
            ttc: Time-to-collision
            is_static: Whether obstacle is stationary
            
        Returns:
            Risk score (0-100, higher is more risky)
        """
        score = 0
        
        # Base score from obstacle type
        class_scores = {
            'human': 40,
            'vehicle': 35,
            'animal': 30,
            'debris': 20
        }
        score += class_scores.get(obstacle_class, 25)
        
        # Zone multiplier
        zone_multipliers = {
            'critical': 2.0,
            'warning': 1.5,
            'safe': 0.5
        }
        score *= zone_multipliers.get(zone, 1.0)
        
        # TTC contribution
        if ttc < 10:
            score += 30
        elif ttc < 20:
            score += 20
        elif ttc < 40:
            score += 10
        
        # Static obstacle penalty
        if is_static:
            score += 10
        
        return min(100, score)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to level"""
        if risk_score >= 75:
            return 'critical'
        elif risk_score >= 50:
            return 'high'
        elif risk_score >= 25:
            return 'medium'
        else:
            return 'low'
    
    def assess_multiple_obstacles(self, 
                                  obstacles: list,
                                  zones: list) -> Dict:
        """
        Assess risk for multiple obstacles
        
        Args:
            obstacles: List of obstacle detections
            zones: List of corresponding zones
            
        Returns:
            Overall risk assessment
        """
        if not obstacles:
            return {
                'max_risk_level': 'low',
                'max_risk_score': 0,
                'obstacle_count': 0,
                'assessments': []
            }
        
        assessments = []
        for obstacle, zone in zip(obstacles, zones):
            assessment = self.assess_risk(obstacle, zone)
            assessments.append(assessment)
        
        # Find maximum risk
        max_assessment = max(assessments, key=lambda x: x['risk_score'])
        
        return {
            'max_risk_level': max_assessment['risk_level'],
            'max_risk_score': max_assessment['risk_score'],
            'obstacle_count': len(obstacles),
            'assessments': assessments,
            'critical_count': sum(1 for a in assessments if a['risk_level'] == 'critical'),
            'high_count': sum(1 for a in assessments if a['risk_level'] == 'high')
        }


if __name__ == "__main__":
    # Test distance estimation
    print("Testing Distance Estimation Module...")
    
    estimator = DistanceEstimator()
    
    # Test obstacle
    test_obstacle = {
        'class': 'human',
        'bbox': (200, 200, 250, 400),  # 200 pixel height
        'confidence': 0.95
    }
    
    distance = estimator.estimate_distance(test_obstacle)
    print(f"Estimated distance: {distance:.2f} meters")
    
    ttc = estimator.calculate_ttc(distance)
    print(f"Time-to-collision: {ttc:.2f} seconds")
    
    ttc_level = estimator.get_ttc_level(ttc)
    print(f"TTC level: {ttc_level}")
    
    # Test collision risk
    assessor = CollisionRiskAssessor()
    risk = assessor.assess_risk(test_obstacle, 'critical')
    print(f"Risk assessment: {risk}")
    
    print("Distance estimation test complete")
