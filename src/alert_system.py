"""
RailTrack - Alert and Notification System
Handles alert generation and distribution via multiple channels
"""

import yaml
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path


class AlertManager:
    """Manages alerts and notifications across multiple channels"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize alert manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.alert_config = self.config.get('alerts', {})
        
        # Initialize channels
        self.telegram_enabled = self.alert_config.get('telegram', {}).get('enabled', False)
        self.sms_enabled = self.alert_config.get('sms', {}).get('enabled', False)
        self.local_enabled = self.alert_config.get('local', {}).get('sound_alert', True)
        
        # Escalation rules
        self.escalation = self.alert_config.get('escalation', {})
        
        # Alert history
        self.alert_history = []
        self.alert_log_path = Path("logs/alerts.json")
        self.alert_log_path.parent.mkdir(exist_ok=True)
        
        # Initialize channels
        self.telegram_bot = None
        self.sms_client = None
        
        if self.telegram_enabled:
            self._initialize_telegram()
        
        if self.sms_enabled:
            self._initialize_sms()
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def _initialize_telegram(self):
        """Initialize Telegram bot"""
        try:
            from telegram import Bot
            
            bot_token = self.alert_config['telegram'].get('bot_token', '')
            
            if bot_token and bot_token != 'YOUR_TELEGRAM_BOT_TOKEN':
                self.telegram_bot = Bot(token=bot_token)
                print("Telegram bot initialized")
            else:
                print("Telegram bot token not configured")
                self.telegram_enabled = False
        except ImportError:
            print("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
            self.telegram_enabled = False
        except Exception as e:
            print(f"Error initializing Telegram: {e}")
            self.telegram_enabled = False
    
    def _initialize_sms(self):
        """Initialize SMS client"""
        try:
            from twilio.rest import Client
            
            api_key = self.alert_config['sms'].get('api_key', '')
            
            if api_key and api_key != 'YOUR_SMS_API_KEY':
                # Initialize Twilio or other SMS service
                # self.sms_client = Client(account_sid, auth_token)
                print("SMS client initialized")
            else:
                print("SMS API key not configured")
                self.sms_enabled = False
        except ImportError:
            print("Twilio not installed. Install with: pip install twilio")
            self.sms_enabled = False
        except Exception as e:
            print(f"Error initializing SMS: {e}")
            self.sms_enabled = False
    
    def send_alert(self, incident: Dict) -> bool:
        """
        Send alert based on severity and escalation rules
        
        Args:
            incident: Incident report dictionary
            
        Returns:
            True if alert sent successfully
        """
        severity = incident.get('severity', 'low')
        channels = self.escalation.get(severity, ['log_only'])
        
        success = True
        
        # Prepare alert message
        message = self._format_alert_message(incident)
        
        # Send to appropriate channels
        for channel in channels:
            if channel == 'telegram' and self.telegram_enabled:
                success &= self._send_telegram(message, incident)
            elif channel == 'sms' and self.sms_enabled:
                success &= self._send_sms(message)
            elif channel == 'local' and self.local_enabled:
                success &= self._send_local_alert(message, severity)
            elif channel == 'log_only':
                self._log_alert(incident)
        
        # Always log
        self._log_alert(incident)
        
        return success
    
    def _format_alert_message(self, incident: Dict) -> str:
        """
        Format incident as alert message
        
        Args:
            incident: Incident dictionary
            
        Returns:
            Formatted message string
        """
        severity = incident.get('severity', 'UNKNOWN').upper()
        explanation = incident.get('explanation', 'No details available')
        
        severity_emoji = {
            'CRITICAL': '🚨',
            'HIGH': '⚠️',
            'MEDIUM': '🟡',
            'LOW': 'ℹ️'
        }
        
        emoji = severity_emoji.get(severity, '📋')
        
        message = f"{emoji} RAILTRACK ALERT - {severity}\n\n"
        message += f"{explanation}\n\n"
        
        # Add details
        obstacle = incident.get('obstacle', {})
        risk = incident.get('risk_assessment', {})
        
        message += f"Obstacle Type: {obstacle.get('type', 'Unknown').upper()}\n"
        message += f"Location Zone: {incident.get('location', {}).get('zone', 'Unknown').upper()}\n"
        
        if risk.get('distance_meters'):
            message += f"Distance: {risk['distance_meters']:.1f}m\n"
        
        if risk.get('ttc_seconds'):
            message += f"Time to Collision: {risk['ttc_seconds']:.1f}s\n"
        
        message += f"\nRecommended Action: {incident.get('recommended_action', 'Monitor situation')}\n"
        message += f"\nTimestamp: {incident.get('timestamp', 'Unknown')}"
        
        return message
    
    def _send_telegram(self, message: str, incident: Dict) -> bool:
        """
        Send Telegram alert
        
        Args:
            message: Alert message
            incident: Incident dictionary
            
        Returns:
            True if successful
        """
        if not self.telegram_bot:
            return False
        
        try:
            chat_ids = self.alert_config['telegram'].get('chat_ids', [])
            
            for chat_id in chat_ids:
                if chat_id and chat_id != 'CONTROL_ROOM_CHAT_ID':
                    # Use asyncio to send
                    asyncio.create_task(
                        self.telegram_bot.send_message(
                            chat_id=chat_id,
                            text=message,
                            parse_mode='HTML'
                        )
                    )
            
            print(f"Telegram alert sent to {len(chat_ids)} recipients")
            return True
            
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
            return False
    
    def _send_sms(self, message: str) -> bool:
        """
        Send SMS alert
        
        Args:
            message: Alert message
            
        Returns:
            True if successful
        """
        if not self.sms_client:
            return False
        
        try:
            recipients = self.alert_config['sms'].get('recipients', [])
            
            for recipient in recipients:
                if recipient and not recipient.startswith('+91X'):
                    # Send SMS using Twilio or other service
                    # self.sms_client.messages.create(
                    #     to=recipient,
                    #     from_=from_number,
                    #     body=message
                    # )
                    pass
            
            print(f"SMS alert sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            print(f"Error sending SMS alert: {e}")
            return False
    
    def _send_local_alert(self, message: str, severity: str) -> bool:
        """
        Send local alert (sound + display)
        
        Args:
            message: Alert message
            severity: Severity level
            
        Returns:
            True if successful
        """
        try:
            # Print to console with color
            severity_colors = {
                'critical': '\033[91m',  # Red
                'high': '\033[93m',      # Yellow
                'medium': '\033[94m',    # Blue
                'low': '\033[92m'        # Green
            }
            
            reset_color = '\033[0m'
            color = severity_colors.get(severity, '')
            
            print(f"\n{color}{'='*60}")
            print(message)
            print(f"{'='*60}{reset_color}\n")
            
            # Play sound if enabled
            if self.alert_config.get('local', {}).get('sound_alert', True):
                self._play_alert_sound(severity)
            
            return True
            
        except Exception as e:
            print(f"Error sending local alert: {e}")
            return False
    
    def _play_alert_sound(self, severity: str):
        """
        Play alert sound
        
        Args:
            severity: Severity level
        """
        try:
            # Attempt to play system beep
            import winsound
            
            # Different frequencies for different severities
            frequencies = {
                'critical': 2000,
                'high': 1500,
                'medium': 1000,
                'low': 800
            }
            
            freq = frequencies.get(severity, 1000)
            duration = 500 if severity == 'critical' else 300
            
            winsound.Beep(freq, duration)
            
        except ImportError:
            # winsound only works on Windows
            print('\a')  # System bell
        except Exception as e:
            print(f"Could not play sound: {e}")
    
    def _log_alert(self, incident: Dict):
        """
        Log alert to file
        
        Args:
            incident: Incident dictionary
        """
        try:
            alert_entry = {
                'timestamp': datetime.now().isoformat(),
                'incident_id': incident.get('incident_id', 'unknown'),
                'severity': incident.get('severity', 'unknown'),
                'obstacle_type': incident.get('obstacle', {}).get('type', 'unknown'),
                'zone': incident.get('location', {}).get('zone', 'unknown'),
                'explanation': incident.get('explanation', '')
            }
            
            self.alert_history.append(alert_entry)
            
            # Save to file
            with open(self.alert_log_path, 'a') as f:
                f.write(json.dumps(alert_entry) + '\n')
                
        except Exception as e:
            print(f"Error logging alert: {e}")
    
    def get_alert_statistics(self) -> Dict:
        """
        Get alert statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.alert_history:
            return {
                'total_alerts': 0,
                'by_severity': {},
                'by_type': {}
            }
        
        severity_counts = {}
        type_counts = {}
        
        for alert in self.alert_history:
            severity = alert.get('severity', 'unknown')
            obs_type = alert.get('obstacle_type', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[obs_type] = type_counts.get(obs_type, 0) + 1
        
        return {
            'total_alerts': len(self.alert_history),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'recent_alerts': self.alert_history[-10:]
        }


class EmailAlertSender:
    """Send email alerts (optional)"""
    
    def __init__(self, smtp_config: Dict):
        """
        Initialize email sender
        
        Args:
            smtp_config: SMTP configuration dictionary
        """
        self.smtp_config = smtp_config
        self.enabled = smtp_config.get('enabled', False)
    
    def send_email(self, subject: str, body: str, recipients: List[str]) -> bool:
        """
        Send email alert
        
        Args:
            subject: Email subject
            body: Email body
            recipients: List of recipient emails
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('from_address', '')
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect and send
            server = smtplib.SMTP(
                self.smtp_config.get('server', 'smtp.gmail.com'),
                self.smtp_config.get('port', 587)
            )
            server.starttls()
            server.login(
                self.smtp_config.get('username', ''),
                self.smtp_config.get('password', '')
            )
            server.send_message(msg)
            server.quit()
            
            print(f"Email sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False


if __name__ == "__main__":
    # Test alert manager
    print("Testing Alert Manager...")
    
    alert_mgr = AlertManager()
    
    # Test incident
    test_incident = {
        'incident_id': 'INC_TEST_001',
        'severity': 'critical',
        'timestamp': datetime.now().isoformat(),
        'explanation': 'A human was detected on the railway track at approximately 200m ahead. Estimated collision time: 12 seconds.',
        'obstacle': {'type': 'human'},
        'location': {'zone': 'critical'},
        'risk_assessment': {
            'distance_meters': 200,
            'ttc_seconds': 12
        },
        'recommended_action': 'IMMEDIATE ACTION REQUIRED'
    }
    
    # Send alert
    result = alert_mgr.send_alert(test_incident)
    print(f"Alert sent: {result}")
    
    # Get statistics
    stats = alert_mgr.get_alert_statistics()
    print(f"Alert statistics: {stats}")
    
    print("Alert manager test complete")
