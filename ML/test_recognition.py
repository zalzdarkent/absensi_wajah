#!/usr/bin/env python3
"""
Test script untuk debug face recognition
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from database.db_manager import DatabaseManager
from models.face_recognizer import FaceRecognizer

def main():
    print("\n=== FACE RECOGNITION DEBUG TEST ===\n")
    
    # Initialize
    db_manager = DatabaseManager()
    face_recognizer = FaceRecognizer(db_manager)
    
    # Load encodings
    print("\n1. Loading encodings from database...")
    face_recognizer.load_encodings_from_db()
    
    print(f"\n2. Total encodings loaded: {len(face_recognizer.known_encodings)}")
    print(f"   Total employees: {len(face_recognizer.known_employees)}")
    
    if len(face_recognizer.known_encodings) == 0:
        print("\n✗ No encodings found! Please enroll an employee first.")
        return
    
    print("\n3. Enrolled employees:")
    for idx, emp in enumerate(face_recognizer.known_employees):
        encoding = face_recognizer.known_encodings[idx]
        print(f"   [{idx}] {emp['full_name']} ({emp['employee_code']}) - Encoding shape: {encoding.shape}")
    
    print(f"\n4. Current recognition threshold: {face_recognizer.recognition_threshold}")
    print(f"   (Lower threshold = easier to recognize, Higher = stricter)")
    
    print("\n5. Testing with webcam...")
    print("   Position your face in camera and press any key to test recognition")
    
    from core.camera import CameraInterface
    import cv2
    
    camera = CameraInterface()
    if not camera.start():
        print("✗ Cannot start camera")
        return
    
    print("   Camera started. Press 'SPACE' to test, 'q' to quit")
    
    try:
        while True:
            frame = camera.read_frame()
            if frame is None:
                break
            
            # Show live preview
            cv2.putText(frame, "Press SPACE to test recognition, Q to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow('Test Recognition', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord(' '):  # Space key
                print("\n   --- Testing recognition ---")
                
                # Detect faces
                results = face_recognizer.process_frame(frame)
                
                if len(results) == 0:
                    print("   ✗ No face detected")
                    continue
                
                if len(results) > 1:
                    print(f"   ⚠ Multiple faces detected ({len(results)})")
                
                # Show results for each detected face
                for idx, result in enumerate(results):
                    print(f"\n   Face #{idx+1}:")
                    print(f"   - Face location: {result['face_location']}")
                    print(f"   - Recognized: {result['recognized']}")
                    print(f"   - Confidence: {result['confidence']:.4f}")
                    
                    if result['recognized']:
                        emp = result['employee_info']
                        print(f"   - Employee: {emp['full_name']} ({emp['employee_code']})")
                    else:
                        print(f"   - Status: Unknown face")
                        print(f"   - Tip: Confidence below threshold ({face_recognizer.recognition_threshold})")
                        
                        # Show distance to all known faces
                        import face_recognition
                        face_encoding = face_recognition.face_encodings(
                            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                            [result['face_location']]
                        )
                        if len(face_encoding) > 0:
                            distances = face_recognition.face_distance(
                                face_recognizer.known_encodings, 
                                face_encoding[0]
                            )
                            print(f"\n   Distances to known faces:")
                            for i, dist in enumerate(distances):
                                emp = face_recognizer.known_employees[i]
                                conf = 1 - dist
                                print(f"   - {emp['full_name']}: distance={dist:.4f}, confidence={conf:.4f}")
                
                # Draw results on frame
                annotated = face_recognizer.draw_results(frame, results)
                cv2.imshow('Test Result', annotated)
                print("\n   Press any key to continue...")
                cv2.waitKey(0)
                cv2.destroyWindow('Test Result')
    
    finally:
        camera.stop()
    
    print("\n=== TEST COMPLETED ===\n")

if __name__ == "__main__":
    main()
