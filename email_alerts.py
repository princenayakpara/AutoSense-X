"""
Email Alerts Module - Send alerts when system is critical
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import psutil
from ai_engine import AISystemBrain

class EmailAlertService:
    """Service for sending email alerts"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.email_from = os.getenv("EMAIL_FROM", self.smtp_user)
        self.ai_engine = AISystemBrain()
        self.last_alert_time = {}
    
    def send_alert(self, to_email: str, subject: str, message: str) -> bool:
        """Send email alert"""
        if not self.smtp_user or not self.smtp_password:
            print("Email not configured. Skipping alert.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; background: #0a0e27; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(45deg, #00ffff, #0066ff); padding: 20px; text-align: center; }}
                    .content {{ background: #16213e; padding: 20px; border-radius: 8px; }}
                    .alert {{ background: #ff0000; padding: 10px; border-radius: 4px; margin: 10px 0; }}
                    .footer {{ text-align: center; padding: 20px; color: #b0b0b0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔥 AutoSense X Alert</h1>
                    </div>
                    <div class="content">
                        <div class="alert">
                            <h2>{subject}</h2>
                        </div>
                        <p>{message}</p>
                        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    <div class="footer">
                        <p>AutoSense X - Ultimate AI System Guardian</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def check_system_and_alert(self, user_email: str, alert_threshold: float = 0.7):
        """Check system health and send alert if critical"""
        try:
            prediction = self.ai_engine.predict_degradation_risk()
            risk_score = prediction.get("risk_score", 0)
            
            # Check if we should alert (avoid spam - max once per hour per type)
            alert_key = "system_health"
            last_alert = self.last_alert_time.get(alert_key)
            if last_alert:
                time_diff = (datetime.now() - last_alert).total_seconds()
                if time_diff < 3600:  # 1 hour cooldown
                    return False
            
            if risk_score >= alert_threshold:
                subject = f"🚨 Critical System Alert - Risk Level: {prediction.get('risk_level', 'HIGH').upper()}"
                message = f"""
                Your system health is at risk!
                
                Risk Score: {risk_score:.1%}
                Risk Level: {prediction.get('risk_level', 'unknown').upper()}
                
                {prediction.get('explanation', '')}
                
                Recommendations:
                {chr(10).join('- ' + rec for rec in prediction.get('recommendations', []))}
                
                Please take action to optimize your system.
                """
                
                if self.send_alert(user_email, subject, message):
                    self.last_alert_time[alert_key] = datetime.now()
                    return True
            
            return False
        except Exception as e:
            print(f"Error checking system and alerting: {e}")
            return False
    
    def send_critical_alert(self, user_email: str, alert_type: str, details: str):
        """Send immediate critical alert"""
        subject = f"🚨 CRITICAL: {alert_type}"
        message = f"""
        Critical system issue detected!
        
        Type: {alert_type}
        Details: {details}
        
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Please check your system immediately.
        """
        
        return self.send_alert(user_email, subject, message)


# Background monitoring service
def start_email_monitoring(user_email: str, check_interval: int = 300):
    """Start background email monitoring"""
    import time
    from threading import Thread
    
    service = EmailAlertService()
    
    def monitor():
        while True:
            try:
                service.check_system_and_alert(user_email)
                time.sleep(check_interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(check_interval)
    
    thread = Thread(target=monitor, daemon=True)
    thread.start()
    return service

