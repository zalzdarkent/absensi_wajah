# Absensi Wajah - Face Recognition Attendance System

Sistem absensi modern menggunakan teknologi face recognition dengan Next.js dan Python FastAPI.

## 🎯 Fitur MVP

- ✅ **Dashboard** - Statistik kehadiran real-time dan ringkasan harian
- ✅ **Manajemen Karyawan** - Daftar karyawan, detail, dan pendaftaran baru dengan foto wajah
- ✅ **Kehadiran** - Check-in dan check-out dengan face recognition
- ✅ **Riwayat Kehadiran** - View dan filter data kehadiran karyawan

## 🛠 Tech Stack

### Frontend
- **Next.js 16** - React framework dengan App Router
- **shadcn/ui** - Component library (New York theme)
- **Tailwind CSS v4** - Styling
- **TypeScript** - Type safety
- **date-fns** - Date formatting
- **Sonner** - Toast notifications

### Backend
- **Python FastAPI** - ML API server
- **OpenCV** - Image processing
- **face-recognition** - Face detection & recognition
- **MySQL** - Database

## 📁 Struktur Folder

```
absen_muka/
├── ML/                           # Python ML Backend
│   ├── api/
│   │   └── main.py              # FastAPI server
│   ├── core/
│   │   ├── attendance.py        # Attendance logic (with AttendanceSystem)
│   │   ├── enrollment.py        # Enrollment logic (with EnrollmentSystem)
│   │   ├── camera.py
│   ├── models/
│   │   └── face_recognizer.py
│   ├── database/
│   │   ├── db_manager.py
│   │   └── schema.sql
│   ├── config/
│   │   └── config.py
│   ├── data/
│   │   └── images/
│   │       ├── employees/       # Face photos
│   │       └── attendance/      # Attendance photos
│   └── requirements.txt
│
├── src/
│   ├── app/
│   │   ├── (dashboard)/         # Dashboard layout group
│   │   │   ├── layout.tsx       # Sidebar layout
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx     # Dashboard page
│   │   │   ├── employees/
│   │   │   │   ├── page.tsx     # Employee list
│   │   │   │   ├── [id]/
│   │   │   │   │   └── page.tsx # Employee detail
│   │   │   │   └── new/
│   │   │   │       └── page.tsx # New employee form
│   │   │   └── attendance/
│   │   │       └── page.tsx     # Attendance page
│   │   ├── api/                 # Next.js API Routes
│   │   │   ├── employees/
│   │   │   ├── attendance/
│   │   │   └── stats/
│   │   ├── layout.tsx           # Root layout
│   │   └── page.tsx             # Redirect to dashboard
│   ├── components/
│   │   ├── ui/                  # shadcn components
│   │   ├── sidebar.tsx
│   │   ├── stats-card.tsx
│   │   ├── status-badge.tsx
│   │   └── camera-capture.tsx
│   └── lib/
│       ├── db.ts                # MySQL connection pool
│       └── utils.ts
└── .env.local                   # Environment variables
```

## 🚀 Setup & Installation

### Prerequisites
- Node.js 18+
- Python 3.8+
- MySQL Server
- Webcam (untuk capture foto)

### 1. Database Setup

Jalankan schema SQL di MySQL:
```bash
cd ML/database
mysql -u root -p < schema.sql
```

Database `absen_wajah` akan dibuat dengan 5 tabel:
- `employees` - Data karyawan
- `face_encodings` - Face encodings untuk recognition
- `attendance_records` - Log kehadiran
- `recognition_logs` - Audit trail
- `system_settings` - Konfigurasi sistem

### 2. Frontend Setup (Next.js)

```bash
# Install dependencies
npm install

# Setup environment variables
cp .env.local.example .env.local
# Edit .env.local dengan credentials MySQL Anda

# Run development server
npm run dev
```

Web akan berjalan di `http://localhost:3000`

### 3. Backend Setup (Python FastAPI)

```bash
# Navigate to ML folder
cd ML

# Create virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
# Buat file .env di folder ML atau gunakan config default

# Run FastAPI server
cd api
python main.py
```

API akan berjalan di `http://localhost:8000`

**Catatan**: FastAPI harus running agar fitur ML (enroll, check-in, check-out) berfungsi!

### 4. Environment Variables

**.env.local** (Root folder - untuk Next.js):
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=absen_wajah

# Python FastAPI URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**ML/.env** (Optional - untuk Python, default sudah ada di config.py):
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
```

## 📖 Cara Menggunakan

### 1. Daftar Karyawan Baru
1. Buka web di browser: `http://localhost:3000`
2. Klik **Dashboard** → **Tambah Karyawan**
3. Isi form data karyawan
4. Klik **Buka Kamera** dan ambil 3-5 foto wajah
5. Klik **Daftarkan Karyawan**

### 2. Check-in
1. Klik tombol **Check In** di Dashboard atau halaman Kehadiran
2. Ambil foto wajah
3. Sistem akan mengenali wajah dan mencatat check-in

### 3. Check-out
1. Klik tombol **Check Out**
2. Ambil foto wajah
3. Sistem akan mencatat check-out

### 4. Lihat Data Kehadiran
- **Dashboard**: Ringkasan hari ini + check-in terbaru
- **Halaman Kehadiran**: Tabel lengkap dengan filter tanggal
- **Detail Karyawan**: Riwayat kehadiran per karyawan

## 🔧 API Endpoints

### Next.js API Routes (Port 3000)
- `GET /api/employees` - List semua karyawan
- `GET /api/employees/[id]` - Detail karyawan + foto + attendance
- `GET /api/attendance?date=YYYY-MM-DD` - List attendance by date
- `GET /api/stats` - Dashboard statistics

### Python FastAPI (Port 8000)
- `POST /api/enroll` - Enroll karyawan baru dengan foto
- `POST /api/recognize` - Recognize face dari foto
- `POST /api/attendance/checkin` - Check-in dengan face recognition
- `POST /api/attendance/checkout` - Check-out dengan face recognition
- `GET /images/{path}` - Serve images (employee & attendance photos)
- `GET /api/health` - Health check

## 🎨 UI/UX Features

- ✅ **Responsive Design** - Mobile, tablet, desktop friendly
- ✅ **Clean UI** - shadcn/ui New York theme dengan Geist fonts
- ✅ **Dark Mode Ready** - Tailwind dark mode support
- ✅ **Real-time Toast** - Notifikasi sukses/error dengan Sonner
- ✅ **Client-side Camera** - WebRTC untuk capture foto
- ✅ **Status Badges** - Visual indicators (Hadir, Terlambat, Tidak Hadir)
- ✅ **Loading States** - Skeleton screens dan loading indicators

## 🔐 Database Schema Highlights

### employees
- Unique `employee_code` (e.g., EMP-001)
- Status: `active`, `inactive`, `suspended`

### face_encodings
- Multiple photos per employee (max 5)
- Quality score untuk setiap foto
- Primary photo designation

### attendance_records
- Auto status: `present`, `late`, `absent`
- Confidence scores untuk check-in/out
- Saved images untuk audit trail
- Unique constraint: 1 record per employee per day

## 📝 TODO / Future Enhancements

- [ ] Authentication & Authorization
- [ ] Live camera recognition (WebSocket streaming)
- [ ] Export reports (Excel, PDF)
- [ ] Advanced analytics & charts
- [ ] Email notifications
- [ ] Manual attendance correction
- [ ] Multiple camera/location support
- [ ] Employee self-service portal

## 🐛 Troubleshooting

### FastAPI tidak bisa start
```bash
# Install ulang dependencies
pip install -r requirements.txt --force-reinstall

# Cek apakah ada conflict dengan face-recognition
pip uninstall face-recognition dlib
pip install dlib-bin face-recognition
```

### Database connection error
- Pastikan MySQL running
- Cek credentials di `.env.local`
- Pastikan database `absen_wajah` sudah dibuat

### Camera tidak bisa diakses
- Pastikan browser memiliki permission untuk camera
- Gunakan HTTPS atau localhost (http)
- Test di browser lain (Chrome recommended)

### Face recognition tidak akurat
- Ambil foto dengan pencahayaan yang baik
- Gunakan 5 foto dengan angle berbeda
- Adjust `RECOGNITION_THRESHOLD` di config (default 0.6)

## 📄 License

MIT License - Feel free to use for your projects!

## 👨‍💻 Developer Notes

Project ini dibuat dengan fokus pada:
- **Clean Architecture** - Separation of concerns (Next.js UI, FastAPI ML)
- **Type Safety** - TypeScript + Zod validation
- **Best Practices** - Server Components, API routes, proper error handling
- **Developer Experience** - Hot reload, clear folder structure, documented code

Happy coding! 🚀
