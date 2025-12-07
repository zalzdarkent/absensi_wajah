import cv2
import os
from datetime import datetime, date
from typing import Optional
import time
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from database.db_manager import DatabaseManager
from models.face_recognizer import FaceRecognizer
from core.camera import CameraInterface

class AttendanceManager:
    def __init__(self, db_manager: DatabaseManager, face_recognizer: FaceRecognizer):
        self.db_manager = db_manager
        self.face_recognizer = face_recognizer
        self.camera = CameraInterface()
        
        # Ensure directories exist
        os.makedirs(Config.ATTENDANCE_IMAGES_PATH, exist_ok=True)
        
        print("✓ Attendance Manager initialized")
    
    def check_in_employee(self) -> bool:
        """
        Check in employee using face recognition
        """
        print(f"\n{'='*50}")
        print(f"CHECK-IN")
        print(f"{'='*50}\n")
        
        # Capture photo
        print("Position your face in front of the camera...")
        frame = self.camera.capture_photo(countdown=3)
        
        if frame is None:
            print("✗ Check-in cancelled")
            return False
        
        # Process frame and recognize face
        start_time = time.time()
        results = self.face_recognizer.process_frame(frame)
        processing_time = int((time.time() - start_time) * 1000)
        
        if len(results) == 0:
            print("✗ No face detected")
            self._log_recognition(None, "Unknown", 0.0, None, 'failed', processing_time)
            return False
        
        if len(results) > 1:
            print(f"✗ Multiple faces detected ({len(results)}). Please ensure only one person is visible.")
            self._log_recognition(None, "Multiple", 0.0, None, 'multiple_faces', processing_time)
            return False
        
        result = results[0]
        
        if not result['recognized']:
            print(f"✗ Face not recognized (confidence: {result['confidence']:.2f})")
            self._log_recognition(None, "Unknown", result['confidence'], None, 'unknown_face', processing_time)
            return False
        
        # Employee recognized
        employee_info = result['employee_info']
        confidence = result['confidence']
        
        print(f"\n✓ Recognized: {employee_info['full_name']}")
        print(f"  Confidence: {confidence:.2f}")
        
        # Save attendance image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"checkin_{employee_info['employee_code']}_{timestamp}.jpg"
        image_path = os.path.join(Config.ATTENDANCE_IMAGES_PATH, image_filename)
        
        # Draw result on frame before saving
        annotated_frame = self.face_recognizer.draw_results(frame, results)
        cv2.imwrite(image_path, annotated_frame)
        
        relative_path = os.path.join('attendance', image_filename)
        
        # Record check-in
        try:
            success, message = self.db_manager.check_in(
                employee_info['employee_id'], confidence, relative_path
            )
            
            if success:
                print(f"\n✓ {message}")
                print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
                self._log_recognition(employee_info['employee_id'], employee_info['full_name'], 
                                    confidence, relative_path, 'success', processing_time)
            else:
                print(f"\n✗ {message}")
            
            print(f"\n{'='*50}\n")
            return success
            
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False
    
    def check_out_employee(self) -> bool:
        """
        Check out employee using face recognition
        """
        print(f"\n{'='*50}")
        print(f"CHECK-OUT")
        print(f"{'='*50}\n")
        
        # Capture photo
        print("Position your face in front of the camera...")
        frame = self.camera.capture_photo(countdown=3)
        
        if frame is None:
            print("✗ Check-out cancelled")
            return False
        
        # Process frame and recognize face
        start_time = time.time()
        results = self.face_recognizer.process_frame(frame)
        processing_time = int((time.time() - start_time) * 1000)
        
        if len(results) == 0:
            print("✗ No face detected")
            return False
        
        if len(results) > 1:
            print(f"✗ Multiple faces detected ({len(results)}). Please ensure only one person is visible.")
            return False
        
        result = results[0]
        
        if not result['recognized']:
            print(f"✗ Face not recognized (confidence: {result['confidence']:.2f})")
            return False
        
        # Employee recognized
        employee_info = result['employee_info']
        confidence = result['confidence']
        
        print(f"\n✓ Recognized: {employee_info['full_name']}")
        print(f"  Confidence: {confidence:.2f}")
        
        # Save attendance image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"checkout_{employee_info['employee_code']}_{timestamp}.jpg"
        image_path = os.path.join(Config.ATTENDANCE_IMAGES_PATH, image_filename)
        
        annotated_frame = self.face_recognizer.draw_results(frame, results)
        cv2.imwrite(image_path, annotated_frame)
        
        relative_path = os.path.join('attendance', image_filename)
        
        # Record check-out
        try:
            success, message = self.db_manager.check_out(
                employee_info['employee_id'], confidence, relative_path
            )
            
            if success:
                print(f"\n✓ {message}")
                print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"\n✗ {message}")
            
            print(f"\n{'='*50}\n")
            return success
            
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False
    
    def live_recognition(self):
        """
        Live face recognition demo
        Shows camera feed with real-time recognition
        """
        print("\n{'='*50}")
        print("LIVE FACE RECOGNITION")
        print("Press 'q' to quit, 'i' to check-in, 'o' to check-out")
        print(f"{'='*50}\n")
        
        if not self.camera.start():
            return
        
        try:
            while True:
                frame = self.camera.read_frame()
                if frame is None:
                    break
                
                # Process frame
                results = self.face_recognizer.process_frame(frame)
                
                # Draw results
                display_frame = self.face_recognizer.draw_results(frame, results)
                
                # Add instructions
                cv2.putText(display_frame, "Press: 'i' check-in, 'o' check-out, 'q' quit", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Live Recognition', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('i'):
                    # Use current frame for check-in
                    if len(results) == 1 and results[0]['recognized']:
                        employee_info = results[0]['employee_info']
                        confidence = results[0]['confidence']
                        
                        # Save image and check-in
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_filename = f"checkin_{employee_info['employee_code']}_{timestamp}.jpg"
                        image_path = os.path.join(Config.ATTENDANCE_IMAGES_PATH, image_filename)
                        cv2.imwrite(image_path, display_frame)
                        
                        relative_path = os.path.join('attendance', image_filename)
                        success, message = self.db_manager.check_in(
                            employee_info['employee_id'], confidence, relative_path
                        )
                        print(f"Check-in: {message}")
                    else:
                        print("Cannot check-in: No face or multiple faces detected")
                        
                elif key == ord('o'):
                    # Use current frame for check-out
                    if len(results) == 1 and results[0]['recognized']:
                        employee_info = results[0]['employee_info']
                        confidence = results[0]['confidence']
                        
                        # Save image and check-out
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        image_filename = f"checkout_{employee_info['employee_code']}_{timestamp}.jpg"
                        image_path = os.path.join(Config.ATTENDANCE_IMAGES_PATH, image_filename)
                        cv2.imwrite(image_path, display_frame)
                        
                        relative_path = os.path.join('attendance', image_filename)
                        success, message = self.db_manager.check_out(
                            employee_info['employee_id'], confidence, relative_path
                        )
                        print(f"Check-out: {message}")
                    else:
                        print("Cannot check-out: No face or multiple faces detected")
        
        finally:
            self.camera.stop()
            print("\nLive recognition stopped")
    
    def view_attendance_today(self):
        """View today's attendance records"""
        today = date.today()
        records = self.db_manager.get_attendance_records(start_date=today, end_date=today)
        
        if not records:
            print(f"\nNo attendance records for {today}")
            return
        
        print(f"\n{'='*100}")
        print(f"ATTENDANCE RECORDS - {today}")
        print(f"{'='*100}")
        print(f"{'Code':<15} {'Name':<25} {'Check-in':<20} {'Check-out':<20} {'Status':<10}")
        print(f"{'='*100}")
        
        for record in records:
            check_in = record['check_in_time'].strftime('%H:%M:%S') if record['check_in_time'] else '-'
            check_out = record['check_out_time'].strftime('%H:%M:%S') if record['check_out_time'] else '-'
            
            print(f"{record['employee_code']:<15} {record['full_name']:<25} "
                  f"{check_in:<20} {check_out:<20} {record['status']:<10}")
        
        print(f"{'='*100}\n")
    
    def _log_recognition(self, employee_id: Optional[int], name: str, confidence: float,
                        image_path: Optional[str], status: str, processing_time: int):
        """Log recognition attempt"""
        try:
            self.db_manager.log_recognition(
                employee_id, name, confidence, image_path, status, processing_time
            )
        except Exception as e:
            print(f"Warning: Failed to log recognition: {e}")
    
    def cleanup(self):
        """Cleanup camera resources"""
        self.camera.stop()


class AttendanceSystem:
    """
    Simplified attendance system for API use
    Processes images from file paths instead of camera
    """
    def __init__(self, db_manager: DatabaseManager, face_recognizer: FaceRecognizer):
        self.db_manager = db_manager
        self.face_recognizer = face_recognizer
        os.makedirs(Config.ATTENDANCE_IMAGES_PATH, exist_ok=True)
    
    def check_in_from_image(self, image_path: str):
        """
        Check-in from uploaded image file
        Returns: (success: bool, employee_info: dict, message: str)
        """
        try:
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                return False, None, "Failed to load image"
            
            # Process and recognize
            results = self.face_recognizer.process_frame(frame)
            
            if len(results) == 0:
                return False, None, "No face detected in image"
            
            if len(results) > 1:
                return False, None, f"Multiple faces detected ({len(results)}). Please ensure only one person is visible"
            
            result = results[0]
            
            if not result['recognized']:
                return False, None, f"Face not recognized (confidence: {result['confidence']:.2f})"
            
            employee_info = result['employee_info']
            confidence = result['confidence']
            
            # Save attendance image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"checkin_{employee_info['employee_code']}_{timestamp}.jpg"
            save_path = os.path.join(Config.ATTENDANCE_IMAGES_PATH, image_filename)
            
            annotated_frame = self.face_recognizer.draw_results(frame, results)
            cv2.imwrite(save_path, annotated_frame)
            
            relative_path = os.path.join('attendance', image_filename)
            
            # Record check-in
            success, message = self.db_manager.check_in(
                employee_info['employee_id'], confidence, relative_path
            )
            
            if success:
                return True, employee_info, f"Check-in successful: {employee_info['full_name']}"
            else:
                return False, employee_info, message
                
        except Exception as e:
            return False, None, f"Error processing check-in: {str(e)}"
    
    def check_out_from_image(self, image_path: str):
        """
        Check-out from uploaded image file
        Returns: (success: bool, employee_info: dict, message: str)
        """
        try:
            # Load image
            frame = cv2.imread(image_path)
            if frame is None:
                return False, None, "Failed to load image"
            
            # Process and recognize
            results = self.face_recognizer.process_frame(frame)
            
            if len(results) == 0:
                return False, None, "No face detected in image"
            
            if len(results) > 1:
                return False, None, f"Multiple faces detected ({len(results)}). Please ensure only one person is visible"
            
            result = results[0]
            
            if not result['recognized']:
                return False, None, f"Face not recognized (confidence: {result['confidence']:.2f})"
            
            employee_info = result['employee_info']
            confidence = result['confidence']
            
            # Save attendance image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"checkout_{employee_info['employee_code']}_{timestamp}.jpg"
            save_path = os.path.join(Config.ATTENDANCE_IMAGES_PATH, image_filename)
            
            annotated_frame = self.face_recognizer.draw_results(frame, results)
            cv2.imwrite(save_path, annotated_frame)
            
            relative_path = os.path.join('attendance', image_filename)
            
            # Record check-out
            success, message = self.db_manager.check_out(
                employee_info['employee_id'], confidence, relative_path
            )
            
            if success:
                return True, employee_info, f"Check-out successful: {employee_info['full_name']}"
            else:
                return False, employee_info, message
                
        except Exception as e:
            return False, None, f"Error processing check-out: {str(e)}"
