from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    return render_template('index.html')

@views_bp.route('/register')
def register():
    return render_template('register.html')

@views_bp.route('/camera')
def camera():
    return render_template('camera.html')

@views_bp.route('/report')
def report():
    return render_template('report.html')
