📄 Software Requirements Specification (SRS)

Face Recognition Attendance System

⸻

1. Introduction

1.1 Purpose

The purpose of this document is to describe the requirements of the Face Recognition Attendance System, a web-based application that uses computer vision and deep learning to automatically mark attendance based on facial recognition.

The system eliminates the need for manual attendance and reduces proxy attendance using real-time face detection and recognition.

⸻

1.2 Scope

The system will:
	•	Capture face images using a webcam
	•	Recognize registered faces using FaceNet embeddings
	•	Automatically mark attendance
	•	Store attendance records in a database
	•	Provide a web interface for admin and users

Technologies used:
	•	Backend: Python (Flask)
	•	Face Processing: OpenCV + FaceNet
	•	Frontend: HTML, CSS, JavaScript
	•	Database: PostgrSQL

⸻

1.3 Definitions & Abbreviations

Term	Description
OpenCV	Computer vision library for image processing
FaceNet	Deep learning model for face embeddings
Flask	Python web framework
Embedding	Numerical representation of a face
Admin	Person managing the system
User	Person whose attendance is marked


⸻

2. Overall Description

2.1 Product Perspective

This system is a standalone web application that uses:
	•	Webcam for image input
	•	Server for face recognition
	•	Database for storing users and attendance

⸻

2.2 Product Functions
	•	User registration with face capture
	•	Face detection from live video
	•	Face recognition using FaceNet
	•	Attendance marking
	•	Attendance report generation
	•	Admin dashboard

⸻

2.3 User Classes

User Type	Description
Admin	Registers users, views attendance
Student/User	Gets attendance marked automatically


⸻

2.4 Operating Environment
	•	OS: Windows/Linux/Mac
	•	Browser: Chrome/Edge/Firefox
	•	Python 3.x
	•	Webcam

⸻

2.5 Constraints
	•	Requires stable lighting for better accuracy
	•	Requires webcam
	•	Face recognition depends on trained model
	•	Internet only needed for deployment

⸻

3. Functional Requirements

3.1 User Registration
	•	The system shall allow admin to register a new user
	•	The system shall capture multiple face images
	•	The system shall generate FaceNet embeddings
	•	The system shall store user details

⸻

3.2 Face Detection
	•	The system shall detect faces using OpenCV
	•	The system shall crop face region
	•	The system shall preprocess images

⸻

3.3 Face Recognition
	•	The system shall compare face embeddings
	•	The system shall recognize registered users
	•	The system shall reject unknown faces

⸻

3.4 Attendance Marking
	•	The system shall mark attendance automatically
	•	The system shall record date and time
	•	The system shall prevent duplicate entries

⸻

3.5 Admin Dashboard
	•	The system shall allow admin to view attendance
	•	The system shall allow filtering by date/user
	•	The system shall allow export of reports

⸻

4. Non-Functional Requirements

4.1 Performance
	•	Face recognition should take less than 2 seconds
	•	System should handle multiple users

⸻

4.2 Security
	•	Only admin can register users
	•	Attendance data shall be stored securely
	•	Unknown faces shall not be marked

⸻

4.3 Usability
	•	UI shall be simple and responsive
	•	System shall be easy to use

⸻

4.4 Reliability
	•	System shall work continuously without crash
	•	Attendance data shall not be lost

⸻

4.5 Maintainability
	•	Code shall be modular
	•	Model can be updated easily

⸻

5. System Architecture

5.1 Architecture Overview
	1.	Webcam captures image
	2.	OpenCV detects face
	3.	FaceNet extracts embeddings
	4.	Flask backend processes request
	5.	Database stores attendance
	6.	Frontend displays result

⸻

5.2 Modules
	•	Face Capture Module
	•	Face Recognition Module
	•	Attendance Module
	•	Database Module
	•	Web Interface Module

⸻

6. Data Requirements

6.1 Database Tables

User Table
	•	user_id
	•	name
	•	face_embedding

Attendance Table
	•	attendance_id
	•	user_id
	•	date
	•	time

⸻

7. External Interface Requirements

7.1 User Interface
	•	Login page
	•	Registration page
	•	Camera page
	•	Attendance report page

⸻

7.2 Hardware Interface
	•	Webcam

⸻

7.3 Software Interface
	•	Python
	•	OpenCV
	•	FaceNet
	•	Flask
	•	Browser

⸻

8. Future Enhancements
	•	Cloud deployment
	•	Mobile app integration
	•	Mask detection
	•	Emotion detection
	•	Multi-camera support

⸻

9. Conclusion

This system provides an automated and accurate attendance management solution using facial recognition. It reduces human error and prevents proxy attendance while ensuring fast and reliable performance.
