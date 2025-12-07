import face_recognition
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from database.db_manager import DatabaseManager

class FaceRecognizer:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.known_encodings = []
        self.known_employees = []
        self.recognition_threshold = Config.RECOGNITION_THRESHOLD
        print("✓ Face Recognizer initialized")
        
    def load_encodings_from_db(self):
        """Load all face encodings from database into memory"""
        print("Loading face encodings from database...")
        start_time = time.time()
        
        encodings_data = self.db_manager.get_face_encodings()
        
        self.known_encodings = []
        self.known_employees = []
        
        for data in encodings_data:
            self.known_encodings.append(data['face_encoding'])
            self.known_employees.append({
                'employee_id': data['employee_id'],
                'employee_code': data['employee_code'],
                'full_name': data['full_name'],
                'encoding_id': data['encoding_id']
            })
        
        elapsed = time.time() - start_time
        print(f"✓ Loaded {len(self.known_encodings)} face encodings in {elapsed:.2f}s")
        
    def detect_faces(self, image: np.ndarray) -> List[Tuple[np.ndarray, Tuple]]:
        """
        Detect faces in image and return encodings with locations
        Returns: List of (encoding, face_location) tuples
        """
        # Convert BGR to RGB (OpenCV uses BGR, face_recognition uses RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Find all face locations and encodings
        face_locations = face_recognition.face_locations(rgb_image, model='hog')
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        return list(zip(face_encodings, face_locations))
    
    def recognize_face(self, face_encoding: np.ndarray) -> Tuple[Optional[Dict], float]:
        """
        Recognize a face encoding against known encodings
        Returns: (employee_info, confidence) or (None, 0.0) if not recognized
        """
        if len(self.known_encodings) == 0:
            return None, 0.0
        
        # Compare face encoding with all known encodings
        face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
        
        # Find the best match
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        # Convert distance to confidence (0-1, where 1 is perfect match)
        confidence = 1 - best_distance
        
        # Check if confidence meets threshold
        if confidence >= self.recognition_threshold:
            return self.known_employees[best_match_index], confidence
        
        return None, confidence
    
    def process_frame(self, frame: np.ndarray) -> List[Dict]:
        """
        Process a frame and return all detected and recognized faces
        Returns: List of dicts with face info, location, and recognition results
        """
        results = []
        
        # Detect faces
        faces = self.detect_faces(frame)
        
        for face_encoding, face_location in faces:
            # Recognize face
            employee_info, confidence = self.recognize_face(face_encoding)
            
            result = {
                'face_location': face_location,
                'recognized': employee_info is not None,
                'employee_info': employee_info,
                'confidence': confidence
            }
            
            results.append(result)
        
        return results
    
    def draw_results(self, frame: np.ndarray, results: List[Dict]) -> np.ndarray:
        """
        Draw bounding boxes and labels on frame
        """
        output_frame = frame.copy()
        
        for result in results:
            top, right, bottom, left = result['face_location']
            
            # Choose color based on recognition status
            if result['recognized']:
                color = (0, 255, 0)  # Green for recognized
                employee_info = result['employee_info']
                label = f"{employee_info['full_name']} ({result['confidence']:.2f})"
            else:
                color = (0, 0, 255)  # Red for unknown
                label = f"Unknown ({result['confidence']:.2f})"
            
            # Draw rectangle
            cv2.rectangle(output_frame, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            cv2.rectangle(output_frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Draw label text
            cv2.putText(output_frame, label, (left + 6, bottom - 6),
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
        
        return output_frame
    
    def encode_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Generate face encoding from an image containing a single face
        Returns: encoding or None if no face or multiple faces found
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_image)
        
        if len(face_locations) == 0:
            print("✗ No face detected in image")
            return None
        
        if len(face_locations) > 1:
            print(f"✗ Multiple faces detected ({len(face_locations)}). Please use image with single face.")
            return None
        
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        return face_encodings[0] if len(face_encodings) > 0 else None
    
    def calculate_image_quality(self, image: np.ndarray, face_location: Tuple) -> float:
        """
        Calculate quality score for face image based on various factors
        Returns: quality score between 0 and 1
        """
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        
        # Calculate face size (larger is better, up to a point)
        face_width = right - left
        face_height = bottom - top
        face_area = face_width * face_height
        
        # Normalize by image size
        image_area = image.shape[0] * image.shape[1]
        size_score = min(face_area / (image_area * 0.3), 1.0)
        
        # Calculate sharpness using Laplacian variance
        gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 500, 1.0)
        
        # Calculate brightness
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 127) / 127
        
        # Combined score
        quality_score = (size_score * 0.4 + sharpness_score * 0.4 + brightness_score * 0.2)
        
        return quality_score
    
    def update_threshold(self, new_threshold: float):
        """Update recognition threshold"""
        if 0 <= new_threshold <= 1:
            self.recognition_threshold = new_threshold
            print(f"✓ Recognition threshold updated to {new_threshold}")
        else:
            print("✗ Threshold must be between 0 and 1")
