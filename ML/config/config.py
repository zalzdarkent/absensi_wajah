import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'absen_wajah')
    
    # System Configuration
    RECOGNITION_THRESHOLD = float(os.getenv('RECOGNITION_THRESHOLD', 0.6))
    MAX_FACES_PER_EMPLOYEE = int(os.getenv('MAX_FACES_PER_EMPLOYEE', 5))
    WORK_START_TIME = os.getenv('WORK_START_TIME', '09:00:00')
    WORK_END_TIME = os.getenv('WORK_END_TIME', '17:00:00')
    LATE_THRESHOLD_MINUTES = int(os.getenv('LATE_THRESHOLD_MINUTES', 15))
    
    # Image Storage
    IMAGE_BASE_PATH = os.getenv('IMAGE_BASE_PATH', './data/images')
    EMPLOYEE_IMAGES_PATH = os.path.join(IMAGE_BASE_PATH, 'employees')
    ATTENDANCE_IMAGES_PATH = os.path.join(IMAGE_BASE_PATH, 'attendance')
    
    @classmethod
    def get_db_config(cls):
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME
        }
