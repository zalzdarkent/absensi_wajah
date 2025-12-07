-- Create database
CREATE DATABASE IF NOT EXISTS absen_wajah CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE absen_wajah;

-- Employees Table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    department VARCHAR(50),
    position VARCHAR(50),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employee_code (employee_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Face Encodings Table
CREATE TABLE IF NOT EXISTS face_encodings (
    encoding_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    face_encoding BLOB NOT NULL,
    encoding_version VARCHAR(20) DEFAULT 'v1',
    image_path VARCHAR(255),
    quality_score FLOAT,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    INDEX idx_employee_id (employee_id),
    INDEX idx_primary (employee_id, is_primary)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Attendance Records Table
CREATE TABLE IF NOT EXISTS attendance_records (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NOT NULL,
    check_in_time TIMESTAMP NULL,
    check_out_time TIMESTAMP NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'late', 'absent', 'half_day', 'on_leave') DEFAULT 'present',
    check_in_image_path VARCHAR(255),
    check_out_image_path VARCHAR(255),
    check_in_confidence FLOAT,
    check_out_confidence FLOAT,
    location VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    UNIQUE KEY unique_daily_attendance (employee_id, attendance_date),
    INDEX idx_date (attendance_date),
    INDEX idx_employee_date (employee_id, attendance_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Recognition Logs Table
CREATE TABLE IF NOT EXISTS recognition_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT NULL,
    recognized_name VARCHAR(100),
    confidence_score FLOAT,
    image_path VARCHAR(255),
    recognition_status ENUM('success', 'failed', 'unknown_face', 'multiple_faces') NOT NULL,
    processing_time_ms INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    INDEX idx_timestamp (timestamp),
    INDEX idx_status (recognition_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    setting_id INT PRIMARY KEY AUTO_INCREMENT,
    setting_key VARCHAR(50) UNIQUE NOT NULL,
    setting_value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default settings
INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('recognition_threshold', '0.6', 'Face recognition confidence threshold (0-1)'),
('max_faces_per_employee', '5', 'Maximum face encodings per employee'),
('late_threshold_minutes', '15', 'Minutes after start time to mark as late'),
('model_version', 'v1', 'Current face recognition model version'),
('work_start_time', '09:00:00', 'Default work start time'),
('work_end_time', '17:00:00', 'Default work end time')
ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value);
