
CREATE DATABASE IF NOT EXISTS db_laundry;
USE db_laundry;

-- Tabel users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_lengkap VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','kasir') DEFAULT 'kasir',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel pelanggan 
CREATE TABLE IF NOT EXISTS pelanggan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    no_hp VARCHAR(20) NOT NULL,
    alamat TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel layanan 
CREATE TABLE IF NOT EXISTS layanan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_layanan VARCHAR(100) NOT NULL,
    harga_per_kg DECIMAL(10,2) NOT NULL,
    estimasi_hari INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel transaksi
CREATE TABLE IF NOT EXISTS transaksi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    kode_transaksi VARCHAR(20) UNIQUE NOT NULL,
    pelanggan_id INT NOT NULL,
    layanan_id INT NOT NULL,
    berat_kg DECIMAL(5,2) NOT NULL,
    total_harga DECIMAL(10,2) NOT NULL,
    status ENUM('Proses','Selesai','Diambil') DEFAULT 'Proses',
    tanggal_masuk DATE NOT NULL,
    tanggal_estimasi DATE NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pelanggan_id) REFERENCES pelanggan(id) ON DELETE CASCADE,
    FOREIGN KEY (layanan_id) REFERENCES layanan(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Data awal: user admin (password = admin123)
INSERT INTO users (nama_lengkap, email, password, role) VALUES
('Administrator', 'admin@laundry.com',
 'scrypt:32768:8:1$irdzapjSLz0mLrgY$00f1d206fbfc26504b6ad4463342c43f4cc583c578b780753ecea8c9b24c8cae0e365b56eb49cf2d09e387e485cea59781440ca01a17e107e691a7389b2ecc3f',
 'admin');

-- Data awal: jenis layanan
INSERT INTO layanan (nama_layanan, harga_per_kg, estimasi_hari) VALUES
('Cuci Reguler', 7000, 3),
('Cuci Express', 12000, 1),
('Cuci Cepetan Dikit', 9000, 2),
('Cuci Selimut / Bed Cover', 15000, 2);

-- Data awal: pelanggan
INSERT INTO pelanggan (nama, no_hp, alamat) VALUES
('Budi Kemaren', '081234567890', 'Jl. Merdeka No. 10'),
('Siti Abadi',  '081298765432', 'Jl. Diponegoro No. 5');
