# Authentication System Implementation Guide

## Quick Start

### 1. Install Dependencies
The new authentication system dependencies are already in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Key new packages:
- `Flask-Login==0.6.3` - Session management and user authentication
- `Flask-WTF==1.2.1` - Form handling with CSRF protection
- `WTForms==3.1.1` - Form validation
- `email-validator==2.1.0` - Email validation
- `APScheduler==3.10.4` - Scheduled background tasks
- `pytz==2023.3` - Timezone management

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Application Settings
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Session Configuration
SESSION_TIMEOUT_MINUTES=30

# Email Configuration (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Admin User (created on first run)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=SecurePassword123!
```

### 3. Initialize Database
On first run, the application will:
1. Create the database with all tables
2. Create default admin user
3. Initialize scheduler
4. Setup logging

```bash
python run.py
```

### 4. Access the Application
1. Open http://localhost:5000
2. You'll be redirected to login page
3. Use admin credentials or register a new account

## File Structure

```
app/
├── models/
│   └── db.py                    # Database models and operations
├── routes/
│   ├── auth.py                  # NEW: Authentication routes
│   ├── views.py                 # Updated: View routes
│   └── api.py                   # Updated: API with auth
├── services/
│   ├── email_service.py         # NEW: Email notifications
│   ├── scheduler.py             # NEW: Scheduled jobs
│   └── face_service.py          # Existing: Face recognition
├── utils/
│   └── logging_config.py        # NEW: Logging configuration
└── templates/
    ├── auth/                    # NEW: Authentication templates
    │   ├── login.html
    │   ├── register.html
    │   ├── profile.html
    │   └── change_password.html
    ├── navbar.html              # Updated: User menu
    ├── sidebar.html             # Updated: Auth-aware navigation
    └── base.html                # Updated: Flask-Login integration
```

## Key Features

### 1. User Registration (/auth/register)
Users can self-register with:
- Full name
- Username (unique, 3-20 characters)
- Gmail address (unique, must be @gmail.com)
- Password with strength validation
- Terms of service agreement

**Flow:**
```
Register Form
    ↓
Validate Inputs
    ↓
Check Uniqueness
    ↓
Hash Password
    ↓
Create User Account
    ↓
Redirect to Login
    ↓
Send Welcome Email (upcoming)
```

### 2. User Login (/auth/login)
Secure login with:
- Username and password
- Remember me option (30 days)
- Account status checking
- Failed attempt logging

**Session Management:**
- Server-side session storage
- HTTP-only secure cookies
- Configurable timeout (30 minutes default)
- Automatic re-authentication on protected routes

### 3. Attendance Marking
When user marks attendance via face recognition:
1. Face is recognized and user identified
2. Attendance status determined (present/late/half-day)
3. Email sent with:
   - Confirmation of attendance
   - Recent 10 attendance records
   - Monthly summary statistics
4. Email logged in database for tracking

### 4. Email Notifications
Automated emails sent for:
- **Attendance Marked**: When user successfully marks attendance
- **Absent Notification**: When user didn't mark attendance by end of day
- **Daily Summary**: Daily attendance report for each user

Configure SMTP in `.env`:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
```

**Gmail Setup:**
1. Enable 2-Factor Authentication in Gmail
2. Create App Password: https://myaccount.google.com/apppasswords
3. Use app password in SENDER_PASSWORD

### 5. Scheduled Background Jobs
Automatically runs these jobs:

**5:30 PM UTC (Weekdays):**
- Identify users without attendance mark
- Mark as 'absent' status
- Log audit entry

**6:00 PM UTC (Daily):**
- Collect today's attendance records
- Send individual summary emails
- Update email_notifications table

**1st of Month, 11:00 PM UTC:**
- Calculate monthly statistics per user
- Store in attendance_reports table
- Generate monthly summary report

Control scheduler in `.env`:
```env
SCHEDULER_ENABLED=true
TIMEZONE=UTC
```

## API Integration

### Protected Endpoints

#### Mark Attendance (Face Recognition)
```
POST /api/recognize-face
Content-Type: application/json

{
    "image": "base64-encoded-image"
}

Response:
{
    "success": true,
    "found": true,
    "user_id": 1,
    "user_name": "John Doe",
    "status": "present",
    "message": "John Doe marked present."
}
```

#### Register Face
```
POST /api/register-user
Authorization: Session Cookie
Content-Type: application/json

{
    "image": "base64-encoded-image"
}

Response:
{
    "success": true,
    "message": "Face registered successfully for John Doe"
}
```

#### Get User Attendance
```
GET /api/attendance
Authorization: Session Cookie

Response:
{
    "success": true,
    "data": [
        {
            "date": "2024-01-15",
            "time_in": "09:00:00",
            "time_out": "17:30:00",
            "status": "present"
        }
    ]
}
```

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    embedding BLOB,
    role TEXT DEFAULT 'user',  -- user, manager, admin
    status TEXT DEFAULT 'active',
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time_in TIME NOT NULL,
    time_out TIME,
    status TEXT,  -- present, late, absent, half_day
    notes TEXT,
    marked_by TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, date),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### Email Notifications Table
```sql
CREATE TABLE email_notifications (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    email_type TEXT,  -- attendance_marked, absent, summary
    recipient_email TEXT,
    subject TEXT,
    status TEXT DEFAULT 'pending',  -- pending, sent, failed
    error_message TEXT,
    created_at TIMESTAMP,
    sent_at TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## Logging

### Log Files Created
```
logs/
├── application.log      # All debug/info/warning messages
├── attendance.log       # Attendance-specific events
├── auth.log            # Authentication events
└── errors.log          # Error and critical messages
```

### Example Logs
```
# auth.log
2024-01-15 10:30:45 - INFO - User logged in: john_doe from 192.168.1.100
2024-01-15 10:35:20 - WARNING - Failed login attempt for username: john from 192.168.1.101
2024-01-15 11:00:00 - INFO - Password changed for user: john_doe

# attendance.log
2024-01-15 09:15:30 - INFO - Attendance marked for user john_doe with status: present
2024-01-15 17:35:00 - INFO - End of day absent marked for users: [jane_smith, bob_jones]

# errors.log
2024-01-15 14:22:10 - ERROR - Failed to send email to john@gmail.com: SMTP connection failed
```

## Development

### Create Demo Users
```python
from app.models.db import create_user, init_db

# Initialize database
init_db()

# Create demo users
create_user(
    username='john_demo',
    email='john.demo@gmail.com',
    password='DemoPass123',
    full_name='John Demo',
    role='user'
)

create_user(
    username='manager_demo',
    email='manager.demo@gmail.com',
    password='DemoPass123',
    full_name='Manager Demo',
    role='manager'
)
```

### Test Authentication
```bash
# Start development server
python run.py

# In another terminal, test login
curl -c cookies.txt -d "username=admin&password=SecurePassword123%21" \
  http://localhost:5000/auth/login

# Test protected route
curl -b cookies.txt http://localhost:5000/dashboard
```

### Debug Logging
Enable debug logging in `.env`:
```env
LOG_LEVEL=DEBUG
FLASK_ENV=development
DEBUG=True
```

## Common Tasks

### Create Admin User
```python
from app.models.db import create_user

create_user(
    username='admin',
    email='admin@gmail.com',
    password='SecurePassword123!',
    full_name='System Administrator',
    role='admin'
)
```

### Change User Role
```python
from app.models.db import get_db_connection

conn = get_db_connection()
c = conn.cursor()
c.execute('UPDATE users SET role = ? WHERE username = ?', ('admin', 'john_doe'))
conn.commit()
conn.close()
```

### Manually Mark Attendance
```python
from app.models.db import mark_attendance
from datetime import datetime, timezone

mark_attendance(user_id=1, attendance_date=datetime.now(timezone.utc))
```

### Send Test Email
```python
from app.services.email_service import EmailService
from app.models.db import get_user_by_id

email_service = EmailService()
user = get_user_by_id(1)

email_service.send_attendance_marked_email(
    user_id=1,
    user_email=user['email'],
    user_name=user['full_name'],
    attendance_time='2024-01-15 09:00:00',
    attendance_date='2024-01-15',
    user_data={'name': user['full_name']}
)
```

## Troubleshooting

### Login Issues
**Problem:** "Invalid username or password"
- Verify username spelling
- Check password case-sensitivity
- Ensure account is active (not deactivated)

**Problem:** "Session expired"
- Update SESSION_TIMEOUT_MINUTES in .env
- Use "Remember me" option
- Browser might be blocking cookies

### Email Issues
**Problem:** "Failed to send email"
- Verify SMTP credentials in .env
- Check email has 2FA enabled
- Use Gmail app-specific password (not regular password)
- Verify SMTP_HOST and SMTP_PORT

**Problem:** "User not found when sending email"
- Ensure user email is in database
- Check user's is_verified status
- Verify email_notifications table exists

### Database Issues
**Problem:** "Database initialization failed"
- Delete `database.db` to reset
- Check file permissions in project folder
- Verify all CREATE TABLE statements are correct
- Check app/models/db.py for syntax errors

### Scheduler Issues
**Problem:** "Scheduler not running"
- Set SCHEDULER_ENABLED=true in .env
- Check logs/application.log for errors
- Verify APScheduler is installed
- Ensure TIMEZONE is valid (UTC, US/Eastern, etc.)

## Security Best Practices

### For Administrators
1. **Change Default Passwords**
   - Change admin password immediately after first login
   - Use strong, unique passwords

2. **Regular Backups**
   - Backup database.db regularly
   - Store in secure location

3. **Monitor Logs**
   - Check logs for failed login attempts
   - Alert on unusual activity
   - Rotate logs regularly

4. **Update Dependencies**
   - Run `pip install --upgrade` regularly
   - Check for security vulnerabilities

### For Users
1. **Password Security**
   - Use 12+ character passwords
   - Mix uppercase, lowercase, numbers, special characters
   - Never share password with anyone
   - Change password every 90 days

2. **Account Security**
   - Use "Remember me" only on personal devices
   - Logout when done using system
   - Don't share Gmail account with others
   - Enable Gmail 2FA

3. **Email Security**
   - Keep Gmail account secure
   - Use strong Gmail password
   - Don't click suspicious links in emails
   - Report phishing attempts

## Next Steps

1. **Configure Email (REQUIRED for notifications)**
   - Set up Gmail app password
   - Update .env with email credentials
   - Test email sending

2. **Customize Branding**
   - Update logo in sidebar
   - Customize email templates
   - Update color scheme in CSS

3. **Deploy to Production**
   - Set FLASK_ENV=production
   - Generate strong SECRET_KEY
   - Use HTTPS only
   - Enable SECURE flag on cookies
   - Set up proper logging/monitoring

4. **Add Additional Features**
   - Email verification on registration
   - Two-factor authentication
   - Password reset functionality
   - User deactivation workflow
   - Audit log dashboard

## Support

For issues or questions:
1. Check AUTHENTICATION.md for detailed documentation
2. Review logs in logs/ directory
3. Check browser console for JavaScript errors
4. Verify environment variables in .env
5. Test with curl or Postman for API endpoints
