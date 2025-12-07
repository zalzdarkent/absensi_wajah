import mysql.connector
from mysql.connector import pooling, Error
import numpy as np
from datetime import datetime, date
from typing import Optional, List, Dict, Tuple
import pickle
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

class DatabaseManager:
    def __init__(self):
        self.connection_pool = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="absen_pool",
                pool_size=5,
                pool_reset_session=True,
                **Config.get_db_config()
            )
            print("✓ Database connection pool initialized")
        except Error as e:
            print(f"✗ Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get connection from pool"""
        try:
            return self.connection_pool.get_connection()
        except Error as e:
            print(f"✗ Error getting connection: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = False):
        """Execute a query with optional parameters"""
        connection = None
        cursor = None
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return cursor.lastrowid
        except Error as e:
            if connection:
                connection.rollback()
            print(f"✗ Database error: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    # ========== EMPLOYEE OPERATIONS ==========
    
    def add_employee(self, employee_code: str, full_name: str, email: str = None, 
                     phone: str = None, department: str = None, position: str = None) -> int:
        """Add new employee"""
        query = """
            INSERT INTO employees (employee_code, full_name, email, phone, department, position)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (employee_code, full_name, email, phone, department, position)
        return self.execute_query(query, params)
    
    def get_employee(self, employee_id: int = None, employee_code: str = None) -> Optional[Dict]:
        """Get employee by ID or code"""
        if employee_id:
            query = "SELECT * FROM employees WHERE employee_id = %s"
            params = (employee_id,)
        elif employee_code:
            query = "SELECT * FROM employees WHERE employee_code = %s"
            params = (employee_code,)
        else:
            return None
        
        result = self.execute_query(query, params, fetch=True)
        return result[0] if result else None
    
    def get_all_employees(self, status: str = 'active') -> List[Dict]:
        """Get all employees with specific status"""
        query = "SELECT * FROM employees WHERE status = %s ORDER BY full_name"
        return self.execute_query(query, (status,), fetch=True)
    
    def update_employee_status(self, employee_id: int, status: str) -> bool:
        """Update employee status"""
        query = "UPDATE employees SET status = %s WHERE employee_id = %s"
        self.execute_query(query, (status, employee_id))
        return True
    
    # ========== FACE ENCODING OPERATIONS ==========
    
    def save_face_encoding(self, employee_id: int, face_encoding: np.ndarray, 
                          image_path: str, quality_score: float = None, 
                          is_primary: bool = False) -> int:
        """Save face encoding to database"""
        # Convert numpy array to binary
        encoding_blob = pickle.dumps(face_encoding)
        
        query = """
            INSERT INTO face_encodings 
            (employee_id, face_encoding, image_path, quality_score, is_primary)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (employee_id, encoding_blob, image_path, quality_score, is_primary)
        return self.execute_query(query, params)
    
    def get_face_encodings(self, employee_id: int = None) -> List[Dict]:
        """Get face encodings for specific employee or all employees"""
        if employee_id:
            query = """
                SELECT fe.*, e.employee_code, e.full_name 
                FROM face_encodings fe
                JOIN employees e ON fe.employee_id = e.employee_id
                WHERE fe.employee_id = %s
            """
            params = (employee_id,)
        else:
            query = """
                SELECT fe.*, e.employee_code, e.full_name 
                FROM face_encodings fe
                JOIN employees e ON fe.employee_id = e.employee_id
                WHERE e.status = 'active'
            """
            params = None
        
        results = self.execute_query(query, params, fetch=True)
        
        # Deserialize face encodings
        deserialized_results = []
        for result in results:
            try:
                result['face_encoding'] = pickle.loads(result['face_encoding'])
                deserialized_results.append(result)
            except Exception as e:
                print(f"Warning: Failed to deserialize encoding_id {result.get('encoding_id')}: {e}")
                continue
        
        return deserialized_results
    
    def get_encoding_count(self, employee_id: int) -> int:
        """Get count of face encodings for an employee"""
        query = "SELECT COUNT(*) as count FROM face_encodings WHERE employee_id = %s"
        result = self.execute_query(query, (employee_id,), fetch=True)
        return result[0]['count'] if result else 0
    
    def delete_face_encoding(self, encoding_id: int) -> bool:
        """Delete a face encoding"""
        query = "DELETE FROM face_encodings WHERE encoding_id = %s"
        self.execute_query(query, (encoding_id,))
        return True
    
    # ========== ATTENDANCE OPERATIONS ==========
    
    def check_in(self, employee_id: int, confidence: float, image_path: str = None) -> Tuple[bool, str]:
        """Record check-in"""
        today = date.today()
        
        # Check if already checked in today
        check_query = """
            SELECT attendance_id, check_in_time FROM attendance_records 
            WHERE employee_id = %s AND attendance_date = %s
        """
        existing = self.execute_query(check_query, (employee_id, today), fetch=True)
        
        if existing and existing[0]['check_in_time']:
            return False, "Already checked in today"
        
        now = datetime.now()
        
        # Determine status (late or present)
        work_start = datetime.strptime(Config.WORK_START_TIME, '%H:%M:%S').time()
        late_minutes = Config.LATE_THRESHOLD_MINUTES
        
        status = 'present'
        if now.time() > work_start:
            minutes_late = (datetime.combine(today, now.time()) - 
                          datetime.combine(today, work_start)).seconds // 60
            if minutes_late > late_minutes:
                status = 'late'
        
        if existing:
            # Update existing record
            query = """
                UPDATE attendance_records 
                SET check_in_time = %s, check_in_confidence = %s, 
                    check_in_image_path = %s, status = %s
                WHERE attendance_id = %s
            """
            params = (now, confidence, image_path, status, existing[0]['attendance_id'])
        else:
            # Create new record
            query = """
                INSERT INTO attendance_records 
                (employee_id, check_in_time, attendance_date, check_in_confidence, 
                 check_in_image_path, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (employee_id, now, today, confidence, image_path, status)
        
        self.execute_query(query, params)
        return True, f"Check-in successful ({status})"
    
    def check_out(self, employee_id: int, confidence: float, image_path: str = None) -> Tuple[bool, str]:
        """Record check-out"""
        today = date.today()
        
        # Check if checked in today
        check_query = """
            SELECT attendance_id, check_in_time, check_out_time 
            FROM attendance_records 
            WHERE employee_id = %s AND attendance_date = %s
        """
        existing = self.execute_query(check_query, (employee_id, today), fetch=True)
        
        if not existing or not existing[0]['check_in_time']:
            return False, "No check-in record found for today"
        
        if existing[0]['check_out_time']:
            return False, "Already checked out today"
        
        now = datetime.now()
        
        query = """
            UPDATE attendance_records 
            SET check_out_time = %s, check_out_confidence = %s, check_out_image_path = %s
            WHERE attendance_id = %s
        """
        params = (now, confidence, image_path, existing[0]['attendance_id'])
        self.execute_query(query, params)
        
        return True, "Check-out successful"
    
    def get_attendance_records(self, employee_id: int = None, start_date: date = None, 
                              end_date: date = None) -> List[Dict]:
        """Get attendance records with filters"""
        query = """
            SELECT ar.*, e.employee_code, e.full_name 
            FROM attendance_records ar
            JOIN employees e ON ar.employee_id = e.employee_id
            WHERE 1=1
        """
        params = []
        
        if employee_id:
            query += " AND ar.employee_id = %s"
            params.append(employee_id)
        
        if start_date:
            query += " AND ar.attendance_date >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND ar.attendance_date <= %s"
            params.append(end_date)
        
        query += " ORDER BY ar.attendance_date DESC, ar.check_in_time DESC"
        
        return self.execute_query(query, tuple(params), fetch=True)
    
    # ========== RECOGNITION LOG OPERATIONS ==========
    
    def log_recognition(self, employee_id: Optional[int], recognized_name: str, 
                       confidence_score: float, image_path: str, 
                       recognition_status: str, processing_time_ms: int) -> int:
        """Log recognition attempt"""
        query = """
            INSERT INTO recognition_logs 
            (employee_id, recognized_name, confidence_score, image_path, 
             recognition_status, processing_time_ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (employee_id, recognized_name, confidence_score, image_path, 
                 recognition_status, processing_time_ms)
        return self.execute_query(query, params)
    
    def get_recognition_logs(self, limit: int = 100) -> List[Dict]:
        """Get recent recognition logs"""
        query = """
            SELECT rl.*, e.full_name 
            FROM recognition_logs rl
            LEFT JOIN employees e ON rl.employee_id = e.employee_id
            ORDER BY rl.timestamp DESC
            LIMIT %s
        """
        return self.execute_query(query, (limit,), fetch=True)
    
    # ========== SYSTEM SETTINGS OPERATIONS ==========
    
    def get_setting(self, setting_key: str) -> Optional[str]:
        """Get system setting value"""
        query = "SELECT setting_value FROM system_settings WHERE setting_key = %s"
        result = self.execute_query(query, (setting_key,), fetch=True)
        return result[0]['setting_value'] if result else None
    
    def update_setting(self, setting_key: str, setting_value: str) -> bool:
        """Update system setting"""
        query = """
            UPDATE system_settings 
            SET setting_value = %s 
            WHERE setting_key = %s
        """
        self.execute_query(query, (setting_value, setting_key))
        return True
    
    def close(self):
        """Close all connections"""
        # Connection pool handles this automatically
        pass
