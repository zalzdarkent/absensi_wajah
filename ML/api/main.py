from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import sys
import os
from typing import List
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.enrollment import EnrollmentSystem
from core.attendance import AttendanceSystem
from models.face_recognizer import FaceRecognizer
from database.db_manager import DatabaseManager
from config.config import Config

app = FastAPI(title="Face Recognition Attendance API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving images
# Fix path relative to api folder
image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images")
if not os.path.exists(image_path):
    os.makedirs(image_path, exist_ok=True)
app.mount("/images", StaticFiles(directory=image_path), name="images")

# Initialize systems
db = DatabaseManager()
face_recognizer = FaceRecognizer(db)
face_recognizer.load_encodings_from_db()  # Load encodings at startup
enrollment_system = EnrollmentSystem(db, face_recognizer)
attendance_system = AttendanceSystem(db, face_recognizer)

@app.get("/")
def read_root():
    return {"message": "Face Recognition Attendance API", "status": "running"}

@app.post("/api/enroll")
async def enroll_employee(
    employee_code: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    department: str = Form(None),
    position: str = Form(None),
    images: List[UploadFile] = File(...)
):
    """
    Enroll a new employee with face images
    """
    print(f"\n=== ENROLLMENT REQUEST ===")
    print(f"Employee: {full_name} ({employee_code})")
    print(f"Number of images received: {len(images)}")
    
    try:
        if len(images) < 3:
            raise HTTPException(status_code=400, detail="Minimum 3 photos required")
        
        if len(images) > Config.MAX_FACES_PER_EMPLOYEE:
            raise HTTPException(
                status_code=400, 
                detail=f"Maximum {Config.MAX_FACES_PER_EMPLOYEE} photos allowed"
            )
        
        # Save uploaded files temporarily
        temp_dir = f"./temp/{employee_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        os.makedirs(temp_dir, exist_ok=True)
        
        image_paths = []
        for idx, image in enumerate(images):
            file_path = os.path.join(temp_dir, f"photo_{idx}.jpg")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_paths.append(file_path)
        
        # Enroll using existing system
        success, employee_id, message = enrollment_system.enroll_from_images(
            employee_code=employee_code,
            full_name=full_name,
            image_paths=image_paths,
            email=email,
            phone=phone,
            department=department,
            position=position
        )
        
        # Clean up temp files
        shutil.rmtree(temp_dir)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "employee_id": employee_id,
                "message": message
            })
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recognize")
async def recognize_face(image: UploadFile = File(...)):
    """
    Recognize a face from uploaded image
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"./temp/recognize_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        os.makedirs("./temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Recognize face
        result = face_recognizer.recognize_from_image(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/attendance/checkin")
async def check_in(image: UploadFile = File(...)):
    """
    Check-in attendance with face recognition
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"./temp/checkin_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        os.makedirs("./temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Process check-in
        success, employee_info, message = attendance_system.check_in_from_image(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "employee": employee_info,
                "message": message
            })
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/attendance/checkout")
async def check_out(image: UploadFile = File(...)):
    """
    Check-out attendance with face recognition
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"./temp/checkout_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        os.makedirs("./temp", exist_ok=True)
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Process check-out
        success, employee_info, message = attendance_system.check_out_from_image(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "employee": employee_info,
                "message": message
            })
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    """
    Health check endpoint
    """
    try:
        # Test database connection
        db.connect()
        db_status = "connected"
        db.close()
    except:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "face_recognizer": "loaded" if face_recognizer.known_face_encodings else "no data"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
