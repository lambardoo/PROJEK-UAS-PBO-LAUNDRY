from flask import Flask
from routes.auth import (
    auth_bp,
    dashboard_bp,
    pelanggan_bp,
    layanan_bp,
    transaksi_bp,
    laporan_bp
)

# Objek Flask
app = Flask(__name__)
app.secret_key = 'kunci_rahasia_laundry_2026'

# Registrasi Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(pelanggan_bp)
app.register_blueprint(layanan_bp)
app.register_blueprint(transaksi_bp)
app.register_blueprint(laporan_bp)

# Menjalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)
