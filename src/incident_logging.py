"""
RailTrack - Incident Logging and Analytics Module
Handles database operations and analytics for incidents
"""

import json
import yaml
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from collections import defaultdict


class IncidentLogger:
    """Logs incidents to database and file system"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize incident logger
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logging_config = self.config.get('logging', {})
        
        # Database configuration
        self.db_config = self.logging_config.get('database', {})
        self.db_type = self.db_config.get('type', 'sqlite')
        
        # Local storage
        self.local_enabled = self.logging_config.get('local_storage', {}).get('enabled', True)
        self.log_dir = Path(self.logging_config.get('local_storage', {}).get('log_directory', 'logs'))
        self.save_images = self.logging_config.get('local_storage', {}).get('save_images', True)
        
        # Create directories
        self.log_dir.mkdir(exist_ok=True)
        (self.log_dir / 'images').mkdir(exist_ok=True)
        (self.log_dir / 'incidents').mkdir(exist_ok=True)
        
        # Initialize database
        self.db_connection = None
        self._initialize_database()
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _initialize_database(self):
        """Initialize database connection"""
        if self.db_type == 'sqlite':
            self._initialize_sqlite()
        elif self.db_type == 'mongodb':
            self._initialize_mongodb()
        else:
            print(f"Unsupported database type: {self.db_type}")
    
    def _initialize_sqlite(self):
        """Initialize SQLite database"""
        try:
            db_path = self.log_dir / 'railtrack.db'
            self.db_connection = sqlite3.connect(str(db_path), check_same_thread=False)
            
            # Create incidents table
            cursor = self.db_connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    obstacle_type TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    distance_m REAL,
                    ttc_seconds REAL,
                    train_speed_kmh REAL,
                    gps_latitude REAL,
                    gps_longitude REAL,
                    confidence REAL,
                    is_static INTEGER,
                    explanation TEXT,
                    image_path TEXT,
                    recommended_action TEXT
                )
            ''')
            
            # Create index on timestamp
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON incidents(timestamp)
            ''')
            
            # Create index on severity
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_severity 
                ON incidents(severity)
            ''')
            
            self.db_connection.commit()
            print("SQLite database initialized")
            
        except Exception as e:
            print(f"Error initializing SQLite: {e}")
    
    def _initialize_mongodb(self):
        """Initialize MongoDB connection"""
        try:
            from pymongo import MongoClient
            
            connection_string = self.db_config.get('connection_string', 'mongodb://localhost:27017/')
            db_name = self.db_config.get('database_name', 'railtrack')
            
            client = MongoClient(connection_string)
            self.db_connection = client[db_name]
            
            print("MongoDB connection initialized")
            
        except ImportError:
            print("pymongo not installed. Install with: pip install pymongo")
        except Exception as e:
            print(f"Error initializing MongoDB: {e}")
    
    def log_incident(self, incident: Dict, image_path: Optional[str] = None) -> bool:
        """
        Log incident to database
        
        Args:
            incident: Incident report dictionary
            image_path: Optional path to saved image
            
        Returns:
            True if successful
        """
        try:
            # Extract fields
            incident_id = incident.get('incident_id', self._generate_incident_id())
            timestamp = incident.get('timestamp', datetime.now().isoformat())
            severity = incident.get('severity', 'unknown')
            
            obstacle = incident.get('obstacle', {})
            location = incident.get('location', {})
            risk = incident.get('risk_assessment', {})
            
            # Prepare data
            data = {
                'incident_id': incident_id,
                'timestamp': timestamp,
                'severity': severity,
                'obstacle_type': obstacle.get('type', 'unknown'),
                'zone': location.get('zone', 'unknown'),
                'distance_m': risk.get('distance_meters'),
                'ttc_seconds': risk.get('ttc_seconds'),
                'train_speed_kmh': risk.get('train_speed_kmh'),
                'gps_latitude': location.get('gps', {}).get('latitude') if isinstance(location.get('gps'), dict) else None,
                'gps_longitude': location.get('gps', {}).get('longitude') if isinstance(location.get('gps'), dict) else None,
                'confidence': obstacle.get('confidence'),
                'is_static': 1 if obstacle.get('is_static', False) else 0,
                'explanation': incident.get('explanation', ''),
                'image_path': image_path,
                'recommended_action': incident.get('recommended_action', '')
            }
            
            # Save to database
            if self.db_type == 'sqlite' and self.db_connection:
                self._save_to_sqlite(data)
            elif self.db_type == 'mongodb' and self.db_connection:
                self._save_to_mongodb(data)
            
            # Save to JSON file
            if self.local_enabled:
                self._save_to_json(incident)
            
            return True
            
        except Exception as e:
            print(f"Error logging incident: {e}")
            return False
    
    def _save_to_sqlite(self, data: Dict):
        """Save incident to SQLite"""
        cursor = self.db_connection.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO incidents VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['incident_id'],
            data['timestamp'],
            data['severity'],
            data['obstacle_type'],
            data['zone'],
            data['distance_m'],
            data['ttc_seconds'],
            data['train_speed_kmh'],
            data['gps_latitude'],
            data['gps_longitude'],
            data['confidence'],
            data['is_static'],
            data['explanation'],
            data['image_path'],
            data['recommended_action']
        ))
        
        self.db_connection.commit()
    
    def _save_to_mongodb(self, data: Dict):
        """Save incident to MongoDB"""
        collection_name = self.db_config.get('collection_name', 'incidents')
        collection = self.db_connection[collection_name]
        
        collection.insert_one(data)
    
    def _save_to_json(self, incident: Dict):
        """Save incident to JSON file"""
        date_str = datetime.now().strftime('%Y%m%d')
        json_file = self.log_dir / 'incidents' / f'incidents_{date_str}.json'
        
        with open(json_file, 'a') as f:
            f.write(json.dumps(incident) + '\n')
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        return f"INC_{timestamp}"
    
    def query_incidents(self, 
                       severity: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       limit: int = 100) -> List[Dict]:
        """
        Query incidents from database
        
        Args:
            severity: Filter by severity
            start_date: Start date filter
            end_date: End date filter
            limit: Maximum number of results
            
        Returns:
            List of incidents
        """
        if self.db_type == 'sqlite' and self.db_connection:
            return self._query_sqlite(severity, start_date, end_date, limit)
        elif self.db_type == 'mongodb' and self.db_connection:
            return self._query_mongodb(severity, start_date, end_date, limit)
        
        return []
    
    def _query_sqlite(self, severity, start_date, end_date, limit) -> List[Dict]:
        """Query SQLite database"""
        cursor = self.db_connection.cursor()
        
        query = "SELECT * FROM incidents WHERE 1=1"
        params = []
        
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        incidents = []
        
        for row in cursor.fetchall():
            incident = dict(zip(columns, row))
            incidents.append(incident)
        
        return incidents
    
    def _query_mongodb(self, severity, start_date, end_date, limit) -> List[Dict]:
        """Query MongoDB database"""
        collection_name = self.db_config.get('collection_name', 'incidents')
        collection = self.db_connection[collection_name]
        
        query = {}
        
        if severity:
            query['severity'] = severity
        
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date.isoformat()
            if end_date:
                query['timestamp']['$lte'] = end_date.isoformat()
        
        incidents = list(collection.find(query).sort('timestamp', -1).limit(limit))
        
        # Remove MongoDB _id field
        for incident in incidents:
            incident.pop('_id', None)
        
        return incidents
    
    def close(self):
        """Close database connection"""
        if self.db_connection:
            if self.db_type == 'sqlite':
                self.db_connection.close()
            print("Database connection closed")


class AnalyticsEngine:
    """Analyzes incident data for patterns and insights"""
    
    def __init__(self, logger: IncidentLogger):
        """
        Initialize analytics engine
        
        Args:
            logger: IncidentLogger instance
        """
        self.logger = logger
    
    def generate_daily_report(self, date: Optional[datetime] = None) -> Dict:
        """
        Generate daily incident report
        
        Args:
            date: Date for report (default: today)
            
        Returns:
            Daily report dictionary
        """
        if date is None:
            date = datetime.now()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        incidents = self.logger.query_incidents(
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        return self._analyze_incidents(incidents, f"Daily Report - {date.strftime('%Y-%m-%d')}")
    
    def _analyze_incidents(self, incidents: List[Dict], title: str) -> Dict:
        """Analyze list of incidents"""
        if not incidents:
            return {
                'title': title,
                'total_incidents': 0,
                'by_severity': {},
                'by_type': {},
                'by_zone': {},
                'high_risk_locations': []
            }
        
        # Count by severity
        by_severity = defaultdict(int)
        by_type = defaultdict(int)
        by_zone = defaultdict(int)
        
        for inc in incidents:
            by_severity[inc.get('severity', 'unknown')] += 1
            by_type[inc.get('obstacle_type', 'unknown')] += 1
            by_zone[inc.get('zone', 'unknown')] += 1
        
        return {
            'title': title,
            'total_incidents': len(incidents),
            'by_severity': dict(by_severity),
            'by_type': dict(by_type),
            'by_zone': dict(by_zone),
            'incidents': incidents[:10]  # Top 10
        }
    
    def identify_high_risk_locations(self, days: int = 30) -> List[Dict]:
        """
        Identify high-risk locations based on incident frequency
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of high-risk location data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        incidents = self.logger.query_incidents(
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        # Group by GPS location (simplified - would need clustering in production)
        location_incidents = defaultdict(list)
        
        for inc in incidents:
            lat = inc.get('gps_latitude')
            lon = inc.get('gps_longitude')
            
            if lat and lon:
                # Round to 3 decimal places (~100m accuracy)
                loc_key = f"{lat:.3f},{lon:.3f}"
                location_incidents[loc_key].append(inc)
        
        # Sort by incident count
        high_risk = []
        for loc_key, loc_incidents in location_incidents.items():
            if len(loc_incidents) >= 3:  # At least 3 incidents
                lat_str, lon_str = loc_key.split(',')
                high_risk.append({
                    'location': {'latitude': float(lat_str), 'longitude': float(lon_str)},
                    'incident_count': len(loc_incidents),
                    'severity_breakdown': self._count_severity(loc_incidents)
                })
        
        high_risk.sort(key=lambda x: x['incident_count'], reverse=True)
        
        return high_risk[:10]  # Top 10 high-risk locations
    
    def _count_severity(self, incidents: List[Dict]) -> Dict:
        """Count incidents by severity"""
        counts = defaultdict(int)
        for inc in incidents:
            counts[inc.get('severity', 'unknown')] += 1
        return dict(counts)


if __name__ == "__main__":
    # Test incident logger
    print("Testing Incident Logger...")
    
    logger = IncidentLogger()
    
    # Test incident
    test_incident = {
        'incident_id': 'INC_TEST_001',
        'timestamp': datetime.now().isoformat(),
        'severity': 'critical',
        'obstacle': {
            'type': 'human',
            'confidence': 0.95,
            'is_static': True
        },
        'location': {
            'zone': 'critical',
            'gps': {'latitude': 28.6139, 'longitude': 77.2090}
        },
        'risk_assessment': {
            'distance_meters': 200,
            'ttc_seconds': 12,
            'train_speed_kmh': 60
        },
        'explanation': 'Test incident',
        'recommended_action': 'IMMEDIATE ACTION'
    }
    
    # Log incident
    result = logger.log_incident(test_incident)
    print(f"Incident logged: {result}")
    
    # Query incidents
    incidents = logger.query_incidents(limit=5)
    print(f"Retrieved {len(incidents)} incidents")
    
    # Test analytics
    analytics = AnalyticsEngine(logger)
    report = analytics.generate_daily_report()
    print(f"Daily report: {report['total_incidents']} incidents")
    
    logger.close()
    print("Incident logger test complete")
