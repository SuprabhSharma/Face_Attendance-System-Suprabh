import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from app.models.db import log_email_notification, update_email_notification_status
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending automated emails"""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.sender_name = 'FaceAttend System'
        
def send_email(self, recipient_email, subject, html_content, user_id=None):
    """Send email to recipient"""
    
    notification_id = None   # ✅ FIX 1
    
    try:
        if not self.sender_email or not self.sender_password:
            print("EMAIL NOT CONFIGURED:", self.sender_email, self.sender_password)  # ✅ FIX 2
            logger.warning('Email credentials not configured')
            return False
        
        print("Sending email to:", recipient_email)  # ✅ DEBUG
        
        # Create email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f'{self.sender_name} <{self.sender_email}>'
        msg['To'] = recipient_email
        
        # Attach HTML
        msg.attach(MIMEText(html_content, 'html'))
        
        # Log notification
        notification_id = log_email_notification(user_id, 'general', recipient_email, subject) if user_id else None
        
        # Send email
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
        
        if notification_id:
            update_email_notification_status(notification_id, 'sent')
        
        print("EMAIL SENT SUCCESSFULLY")  # ✅ DEBUG
        logger.info(f'Email sent to {recipient_email}')
        return True
        
    except Exception as e:
        print("EMAIL ERROR:", str(e))  # ✅ FIX 3
        logger.error(f'Error sending email: {str(e)}')
        
        if notification_id:
            update_email_notification_status(notification_id, 'failed', str(e)[:500])
        
        return False
    
    def send_attendance_marked_email(self, user_id, user_email, user_name, attendance_time, attendance_date, user_data):
        """Send email when attendance is marked"""
        html_content = self._build_attendance_email_template(user_name, attendance_time, attendance_date, user_data)
        subject = f'✓ Attendance Marked - {attendance_date} at {attendance_time}'
        
        notification_id = log_email_notification(user_id, 'attendance_marked', user_email, subject)
        success = self.send_email(user_email, subject, html_content, user_id)
        if not success and notification_id:
            update_email_notification_status(notification_id, 'failed', 'SMTP error')
        return success
    
    def send_absent_notification(self, user_id, user_email, user_name, date):
        """Send email when user marked absent"""
        html_content = self._build_absent_email_template(user_name, date)
        subject = f'⚠ Absent - {date}'
        
        notification_id = log_email_notification(user_id, 'absent_notification', user_email, subject)
        success = self.send_email(user_email, subject, html_content, user_id)
        if not success and notification_id:
            update_email_notification_status(notification_id, 'failed', 'SMTP error')
        return success
    
    def send_daily_summary(self, user_id, user_email, user_name, summary_data):
        """Send daily attendance summary"""
        html_content = self._build_daily_summary_template(user_name, summary_data)
        subject = f'Daily Attendance Summary - {summary_data.get("date", "")}'
        
        notification_id = log_email_notification(user_id, 'daily_summary', user_email, subject)
        success = self.send_email(user_email, subject, html_content, user_id)
        if not success and notification_id:
            update_email_notification_status(notification_id, 'failed', 'SMTP error')
        return success
    
    @staticmethod
    def _build_attendance_email_template(user_name, attendance_time, attendance_date, user_data):
        """Build HTML template for attendance marked email"""
        recent_records = user_data.get('recent_records', [])
        records_html = ''.join([
            f'''
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">{r.get('date', '')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">{r.get('time_in', '')}</td>
                <td style="padding: 10px; border-bottom: 1px solid #e0e0e0;">
                    <span style="padding: 5px 10px; border-radius: 4px; background-color: #d4edda; color: #155724;">
                        {r.get('status', 'present').upper()}
                    </span>
                </td>
            </tr>
            '''
            for r in recent_records[:10]
        ])
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .content {{ background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .success-badge {{ display: inline-block; background-color: #d4edda; color: #155724; padding: 10px 20px; border-radius: 4px; font-weight: bold; margin: 10px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">✓ Attendance Marked Successfully</h1>
                </div>
                
                <div class="content">
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <p>Your attendance has been marked for today.</p>
                    
                    <div class="success-badge">
                        ✓ {attendance_date} | {attendance_time}
                    </div>
                    
                    <h3 style="margin-top: 30px;">Your Recent Attendance Records:</h3>
                    <table>
                        <thead>
                            <tr style="background-color: #f5f5f5;">
                                <th style="padding: 10px; text-align: left;">Date</th>
                                <th style="padding: 10px; text-align: left;">Time</th>
                                <th style="padding: 10px; text-align: left;">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records_html}
                        </tbody>
                    </table>
                    
                    <p style="margin-top: 20px; color: #666;">
                        If you have any questions, please contact your administrator.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated email from FaceAttend System. Please do not reply.</p>
                    <p>&copy; 2024 Face Recognition Attendance System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    @staticmethod
    def _build_absent_email_template(user_name, date):
        """Build HTML template for absent notification"""
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .content {{ background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .warning-badge {{ display: inline-block; background-color: #fff3cd; color: #856404; padding: 10px 20px; border-radius: 4px; font-weight: bold; margin: 10px 0; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">⚠ Absent Notification</h1>
                </div>
                
                <div class="content">
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <p>You have been marked as <strong>ABSENT</strong> for the following date:</p>
                    
                    <div class="warning-badge">
                        ⚠ {date}
                    </div>
                    
                    <p style="margin-top: 20px; color: #666;">
                        If you believe this is an error or if you were present but couldn't mark attendance, 
                        please contact your administrator immediately.
                    </p>
                    
                    <p style="color: #666;">
                        <strong>Note:</strong> Repeated absences may result in disciplinary action as per company policy.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated email from FaceAttend System. Please do not reply.</p>
                    <p>&copy; 2024 Face Recognition Attendance System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        '''
    
    @staticmethod
    def _build_daily_summary_template(user_name, summary_data):
        """Build HTML template for daily summary"""
        date = summary_data.get('date', '')
        present = summary_data.get('present', 0)
        absent = summary_data.get('absent', 0)
        late = summary_data.get('late', 0)
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .content {{ background: white; padding: 20px; border-radius: 8px; margin-top: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .stats {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 20px 0; }}
                .stat-box {{ background: #f5f5f5; padding: 15px; border-radius: 4px; text-align: center; }}
                .stat-number {{ font-size: 24px; font-weight: bold; color: #667eea; }}
                .stat-label {{ margin-top: 5px; color: #666; font-size: 12px; }}
                .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid #e0e0e0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0;">📊 Daily Attendance Summary</h1>
                </div>
                
                <div class="content">
                    <p>Hello <strong>{user_name}</strong>,</p>
                    
                    <p>Here's your attendance summary for <strong>{date}</strong>:</p>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number" style="color: #10b981;">✓ {present}</div>
                            <div class="stat-label">Present</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number" style="color: #f59e0b;">⚠ {late}</div>
                            <div class="stat-label">Late</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number" style="color: #ef4444;">✕ {absent}</div>
                            <div class="stat-label">Absent</div>
                        </div>
                    </div>
                    
                    <p style="color: #666; margin-top: 20px;">
                        Keep up the good attendance! If you have any discrepancies, please contact your administrator.
                    </p>
                </div>
                
                <div class="footer">
                    <p>This is an automated email from FaceAttend System. Please do not reply.</p>
                    <p>&copy; 2024 Face Recognition Attendance System. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        '''


# Global instance
email_service = EmailService()
