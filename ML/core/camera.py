import cv2
import numpy as np
from typing import Optional
import time

class CameraInterface:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.capture = None
        print(f"✓ Camera Interface initialized (index: {camera_index})")
    
    def start(self) -> bool:
        """Start camera capture"""
        self.capture = cv2.VideoCapture(self.camera_index)
        
        if not self.capture.isOpened():
            print(f"✗ Cannot open camera {self.camera_index}")
            return False
        
        # Set camera properties for better performance
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        
        print("✓ Camera started")
        return True
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a single frame from camera"""
        if self.capture is None or not self.capture.isOpened():
            print("✗ Camera not started")
            return None
        
        ret, frame = self.capture.read()
        
        if not ret:
            print("✗ Failed to capture frame")
            return None
        
        return frame
    
    def capture_photo(self, countdown: int = 3) -> Optional[np.ndarray]:
        """
        Capture a photo with countdown
        Shows live preview with countdown overlay
        """
        if self.capture is None or not self.capture.isOpened():
            if not self.start():
                return None
        
        print(f"Preparing to capture photo in {countdown} seconds...")
        
        start_time = time.time()
        
        while True:
            frame = self.read_frame()
            if frame is None:
                return None
            
            elapsed = time.time() - start_time
            remaining = countdown - int(elapsed)
            
            if remaining <= 0:
                # Capture the photo
                print("✓ Photo captured!")
                cv2.destroyWindow('Capture Photo')
                return frame
            
            # Draw countdown on frame
            display_frame = frame.copy()
            text = f"Capturing in {remaining}..."
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.5
            thickness = 3
            
            # Get text size for centering
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            x = (display_frame.shape[1] - text_width) // 2
            y = (display_frame.shape[0] + text_height) // 2
            
            # Draw text with background
            cv2.rectangle(display_frame, (x - 10, y - text_height - 10), 
                         (x + text_width + 10, y + 10), (0, 0, 0), -1)
            cv2.putText(display_frame, text, (x, y), font, font_scale, 
                       (0, 255, 0), thickness)
            
            # Show frame
            cv2.imshow('Capture Photo', display_frame)
            
            # Check if window was closed manually
            if cv2.getWindowProperty('Capture Photo', cv2.WND_PROP_VISIBLE) < 1:
                print("✗ Capture cancelled (window closed)")
                return None
            
            # Break if 'q' pressed
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("✗ Capture cancelled")
                cv2.destroyWindow('Capture Photo')
                return None
    
    def live_preview(self, window_name: str = 'Camera Preview'):
        """
        Show live camera preview
        Press 'q' to quit, 'c' to capture
        Returns: captured frame or None
        """
        if self.capture is None or not self.capture.isOpened():
            if not self.start():
                return None
        
        print("Live preview started. Press 'c' to capture, 'q' to quit")
        
        while True:
            frame = self.read_frame()
            if frame is None:
                break
            
            # Add instructions to frame
            cv2.putText(frame, "Press 'c' to capture, 'q' to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow(window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Preview closed")
                cv2.destroyWindow(window_name)
                return None
            elif key == ord('c'):
                print("✓ Frame captured")
                cv2.destroyWindow(window_name)
                return frame
    
    def stop(self):
        """Stop camera capture and release resources"""
        if self.capture is not None:
            self.capture.release()
            cv2.destroyAllWindows()
            print("✓ Camera stopped")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop()
