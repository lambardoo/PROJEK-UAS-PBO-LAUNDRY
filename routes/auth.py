from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from datetime import datetime, timedelta

from models.database import get_db_connection


# ════════════════════════════════════════════════════════════════════════
#  IMPLEMENTASI OOP :
#  Class & Object, Constructor, Method, Encapsulation,Inheritance, Polymorphism 
# ════════════════════════════════════════════════════════════════════════

class BaseModel:
    table_name = None 
    def __init__(self, id=None):
        self._id = id 

    @property
    def id(self):
        return self._id

    def to_dict(self):
        return {'id': self._id}

    def info(self):
        return f"{self.__class__.__name__} #{self._id}"

    @classmethod
    def count(cls):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute(f"SELECT COUNT(*) AS total FROM {cls.table_name}")
            return cursor.fetchone()['total']
        finally:
            cursor.close()
            db.close()

    @classmethod
    def delete(cls, id):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(f"DELETE FROM {cls.table_name} WHERE id = %s", (id,))
            db.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            db.close()


class Pelanggan(BaseModel):
    table_name = 'pelanggan'

    def __init__(self, nama='', no_hp='', alamat='', id=None):
        super().__init__(id)            
        self.__nama   = nama            
        self.__no_hp  = no_hp
        self.__alamat = alamat

    @property
    def nama(self):   return self.__nama
    @property
    def no_hp(self):  return self.__no_hp
    @property
    def alamat(self): return self.__alamat

    def to_dict(self):                 
        return {'id': self._id, 'nama': self.__nama,
                'no_hp': self.__no_hp, 'alamat': self.__alamat}

    def info(self):                     
        return f"Pelanggan: {self.__nama} ({self.__no_hp})"

    def save(self):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO pelanggan (nama, no_hp, alamat) VALUES (%s, %s, %s)",
                (self.__nama, self.__no_hp, self.__alamat)
            )
            db.commit()
            self._id = cursor.lastrowid
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            db.close()

    def update(self):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE pelanggan SET nama=%s, no_hp=%s, alamat=%s WHERE id=%s",
                (self.__nama, self.__no_hp, self.__alamat, self._id)
            )
            db.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            db.close()


class Layanan(BaseModel):
    table_name = 'layanan'

    def __init__(self, nama_layanan='', harga_per_kg=0, estimasi_hari=1, id=None):
        super().__init__(id)
        self.__nama_layanan  = nama_layanan
        self.__harga_per_kg  = float(harga_per_kg) if harga_per_kg else 0
        self.__estimasi_hari = int(estimasi_hari)   if estimasi_hari else 1

    @property
    def nama_layanan(self):  return self.__nama_layanan
    @property
    def harga_per_kg(self):  return self.__harga_per_kg
    @property
    def estimasi_hari(self): return self.__estimasi_hari

    def to_dict(self):                 
        return {'id': self._id,
                'nama_layanan': self.__nama_layanan,
                'harga_per_kg': self.__harga_per_kg,
                'estimasi_hari': self.__estimasi_hari}

    def info(self):                     
        return f"Layanan: {self.__nama_layanan} - Rp{self.__harga_per_kg:,.0f}/kg"

    def hitung_harga(self, berat_kg):
        return self.__harga_per_kg * float(berat_kg)

    def hitung_estimasi_selesai(self, tanggal_masuk):
        return tanggal_masuk + timedelta(days=self.__estimasi_hari)

    def save(self):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO layanan (nama_layanan, harga_per_kg, estimasi_hari) VALUES (%s, %s, %s)",
                (self.__nama_layanan, self.__harga_per_kg, self.__estimasi_hari)
            )
            db.commit()
            self._id = cursor.lastrowid
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            db.close()

    def update(self):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute(
                "UPDATE layanan SET nama_layanan=%s, harga_per_kg=%s, estimasi_hari=%s WHERE id=%s",
                (self.__nama_layanan, self.__harga_per_kg, self.__estimasi_hari, self._id)
            )
            db.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            db.close()

    @classmethod
    def get_by_id(cls, id):
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM layanan WHERE id = %s", (id,))
            row = cursor.fetchone()
            if not row:
                return None
            return cls(nama_layanan=row['nama_layanan'],
                        harga_per_kg=row['harga_per_kg'],
                        estimasi_hari=row['estimasi_hari'],
                        id=row['id'])
        finally:
            cursor.close()
            db.close()


class Transaksi(BaseModel):
    table_name = 'transaksi'

    def __init__(self, pelanggan_id=None, layanan_id=None, berat_kg=0,
                 total_harga=0, tanggal_masuk='', tanggal_estimasi='',
                 user_id=None, kode_transaksi='', id=None):
        super().__init__(id)
        self.__pelanggan_id     = pelanggan_id
        self.__layanan_id       = layanan_id
        self.__berat_kg         = float(berat_kg) if berat_kg else 0
        self.__total_harga      = float(total_harga) if total_harga else 0
        self.__tanggal_masuk    = tanggal_masuk
        self.__tanggal_estimasi = tanggal_estimasi
        self.__user_id          = user_id
        self.__kode_transaksi   = kode_transaksi

    @property
    def kode_transaksi(self): return self.__kode_transaksi
    @property
    def total_harga(self):    return self.__total_harga

    def to_dict(self):               
        return {'id': self._id,
                'kode_transaksi': self.__kode_transaksi,
                'pelanggan_id': self.__pelanggan_id,
                'layanan_id'  : self.__layanan_id,
                'berat_kg'    : self.__berat_kg,
                'total_harga' : self.__total_harga}

    def info(self):                  
        return f"Transaksi {self.__kode_transaksi}: {self.__berat_kg}kg - Rp{self.__total_harga:,.0f}"

    def save(self):
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO transaksi
                    (kode_transaksi, pelanggan_id, layanan_id, berat_kg,
                     total_harga, status, tanggal_masuk, tanggal_estimasi, user_id)
                VALUES (%s, %s, %s, %s, %s, 'Proses', %s, %s, %s)
            """, (self.__kode_transaksi, self.__pelanggan_id, self.__layanan_id,
                  self.__berat_kg, self.__total_harga, self.__tanggal_masuk,
                  self.__tanggal_estimasi, self.__user_id))
            db.commit()
            self._id = cursor.lastrowid
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def generate_kode():
        db = get_db_connection()
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

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Akses ditolak. Hanya Admin yang diizinkan.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════════════
# AUTH (login, register, logout, manajemen user)
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
    var_nama    = request.form.get('nama')
    var_email   = request.form.get('email')
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
@admin_required
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
@admin_required
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
@admin_required
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
@admin_required
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
# DASHBOARD
# ════════════════════════════════════════════════════════════════════════
dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    db     = get_db_connection()
    cursor = db.cursor(dictionary=True)

    try:
        # Menggunakan method count() dari class OOP (BaseModel.count, di-inherit
        # oleh Pelanggan, Layanan, Transaksi) alih-alih query manual berulang.
        total_pelanggan  = Pelanggan.count()
        total_layanan    = Layanan.count()
        total_transaksi  = Transaksi.count()

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

        # ── Demonstrasi POLYMORPHISM ──────────────────────────────────────
        # Tiga object dari class berbeda (semua turunan BaseModel) disimpan
        # dalam satu list, lalu dipanggil method info() yang sama namanya
        # tapi hasilnya berbeda-beda tergantung class objectnya masing-masing.
        objek_terbaru = []
        if transaksi_terbaru:
            t = transaksi_terbaru[0]
            objek_pelanggan = Pelanggan(nama=t['nama_pelanggan'])
            objek_layanan   = Layanan(nama_layanan=t['nama_layanan'])
            objek_transaksi = Transaksi(kode_transaksi=t['kode_transaksi'],
                                         berat_kg=t['berat_kg'],
                                         total_harga=t['total_harga'])
            for obj in (objek_pelanggan, objek_layanan, objek_transaksi):
                objek_terbaru.append(obj.info())   # method sama, output beda (polymorphism)

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
            transaksi_terbaru    = transaksi_terbaru,
            objek_terbaru        = objek_terbaru
        )

    finally:
        cursor.close()
        db.close()


# ════════════════════════════════════════════════════════════════════════
# PELANGGAN
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

    # Membuat object Pelanggan lalu memanggil method save() miliknya sendiri
    objek_pelanggan = Pelanggan(nama=var_nama, no_hp=var_hp, alamat=var_alamat)

    if objek_pelanggan.save():
        flash('Data pelanggan berhasil ditambahkan.', 'success')
    else:
        flash('Gagal menambahkan data pelanggan.', 'danger')

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

    # Object Pelanggan dengan id yang sudah ada, lalu panggil method update()
    objek_pelanggan = Pelanggan(nama=var_nama, no_hp=var_hp, alamat=var_alamat, id=id)

    if objek_pelanggan.update():
        flash('Data pelanggan berhasil diperbarui.', 'success')
    else:
        flash('Gagal memperbarui data pelanggan.', 'danger')

    return redirect(url_for('pelanggan.index'))


@pelanggan_bp.route('/pelanggan/hapus/<int:id>')
@login_required
def hapus(id):
    # Method delete() diwarisi dari BaseModel, dipakai lewat Pelanggan.delete()
    if Pelanggan.delete(id):
        flash('Data pelanggan berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus. Pelanggan mungkin masih memiliki transaksi.', 'danger')

    return redirect(url_for('pelanggan.index'))


# ════════════════════════════════════════════════════════════════════════
# LAYANAN
# ════════════════════════════════════════════════════════════════════════
layanan_bp = Blueprint('layanan', __name__)


@layanan_bp.route('/layanan')
@login_required
@admin_required
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
@admin_required
def tambah():
    var_nama  = request.form.get('nama_layanan')
    var_harga = request.form.get('harga_per_kg')
    var_hari  = request.form.get('estimasi_hari')

    objek_layanan = Layanan(nama_layanan=var_nama, harga_per_kg=var_harga, estimasi_hari=var_hari)

    if objek_layanan.save():
        flash('Data layanan berhasil ditambahkan.', 'success')
    else:
        flash('Gagal menambahkan data layanan.', 'danger')

    return redirect(url_for('layanan.index'))


@layanan_bp.route('/layanan/edit/<int:id>')
@login_required
@admin_required
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

    objek_layanan = Layanan(nama_layanan=var_nama, harga_per_kg=var_harga,
                             estimasi_hari=var_hari, id=id)

    if objek_layanan.update():
        flash('Data layanan berhasil diperbarui.', 'success')
    else:
        flash('Gagal memperbarui data layanan.', 'danger')

    return redirect(url_for('layanan.index'))


@layanan_bp.route('/layanan/hapus/<int:id>')
@login_required
def hapus(id):
    if Layanan.delete(id):
        flash('Data layanan berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus. Layanan mungkin masih digunakan dalam transaksi.', 'danger')

    return redirect(url_for('layanan.index'))


# ════════════════════════════════════════════════════════════════════════
# TRANSAKSI
# ════════════════════════════════════════════════════════════════════════
transaksi_bp = Blueprint('transaksi', __name__)


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

    try:
        # Ambil object Layanan dari database (classmethod get_by_id)
        objek_layanan = Layanan.get_by_id(var_layanan)
        if not objek_layanan:
            flash('Layanan tidak ditemukan.', 'danger')
            return redirect(url_for('transaksi.tambah_page'))

        # Method milik object Layanan dipakai untuk menghitung harga & estimasi
        total_harga  = objek_layanan.hitung_harga(var_berat)
        tgl_masuk    = datetime.strptime(var_tgl_masuk, '%Y-%m-%d')
        tgl_estimasi = objek_layanan.hitung_estimasi_selesai(tgl_masuk)

        # Static method milik class Transaksi untuk generate kode otomatis
        kode = Transaksi.generate_kode()

        # Membuat object Transaksi lalu menyimpannya lewat method save() miliknya
        objek_transaksi = Transaksi(
            pelanggan_id     = var_pelanggan,
            layanan_id       = var_layanan,
            berat_kg         = var_berat,
            total_harga      = total_harga,
            tanggal_masuk    = var_tgl_masuk,
            tanggal_estimasi = tgl_estimasi.strftime('%Y-%m-%d'),
            user_id          = var_user,
            kode_transaksi   = kode
        )

        if objek_transaksi.save():
            flash(f'Transaksi {objek_transaksi.kode_transaksi} berhasil dibuat.', 'success')
        else:
            flash('Gagal membuat transaksi.', 'danger')

    except Exception as e:
        flash(f'Gagal membuat transaksi: {e}', 'danger')

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
    if Transaksi.delete(id):
        flash('Transaksi berhasil dihapus.', 'success')
    else:
        flash('Gagal menghapus transaksi.', 'danger')

    return redirect(url_for('transaksi.index'))


# ════════════════════════════════════════════════════════════════════════
# LAPORAN
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
