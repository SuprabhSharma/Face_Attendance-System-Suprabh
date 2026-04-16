# Authentication System Documentation

## Overview

The Face Recognition Attendance System now includes a comprehensive user authentication system built with Flask-Login. This system manages user registration, login, password management, and role-based access control.

## Features

### 1. User Registration
- **Self-registration** with email validation
- **Gmail-only accounts** for email notifications
- **Password strength meter** with validation
- **Email verification** (upcoming)
- **Role assignment** (default: user)

### 2. User Login
- **Username/password authentication**
- **Session management** with remember me option
- **Secure password hashing** (PBKDF2-HMAC SHA256)
- **Login attempt logging** for security
- **Automatic redirect** to requested page after login

### 3. Session Management
- **Configurable timeout** (default: 30 minutes)
- **Remember me functionality** (30 days)
- **Secure cookies** (HTTPONLY, SECURE in production)
- **Automatic logout** on timeout

### 4. Password Management
- **Change password** functionality
- **Current password verification** required
- **Password strength validation**
- **Password history** (upcoming)

### 5. Role-Based Access Control (RBAC)
- **Three user roles**: user, manager, admin
- **Role-specific navigation** in sidebar
- **Protected routes** with @login_required and @role_required
- **Admin dashboard** for system management

## User Registration

### Registration Form Fields
1. **Full Name** - 2-50 characters
2. **Username** - 3-20 characters, alphanumeric with underscores
3. **Gmail Address** - Must end with @gmail.com
4. **Password** - Minimum 8 characters, letters + numbers required
5. **Confirm Password** - Must match password field
6. **Terms of Service** - Must agree to continue

### Registration Process
```
1. User navigates to /auth/register
2. Fills out registration form
3. System validates all fields
4. Checks username and email uniqueness
5. Hashes password securely
6. Creates user account in database
7. Redirects to login page
```

### Password Strength Indicator
- **Weak** (Red): Less than 8 characters
- **Fair** (Orange): 8+ characters, either letters or numbers
- **Good** (Blue): 8+ characters with letters and numbers
- **Strong** (Green): 12+ characters with letters, numbers, and special characters

## User Login

### Login Form
- **Username** field
- **Password** field with show/hide toggle
- **Remember me** checkbox for extended session

### Login Process
```
1. User navigates to /auth/login
2. Enters username and password
3. System validates credentials
4. Creates Flask-Login session
5. Sets secure session cookie
6. Redirects to dashboard or requested page
```

### Session Security
- Sessions stored server-side
- Cookies are HTTP-only (no JavaScript access)
- In production: Secure flag requires HTTPS
- Session timeout: 30 minutes (configurable)
- Remember me: 30 days

## User Profile

### Profile Page (/auth/profile)
- **Account Information**
  - Full Name
  - Username
  - Email with verification status
  - User Role (badge)
  - Account Status
  
- **Attendance Summary**
  - Present count (today/month)
  - Late count
  - Absent count
  - Last attendance marked

- **Recent Attendance Records**
  - Paginated list of last 50 records
  - Date, check-in, check-out, status
  - Sortable by date

## Password Management

### Change Password (/auth/change-password)
- **Current Password** verification required
- **New Password** with strength meter
- **Password validation rules**:
  - Minimum 8 characters
  - Must contain letters
  - Must contain numbers
  - Can't be same as old password
  
### Password Security Tips
1. Use unique passwords for different accounts
2. Avoid personal information in passwords
3. Change password every 90 days
4. Never share password with anyone
5. Use 12+ characters with mixed case and special characters

## Role-Based Access Control

### User Roles

#### 1. User (Default)
- Access to personal dashboard
- Mark own attendance
- View own reports
- Change own password

#### 2. Manager
- Access to team dashboard
- View team reports
- Generate team summaries
- Monitor team attendance

#### 3. Admin
- Access to admin dashboard
- User management (create, edit, deactivate)
- System configuration
- View all reports
- Email configuration
- Scheduler management

### Protected Routes

```python
# All routes requiring authentication
/dashboard              # @login_required
/camera               # @login_required
/report               # @login_required
/register             # @login_required (face registration)
/auth/profile         # @login_required
/auth/change-password # @login_required

# Admin-only routes
/admin/*              # @role_required('admin')
```

## API Endpoints with Authentication

### Authentication Required
All API endpoints in `/api/*` now require authentication:

```python
@api_bp.route('/mark-attendance', methods=['POST'])
@login_required
def mark_attendance():
    """Mark attendance for logged-in user"""
    # current_user.id provides user's ID
    # current_user.email for email notifications
```

### Email Notifications
When attendance is marked:
1. System captures attendance timestamp
2. Retrieves user's recent attendance history
3. Sends email with:
   - Attendance confirmation
   - Last 10 attendance records
   - Monthly summary statistics
4. Logs email in database for tracking

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
    role TEXT DEFAULT 'user',
    status TEXT DEFAULT 'active',  -- active/inactive
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Session Management
Flask-Login uses Python's built-in session system:
- Server-side session data stored in database
- Client receives encrypted session cookie
- Session expires after configured timeout
- User can remain logged in with "Remember Me"

## Configuration

### Environment Variables (.env)
```env
# Session Configuration
SESSION_TIMEOUT_MINUTES=30
SECRET_KEY=your-secret-key-here

# Admin Initialization
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@gmail.com
ADMIN_PASSWORD=SecurePassword123!

# Email Settings (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
```

## Security Considerations

### Password Security
- **Hashed with PBKDF2-HMAC SHA256**
  - 100,000 iterations
  - 32-byte salt
  - Constant-time comparison to prevent timing attacks
  
### Session Security
- **Secure Cookies**
  - HTTP-Only: Prevents JavaScript access
  - Secure: Only transmitted over HTTPS (production)
  - SameSite: Prevents CSRF attacks
  
### Database Security
- **SQL Injection Prevention**: Parameterized queries
- **User Input Validation**: All inputs validated
- **Audit Logging**: All actions logged with user and timestamp

### Best Practices
1. **Never store plaintext passwords**
2. **Always validate user input**
3. **Use HTTPS in production**
4. **Implement rate limiting** on login (upcoming)
5. **Log security events** (authentication, role changes)
6. **Rotate SECRET_KEY** regularly
7. **Monitor failed login attempts**
8. **Implement password expiration** policy

## Logging

### Authentication Logs
File: `logs/auth.log`
```
2024-01-15 10:30:45 - AUTH - User logged in: john_doe from 192.168.1.100
2024-01-15 10:35:20 - AUTH - Failed login attempt for username: john from 192.168.1.101
2024-01-15 11:00:00 - AUTH - Password changed for user: john_doe
```

### Application Logs
File: `logs/application.log`
```
2024-01-15 10:30:45 - INFO - New user registered: john_doe with email: john@gmail.com
2024-01-15 10:31:00 - DEBUG - User john_doe authenticated successfully
```

## Integration with Existing Features

### Face Recognition
- User must be logged in to register face
- Face embedding stored with user ID
- Attendance marked for current user

### Email Notifications
- Triggered on successful attendance marking
- User's Gmail address from registration
- HTML email with attendance records
- Status tracking in email_notifications table

### Scheduler
- Runs automated tasks as logged-in system
- Marks absentees for all users at 5:30 PM UTC
- Sends daily summaries at 6:00 PM UTC
- Generates monthly reports

## Troubleshooting

### Login Issues
```
Issue: "Invalid username or password"
Solution: Check username spelling and password case-sensitivity

Issue: "Session expired"
Solution: Use "Remember me" option for longer sessions

Issue: "Account has been deactivated"
Solution: Contact system administrator to reactivate account
```

### Password Issues
```
Issue: "Password must be at least 8 characters"
Solution: Use minimum 8 characters with letters and numbers

Issue: "Passwords do not match"
Solution: Confirm password fields match exactly

Issue: "Current password is incorrect"
Solution: Enter current password correctly to change it
```

### Email Verification
```
Issue: "Email must be a valid Gmail address"
Solution: Use email address ending with @gmail.com

Issue: "Email already registered"
Solution: Use different email or login with existing account
```

## API Examples

### Register User
```bash
POST /auth/register
Content-Type: application/x-www-form-urlencoded

full_name=John+Doe&username=johndoe&email=john@gmail.com&password=SecurePass123&confirm_password=SecurePass123&agree_terms=on
```

### Login User
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=SecurePass123&remember=on
```

### Access Protected Route
```bash
GET /dashboard
Cookie: session=eyJ...
# Returns dashboard for authenticated user
```

### Logout
```bash
GET /auth/logout
# Clears session and redirects to login
```

## Future Enhancements

1. **Email Verification**
   - Send verification link on registration
   - Email confirmation required before account activation

2. **Two-Factor Authentication (2FA)**
   - SMS or email code verification
   - Increased security for sensitive operations

3. **OAuth Integration**
   - Google authentication via Gmail
   - Single sign-on capability

4. **Password Reset**
   - Forgot password functionality
   - Email link for password reset

5. **Login History**
   - Track all login attempts
   - Device and location information
   - Security alert for suspicious logins

6. **Account Deactivation**
   - Self-service account deletion
   - Data export before deletion
   - Recovery period before permanent deletion

7. **Biometric Authentication**
   - Face recognition login
   - Fingerprint on mobile

8. **Audit Trail**
   - Complete action history per user
   - Data change tracking
   - Compliance reporting

## References

- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [PBKDF2 NIST Guidance](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-132.pdf)
