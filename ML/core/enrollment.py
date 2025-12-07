import cv2
import os
from datetime import datetime
from typing import Optional, List
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from database.db_manager import DatabaseManager
from models.face_recognizer import FaceRecognizer
from core.camera import CameraInterface

class FaceEnrollment:
    def __init__(self, db_manager: DatabaseManager, face_recognizer: FaceRecognizer):
        self.db_manager = db_manager
        self.face_recognizer = face_recognizer
        self.camera = CameraInterface()
        
        # Ensure directories exist
        os.makedirs(Config.EMPLOYEE_IMAGES_PATH, exist_ok=True)
        
        print("✓ Face Enrollment module initialized")
    
    def enroll_employee(self, employee_code: str, full_name: str, 
                       email: str = None, phone: str = None,
                       department: str = None, position: str = None,
                       num_photos: int = 3) -> bool:
        """
        Enroll a new employee with face recognition
        Captures multiple photos for better accuracy
        """
        print(f"\n{'='*50}")
        print(f"ENROLLING EMPLOYEE: {full_name} ({employee_code})")
        print(f"{'='*50}\n")
        
        # Check if employee already exists
        existing = self.db_manager.get_employee(employee_code=employee_code)
        if existing:
            print(f"✗ Employee with code {employee_code} already exists!")
            return False
        
        # Add employee to database
        try:
            employee_id = self.db_manager.add_employee(
                employee_code, full_name, email, phone, department, position
            )
            print(f"✓ Employee added to database (ID: {employee_id})")
        except Exception as e:
            print(f"✗ Failed to add employee: {e}")
            return False
        
        # Create employee image directory
        employee_dir = os.path.join(Config.EMPLOYEE_IMAGES_PATH, employee_code)
        os.makedirs(employee_dir, exist_ok=True)
        
        # Capture and process photos
        encodings_saved = 0
        
        for i in range(num_photos):
            print(f"\n--- Capturing photo {i+1}/{num_photos} ---")
            print("Position your face clearly in the camera")
            print("Try different angles for better accuracy")
            
            # Capture photo
            frame = self.camera.capture_photo(countdown=3)
            
            if frame is None:
                print("✗ Photo capture failed")
                continue
            
            # Generate face encoding
            face_encoding = self.face_recognizer.encode_face(frame)
            
            if face_encoding is None:
                print("✗ Could not detect face in photo. Retrying...")
                i -= 1  # Retry this photo
                continue
            
            # Calculate quality score
            face_locations = self.face_recognizer.detect_faces(frame)
            if len(face_locations) > 0:
                _, face_location = face_locations[0]
                quality_score = self.face_recognizer.calculate_image_quality(frame, face_location)
                print(f"  Image quality: {quality_score:.2f}")
            else:
                quality_score = 0.5
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{employee_code}_{timestamp}_{i+1}.jpg"
            image_path = os.path.join(employee_dir, image_filename)
            cv2.imwrite(image_path, frame)
            print(f"✓ Image saved: {image_filename}")
            
            # Save encoding to database
            try:
                relative_path = os.path.join('employees', employee_code, image_filename)
                encoding_id = self.db_manager.save_face_encoding(
                    employee_id, face_encoding, relative_path, quality_score, 
                    is_primary=(i == 0)  # First photo is primary
                )
                print(f"✓ Face encoding saved (ID: {encoding_id})")
                encodings_saved += 1
            except Exception as e:
                print(f"✗ Failed to save encoding: {e}")
        
        # Check if enrollment successful
        if encodings_saved > 0:
            print(f"\n{'='*50}")
            print(f"✓ ENROLLMENT SUCCESSFUL!")
            print(f"  Employee: {full_name}")
            print(f"  Photos captured: {encodings_saved}/{num_photos}")
            print(f"{'='*50}\n")
            
            # Reload encodings
            self.face_recognizer.load_encodings_from_db()
            
            return True
        else:
            print(f"\n{'='*50}")
            print(f"✗ ENROLLMENT FAILED!")
            print(f"  No valid face encodings captured")
            print(f"{'='*50}\n")
            
            # Remove employee from database
            self.db_manager.update_employee_status(employee_id, 'inactive')
            
            return False
    
    def add_face_photo(self, employee_code: str) -> bool:
        """
        Add additional face photo for existing employee
        """
        # Get employee
        employee = self.db_manager.get_employee(employee_code=employee_code)
        if not employee:
            print(f"✗ Employee {employee_code} not found")
            return False
        
        employee_id = employee['employee_id']
        
        # Check current encoding count
        current_count = self.db_manager.get_encoding_count(employee_id)
        
        if current_count >= Config.MAX_FACES_PER_EMPLOYEE:
            print(f"✗ Maximum face encodings ({Config.MAX_FACES_PER_EMPLOYEE}) reached for this employee")
            return False
        
        print(f"\nAdding face photo for: {employee['full_name']}")
        print(f"Current photos: {current_count}/{Config.MAX_FACES_PER_EMPLOYEE}")
        
        # Capture photo
        frame = self.camera.capture_photo(countdown=3)
        
        if frame is None:
            print("✗ Photo capture failed")
            return False
        
        # Generate face encoding
        face_encoding = self.face_recognizer.encode_face(frame)
        
        if face_encoding is None:
            return False
        
        # Calculate quality
        face_locations = self.face_recognizer.detect_faces(frame)
        quality_score = 0.5
        if len(face_locations) > 0:
            _, face_location = face_locations[0]
            quality_score = self.face_recognizer.calculate_image_quality(frame, face_location)
        
        # Save image
        employee_dir = os.path.join(Config.EMPLOYEE_IMAGES_PATH, employee_code)
        os.makedirs(employee_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{employee_code}_{timestamp}_add.jpg"
        image_path = os.path.join(employee_dir, image_filename)
        cv2.imwrite(image_path, frame)
        
        # Save encoding
        try:
            relative_path = os.path.join('employees', employee_code, image_filename)
            encoding_id = self.db_manager.save_face_encoding(
                employee_id, face_encoding, relative_path, quality_score
            )
            print(f"✓ Face photo added successfully (ID: {encoding_id})")
            
            # Reload encodings
            self.face_recognizer.load_encodings_from_db()
            
            return True
        except Exception as e:
            print(f"✗ Failed to save encoding: {e}")
            return False
    
    def list_employees(self):
        """List all enrolled employees"""
        employees = self.db_manager.get_all_employees()
        
        if not employees:
            print("No employees enrolled yet")
            return
        
        print(f"\n{'='*70}")
        print(f"{'Code':<15} {'Name':<25} {'Department':<20} {'Photos':<10}")
        print(f"{'='*70}")
        
        for emp in employees:
            count = self.db_manager.get_encoding_count(emp['employee_id'])
            print(f"{emp['employee_code']:<15} {emp['full_name']:<25} "
                  f"{emp['department'] or '-':<20} {count:<10}")
        
        print(f"{'='*70}\n")
    
    def cleanup(self):
        """Cleanup camera resources"""
        self.camera.stop()


class EnrollmentSystem:
    """
    Simplified enrollment system for API use
    Processes images from file paths instead of camera
    """
    def __init__(self, db_manager: DatabaseManager, face_recognizer: FaceRecognizer):
        self.db_manager = db_manager
        self.face_recognizer = face_recognizer
        # Use absolute path relative to ML directory
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.employee_images_path = os.path.join(self.base_path, 'data', 'images', 'employees')
        os.makedirs(self.employee_images_path, exist_ok=True)
    
    def enroll_from_images(self, employee_code: str, full_name: str, 
                          image_paths: List[str],
                          email: str = None, phone: str = None,
                          department: str = None, position: str = None):
        """
        Enroll employee from uploaded image files
        Returns: (success: bool, employee_id: int, message: str)
        """
        try:
            # Check if employee already exists
            existing = self.db_manager.get_employee(employee_code=employee_code)
            if existing:
                return False, None, f"Employee with code {employee_code} already exists"
            
            # Add employee to database
            employee_id = self.db_manager.add_employee(
                employee_code, full_name, email, phone, department, position
            )
            
            # Create employee directory
            employee_dir = os.path.join(self.employee_images_path, employee_code)
            os.makedirs(employee_dir, exist_ok=True)
            
            # Process each image
            success_count = 0
            for idx, image_path in enumerate(image_paths):
                frame = cv2.imread(image_path)
                if frame is None:
                    continue
                
                # Generate face encoding
                face_encoding = self.face_recognizer.encode_face(frame)
                if face_encoding is None:
                    continue
                
                # Calculate quality
                face_locations = self.face_recognizer.detect_faces(frame)
                quality_score = 0.5
                if len(face_locations) > 0:
                    _, face_location = face_locations[0]
                    quality_score = self.face_recognizer.calculate_image_quality(frame, face_location)
                
                # Save image with absolute path
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_filename = f"{employee_code}_{timestamp}_{idx}.jpg"
                save_path = os.path.join(employee_dir, image_filename)
                cv2.imwrite(save_path, frame)
                print(f"✓ Saved image: {save_path}")  # Debug log
                
                # Save encoding with relative path for database
                relative_path = os.path.join('employees', employee_code, image_filename)
                is_primary = (idx == 0)
                self.db_manager.save_face_encoding(
                    employee_id, face_encoding, relative_path, quality_score, is_primary
                )
                success_count += 1
            
            if success_count == 0:
                # Rollback - delete employee if no photos saved
                self.db_manager.connect()
                self.db_manager.cursor.execute(
                    "DELETE FROM employees WHERE employee_id = %s", (employee_id,)
                )
                self.db_manager.connection.commit()
                self.db_manager.close()
                return False, None, "No valid faces detected in uploaded images"
            
            # Reload encodings
            self.face_recognizer.load_encodings_from_db()
            
            return True, employee_id, f"Employee enrolled successfully with {success_count} photos"
            
        except Exception as e:
            return False, None, f"Enrollment failed: {str(e)}"
