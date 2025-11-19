import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from collections import defaultdict

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Sistem Logistik Tambak Udang", layout="wide")

# ========== DUMMY DATA (Data Tambahan untuk PR yang Disetujui) ==========
approved_pr_data = pd.DataFrame({
    "PR No.": ["PR-INA/00100", "PR-INA/00100", "PR-INA/00101", "PR-INA/00102"],
    "Deskripsi Barang": ["Pakan Udang Premium Type A", "Obat Antibiotik Air", "Benur Vaname Size 10", "Alat Aerator 5PK"],
    "Qty": [50, 10, 50000, 2],
    "UOM": ["karung", "botol", "ekor", "unit"],
    # Harga Final (misalnya dari negosiasi)
    "Unit Price (Final)": [540000, 115000, 70, 4400000],
    "Total Final": [27000000, 1150000, 3500000, 8800000],
    "Supplier Rekomendasi": ["PT Pakan Jaya", "CV Kimia Air", "Penangkar Benur Sukses", "Toko Peralatan Tambak"],
    "Tgl Target Terima": [date(2025, 12, 1), date(2025, 12, 1), date(2025, 11, 25), date(2025, 12, 10)]
})

# ========== CUSTOM STYLE (Disesuaikan untuk st.radio) ==========
menu_items = {
    "Dashboard": "📊 Dashboard",
    "Inventori": "📦 Inventori", # NEW MENU ITEM
    "Stok Masuk": "⬆️ Stok Masuk",
    "Stok Keluar": "⬇️ Stok Keluar",
    "Purchase Request": "📝 Purchase Request",
    "Purchase Order": "📄 Purchase Order",
    "Setting": "⚙️ Setting"
}

# Inisialisasi session state untuk halaman aktif
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

# Inisialisasi session state untuk menyimpan daftar item PR
if "pr_items" not in st.session_state:
    st.session_state.pr_items = []

# Inisialisasi session state untuk menyimpan daftar transaksi stok (In/Out)
if "stock_history" not in st.session_state:
    # Default data: 50 karung pakan masuk, 10 karung keluar
    st.session_state.stock_history = [
        {"Jenis Barang": "Pakan Udang Premium Type A", "Qty": 50, "UOM": "karung", "Type": "Masuk", "Date": date(2025, 10, 10)},
        {"Jenis Barang": "Benur Vaname Size 10", "Qty": 100000, "UOM": "ekor", "Type": "Masuk", "Date": date(2025, 10, 11)},
        {"Jenis Barang": "Pakan Udang Premium Type A", "Qty": -10, "UOM": "karung", "Type": "Keluar", "Date": date(2025, 10, 20)},
        {"Jenis Barang": "Obat Antibiotik Air", "Qty": 5, "UOM": "botol", "Type": "Masuk", "Date": date(2025, 10, 22)},
    ]

# Inisialisasi Master Data (untuk halaman Setting)
if "master_suppliers" not in st.session_state:
    st.session_state.master_suppliers = ["PT Pakan Jaya", "CV Kimia Air", "Penangkar Benur Sukses", "Toko Peralatan Tambak"]
if "master_categories" not in st.session_state:
    st.session_state.master_categories = ["Pakan", "Obat/Kimia", "Benur", "Peralatan"]


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
    color: white; /* Sidebar title tetap putih */
    font-weight: bold;
    font-size: 22px;
    text-align: left;
    padding-left: 15px;
    margin-bottom: 25px;
}}

/* Custom Styling for Streamlit Radio Buttons to look like menu items */
[data-testid="stSidebar"] [data-testid="stForm"] > div > div > div {{
    padding: 0 !important;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label {{
    display: flex;
    align-items: center;
    margin: 6px 12px;
    border-radius: 10px;
    padding: 10px 20px;
    color: #fff !important; 
    transition: all 0.2s ease;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
    background-color: #1f2937;
    color: #fff !important;
}}

[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {{
    display: none !important; 
}}

/* Gaya untuk opsi yang aktif (terpilih) */
[data-testid="stSidebar"] [data-testid="stRadio"] label.st-emotion-cache-1bvk7l-container:has(input[aria-checked="true"]) {{
    background-color: #374151;
    color: #fff !important; 
    font-weight: 600;
}}

/* Metric cards (Main dashboard) */
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

/* Grand Total Card (for PO) */
.grand-total-card {{
    background-color: #34D399; /* Green/Teal */
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 20px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
}}
.grand-total-label {{
    font-size: 16px;
    font-weight: 500;
}}
.grand-total-value {{
    font-size: 36px;
    font-weight: bold;
}}


/* Table styling (Enhancing Streamlit Dataframe) */
thead tr th {{
    background-color: #374151 !important;
    color: white !important;
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

menu_keys = list(menu_items.keys())
selected_page = st.sidebar.radio(
    "Navigasi", 
    options=menu_keys,
    index=menu_keys.index(st.session_state.active_page),
    format_func=lambda key: menu_items[key],
    key='app_navigation_radio'
)

st.session_state.active_page = selected_page

# DUMMY DATA UTAMA (BISA DIGUNAKAN DI DASHBOARD)
shipment_data = pd.DataFrame({
    "Order ID": ["BA92123", "KH92129", "SD92123", "BA92124", "SD92125"],
    "Jenis Barang": ["Pakan Udang", "Obat Air", "Benur Vaname", "Vitamin Tambak", "Alat Aerator"],
    "Lokasi Tujuan": ["Situbondo", "Probolinggo", "Lamongan", "Sidoarjo", "Gresik"],
    "Tanggal Kirim": ["2025-10-12", "2025-10-15", "2025-10-18", "2025-10-19", "2025-10-20"],
    "Status": ["On Delivery", "Complete", "Pending", "On Delivery", "Pending"]
})


# ========== FUNGSI UNTUK MENGHAPUS ITEM PR ==========
def delete_pr_item(index):
    """Menghapus item PR dari list berdasarkan index."""
    if 0 <= index < len(st.session_state.pr_items):
        st.session_state.pr_items.pop(index)
        st.rerun() 

# ========== FUNGSI UNTUK MENGHITUNG INVENTORI AKTIF ==========
def calculate_inventory_balance():
    """Menghitung saldo inventori aktif dari riwayat transaksi."""
    balance = defaultdict(lambda: {"Qty": 0, "UOM": "", "Category": "Uncategorized"})
    
    for item in st.session_state.stock_history:
        name = item["Jenis Barang"]
        qty = item["Qty"]
        
        # Tambahkan ke saldo (qty sudah positif untuk masuk dan negatif untuk keluar)
        balance[name]["Qty"] += qty
        balance[name]["UOM"] = item["UOM"] # Asumsi UOM untuk barang yang sama selalu sama
        
    # Konversi ke list of dicts/DataFrame untuk ditampilkan
    inventory_list = []
    for name, data in balance.items():
        if data["Qty"] != 0: # Hanya tampilkan saldo > 0
            inventory_list.append({
                "Jenis Barang": name,
                "Qty Aktif": data["Qty"],
                "Satuan": data["UOM"]
            })
            
    return pd.DataFrame(inventory_list)

# ========== TAMPILKAN KONTEN BERDASARKAN HALAMAN AKTIF ==========
if st.session_state.active_page == "Dashboard":
    # --- Konten Dashboard ---
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

    st.markdown("### 🚚 Daftar Pengiriman Barang Terbaru")
    st.dataframe(shipment_data, use_container_width=True, hide_index=True)


# ===============================================
# ========== HALAMAN INVENTORI AKTIF (NEW) ==========
# ===============================================
elif st.session_state.active_page == "Inventori":
    st.title("📦 Inventori Aktif (Saldo Stok Saat Ini)")
    st.write("Ringkasan saldo stok per jenis barang di gudang utama.")
    
    inventory_df = calculate_inventory_balance()
    
    if not inventory_df.empty:
        st.markdown(f"**Total Item Unik:** {len(inventory_df)}")
        
        st.dataframe(
            inventory_df.style.format({
                'Qty Aktif': "{:,.0f}"
            }),
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Qty Aktif": st.column_config.NumberColumn("Qty Aktif", help="Saldo stok saat ini", format="%i"),
            }
        )
        
        st.markdown("---")
        st.info("Saldo ini dihitung dari akumulasi semua transaksi **Stok Masuk** dikurangi **Stok Keluar** yang tercatat.")
    else:
        st.warning("Inventori saat ini kosong. Silakan input transaksi Stok Masuk terlebih dahulu.")


# ===============================================
# ========== HALAMAN STOK MASUK (UPDATED) ==========
# ===============================================
elif st.session_state.active_page == "Stok Masuk":
    st.title("⬆️ Input Stok Masuk")
    
    with st.form("form_masuk"):
        col_in_1, col_in_2 = st.columns(2)
        with col_in_1:
            jenis = st.text_input("Jenis Barang*")
            jumlah = st.number_input("Jumlah (Qty)*", min_value=1, value=1)
            uom = st.text_input("Satuan (UOM)*", value="unit")
        with col_in_2:
            tanggal = st.date_input("Tanggal Transaksi*", value=date.today())
            supplier_in = st.selectbox("Supplier/Sumber", options=["(Pilih Supplier)"] + st.session_state.master_suppliers)
        
        submitted = st.form_submit_button("Simpan Stok Masuk")
        
    if submitted:
        if jenis and jumlah > 0 and uom and supplier_in != "(Pilih Supplier)":
            st.session_state.stock_history.append({
                "Jenis Barang": jenis, 
                "Qty": jumlah, # Qty positif untuk Masuk
                "UOM": uom,
                "Type": "Masuk", 
                "Date": tanggal,
                "Supplier/Pond": supplier_in
            })
            st.success(f"✅ Data stok masuk **'{jenis}'** sejumlah **{jumlah} {uom}** berhasil disimpan!")
            st.rerun()
        else:
            st.error("⚠️ Mohon lengkapi semua kolom yang wajib diisi, termasuk Jenis Barang, Jumlah, Satuan, dan Supplier.")

    st.markdown("---")
    st.subheader("History Stok Masuk Terbaru")
    
    in_history_df = pd.DataFrame([item for item in st.session_state.stock_history if item["Type"] == "Masuk"])
    
    if not in_history_df.empty:
        # Tampilkan hanya kolom yang relevan
        display_df = in_history_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
        display_df = display_df.rename(columns={"Jenis Barang": "Barang", "Qty": "Jumlah", "UOM": "Satuan", "Date": "Tanggal"})
        
        st.dataframe(
            display_df[['Tanggal', 'Barang', 'Jumlah', 'Satuan', 'Supplier/Pond']], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Jumlah": st.column_config.NumberColumn("Jumlah", format="%i"),
                "Tanggal": st.column_config.DateColumn("Tanggal", format="YYYY/MM/DD")
            }
        )
    else:
        st.info("Belum ada riwayat Stok Masuk.")


# ===============================================
# ========== HALAMAN STOK KELUAR (UPDATED) ==========
# ===============================================
elif st.session_state.active_page == "Stok Keluar":
    st.title("⬇️ Input Stok Keluar")
    
    inventory_df = calculate_inventory_balance()
    item_options = ["(Pilih Barang)"] + inventory_df['Jenis Barang'].tolist()
    
    with st.form("form_keluar"):
        col_out_1, col_out_2 = st.columns(2)
        with col_out_1:
            jenis = st.selectbox("Jenis Barang*", options=item_options, key="keluar_jenis")
            
            # Mendapatkan UOM dan stok max
            uom_value = ""
            max_qty = 0
            if jenis != "(Pilih Barang)":
                current_stock = inventory_df[inventory_df['Jenis Barang'] == jenis].iloc[0]
                max_qty = current_stock['Qty Aktif']
                uom_value = current_stock['Satuan']
                st.info(f"Stok Tersedia: **{max_qty:,.0f} {uom_value}**")
            
            jumlah = st.number_input(f"Jumlah (Qty)* ({uom_value})", min_value=1, max_value=max_qty if max_qty > 0 else 100000, value=1, key="keluar_jumlah")
        
        with col_out_2:
            tanggal = st.date_input("Tanggal Transaksi*", value=date.today())
            lokasi = st.selectbox("Lokasi Tujuan/Kolam", options=["(Pilih Lokasi)", "Kolam A1", "Kolam A2", "Kolam B1", "Gudang Cabang"])
            
        submitted = st.form_submit_button("Simpan Stok Keluar")
        
    if submitted:
        if jenis != "(Pilih Barang)" and jumlah > 0 and lokasi != "(Pilih Lokasi)":
            if jumlah > max_qty:
                st.error("⚠️ Gagal: Jumlah stok keluar melebihi saldo yang tersedia. Harap periksa kembali.")
            else:
                st.session_state.stock_history.append({
                    "Jenis Barang": jenis, 
                    "Qty": -jumlah, # Qty negatif untuk Keluar
                    "UOM": uom_value,
                    "Type": "Keluar", 
                    "Date": tanggal,
                    "Supplier/Pond": lokasi # Menggunakan kolom yang sama untuk tujuan
                })
                st.success(f"✅ Data stok keluar **'{jenis}'** sejumlah **{jumlah} {uom_value}** berhasil disimpan untuk **{lokasi}**!")
                st.rerun()
        else:
            st.error("⚠️ Mohon lengkapi semua kolom yang wajib diisi, termasuk Jenis Barang dan Lokasi Tujuan.")

    st.markdown("---")
    st.subheader("History Stok Keluar Terbaru")
    
    out_history_df = pd.DataFrame([item for item in st.session_state.stock_history if item["Type"] == "Keluar"])
    
    if not out_history_df.empty:
        # Tampilkan hanya kolom yang relevan dan ubah Qty menjadi positif untuk tampilan
        display_df = out_history_df.sort_values(by="Date", ascending=False).reset_index(drop=True)
        display_df['Qty Keluar'] = display_df['Qty'].abs()
        display_df = display_df.rename(columns={"Jenis Barang": "Barang", "UOM": "Satuan", "Date": "Tanggal", "Supplier/Pond": "Lokasi Tujuan"})
        
        st.dataframe(
            display_df[['Tanggal', 'Barang', 'Qty Keluar', 'Satuan', 'Lokasi Tujuan']], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Qty Keluar": st.column_config.NumberColumn("Jumlah", format="%i"),
                "Tanggal": st.column_config.DateColumn("Tanggal", format="YYYY/MM/DD")
            }
        )
    else:
        st.info("Belum ada riwayat Stok Keluar.")


# ===============================================
# ========== HALAMAN PURCHASE REQUEST FULL =====
# ===============================================
elif st.session_state.active_page == "Purchase Request":
    st.title("📝 Input Purchase Request")
    st.write("Silakan input setiap item barang satu per satu.")

    # ---------------------------
    # 1️⃣ Form Input Item PR
    # ---------------------------
    with st.expander("➕ Tambah Item Baru", expanded=True):
        with st.form("form_add_item", clear_on_submit=True):
            st.markdown("### Detail Item yang Dibutuhkan")
            
            col0, col1, col2, col3, col4 = st.columns([2, 3, 1.5, 1, 2.5])
            with col0:
                pr_number_item = st.text_input("Nomor PR (Per Item)*", key="item_pr_number")
            with col1:
                description = st.text_input("Deskripsi Barang/Jasa*")
            with col2:
                qty = st.number_input("Qty*", min_value=1, value=1, key="item_qty")
            with col3:
                uom = st.text_input("UOM*", value="unit", key="item_uom")
            with col4:
                unit_price = st.number_input("Harga Satuan (Rp)*", min_value=0, format="%i", key="item_price")
            
            col_sup1, col_sup2 = st.columns(2)
            with col_sup1:
                supplier = st.selectbox("Supplier/Vendor*", options=["(Pilih Supplier)"] + st.session_state.master_suppliers)
            with col_sup2:
                exp_receive_date = st.date_input("Tanggal Target Terima*", min_value=date.today())
            
            total_price = qty * unit_price
            st.info(f"Total Harga Estimasi: Rp {total_price:,.0f}")
            
            submitted_item = st.form_submit_button("Tambahkan ke Daftar PR")
        
        if submitted_item:
            if description and supplier != "(Pilih Supplier)" and total_price > 0 and pr_number_item:
                st.session_state.pr_items.append({
                    "PR Number": pr_number_item,
                    "Description": description,
                    "Qty": qty,
                    "UOM": uom,
                    "Unit Price (Est)": unit_price,
                    "Total Price (Est)": total_price,
                    "Supplier Recomendation": supplier,
                    "Exp Receive Date": exp_receive_date.strftime('%Y-%m-%d')
                })
                st.success(f"✅ Item '{description}' ditambahkan ke PR No. {pr_number_item}")
                st.rerun()
            else:
                st.error("Lengkapi semua kolom bertanda *.")

    st.markdown("---")
    
    # ---------------------------
    # 2️⃣ Daftar Item PR
    # ---------------------------
    st.markdown("### Daftar Item PR Siap Proses")
    
    if st.session_state.pr_items:
        total_all = sum(item["Total Price (Est)"] for item in st.session_state.pr_items)
        pr_numbers_list = list(set(item["PR Number"] for item in st.session_state.pr_items))
        
        if len(pr_numbers_list) > 1:
            st.warning(f"⚠️ Ditemukan beberapa Nomor PR: {', '.join(pr_numbers_list)}")
        else:
            st.info(f"Semua item akan dikonsolidasikan dalam PR No: {pr_numbers_list[0]}")
        
        # Tabel PR Items
        for i, item in enumerate(st.session_state.pr_items):
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1,4,1,1,2,2,3,2,1])
            with col1: st.write(i+1)
            with col2: 
                st.markdown(f"**{item['Description']}**\nPR No: `{item['PR Number']}`")
            with col3: st.write(item["Qty"])
            with col4: st.write(item["UOM"])
            with col5: st.write(f"Rp {item['Unit Price (Est)']:,.0f}")
            with col6: st.write(f"Rp {item['Total Price (Est)']:,.0f}")
            with col7: st.write(item["Supplier Recomendation"])
            with col8: st.write(item["Exp Receive Date"])
            with col9: st.button("❌", key=f"del_{i}", on_click=delete_pr_item, args=(i,))
        
        st.subheader(f"💰 Grand Total Estimasi: Rp {total_all:,.0f}")
        st.markdown("---")
        
        # ---------------------------
        # 3️⃣ Form Submit PR Header
        # ---------------------------
        st.markdown("### Konfirmasi & Submit PR")
        with st.form("form_submit_pr"):
            colh1, colh2 = st.columns(2)
            with colh1:
                pr_number_final = st.text_input("Nomor PR Final*", value=pr_numbers_list[0] if len(pr_numbers_list)==1 else "")
                category = st.selectbox("Category/Proyek*", ["Sumbawa", "Kantor Bali", "Operasional Lain"])
                date_request = st.date_input("Tanggal Request*", value=date.today(), disabled=True)
            with colh2:
                prepared_by = st.text_input("Prepared By*")
                reason = st.text_area("Alasan / Tujuan Pembelian*")
            
            submitted_pr = st.form_submit_button("✅ Submit PR")
            
            if submitted_pr:
                if pr_number_final and prepared_by and reason and category:
                    # --- Simulasi master lookup ---
                    m_item = {"Pakan Udang Premium Type A":"ITM001", "Obat Antibiotik Air":"ITM002", "Benur Vaname Size 10":"ITM003", "Alat Aerator 5PK":"ITM004"}
                    m_supplier = {"PT Pakan Jaya":"SUP001","CV Kimia Air":"SUP002","Penangkar Benur Sukses":"SUP003","Toko Peralatan Tambak":"SUP004"}
                    
                    t_pr_header_db = []
                    t_pr_detail_db = []
                    
                    # Simpan header
                    t_pr_header_db.append({
                        "pr_id": pr_number_final,
                        "employee_id": prepared_by,
                        "pr_date": date.today(),
                        "category_id": category,
                        "remarks": reason
                    })
                    
                    failed_items = []
                    for item in st.session_state.pr_items:
                        item_id = m_item.get(item["Description"])
                        supplier_id = m_supplier.get(item["Supplier Recomendation"])
                        if item_id is None or supplier_id is None:
                            failed_items.append(item["Description"])
                            continue
                        t_pr_detail_db.append({
                            "pr_id": pr_number_final,
                            "item_id": item_id,
                            "qty": item["Qty"],
                            "uom": item["UOM"],
                            "unit_price": item["Unit Price (Est)"],
                            "total_price": item["Total Price (Est)"],
                            "supplier_id": supplier_id,
                            "expected_date": item["Exp Receive Date"]
                        })
                    
                    if failed_items:
                        st.warning(f"⚠️ Item gagal submit (tidak ada master data): {', '.join(failed_items)}")
                    
                    st.success(f"🎉 PR {pr_number_final} berhasil diajukan dengan {len(st.session_state.pr_items) - len(failed_items)} item.")
                    st.balloons()
                    st.session_state.pr_items = []
                    st.rerun()
                else:
                    st.error("Lengkapi semua data header PR.")



# ===============================================
# ========== HALAMAN PURCHASE ORDER (MODIFIED) ==========
# ===============================================
elif st.session_state.active_page == "Purchase Order":
    st.title("📄 Pembuatan Purchase Order")
    st.subheader("Daftar Item Purchase Request yang Siap Dibuatkan PO")

    st.info("💡 Data di bawah adalah Purchase Request yang statusnya sudah **Approved** dan siap diproses menjadi Purchase Order. Anda bisa menyesuaikan Harga Final di kolom **Harga Final (Rp)**.")
    
    # 1. Buat salinan data dan tambahkan kolom 'select' secara eksplisit
    po_df = approved_pr_data.copy()
    if 'select' not in po_df.columns:
        po_df.insert(0, 'select', False)
        
    st.markdown("### Item PR Approved")
    
    # 2. Gunakan st.data_editor pada DataFrame yang sudah memiliki kolom 'select'
    edited_df = st.data_editor(
        po_df,
        column_config={
            "select": st.column_config.CheckboxColumn(
                "Pilih",
                help="Pilih item yang akan dibuatkan Purchase Order",
                default=False,
            ),
            "Total Final": st.column_config.NumberColumn(
                "Total Final (Rp)",
                format="Rp %,.0f",
                disabled=True
            ),
            # Kolom Unit Price (Final) dibuat editable agar bisa negosiasi harga
            "Unit Price (Final)": st.column_config.NumberColumn(
                "Harga Final (Rp)",
                format="Rp %,.0f",
                min_value=0,
                step=1000
            ),
            "Tgl Target Terima": st.column_config.DateColumn(
                "Tgl Target Terima",
                format="YYYY/MM/DD",
            )
        },
        # Kolom selain select dan harga final di-disable
        disabled=("PR No.", "Deskripsi Barang", "Qty", "UOM", "Supplier Rekomendasi", "Tgl Target Terima", "Total Final"),
        use_container_width=True,
        key="po_data_editor",
        hide_index=True
    )

    # 3. Filter DataFrame yang sudah diedit.
    selected_items = edited_df[edited_df['select']].copy() 
    
    # 4. Recalculate Total Final based on edited Unit Price (Final)
    if not selected_items.empty:
        # Recalculate the total in the selected dataframe based on the user's input/edit
        selected_items['Total Final'] = selected_items['Qty'] * selected_items['Unit Price (Final)']
        
        # Calculate Grand Total PO
        grand_total_po = selected_items['Total Final'].sum()

    st.markdown("---")

    if not selected_items.empty:
        
        pr_numbers = selected_items['PR No.'].unique()
        suppliers = selected_items['Supplier Rekomendasi'].unique()

        # Display Grand Total Card
        st.markdown(f"""
        <div class='grand-total-card'>
            <div class='grand-total-label'>GRAND TOTAL NILAI PO</div>
            <div class='grand-total-value'>Rp {grand_total_po:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        
        if len(suppliers) > 1:
            st.error("⚠️ Item yang dipilih memiliki lebih dari satu supplier. Harap pilih item dari satu supplier saja untuk membuat satu PO.")
        
        else:
            st.subheader(f"Form Purchase Order ({len(selected_items)} Item Terpilih)")
            
            with st.form("form_purchase_order"):
                col_po_1, col_po_2 = st.columns(2)
                
                with col_po_1:
                    po_number = st.text_input("Nomor PO", value=f"PO-INA/{pd.Timestamp.today().strftime('%Y%m%d')}-001", disabled=True)
                    po_supplier = st.text_input("Supplier PO", value=suppliers[0] if suppliers.size > 0 else "N/A", disabled=True)
                    po_date = st.date_input("Tanggal PO", value=date.today(), disabled=True)
                
                with col_po_2:
                    st.text_input("Termin Pembayaran", value="30 Hari Setelah Invoice")
                    st.text_input("Alamat Pengiriman", value="Tambak Situbondo")
                    st.text_input("PIC Penerima Barang", value="Bayu Logistik")
                
                st.markdown("---")
                st.markdown("#### Item yang Dipesan")
                
                # Menampilkan kembali item yang dipilih dengan harga final yang sudah di-recalculate
                final_df_display = selected_items[['PR No.', 'Deskripsi Barang', 'Qty', 'UOM', 'Unit Price (Final)', 'Total Final']]
                final_df_display = final_df_display.rename(columns={
                    'Unit Price (Final)': 'Harga Satuan Final',
                    'Total Final': 'Total Harga'
                })
                
                st.dataframe(
                    final_df_display.style.format({
                        'Harga Satuan Final': "Rp {:,.0f}", 
                        'Total Harga': "Rp {:,.0f}",
                        'Qty': "{:,.0f}"}),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                submitted = st.form_submit_button("🎉 Generate & Submit Purchase Order")
                
                if submitted:
                    st.success(f"🎉 Purchase Order **{po_number}** senilai **Rp {grand_total_po:,.0f}** untuk supplier **{po_supplier}** berhasil dibuat!")
                    st.balloons()
    else:
        st.warning("Silakan pilih minimal satu item PR yang sudah di-approve di tabel di atas untuk membuat Purchase Order baru.")


# ===============================================
# ========== HALAMAN SETTING (UPDATED) ==========
# ===============================================
elif st.session_state.active_page == "Setting":
    st.title("⚙️ Pengaturan Sistem: Master Data")
    st.write("Kelola daftar Supplier dan Kategori Barang yang digunakan dalam sistem.")

    # --- TABBED INTERFACE ---
    tab_supplier, tab_category = st.tabs(["Master Supplier", "Master Kategori"])

    # 1. Master Supplier
    with tab_supplier:
        st.subheader("Daftar Supplier Aktif")
        
        # Tampilkan daftar
        supplier_df = pd.DataFrame({"Nama Supplier": st.session_state.master_suppliers})
        st.dataframe(supplier_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Form Tambah Supplier
        with st.form("form_add_supplier", clear_on_submit=True):
            new_supplier = st.text_input("Nama Supplier Baru")
            col_sup_add, col_sup_empty = st.columns([1, 4])
            with col_sup_add:
                submit_supplier = st.form_submit_button("➕ Tambah Supplier")
            
            if submit_supplier:
                if new_supplier and new_supplier not in st.session_state.master_suppliers:
                    st.session_state.master_suppliers.append(new_supplier)
                    st.success(f"Supplier **'{new_supplier}'** berhasil ditambahkan.")
                    st.rerun()
                elif new_supplier in st.session_state.master_suppliers:
                    st.warning(f"Supplier **'{new_supplier}'** sudah ada dalam daftar.")
                else:
                    st.error("Nama supplier tidak boleh kosong.")

    # 2. Master Kategori
    with tab_category:
        st.subheader("Daftar Kategori Barang Aktif")
        
        # Tampilkan daftar
        category_df = pd.DataFrame({"Nama Kategori": st.session_state.master_categories})
        st.dataframe(category_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Form Tambah Kategori
        with st.form("form_add_category", clear_on_submit=True):
            new_category = st.text_input("Nama Kategori Baru")
            col_cat_add, col_cat_empty = st.columns([1, 4])
            with col_cat_add:
                submit_category = st.form_submit_button("➕ Tambah Kategori")
            
            if submit_category:
                if new_category and new_category not in st.session_state.master_categories:
                    st.session_state.master_categories.append(new_category)
                    st.success(f"Kategori **'{new_category}'** berhasil ditambahkan.")
                    st.rerun()
                elif new_category in st.session_state.master_categories:
                    st.warning(f"Kategori **'{new_category}'** sudah ada dalam daftar.")
                else:
                    st.error("Nama kategori tidak boleh kosong.")
