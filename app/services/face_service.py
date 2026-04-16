import cv2
import numpy as np
import json
import importlib
from app.models.db import get_all_users
import logging

logger = logging.getLogger(__name__)

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

face_recognition = None
FACE_RECOGNITION_LOADED = False
FACE_RECOGNITION_ERROR = None


def _load_face_recognition():
    """Load face_recognition safely even if its dependencies are partially installed."""
    global face_recognition, FACE_RECOGNITION_LOADED, FACE_RECOGNITION_ERROR

    if face_recognition is not None or FACE_RECOGNITION_ERROR is not None:
        return FACE_RECOGNITION_LOADED

    try:
        face_recognition = importlib.import_module('face_recognition')
        FACE_RECOGNITION_LOADED = True
        return True
    except BaseException as e:
        FACE_RECOGNITION_LOADED = False
        FACE_RECOGNITION_ERROR = str(e).strip() or repr(e) or e.__class__.__name__
        logger.warning(f"face_recognition not available: {FACE_RECOGNITION_ERROR}")
        return False


_load_face_recognition()

def get_face_embedding(img, model='hog'):
    """
    Takes a cv2 BGR image.
    Returns the first matching face encoding, or None if no face is found.
    Uses HOG model (faster) by default, can use 'cnn' for better accuracy (slower)
    """
    if not _load_face_recognition():
        return None, "Face recognition system is unavailable. Please verify the face-recognition dependencies are installed."
    
    try:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Resize aggressively to keep registration responsive on CPU-only systems.
        height, width = img_rgb.shape[:2]
        max_width = 640
        if width > max_width:
            scale = max_width / width
            img_rgb = cv2.resize(img_rgb, (max_width, int(height * scale)))
        
        # Detect faces using HOG (fast) model
        face_locations = face_recognition.face_locations(img_rgb, model=model)
        
        if len(face_locations) == 0:
            return None, "No face detected. Please look directly at the camera and ensure good lighting."
            
        if len(face_locations) > 1:
            logger.warning(f"Multiple faces detected: {len(face_locations)}")
            return None, f"Multiple faces detected ({len(face_locations)}). Please ensure only 1 person is in frame."
        
        # Get face encoding for the first (and only) face
        encodings = face_recognition.face_encodings(img_rgb, face_locations, num_jitters=1)
        
        if not encodings:
            return None, "Could not extract face features. Please adjust lighting and position."
            
        embedding = encodings[0]
        return embedding, None
        
    except Exception as e:
        logger.error(f"Error in get_face_embedding: {str(e)}")
        return None, f"Face detection error: {str(e)}"

def recognize_user(embedding, tolerance=0.6):
    """
    Compares given embedding against all known users in DB.
    Returns user_id, user_name or None, None
    
    Tolerance levels:
    - 0.5: Strict (fewer false positives)
    - 0.6: Default (good balance)
    - 0.7: Loose (more matches, some false positives)
    """
    if not _load_face_recognition():
        logger.error("Face recognition not loaded")
        return None, None
    
    try:
        users = get_all_users()
        if not users:
            logger.warning("No users in database")
            return None, None
            
        known_encodings = []
        user_data = []
        
        for u in users:
            if not u.get('embedding'):
                continue
            try:
                # Reconstruct numpy array from stored embedding
                if isinstance(u['embedding'], bytes):
                    # If stored as binary (BLOB), convert back
                    embedding_array = np.frombuffer(u['embedding'], dtype=np.float64)
                else:
                    # If stored as JSON string
                    enc_list = json.loads(u['embedding'])
                    embedding_array = np.array(enc_list)
                
                known_encodings.append(embedding_array)
                user_data.append(u)
            except Exception as e:
                logger.warning(f"Could not load embedding for user {u.get('id')}: {e}")
                continue
        
        if not known_encodings:
            logger.warning("No valid embeddings found in database")
            return None, None
        
        # Compare embeddings
        matches = face_recognition.compare_faces(known_encodings, embedding, tolerance=tolerance)
        face_distances = face_recognition.face_distance(known_encodings, embedding)
        
        logger.info(f"Face distance results: {face_distances}")
        
        # Find best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        logger.info(f"Best match distance: {best_distance}, matches: {matches[best_match_index]}")
        
        if matches[best_match_index] and best_distance < tolerance:
            matched_user = user_data[best_match_index]
            logger.info(f"Face recognized: {matched_user.get('username')} (distance: {best_distance:.4f})")
            return matched_user['id'], matched_user.get('full_name') or matched_user.get('username')
        else:
            logger.info(f"No matching face found (best distance: {best_distance:.4f})")
            
        return None, None
        
    except Exception as e:
        logger.error(f"Error in recognize_user: {str(e)}")
        return None, None
    
def check_duplicate_face(embedding, tolerance=0.6):
    """
    Check if face already exists in the database during registration.
    Uses stricter tolerance to prevent duplicates.
    """
    strict_tolerance = tolerance - 0.1  # Use stricter tolerance for registration
    user_id, name = recognize_user(embedding, tolerance=strict_tolerance)
    if user_id:
        return True, name
    return False, None
