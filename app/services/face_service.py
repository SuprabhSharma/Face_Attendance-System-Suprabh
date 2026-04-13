import cv2
import face_recognition
import numpy as np
import json
from app.models.db import get_all_users

def get_face_embedding(img):
    """
    Takes a cv2 BGR image.
    Returns the first matching face encoding, or None if no face is found.
    """
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)
    
    if len(face_locations) == 0:
        return None, "Error: No face detected. Please look directly at the camera."
        
    if len(face_locations) > 1:
        return None, "Error: Multiple faces detected. Please ensure only 1 person is in frame."
        
    embedding = face_recognition.face_encodings(img_rgb, face_locations)[0]
    return embedding, None

def recognize_user(embedding, tolerance=0.5):
    """
    Compares given embedding against all known users in DB.
    Returns user_id, user_name or None, None
    """
    users = get_all_users()
    if not users:
        return None, None
        
    known_encodings = []
    user_data = []
    
    for u in users:
        # Re-construct numpy array from JSON
        enc_list = json.loads(u['embedding'])
        known_encodings.append(np.array(enc_list))
        user_data.append(u)
        
    # Compare
    matches = face_recognition.compare_faces(known_encodings, embedding, tolerance=tolerance)
    faceDis = face_recognition.face_distance(known_encodings, embedding)
    
    if len(faceDis) > 0:
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            matched_user = user_data[matchIndex]
            return matched_user['id'], matched_user['name']
            
    return None, None
    
def check_duplicate_face(embedding, tolerance=0.5):
    """
    Check if face already exists in the database.
    """
    user_id, name = recognize_user(embedding, tolerance)
    if user_id:
        return True, name
    return False, None
