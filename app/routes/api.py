from flask import Blueprint, request, jsonify
from app.utils.helpers import base64_to_cv2
from app.services.face_service import get_face_embedding, recognize_user, check_duplicate_face
from app.models.db import add_user, mark_attendance, get_attendance_records, get_all_users
import traceback

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/register-user', methods=['POST'])
def register():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'message': 'Invalid data provided.'}), 400
            
        name = data.get('name', '').strip()
        image_b64 = data.get('image', '')
        
        if not name or not image_b64:
            return jsonify({'success': False, 'message': 'Name and image are required.'}), 400
            
        img = base64_to_cv2(image_b64)
        if img is None:
             return jsonify({'success': False, 'message': 'Invalid image format.'}), 400
             
        embedding, err = get_face_embedding(img)
        if err:
            return jsonify({'success': False, 'message': err}), 400
            
        # Check duplicate
        is_dup, dup_name = check_duplicate_face(embedding)
        if is_dup:
            return jsonify({'success': False, 'message': f'Face already registered under name: {dup_name}'}), 400
            
        # Save
        add_user(name, embedding)
        return jsonify({'success': True, 'message': f"User '{name}' registered successfully."})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/recognize-face', methods=['POST'])
def recognize():
    try:
        data = request.json
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
            
        user_id, name = recognize_user(embedding)
        
        if user_id:
            marked = mark_attendance(user_id)
            if marked:
                return jsonify({'success': True, 'found': True, 'name': name, 'message': f'{name} marked present.'})
            else:
                return jsonify({'success': True, 'found': True, 'name': name, 'message': f'{name} already marked today.'})
        else:
            return jsonify({'success': True, 'found': False, 'message': 'Unknown face.'})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@api_bp.route('/attendance', methods=['GET'])
def attendance():
    records = get_attendance_records()
    res = [{'name': r['name'], 'date': r['date'], 'time': r['time']} for r in records]
    return jsonify({'success': True, 'data': res})

@api_bp.route('/users', methods=['GET'])
def get_users():
    users = get_all_users()
    res = [{'id': u['id'], 'name': u['name']} for u in users]
    return jsonify({'success': True, 'data': res})
