# Sistem Absensi Wajah - Machine Learning Module

Sistem absensi berbasis face recognition menggunakan Python, OpenCV, dan MySQL.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Setup database:
   - Buat database MySQL
   - Jalankan `database/schema.sql`

3. Konfigurasi:
   - Copy `.env.example` ke `.env`
   - Edit kredensial database dan pengaturan

4. Jalankan:
```bash
python main.py
```

## Struktur Project

- `config/` - Konfigurasi sistem
- `database/` - Database manager dan schema
- `models/` - Face recognition engine
- `core/` - Enrollment dan attendance logic
- `utils/` - Helper functions
- `data/` - Storage untuk images dan logs
