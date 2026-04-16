from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.db import get_all_users_admin, get_all_attendance_admin
from app.routes.auth import role_required

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """Home page - redirect to dashboard if authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    return redirect(url_for('auth.login'))

@views_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for authenticated users"""
    return render_template('index.html')

@views_bp.route('/register')
@login_required
def register():
    """User registration for face recognition"""
    return render_template('register.html')

@views_bp.route('/camera')
@login_required
def camera():
    """Camera view for marking attendance"""
    return render_template('camera.html')

@views_bp.route('/report')
@login_required
def report():
    """Attendance reports page"""
    return render_template('report.html')

@views_bp.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    """Administrator overview page."""
    users = get_all_users_admin()
    attendance_records = get_all_attendance_admin(limit=200)
    return render_template(
        'admin/dashboard.html',
        users=users,
        attendance_records=attendance_records
    )

@views_bp.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Administrator user management view."""
    users = get_all_users_admin()
    return render_template('admin/users.html', users=users)

@views_bp.route('/admin/attendance')
@login_required
@role_required('admin')
def admin_attendance():
    """Administrator attendance overview."""
    attendance_records = get_all_attendance_admin(limit=1000)
    return render_template('admin/attendance.html', attendance_records=attendance_records)


# Error handlers
@views_bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@views_bp.app_errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

