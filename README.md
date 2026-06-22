# Sistem Informasi Manajemen Laundry - Flask

Studi kasus UAS Pemrograman Berorientasi Objek (TIB04).

## Struktur Project
```
laundry_app/
├── main.py            # Entry point Flask, registrasi blueprint
├── models.py          # Koneksi database (get_db_connection)
├── routes.py          # Semua route/blueprint (auth, dashboard, pelanggan, layanan, transaksi, laporan)
├── database.sql       # Skema database + data awal
├── requirements.txt
├── templates/          # Jinja2 templates (Bootstrap 5)
└── static/css/style.css
```

## Cara Menjalankan

1. **Buat database MySQL**
   ```bash
   mysql -u root -p < database.sql
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Sesuaikan koneksi database** (jika perlu) di `models.py`.

4. **Jalankan aplikasi**
   ```bash
   python main.py
   ```
   Akses di `http://127.0.0.1:5000`

5. **Login default**
   - Email: `admin@laundry.com`
   - Password: `admin123`

## Fitur

| Fitur | Keterangan |
|---|---|
| Autentikasi | Login, Register, Manajemen User (admin/kasir) |
| Dashboard | Statistik pelanggan, layanan, transaksi, pendapatan |
| Data Master | CRUD Pelanggan & Layanan |
| Transaksi | Input transaksi, hitung otomatis total & estimasi selesai |
| Laporan | Filter berdasarkan tanggal & status, rekap pendapatan & berat |
