# Sistem Absensi Wajah (Face Recognition Attendance)

Aplikasi web untuk sistem absensi karyawan menggunakan teknologi face recognition berbasis Next.js dan Python FastAPI.

## 🚀 Fitur

- ✅ **Dashboard** - Statistik kehadiran real-time
- 👥 **Manajemen Karyawan** - Daftarkan, lihat, dan kelola data karyawan
- 📸 **Face Recognition** - Check-in dan check-out menggunakan pengenalan wajah
- 📊 **Laporan Kehadiran** - Lihat history kehadiran dengan filter tanggal
- 🎥 **Camera Capture** - Ambil foto langsung dari browser

## 🛠️ Tech Stack

### Frontend
- **Next.js 16** - React framework dengan App Router
- **TypeScript** - Type safety
- **Tailwind CSS v4** - Styling
- **shadcn/ui** - UI components
- **Recharts** - Data visualization
- **Sonner** - Toast notifications

### Backend
- **FastAPI** - Python REST API framework
- **OpenCV** - Image processing
- **face-recognition** - Face detection & recognition
- **MySQL** - Database
- **dlib** - Machine learning toolkit

## 📋 Prerequisites

- Node.js 18+ 
- Python 3.8+
- MySQL 8.0+
- Webcam (untuk capture foto)

## ⚙️ Setup & Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd absen_muka
```

### 2. Setup Database

```bash
# Buat database MySQL
mysql -u root -p
CREATE DATABASE absen_wajah;
USE absen_wajah;
SOURCE ML/database/schema.sql;
```

### 3. Setup Environment Variables

Buat file `.env` di root folder:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=absen_wajah

RECOGNITION_THRESHOLD=0.6
MAX_FACES_PER_EMPLOYEE=5
WORK_START_TIME=09:00:00
WORK_END_TIME=17:00:00
LATE_THRESHOLD_MINUTES=15

NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
cd ML
pip install -r requirements.txt
```

### 5. Run Application

**Terminal 1 - Next.js Frontend:**
```bash
npm run dev
```
Aplikasi akan berjalan di `http://localhost:3000`

**Terminal 2 - FastAPI Backend:**
```bash
cd ML/api
python main.py
```
API akan berjalan di `http://localhost:8000`

## 📖 Cara Penggunaan

### 1. Daftarkan Karyawan Baru

1. Buka `http://localhost:3000/employees/new`
2. Isi data karyawan (kode, nama, email, dll)
3. Ambil minimal 3 foto wajah dari berbagai sudut
4. Klik "Daftarkan Karyawan"

### 2. Check-In / Check-Out

1. Buka halaman **Kehadiran** (`/attendance`)
2. Klik tombol **Check In** atau **Check Out**
3. Klik **Buka Kamera** dan izinkan akses kamera
4. Ambil foto wajah Anda
5. Sistem akan mengenali wajah dan mencatat kehadiran

### 3. Lihat Data Kehadiran

- **Dashboard**: Lihat statistik hari ini
- **Kehadiran**: Filter data kehadiran berdasarkan tanggal
- **Karyawan**: Lihat detail karyawan dan history kehadiran

## 📁 Struktur Folder

```
absen_muka/
├── src/                    # Next.js frontend
│   ├── app/               # App router pages
│   ├── components/        # Reusable components
│   └── lib/               # Utilities & database
├── ML/                    # Python backend
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Business logic
│   ├── models/           # Face recognition models
│   ├── database/         # Database manager
│   ├── data/             # Stored images
│   └── config/           # Configuration
└── public/               # Static assets
```

## 🔧 Troubleshooting

### Camera tidak muncul
- Pastikan browser sudah diberikan izin akses kamera
- Refresh browser dan coba lagi
- Cek console browser (F12) untuk error

### Face not recognized
- Pastikan karyawan sudah terdaftar dengan minimal 3 foto
- Pastikan FastAPI server sudah running
- Restart FastAPI server untuk reload face encodings

### Database connection error
- Pastikan MySQL sudah running
- Cek kredensial di file `.env`
- Pastikan database `absen_wajah` sudah dibuat

## 📝 API Endpoints

- `POST /api/enroll` - Daftarkan karyawan baru
- `POST /api/attendance/checkin` - Check-in dengan foto
- `POST /api/attendance/checkout` - Check-out dengan foto
- `POST /api/recognize` - Kenali wajah dari foto
- `GET /api/health` - Health check

## 👨‍💻 Development

```bash
# Frontend development
npm run dev

# Backend development
cd ML/api
python main.py

# Database check
node check_face_encodings.js
```

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.
