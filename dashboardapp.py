import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date 

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Sistem Logistik Tambak Udang", layout="wide")

# ========== DUMMY DATA (Data Tambahan untuk PR yang Disetujui) ==========
approved_pr_data = pd.DataFrame({
    "PR No.": ["PR-INA/00100", "PR-INA/00100", "PR-INA/00101", "PR-INA/00102"],
    "Deskripsi Barang": ["Pakan Udang Premium Type A", "Obat Antibiotik Air", "Benur Vaname Size 10", "Alat Aerator 5PK"],
    "Qty": [50, 10, 50000, 2],
    "UOM": ["karung", "botol", "ekor", "unit"],
    "Unit Price (Estimasi)": [550000, 120000, 75, 4500000],
    "Total Estimasi": [27500000, 1200000, 3750000, 9000000],
    "Supplier Rekomendasi": ["PT Pakan Jaya", "CV Kimia Air", "Penangkar Benur Sukses", "Toko Peralatan Tambak"],
    "Tgl Target Terima": [date(2025, 12, 1), date(2025, 12, 1), date(2025, 11, 25), date(2025, 12, 10)]
})

# ========== CUSTOM STYLE (Disesuaikan untuk st.radio) ==========
# Memanfaatkan Session State untuk menentukan item yang aktif
menu_items = {
    "Dashboard": "📊 Dashboard",
    "Stok Masuk": "⬆️ Stok Masuk",
    "Stok Keluar": "⬇️ Stok Keluar",
    "Purchase Request": "📝 Purchase Request",
    "Purchase Order": "📄 Purchase Order",
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
    /* PERUBAHAN DI SINI: Warna teks diubah menjadi #fff (putih) dan ditambahkan !important */
    color: #fff !important; 
    transition: all 0.2s ease;
}}

/* Warna hover */
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background-color: #1f2937;
    /* Warna teks saat hover juga di-enforce dengan !important */
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
selected_page = st.sidebar.radio(
    "Navigasi", 
    options=menu_keys,
    index=menu_keys.index(st.session_state.active_page),
    format_func=lambda key: menu_items[key],
    key='app_navigation_radio'
)

# Sinkronisasi Session State dengan pilihan radio
st.session_state.active_page = selected_page


# ========== DUMMY DATA UTAMA (BISA DIGUNAKAN DI DASHBOARD) ==========
shipment_data = pd.DataFrame({
    "Order ID": ["BA92123", "KH92129", "SD92123", "BA92124", "SD92125"],
    "Type of Goods": ["Pakan Udang", "Obat Air", "Benur Vaname", "Vitamin Tambak", "Alat Aerator"],
    "Place of Discharge": ["Situbondo", "Probolinggo", "Lamongan", "Sidoarjo", "Gresik"],
    "Date": ["2025-10-12", "2025-10-15", "2025-10-18", "2025-10-19", "2025-10-20"],
    "Status": ["On Delivery", "Complete", "Pending", "On Delivery", "Pending"]
})


# ========== TAMPILKAN KONTEN BERDASARKAN HALAMAN AKTIF ==========
if st.session_state.active_page == "Dashboard":
    # --- Konten Dashboard (Tidak Berubah) ---
    st.title("📊 Dashboard Logistik Tambak Udang")
    st.write("Selamat datang kembali, Bayu 👋")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'><div class='metric-label'>Total Shipment</div><div class='metric-value'>91.123</div><div class='metric-label'>+100 Packages</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><div class='metric-label'>Pending Shipment</div><div class='metric-value'>12.349</div><div class='metric-label'>-20 Packages</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><div class='metric-label'>Ongoing Shipment</div><div class='metric-value'>32.021</div><div class='metric-label'>+80 Packages</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'><div class='metric-label'>Delivery Shipment</div><div class='metric-value'>46.753</div><div class='metric-label'>+140 Packages</div></div>", unsafe_allow_html=True)

    st.markdown("### 📈 Statistik Pengiriman")
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

    st.markdown("### 🚚 Daftar Pengiriman Barang")
    st.dataframe(shipment_data, use_container_width=True, hide_index=True)


# ========== HALAMAN STOK MASUK ==========
elif st.session_state.active_page == "Stok Masuk":
    # --- Konten Stok Masuk (Tidak Berubah) ---
    st.title("⬆️ Input Stok Masuk")
    with st.form("form_masuk"):
        jenis = st.text_input("Jenis Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        tanggal = st.date_input("Tanggal")
        submitted = st.form_submit_button("Simpan")
    if submitted:
        st.success(f"✅ Data stok masuk '{jenis}' sejumlah {jumlah} berhasil disimpan!")


# ========== HALAMAN STOK KELUAR ==========
elif st.session_state.active_page == "Stok Keluar":
    # --- Konten Stok Keluar (Tidak Berubah) ---
    st.title("⬇️ Input Stok Keluar")
    with st.form("form_keluar"):
        jenis = st.text_input("Jenis Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        tanggal = st.date_input("Tanggal")
        submitted = st.form_submit_button("Simpan")
    if submitted:
        st.success(f"✅ Data stok keluar '{jenis}' sejumlah {jumlah} berhasil disimpan!")


# ========== HALAMAN PURCHASE REQUEST ==========
elif st.session_state.active_page == "Purchase Request":
    st.title("📝 Input Purchase Request")
    st.subheader("Informasi Umum Permintaan")
    
    with st.form("form_purchase_request"):
        col_pr_1, col_pr_2 = st.columns(2)
        
        # Kolom Kiri
        with col_pr_1:
            today_date_str = pd.Timestamp.today().strftime('%Y%m%d') 
            pr_number = st.text_input("Nomor PR", value=f"PR-INA/{today_date_str}-XXX", disabled=True, help="Nomor PR akan di-generate otomatis oleh sistem.")
            category = st.selectbox("Category", ["Sumbawa", "Kantor Bali", "Operasional Lain"], help="Lokasi/Project yang mengajukan PR.")
            # Tanggal Request di-fix-kan hari ini dan disabled
            date_request = st.date_input("Tanggal Request", value=date.today(), disabled=True) 
            prepared_by = st.text_input("Prepared by", help="Nama karyawan yang mengajukan permintaan.")
            
        # Kolom Kanan
        with col_pr_2:
            supplier = st.text_input("Supplier/Vendor Direkomendasikan")
            exp_receive_date = st.date_input("Tanggal Penerimaan Target")
            contact_person = st.text_input("Kontak Supplier (Opsional)", help="Nomor Telepon atau Email Supplier.")
            reason = st.text_area("Alasan / Tujuan Pembelian", help="Contoh: Pembelian Alat Pencuci Mobil, Maintenance Excavator.")
        
        st.markdown("---")
        st.subheader("Detail Item yang Dibutuhkan")
        
        # Grid untuk detail item
        col_item_1, col_item_2, col_item_3, col_item_4 = st.columns(4)
        with col_item_1:
            description = st.text_input("Deskripsi Barang/Jasa")
        with col_item_2:
            qty = st.number_input("Kuantitas (Qty)", min_value=1, value=1)
        with col_item_3:
            uom = st.text_input("Satuan (UOM)", value="unit")
        with col_item_4:
            unit_price = st.number_input("Harga Satuan (Unit Price)", min_value=0, format="%i")

        total_price = qty * unit_price
        st.info(f"**Total Harga Estimasi:** Rp {total_price:,.0f}")
        
        st.markdown("---")
        submitted = st.form_submit_button("Submit Purchase Request")
        
    if submitted:
        if description and prepared_by and supplier and reason and total_price > 0:
            st.success(f"""
            ✅ Purchase Request **{pr_number}** berhasil dibuat dan menunggu persetujuan!
            - Barang: {description} ({qty} {uom})
            - Total Estimasi: Rp {total_price:,.0f}
            """)
        else:
            st.error("⚠️ Mohon isi semua kolom penting.")

# ========== HALAMAN PURCHASE ORDER (BARU) ==========
elif st.session_state.active_page == "Purchase Order":
    st.title("📄 Pembuatan Purchase Order")
    st.subheader("Daftar Item Purchase Request yang Siap Dibuatkan PO")

    st.info("💡 Data di bawah adalah Purchase Request yang statusnya sudah **Approved** dan siap diproses menjadi Purchase Order.")
    
    # Menampilkan data PR yang sudah disetujui (Dummy Data)
    st.markdown("### Item PR Approved")
    edited_df = st.data_editor(
        approved_pr_data,
        column_config={
            "select": st.column_config.CheckboxColumn(
                "Pilih",
                help="Pilih item yang akan dibuatkan Purchase Order",
                default=False,
            ),
            "Total Estimasi": st.column_config.NumberColumn(
                "Total Estimasi (Rp)",
                format="Rp %,.0f",
            ),
            "Unit Price (Estimasi)": st.column_config.NumberColumn(
                "Unit Price (Rp)",
                format="Rp %,.0f",
            ),
            "Tgl Target Terima": st.column_config.DateColumn(
                "Tgl Target Terima",
                format="YYYY/MM/DD",
            )
        },
        disabled=("PR No.", "Deskripsi Barang", "Qty", "UOM", "Total Estimasi", "Supplier Rekomendasi"),
        use_container_width=True,
        hide_index=True
    )

    # PERBAIKAN: Menggunakan bracket notation ['select'] untuk menghindari AttributeError
    selected_items = edited_df[edited_df['select']] 
    
    st.markdown("---")

    if not selected_items.empty:
        st.subheader(f"Form Purchase Order ({len(selected_items)} Item Terpilih)")
        
        pr_numbers = selected_items['PR No.'].unique()
        suppliers = selected_items['Supplier Rekomendasi'].unique()

        st.warning(f"Membuat PO untuk Item dari PR No.: **{', '.join(pr_numbers)}**")
        
        if len(suppliers) > 1:
            st.error("⚠️ Item yang dipilih memiliki lebih dari satu supplier. Harap pilih item dari satu supplier saja.")
        
        else:
            with st.form("form_purchase_order"):
                col_po_1, col_po_2 = st.columns(2)
                
                with col_po_1:
                    po_number = st.text_input("Nomor PO", value=f"PO-INA/{pd.Timestamp.today().strftime('%Y%m%d')}-XXX", disabled=True)
                    po_supplier = st.text_input("Supplier PO", value=suppliers[0] if suppliers.size > 0 else "N/A", disabled=True)
                    po_date = st.date_input("Tanggal PO", value=date.today(), disabled=True)
                
                with col_po_2:
                    st.text_input("Termin Pembayaran", value="30 Hari Setelah Invoice")
                    st.text_input("Alamat Pengiriman", value="Tambak Situbondo")
                    st.text_input("PIC Penerima Barang", value="Bayu Logistik")
                
                st.markdown("---")
                st.markdown("#### Detail Item Finalisasi Harga")
                
                final_df = selected_items.copy()
                final_df['Harga Final (Rp)'] = final_df['Unit Price (Estimasi)']
                final_df = final_df.drop(columns=['select', 'Unit Price (Estimasi)', 'Total Estimasi'])

                # Menampilkan item yang dipilih dan memungkinkan input harga final
                st.dataframe(
                    final_df.style.format({
                        'Harga Final (Rp)': "Rp {:,.0f}", 
                        'Qty': "{:,.0f}"}),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                submitted = st.form_submit_button("Generate Purchase Order")
                
                if submitted:
                    st.success(f"🎉 Purchase Order **{po_number}** untuk supplier **{po_supplier}** berhasil dibuat!")
                    st.balloons()
    else:
        st.warning("Silakan pilih minimal satu item PR yang sudah di-approve di tabel di atas untuk membuat Purchase Order baru.")


# ========== HALAMAN SETTING ==========
elif st.session_state.active_page == "Setting":
    # --- Konten Setting (Tidak Berubah) ---
    st.title("⚙️ Pengaturan Sistem")
    st.write("Tempat untuk konfigurasi API Key, database, dan backup data.")
