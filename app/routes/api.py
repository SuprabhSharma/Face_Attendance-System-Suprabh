from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import traceback
import logging
import json
from datetime import datetime, timezone

api_bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger('app')

from app.models.db import (
    get_user_by_id, get_attendance_by_user, mark_attendance, get_all_users
)
from app.services.email_service import EmailService

email_service = EmailService()

# Lazy loading helper for face recognition
def get_face_recognition_modules():
    """Lazy load face recognition modules"""
    try:
        from app.utils.helpers import base64_to_cv2
        from app.services.face_service import get_face_embedding, recognize_user, check_duplicate_face
        return (base64_to_cv2, get_face_embedding, recognize_user, check_duplicate_face, True)
    except BaseException as e:
        logger.warning(f"Face recognition not available: {e}")
        return (None, None, None, None, False)

@api_bp.route('/register-user', methods=['POST'])
@login_required
def register():
    """Register face for current authenticated user"""
    try:
        logger.info(f"Face registration request started for user_id={current_user.id}")
        base64_to_cv2, get_face_embedding, recognize_user_fn, check_duplicate_face, available = get_face_recognition_modules()
        
        if not available:
            return jsonify({'success': False, 'message': 'Face recognition not available yet. Please try again later.'}), 503
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data provided.'}), 400
            
        image_b64 = data.get('image', '')
        
        if not image_b64:
            return jsonify({'success': False, 'message': 'Image is required.'}), 400

        logger.info(f"Received registration image payload for user_id={current_user.id}, size={len(image_b64)} chars")
            
        img = base64_to_cv2(image_b64)
        if img is None:
            return jsonify({'success': False, 'message': 'Invalid image format.'}), 400

        logger.info(f"Decoded registration image for user_id={current_user.id}, shape={img.shape}")
            
        embedding, err = get_face_embedding(img)
        if err:
            logger.warning(f"Face embedding error during registration: {err}")
            return jsonify({'success': False, 'message': err}), 400
            
        if embedding is None:
            return jsonify({'success': False, 'message': 'Failed to extract face features. Try different lighting or angle.'}), 400
            
        # Check duplicate face
        is_dup, dup_name = check_duplicate_face(embedding)
        if is_dup:
            logger.warning(f"Duplicate face attempted for registration: {dup_name}")
            return jsonify({'success': False, 'message': f'This face is already registered to {dup_name}.'}), 400
            
        # Get current user data
        user_data = get_user_by_id(current_user.id)
        if not user_data:
            return jsonify({'success': False, 'message': 'User not found.'}), 404
        
        # Save face embedding for current user (convert to bytes for BLOB storage)
        try:
            from app.models.db import get_db_connection
            conn = get_db_connection()
            c = conn.cursor()
            # Store as JSON string for compatibility
            embedding_json = json.dumps(embedding.tolist())
            c.execute('''
                UPDATE users SET embedding = ? WHERE id = ?
            ''', (embedding_json, current_user.id))
            conn.commit()
            conn.close()
            logger.info(f"Face registered successfully for user {current_user.username}")
        except Exception as db_err:
            logger.error(f"Database error saving embedding: {str(db_err)}")
            return jsonify({'success': False, 'message': 'Failed to save face data. Please try again.'}), 500
        
        return jsonify({
            'success': True, 
            'message': f"Face registered successfully for {user_data['full_name']}! You can now use face recognition to mark attendance."
        })
        
    except Exception as e:
        logger.error(f"Error registering face: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Registration error: {str(e)}'}), 500

@api_bp.route('/recognize-face', methods=['POST'])
def recognize():
    """Recognize face and mark attendance"""
    try:
        recognition_time = datetime.now(timezone.utc)
        base64_to_cv2, get_face_embedding, recognize_user_fn, check_duplicate_face, available = get_face_recognition_modules()
        
        if not available:
            return jsonify({'success': False, 'message': 'Face recognition not available. Please contact administrator.'}), 503
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data provided.'}), 400
            
        image_b64 = data.get('image', '')
        
        if not image_b64:
            return jsonify({'success': False, 'message': 'Image is required.'}), 400
            
        img = base64_to_cv2(image_b64)
        if img is None:
            return jsonify({'success': False, 'message': 'Invalid image format.'}), 400
            
        embedding, err = get_face_embedding(img)
        if err:
            return jsonify({'success': False, 'message': err}), 400
            
        # Recognize user from face
        user_id, name = recognize_user_fn(embedding)
        
        if user_id:
            # Get user data
            user_data = get_user_by_id(user_id)
            if not user_data:
                return jsonify({'success': True, 'found': False, 'message': 'User data not found.'}), 200
            
            # Mark attendance
            marked, status = mark_attendance(user_id, recognition_time)
            
            if marked:
                logger.info(f"Attendance marked for user {user_data['username']} with status: {status}")
                
                # Send email notification
                try:
                    attendance_time = recognition_time.strftime('%Y-%m-%d %H:%M:%S')
                    recent_records = get_attendance_by_user(user_id, limit=10)
                    
                    email_service.send_attendance_marked_email(
                        user_id=user_id,
                        user_email=user_data['email'],
                        user_name=user_data['full_name'],
                        attendance_time=attendance_time,
                        attendance_date=recognition_time.strftime('%Y-%m-%d'),
                        user_data={
                            'name': user_data['full_name'],
                            'email': user_data['email'],
                            'recent_records': recent_records
                        }
                    )
                    logger.info(f"Attendance email sent to {user_data['email']}")
                except Exception as email_err:
                    logger.error(f"Failed to send attendance email: {str(email_err)}")
                    # Don't fail the request if email fails
                
                return jsonify({
                    'success': True, 
                    'found': True, 
                    'user_id': user_id,
                    'user_name': user_data['full_name'],
                    'status': status,
                    'marked_at': recognition_time.isoformat(),
                    'message': f"{user_data['full_name']} marked {status} at {recognition_time.strftime('%Y-%m-%d %H:%M:%S UTC')}."
                })
            else:
                next_allowed_at = status
                duplicate_message = f"{user_data['full_name']} present already marked. Next attendance allowed after {next_allowed_at}."
                return jsonify({
                    'success': True, 
                    'found': True, 
                    'user_id': user_id,
                    'user_name': user_data['full_name'],
                    'status': 'duplicate',
                    'marked_at': recognition_time.isoformat(),
                    'next_allowed_at': next_allowed_at,
                    'message': duplicate_message
                })
        else:
            logger.warning("Unknown face recognition attempt")
            return jsonify({'success': True, 'found': False, 'message': 'Unknown face. Please register first.'})
            
    except Exception as e:
        logger.error(f"Error in face recognition: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/attendance', methods=['GET'])
@login_required
def attendance():
    """Get attendance records for current user"""
    try:
        records = get_attendance_by_user(current_user.id, limit=50)
        user_data = get_user_by_id(current_user.id)
        display_name = None
        if user_data:
            display_name = user_data.get('full_name') or user_data.get('username')

        res = [{
            'date': r['date'],
            'name': display_name,
            'time': r['time_in'],
            'time_in': r['time_in'],
            'time_out': r.get('time_out'),
            'marked_at': f"{r['date']}T{r['time_in']}+00:00" if r.get('time_in') else None,
            'status': r.get('status', 'present')
        } for r in records]
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        logger.error(f"Error retrieving attendance: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get all registered users (public endpoint)"""
    try:
        users = get_all_users()
        res = [{'id': u['id'], 'name': u['full_name'] if 'full_name' in u else u['name']} for u in users]
        return jsonify({'success': True, 'data': res})
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500
