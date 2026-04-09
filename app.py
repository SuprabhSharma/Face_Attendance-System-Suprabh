from flask import Flask, render_template, request
import cv2
import os
import numpy as np
import face_recognition
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Folder for storing faces
path = 'faces'
images = []
names = []

# Make sure 'faces' folder exists
if not os.path.exists(path):
    os.makedirs(path)

# Load images
def load_images():
    images.clear()
    names.clear()
    
    for file in os.listdir(path):
        img = cv2.imread(f'{path}/{file}')
        if img is not None:
            images.append(img)
            names.append(os.path.splitext(file)[0])

# Encode faces
def encode_faces(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        # Safety check: agar photo me face detect na ho toh crash hone se bachaye
        if len(encodings) > 0:
            encodeList.append(encodings[0])
    return encodeList


@app.route('/')
def index():
    return "Face Recognition Attendance System"


# Register Face
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    
    # 1. Pehle se saved faces ko load karein (Duplicate check ke liye)
    load_images()
    encodeListKnown = encode_faces(images) if len(images) > 0 else []

    cap = cv2.VideoCapture(0)
    msg = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            msg = "Error: Camera se frame read nahi ho paaya."
            break
            
        cv2.imshow("Register Face", frame)

        # Jab user 'q' press kare
        if cv2.waitKey(1) & 0xFF == ord('q'):
            
            # 2. Capture kiye gaye frame me face dhoondein
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(img_rgb)
            
            # Agar koi face nahi mila
            if len(face_locations) == 0:
                msg = "Error: Koi face detect nahi hua! Camera ke samne theek se dekhein."
                break
                
            # Agar 1 se zyada face mil gaye
            if len(face_locations) > 1:
                msg = "Error: Ek se zyada faces detect hue! Registration ke time frame me sirf 1 person hona chahiye."
                break

            # 3. Naye face ki encoding nikalein
            new_encode = face_recognition.face_encodings(img_rgb, face_locations)[0]
            
            # 4. Duplicate check karein
            duplicate_found = False
            if len(encodeListKnown) > 0:
                # Tolerance 0.5 rakha hai (0.6 default hota hai), taaki zyada strictly match kare
                matches = face_recognition.compare_faces(encodeListKnown, new_encode, tolerance=0.5)
                faceDis = face_recognition.face_distance(encodeListKnown, new_encode)
                
                if len(faceDis) > 0:
                    matchIndex = np.argmin(faceDis)
                    
                    # Agar match mil gaya (True)
                    if matches[matchIndex]:
                        existing_name = names[matchIndex].upper()
                        duplicate_found = True
                        msg = f"Registration Failed! This face is already registered under the name '{existing_name}'."
                        break

            # 5. Agar duplicate nahi mila, tabhi photo save karein
            if not duplicate_found:
                cv2.imwrite(f'{path}/{name}.jpg', frame)
                msg = f"Success! '{name}' Registered Successfully"
                break

    cap.release()
    cv2.destroyAllWindows()

    return msg


# Mark Attendance
@app.route('/attendance')
def attendance():
    load_images()
    
    if len(images) == 0:
        return "Error: No such registered face found! Register the face first before marking attendance."
        
    encodeListKnown = encode_faces(images)
    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        if not success:
            break
            
        imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    matched_name = names[matchIndex].upper()
                    mark_attendance(matched_name)
                    
                    cap.release()
                    cv2.destroyAllWindows()
                    return f"{matched_name} Attendance Marked Successfully!"

        cv2.imshow("Attendance", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return "Attendance Closed Without Marking."


# Save attendance
def mark_attendance(name):
    # Check if file exists, if not create with headers
    if not os.path.isfile('attendance.csv'):
        with open('attendance.csv', 'w') as f:
            f.write('Name,Date,Time\n')

    with open('attendance.csv','a') as f:
        now = datetime.now()
        time = now.strftime('%H:%M:%S')
        date = now.strftime('%Y-%m-%d')
        f.write(f'{name},{date},{time}\n')


if __name__ == "__main__":
    app.run(debug=True)