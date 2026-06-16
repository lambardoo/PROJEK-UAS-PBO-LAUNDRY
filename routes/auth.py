from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, timedelta

from models.database import get_db_connection


# ════════════════════════════════════════════════════════════════════════
#  DECORATOR: wajib login
# ════════════════════════════════════════════════════════════════════════
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'warning')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════════════
#  BLUEPRINT: AUTH (login, register, logout, manajemen user)
# ════════════════════════════════════════════════════════════════════════
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@auth_bp.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    var_email    = request.form.get('email')
    var_password = request.form.get('password')

    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (var_email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], var_password):
            session['user_id']      = user['id']
            session['nama_lengkap'] = user['nama_lengkap']
            session['email']        = user['email']
            session['role']         = user['role']
            flash(f"Selamat datang, {user['nama_lengkap']}!", 'success')
            return redirect(url_for('dashboard.index'))

        flash('Email atau password salah.', 'danger')
        return redirect(url_for('auth.login_page'))

    finally:
        cursor.close()
        db.close()


@auth_bp.route('/register')
def register_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('register.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    var_nama     = request.form.get('nama')
    var_email    = request.form.get('email')
    var_password = request.form.get('password')
    var_konfirm  = request.form.get('konfirmasi_password')

    if var_password != var_konfirm:
        flash('Konfirmasi password tidak cocok.', 'danger')
        return redirect(url_for('auth.register_page'))

    hashed_pw = generate_password_hash(var_password)

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        query = "INSERT INTO users (nama_lengkap, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (var_nama, var_email, hashed_pw))
        db.commit()
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login_page'))

    except Exception as e:
        flash('Email sudah terdaftar atau terjadi kesalahan.', 'danger')
        return redirect(url_for('auth.register_page'))

    finally:
        cursor.close()
        db.close()


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login_page'))


@auth_bp.route('/users')
@login_required
def users_page():
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users ORDER BY id ASC")
        data = cursor.fetchall()
        return render_template('users.html', data=data)
    finally:
        cursor.close()
        db.close()


@auth_bp.route('/users/edit/<int:id>')
@login_required
def edit_user_page(id):
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cursor.fetchone()
        if not user:
            flash('User tidak ditemukan.', 'danger')
            return redirect(url_for('auth.users_page'))
        return render_template('edit_user.html', user=user)
    finally:
        cursor.close()
        db.close()


@auth_bp.route('/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    var_nama = request.form.get('nama_lengkap')
    var_role = request.form.get('role')
    var_pass = request.form.get('password')

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        if var_pass:
            hashed = generate_password_hash(var_pass)
            cursor.execute(
                "UPDATE users SET nama_lengkap=%s, role=%s, password=%s WHERE id=%s",
                (var_nama, var_role, hashed, id)
            )
        else:
            cursor.execute(
                "UPDATE users SET nama_lengkap=%s, role=%s WHERE id=%s",
                (var_nama, var_role, id)
            )
        db.commit()
        flash('Data user berhasil diperbarui.', 'success')
        return redirect(url_for('auth.users_page'))

    except Exception as e:
        flash('Gagal memperbarui data user.', 'danger')
        return redirect(url_for('auth.users_page'))

    finally:
        cursor.close()
        db.close()


@auth_bp.route('/users/hapus/<int:id>')
@login_required
def hapus_user(id):
    if id == session.get('user_id'):
        flash('Tidak dapat menghapus akun yang sedang digunakan.', 'danger')
        return redirect(url_for('auth.users_page'))

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        db.commit()
        flash('User berhasil dihapus.', 'success')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('auth.users_page'))


# ════════════════════════════════════════════════════════════════════════
#  BLUEPRINT: DASHBOARD
# ════════════════════════════════════════════════════════════════════════
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM pelanggan")
        total_pelanggan = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM layanan")
        total_layanan = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM transaksi")
        total_transaksi = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM transaksi WHERE status='Proses'")
        total_proses = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM transaksi WHERE status='Selesai'")
        total_selesai = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) AS total FROM transaksi WHERE status='Diambil'")
        total_diambil = cursor.fetchone()['total']

        hari_ini = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            "SELECT COALESCE(SUM(total_harga), 0) AS total FROM transaksi WHERE tanggal_masuk = %s",
            (hari_ini,)
        )
        pendapatan_hari_ini = cursor.fetchone()['total']

        bulan_ini = datetime.now().strftime('%Y-%m')
        cursor.execute(
            "SELECT COALESCE(SUM(total_harga), 0) AS total FROM transaksi WHERE DATE_FORMAT(tanggal_masuk, '%%Y-%%m') = %s",
            (bulan_ini,)
        )
        pendapatan_bulan_ini = cursor.fetchone()['total']

        cursor.execute("""
            SELECT t.kode_transaksi, p.nama AS nama_pelanggan, l.nama_layanan,
                   t.berat_kg, t.total_harga, t.status, t.tanggal_masuk
            FROM transaksi t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            JOIN layanan   l ON t.layanan_id   = l.id
            ORDER BY t.created_at DESC
            LIMIT 5
        """)
        transaksi_terbaru = cursor.fetchall()

        return render_template(
            'dashboard.html',
            total_pelanggan      = total_pelanggan,
            total_layanan        = total_layanan,
            total_transaksi      = total_transaksi,
            total_proses         = total_proses,
            total_selesai        = total_selesai,
            total_diambil        = total_diambil,
            pendapatan_hari_ini  = pendapatan_hari_ini,
            pendapatan_bulan_ini = pendapatan_bulan_ini,
            transaksi_terbaru    = transaksi_terbaru
        )

    finally:
        cursor.close()
        db.close()


# ════════════════════════════════════════════════════════════════════════
#  BLUEPRINT: PELANGGAN (data master 1)
# ════════════════════════════════════════════════════════════════════════
pelanggan_bp = Blueprint('pelanggan', __name__)


@pelanggan_bp.route('/pelanggan')
@login_required
def index():
    keyword = request.args.get('q', '')
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        if keyword:
            cursor.execute(
                "SELECT * FROM pelanggan WHERE nama LIKE %s OR no_hp LIKE %s ORDER BY nama ASC",
                (f'%{keyword}%', f'%{keyword}%')
            )
        else:
            cursor.execute("SELECT * FROM pelanggan ORDER BY nama ASC")

        data = cursor.fetchall()
        return render_template('pelanggan/index.html', data=data, keyword=keyword)
    finally:
        cursor.close()
        db.close()


@pelanggan_bp.route('/pelanggan/tambah')
@login_required
def tambah_page():
    return render_template('pelanggan/form.html', data=None, action='Tambah')


@pelanggan_bp.route('/pelanggan/tambah', methods=['POST'])
@login_required
def tambah():
    var_nama   = request.form.get('nama')
    var_hp     = request.form.get('no_hp')
    var_alamat = request.form.get('alamat')

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO pelanggan (nama, no_hp, alamat) VALUES (%s, %s, %s)",
            (var_nama, var_hp, var_alamat)
        )
        db.commit()
        flash('Data pelanggan berhasil ditambahkan.', 'success')
    except Exception as e:
        flash('Gagal menambahkan data pelanggan.', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('pelanggan.index'))


@pelanggan_bp.route('/pelanggan/edit/<int:id>')
@login_required
def edit_page(id):
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM pelanggan WHERE id = %s", (id,))
        data = cursor.fetchone()
        if not data:
            flash('Data pelanggan tidak ditemukan.', 'danger')
            return redirect(url_for('pelanggan.index'))
        return render_template('pelanggan/form.html', data=data, action='Edit')
    finally:
        cursor.close()
        db.close()


@pelanggan_bp.route('/pelanggan/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    var_nama   = request.form.get('nama')
    var_hp     = request.form.get('no_hp')
    var_alamat = request.form.get('alamat')

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "UPDATE pelanggan SET nama=%s, no_hp=%s, alamat=%s WHERE id=%s",
            (var_nama, var_hp, var_alamat, id)
        )
        db.commit()
        flash('Data pelanggan berhasil diperbarui.', 'success')
    except Exception as e:
        flash('Gagal memperbarui data pelanggan.', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('pelanggan.index'))


@pelanggan_bp.route('/pelanggan/hapus/<int:id>')
@login_required
def hapus(id):
    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM pelanggan WHERE id = %s", (id,))
        db.commit()
        flash('Data pelanggan berhasil dihapus.', 'success')
    except Exception as e:
        flash('Gagal menghapus. Pelanggan mungkin masih memiliki transaksi.', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('pelanggan.index'))


# ════════════════════════════════════════════════════════════════════════
#  BLUEPRINT: LAYANAN (data master 2)
# ════════════════════════════════════════════════════════════════════════
layanan_bp = Blueprint('layanan', __name__)


@layanan_bp.route('/layanan')
@login_required
def index():
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM layanan ORDER BY nama_layanan ASC")
        data = cursor.fetchall()
        return render_template('layanan/index.html', data=data)
    finally:
        cursor.close()
        db.close()


@layanan_bp.route('/layanan/tambah')
@login_required
def tambah_page():
    return render_template('layanan/form.html', data=None, action='Tambah')


@layanan_bp.route('/layanan/tambah', methods=['POST'])
@login_required
def tambah():
    var_nama  = request.form.get('nama_layanan')
    var_harga = request.form.get('harga_per_kg')
    var_hari  = request.form.get('estimasi_hari')

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "INSERT INTO layanan (nama_layanan, harga_per_kg, estimasi_hari) VALUES (%s, %s, %s)",
            (var_nama, var_harga, var_hari)
        )
        db.commit()
        flash('Data layanan berhasil ditambahkan.', 'success')
    except Exception as e:
        flash('Gagal menambahkan data layanan.', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('layanan.index'))


@layanan_bp.route('/layanan/edit/<int:id>')
@login_required
def edit_page(id):
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM layanan WHERE id = %s", (id,))
        data = cursor.fetchone()
        if not data:
            flash('Data layanan tidak ditemukan.', 'danger')
            return redirect(url_for('layanan.index'))
        return render_template('layanan/form.html', data=data, action='Edit')
    finally:
        cursor.close()
        db.close()


@layanan_bp.route('/layanan/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    var_nama  = request.form.get('nama_layanan')
    var_harga = request.form.get('harga_per_kg')
    var_hari  = request.form.get('estimasi_hari')

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute(
            "UPDATE layanan SET nama_layanan=%s, harga_per_kg=%s, estimasi_hari=%s WHERE id=%s",
            (var_nama, var_harga, var_hari, id)
        )
        db.commit()
        flash('Data layanan berhasil diperbarui.', 'success')
    except Exception as e:
        flash('Gagal memperbarui data layanan.', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('layanan.index'))


@layanan_bp.route('/layanan/hapus/<int:id>')
@login_required
def hapus(id):
    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM layanan WHERE id = %s", (id,))
        db.commit()
        flash('Data layanan berhasil dihapus.', 'success')
    except Exception as e:
        flash('Gagal menghapus. Layanan mungkin masih digunakan dalam transaksi.', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('layanan.index'))


# ════════════════════════════════════════════════════════════════════════
#  BLUEPRINT: TRANSAKSI
# ════════════════════════════════════════════════════════════════════════
transaksi_bp = Blueprint('transaksi', __name__)


def generate_kode():
    """Generate kode transaksi otomatis: TRX-YYYYMMDD-XXXX"""
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        hari_ini = datetime.now().strftime('%Y%m%d')
        cursor.execute(
            "SELECT COUNT(*) AS total FROM transaksi WHERE kode_transaksi LIKE %s",
            (f'TRX-{hari_ini}-%',)
        )
        urutan = cursor.fetchone()['total'] + 1
        return f'TRX-{hari_ini}-{urutan:04d}'
    finally:
        cursor.close()
        db.close()


@transaksi_bp.route('/transaksi')
@login_required
def index():
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.*, p.nama AS nama_pelanggan, l.nama_layanan,
                   u.nama_lengkap AS nama_kasir
            FROM transaksi t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            JOIN layanan   l ON t.layanan_id   = l.id
            JOIN users     u ON t.user_id       = u.id
            ORDER BY t.created_at DESC
        """)
        data = cursor.fetchall()
        return render_template('transaksi/index.html', data=data)
    finally:
        cursor.close()
        db.close()


@transaksi_bp.route('/transaksi/tambah')
@login_required
def tambah_page():
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM pelanggan ORDER BY nama ASC")
        daftar_pelanggan = cursor.fetchall()

        cursor.execute("SELECT * FROM layanan ORDER BY nama_layanan ASC")
        daftar_layanan = cursor.fetchall()

        return render_template(
            'transaksi/form.html',
            daftar_pelanggan = daftar_pelanggan,
            daftar_layanan   = daftar_layanan
        )
    finally:
        cursor.close()
        db.close()


@transaksi_bp.route('/transaksi/tambah', methods=['POST'])
@login_required
def tambah():
    var_pelanggan = request.form.get('pelanggan_id')
    var_layanan   = request.form.get('layanan_id')
    var_berat     = float(request.form.get('berat_kg'))
    var_tgl_masuk = request.form.get('tanggal_masuk')
    var_user      = session['user_id']

    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM layanan WHERE id = %s", (var_layanan,))
        layanan = cursor.fetchone()

        total_harga = float(layanan['harga_per_kg']) * var_berat

        tgl_masuk    = datetime.strptime(var_tgl_masuk, '%Y-%m-%d')
        tgl_estimasi = tgl_masuk + timedelta(days=int(layanan['estimasi_hari']))

        kode = generate_kode()

        cursor2 = db.cursor()
        cursor2.execute("""
            INSERT INTO transaksi
                (kode_transaksi, pelanggan_id, layanan_id, berat_kg,
                 total_harga, status, tanggal_masuk, tanggal_estimasi, user_id)
            VALUES (%s, %s, %s, %s, %s, 'Proses', %s, %s, %s)
        """, (kode, var_pelanggan, var_layanan, var_berat,
              total_harga, var_tgl_masuk, tgl_estimasi.strftime('%Y-%m-%d'), var_user))
        db.commit()
        cursor2.close()

        flash(f'Transaksi {kode} berhasil dibuat.', 'success')
    except Exception as e:
        flash(f'Gagal membuat transaksi: {e}', 'danger')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('transaksi.index'))


@transaksi_bp.route('/transaksi/detail/<int:id>')
@login_required
def detail(id):
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT t.*, p.nama AS nama_pelanggan, p.no_hp, p.alamat,
                   l.nama_layanan, l.harga_per_kg
            FROM transaksi t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            JOIN layanan   l ON t.layanan_id   = l.id
            WHERE t.id = %s
        """, (id,))
        data = cursor.fetchone()
        if not data:
            flash('Transaksi tidak ditemukan.', 'danger')
            return redirect(url_for('transaksi.index'))
        return render_template('transaksi/detail.html', data=data)
    finally:
        cursor.close()
        db.close()


@transaksi_bp.route('/transaksi/status/<int:id>/<string:status>')
@login_required
def ubah_status(id, status):
    status_valid = ['Proses', 'Selesai', 'Diambil']
    if status not in status_valid:
        flash('Status tidak valid.', 'danger')
        return redirect(url_for('transaksi.index'))

    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE transaksi SET status=%s WHERE id=%s", (status, id))
        db.commit()
        flash(f'Status berhasil diubah menjadi {status}.', 'success')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('transaksi.index'))


@transaksi_bp.route('/transaksi/hapus/<int:id>')
@login_required
def hapus(id):
    db     = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM transaksi WHERE id = %s", (id,))
        db.commit()
        flash('Transaksi berhasil dihapus.', 'success')
    finally:
        cursor.close()
        db.close()

    return redirect(url_for('transaksi.index'))


# ════════════════════════════════════════════════════════════════════════
#  BLUEPRINT: LAPORAN
# ════════════════════════════════════════════════════════════════════════
laporan_bp = Blueprint('laporan', __name__)


@laporan_bp.route('/laporan')
@login_required
def index():
    tgl_awal  = request.args.get('tgl_awal', '')
    tgl_akhir = request.args.get('tgl_akhir', '')
    status    = request.args.get('status', '')

    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        query = """
            SELECT t.*, p.nama AS nama_pelanggan, l.nama_layanan
            FROM transaksi t
            JOIN pelanggan p ON t.pelanggan_id = p.id
            JOIN layanan   l ON t.layanan_id   = l.id
            WHERE 1=1
        """
        params = []

        if tgl_awal:
            query += " AND t.tanggal_masuk >= %s"
            params.append(tgl_awal)
        if tgl_akhir:
            query += " AND t.tanggal_masuk <= %s"
            params.append(tgl_akhir)
        if status:
            query += " AND t.status = %s"
            params.append(status)

        query += " ORDER BY t.tanggal_masuk DESC"
        cursor.execute(query, tuple(params))
        data = cursor.fetchall()

        total_pendapatan = sum(float(row['total_harga']) for row in data)
        total_berat      = sum(float(row['berat_kg'])    for row in data)

        return render_template(
            'laporan/index.html',
            data             = data,
            total_pendapatan = total_pendapatan,
            total_berat      = total_berat,
            tgl_awal         = tgl_awal,
            tgl_akhir        = tgl_akhir,
            status           = status
        )

    finally:
        cursor.close()
        db.close()
