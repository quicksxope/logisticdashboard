import streamlit as st
import pandas as pd
import plotly.graph_objects as go
# Import untuk Google Sheets (perlu instalasi: pip install st-gsheets-connection)
from streamlit_gsheets_connection import GSheetsConnection

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Sistem Logistik Tambak Udang", layout="wide")

# ========== INICIALISASI KONEKSI GOOGLE SHEETS ==========
try:
    # Menginisialisasi koneksi Google Sheets
    conn = st.connection('gsheets_logistik', type=GSheetsConnection)
    
    # URL Google Sheet Anda (Ganti dengan URL sheet Anda)
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1B-iT5Q_b_d_l_X_X_X_X_X_X_X_X_X/edit#gid=0"
    
    # Fungsi untuk memuat data dari Google Sheet
    @st.cache_data(ttl=5) # Cache data selama 5 detik
    def load_data():
        # Sheet_name di sini adalah nama tab (worksheet) di Google Sheets
        # Contoh: Sheet yang menampung data pengiriman
        return conn.read(spreadsheet=SHEET_URL, worksheet="DataPengiriman", usecols=list(range(5)))

    # Fungsi untuk menambahkan data baru ke Sheet
    def add_data(data: dict, worksheet_name: str):
        # Membaca data yang ada
        existing_data = conn.read(spreadsheet=SHEET_URL, worksheet=worksheet_name)
        
        # Membuat DataFrame baru dari data input
        new_row_df = pd.DataFrame([data])
        
        # Menggabungkan data lama dan data baru
        updated_df = pd.concat([existing_data, new_row_df], ignore_index=True)
        
        # Menulis kembali seluruh data ke Google Sheet
        conn.write(
            spreadsheet=SHEET_URL,
            worksheet=worksheet_name,
            data=updated_df
        )
        return True

    # Muat data untuk dashboard
    shipment_data = load_data()

except Exception as e:
    # Handle error jika kredensial belum dikonfigurasi atau koneksi gagal
    st.sidebar.warning("⚠️ Google Sheets API belum dikonfigurasi. Menggunakan data dummy.")
    
    # ========== DUMMY DATA (Fallback) ==========
    shipment_data = pd.DataFrame({
        "Order ID": ["BA92123", "KH92129", "SD92123", "BA92124", "SD92125"],
        "Type of Goods": ["Pakan Udang", "Obat Air", "Benur Vaname", "Vitamin Tambak", "Alat Aerator"],
        "Place of Discharge": ["Situbondo", "Probolinggo", "Lamongan", "Sidoarjo", "Gresik"],
        "Date": ["2025-10-12", "2025-10-15", "2025-10-18", "2025-10-19", "2025-10-20"],
        "Status": ["On Delivery", "Complete", "Pending", "On Delivery", "Pending"]
    })
    
    # Placeholder function jika koneksi gagal
    def add_data(data: dict, worksheet_name: str):
        st.error(f"❌ Gagal menyimpan ke Google Sheets: Koneksi tidak tersedia.")
        return False
    
# ========== CUSTOM STYLE (Disesuaikan untuk st.radio) ==========
# Memanfaatkan Session State untuk menentukan item yang aktif
menu_items = {
    "Dashboard": "📊 Dashboard",
    "Stok Masuk": "⬆️ Stok Masuk",
    "Stok Keluar": "⬇️ Stok Keluar",
    "Setting": "⚙️ Setting"
}

# Inisialisasi session state untuk halaman aktif
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# CSS untuk styling custom dan override Streamlit Radio
st.markdown(f"""
<style>
/* Sidebar styling */
[data-testid="stSidebar"] {{
    background-color: #111827;
    padding-top: 2rem;
    width: 260px;
}}
.sidebar-title {{
    color: white;
    font-weight: bold;
    font-size: 22px;
    text-align: left;
    padding-left: 15px;
    margin-bottom: 25px;
}}

/* Custom Styling for Streamlit Radio Buttons to look like menu items */
/* Menghapus padding default untuk container radio */
[data-testid="stSidebar"] [data-testid="stForm"] > div > div > div {{
    padding: 0 !important;
}}

/* Target setiap opsi radio */
[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    /* Menghilangkan radio circle (Titik/Lingkaran Radio) */
    display: flex;
    align-items: center;
    
    /* Menggunakan styling .menu-item yang kamu buat */
    margin: 6px 12px;
    border-radius: 10px;
    padding: 10px 20px;
    /* Warna default untuk label */
    color: #fff !important; 
    transition: all 0.2s ease;
}}

/* FIX: Target semua elemen teks (span, div) di dalam label untuk memaksa warna putih */
/* Ini adalah trik yang paling kuat untuk mengatasi penimpaan warna Streamlit */
[data-testid="stSidebar"] [data-testid="stRadio"] label * {{
    color: #fff !important;
}}
/* END FIX */

/* Warna hover */
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background-color: #1f2937;
    color: #fff !important; 
}}


/* Target container radio circle */
[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {{
    display: none !important; /* Hilangkan radio circle sepenuhnya */
}}

/* Gaya untuk opsi yang aktif (terpilih) */
[data-testid="stSidebar"] [data-testid="stRadio"] label.st-emotion-cache-1bvk7l-container:has(input[aria-checked="true"]) {{
    background-color: #374151; /* Warna aktif */
    color: #fff !important; /* Di-enforce juga di sini dengan !important */
    font-weight: 600;
}}

/* Metric cards */
.metric-card {{
    background-color: #1F2937;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
}}
.metric-value {{
    font-size: 28px;
    font-weight: bold;
}}
.metric-label {{
    font-size: 14px;
    color: #9CA3AF;
}}

/* Table styling */
thead tr th {{
    background-color: #374151 !important;
    color: white !important;
    text-align: center !important;
}}
tbody tr td {{
    text-align: center !important;
}}

/* Main background */
.stApp {{
    background-color: #F9FAFB;
}}
</style>
""", unsafe_allow_html=True)


# ========== SIDEBAR MENU (FIXED) ==========
st.sidebar.markdown("<div class='sidebar-title'>🦐 Tambak Logistik</div>", unsafe_allow_html=True)

# List kunci untuk opsi radio
menu_keys = list(menu_items.keys())

# Menggunakan st.sidebar.radio untuk navigasi yang berfungsi penuh
# format_func digunakan untuk menampilkan label dengan ikon (e.g., "📊 Dashboard")
# key memastikan state navigasi tersimpan
selected_page = st.sidebar.radio(
    "Navigasi", # Label ini disembunyikan oleh CSS
    options=menu_keys,
    index=menu_keys.index(st.session_state.active_page),
    format_func=lambda key: menu_items[key],
    key='app_navigation_radio'
)

# Sinkronisasi Session State dengan pilihan radio
st.session_state.active_page = selected_page


# ========== TAMPILKAN KONTEN BERDASARKAN HALAMAN AKTIF ==========
if st.session_state.active_page == "Dashboard":
    st.title("📊 Dashboard Logistik Tambak Udang")
    st.write("Selamat datang kembali, Bayu 👋")

    # Ambil data dari data frame yang sudah dimuat (baik dari GSheets atau dummy)
    total_shipment = len(shipment_data)
    pending_shipment = len(shipment_data[shipment_data['Status'] == 'Pending'])
    ongoing_shipment = len(shipment_data[shipment_data['Status'] == 'On Delivery'])
    delivery_shipment = len(shipment_data[shipment_data['Status'] == 'Complete'])


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Shipment</div><div class='metric-value'>{total_shipment:,}</div><div class='metric-label'></div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Pending Shipment</div><div class='metric-value'>{pending_shipment:,}</div><div class='metric-label'></div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Ongoing Shipment</div><div class='metric-value'>{ongoing_shipment:,}</div><div class='metric-label'></div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Delivery Shipment</div><div class='metric-value'>{delivery_shipment:,}</div><div class='metric-label'></div></div>", unsafe_allow_html=True)

    st.markdown("### 📈 Daftar Pengiriman Barang")
    st.dataframe(shipment_data, use_container_width=True, hide_index=True)

    # Note: Grafik statistik masih menggunakan dummy data untuk x dan y karena data GSheet yang dimuat mungkin tidak memiliki kolom waktu yang konsisten.

    st.markdown("### 📈 Statistik Pengiriman (Dummy Data)")
    shipment_stats = go.Figure()
    shipment_stats.add_trace(go.Scatter(x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
                                         y=[30, 40, 45, 50, 65, 70, 80, 81, 90],
                                         name="Total Shipment",
                                         line=dict(color="#636EFA", width=3)))
    shipment_stats.add_trace(go.Scatter(x=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
                                         y=[20, 25, 35, 40, 55, 65, 70, 78, 85],
                                         name="Delivery Shipment",
                                         line=dict(color="#00CC96", width=3)))
    shipment_stats.update_layout(template="plotly_white", height=350, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(shipment_stats, use_container_width=True)


# ========== HALAMAN STOK MASUK ==========
elif st.session_state.active_page == "Stok Masuk":
    st.title("⬆️ Input Stok Masuk")
    with st.form("form_masuk"):
        st.write("Silakan masukkan detail stok yang masuk.")
        order_id = st.text_input("ID Pesanan (Contoh: BA92123)")
        jenis = st.text_input("Jenis Barang (Contoh: Pakan Udang)")
        jumlah = st.number_input("Jumlah", min_value=1, format="%d")
        lokasi = st.text_input("Lokasi Gudang Masuk (Contoh: Surabaya)")
        tanggal = st.date_input("Tanggal Masuk").strftime("%Y-%m-%d")
        
        submitted = st.form_submit_button("Simpan Data Stok Masuk")
        
    if submitted:
        if order_id and jenis and jumlah and lokasi:
            new_data = {
                "Order ID": order_id,
                "Type of Goods": jenis,
                "Place of Discharge": lokasi,
                "Date": tanggal,
                "Status": "Complete (Stock In)" # Status khusus untuk Stok Masuk
            }
            if add_data(new_data, "DataStokMasuk"):
                st.success(f"✅ Data stok masuk '{jenis}' sejumlah {jumlah} berhasil disimpan ke Google Sheets!")
                # st.rerun() # Batalkan komen ini setelah GSheet API dikonfigurasi
        else:
            st.error("Semua field harus diisi.")


# ========== HALAMAN STOK KELUAR ==========
elif st.session_state.active_page == "Stok Keluar":
    st.title("⬇️ Input Stok Keluar")
    with st.form("form_keluar"):
        st.write("Silakan masukkan detail pengiriman yang keluar.")
        order_id = st.text_input("ID Pesanan (Contoh: KH92129)")
        jenis = st.text_input("Jenis Barang (Contoh: Benur Vaname)")
        jumlah = st.number_input("Jumlah", min_value=1, format="%d")
        lokasi_tujuan = st.text_input("Lokasi Tambak/Tujuan (Contoh: Situbondo)")
        tanggal = st.date_input("Tanggal Keluar/Pengiriman").strftime("%Y-%m-%d")

        submitted = st.form_submit_button("Simpan Data Stok Keluar")

    if submitted:
        if order_id and jenis and jumlah and lokasi_tujuan:
            new_data = {
                "Order ID": order_id,
                "Type of Goods": jenis,
                "Place of Discharge": lokasi_tujuan,
                "Date": tanggal,
                "Status": "On Delivery" # Status khas untuk Stok Keluar
            }
            if add_data(new_data, "DataPengiriman"):
                st.success(f"✅ Data stok keluar '{jenis}' sejumlah {jumlah} berhasil disimpan ke Google Sheets!")
                # st.rerun() # Batalkan komen ini setelah GSheet API dikonfigurasi
        else:
            st.error("Semua field harus diisi.")


# ========== HALAMAN SETTING ==========
elif st.session_state.active_page == "Setting":
    st.title("⚙️ Pengaturan Sistem")
    st.write("Tempat untuk konfigurasi API Key, database, dan backup data.")
    st.markdown("""
        ### Konfigurasi Google Sheets API

        Untuk mengaktifkan koneksi Google Sheets, Anda harus:
        1.  **Instalasi:** Pastikan pustaka `streamlit-gsheets-connection` sudah terinstal.
        2.  **Buat Google Sheet:** Buat Google Sheet baru dengan tab (worksheet) bernama `DataPengiriman` dan `DataStokMasuk`.
        3.  **URL Sheet:** Ganti nilai `SHEET_URL` di dalam kode dengan URL Google Sheet Anda.
        4.  **Kredensial Streamlit:** Tambahkan kredensial akun layanan (Service Account) ke file `.streamlit/secrets.toml` Anda. Kredensial ini didapatkan dari Google Cloud Platform (GCP).

        Jika langkah 4 sudah dilakukan, aplikasi akan secara otomatis memuat dan menyimpan data ke Google Sheets Anda.
    """)
