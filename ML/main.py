#!/usr/bin/env python3
"""
Face Recognition Attendance System - Main Entry Point
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from database.db_manager import DatabaseManager
from models.face_recognizer import FaceRecognizer
from core.enrollment import FaceEnrollment
from core.attendance import AttendanceManager

class AttendanceSystem:
    def __init__(self):
        print("\n" + "="*60)
        print("  FACE RECOGNITION ATTENDANCE SYSTEM")
        print("="*60 + "\n")
        
        try:
            # Initialize components
            print("Initializing system components...\n")
            
            self.db_manager = DatabaseManager()
            self.face_recognizer = FaceRecognizer(self.db_manager)
            self.enrollment = FaceEnrollment(self.db_manager, self.face_recognizer)
            self.attendance = AttendanceManager(self.db_manager, self.face_recognizer)
            
            # Load face encodings
            self.face_recognizer.load_encodings_from_db()
            
            print("\n✓ System initialized successfully!\n")
            
        except Exception as e:
            print(f"\n✗ System initialization failed: {e}\n")
            sys.exit(1)
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("  MAIN MENU")
        print("="*60)
        print("\n  ENROLLMENT")
        print("  1. Enroll new employee")
        print("  2. Add face photo to existing employee")
        print("  3. List all employees")
        print("\n  ATTENDANCE")
        print("  4. Check-in")
        print("  5. Check-out")
        print("  6. Live recognition demo")
        print("  7. View today's attendance")
        print("\n  SYSTEM")
        print("  8. Reload face encodings")
        print("  9. Update recognition threshold")
        print("  0. Exit")
        print("\n" + "="*60)
    
    def enroll_new_employee(self):
        """Enroll new employee"""
        print("\n--- ENROLL NEW EMPLOYEE ---\n")
        
        employee_code = input("Employee Code: ").strip()
        if not employee_code:
            print("✗ Employee code is required")
            return
        
        full_name = input("Full Name: ").strip()
        if not full_name:
            print("✗ Full name is required")
            return
        
        email = input("Email (optional): ").strip() or None
        phone = input("Phone (optional): ").strip() or None
        department = input("Department (optional): ").strip() or None
        position = input("Position (optional): ").strip() or None
        
        num_photos_input = input("Number of photos (default 3): ").strip()
        num_photos = int(num_photos_input) if num_photos_input.isdigit() else 3
        
        self.enrollment.enroll_employee(
            employee_code, full_name, email, phone, department, position, num_photos
        )
    
    def add_face_photo(self):
        """Add face photo to existing employee"""
        print("\n--- ADD FACE PHOTO ---\n")
        
        employee_code = input("Employee Code: ").strip()
        if not employee_code:
            print("✗ Employee code is required")
            return
        
        self.enrollment.add_face_photo(employee_code)
    
    def update_threshold(self):
        """Update recognition threshold"""
        print("\n--- UPDATE RECOGNITION THRESHOLD ---\n")
        print(f"Current threshold: {self.face_recognizer.recognition_threshold}")
        print("Threshold range: 0.0 (loose) to 1.0 (strict)")
        print("Recommended: 0.5 - 0.7")
        
        new_threshold_input = input("\nNew threshold: ").strip()
        
        try:
            new_threshold = float(new_threshold_input)
            self.face_recognizer.update_threshold(new_threshold)
        except ValueError:
            print("✗ Invalid threshold value")
    
    def run(self):
        """Main application loop"""
        while True:
            try:
                self.show_menu()
                choice = input("\nSelect option: ").strip()
                
                if choice == '1':
                    self.enroll_new_employee()
                
                elif choice == '2':
                    self.add_face_photo()
                
                elif choice == '3':
                    self.enrollment.list_employees()
                
                elif choice == '4':
                    self.attendance.check_in_employee()
                
                elif choice == '5':
                    self.attendance.check_out_employee()
                
                elif choice == '6':
                    self.attendance.live_recognition()
                
                elif choice == '7':
                    self.attendance.view_attendance_today()
                
                elif choice == '8':
                    print("\nReloading face encodings...")
                    self.face_recognizer.load_encodings_from_db()
                
                elif choice == '9':
                    self.update_threshold()
                
                elif choice == '0':
                    print("\n" + "="*60)
                    print("  Thank you for using the system!")
                    print("="*60 + "\n")
                    break
                
                else:
                    print("\n✗ Invalid option. Please try again.")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")
        
        # Cleanup
        self.enrollment.cleanup()
        self.attendance.cleanup()

def main():
    """Entry point"""
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n⚠ Warning: .env file not found!")
        print("Please copy .env.example to .env and configure your settings.\n")
        
        create_env = input("Create .env from .env.example? (y/n): ").strip().lower()
        if create_env == 'y':
            if os.path.exists('.env.example'):
                import shutil
                shutil.copy('.env.example', '.env')
                print("✓ .env file created. Please edit it with your database credentials.")
                print("Then run this script again.\n")
                sys.exit(0)
            else:
                print("✗ .env.example not found\n")
                sys.exit(1)
        else:
            sys.exit(1)
    
    # Initialize and run system
    system = AttendanceSystem()
    system.run()

if __name__ == "__main__":
    main()
