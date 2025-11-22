import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from collections import defaultdict
import os
from dotenv import load_dotenv
import psycopg2
from db_utils import run_query, run_exec








# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Sistem Logistik Tambak Udang", layout="wide")

master_items = run_query("SELECT item_id, name, base_uom_id FROM procwh.m_item")
st.session_state.master_items = master_items

master_vendors = run_query("SELECT vendor_id, name FROM procwh.m_vendor")
st.session_state.master_suppliers = [s["name"] for s in master_vendors]

master_categories = run_query("SELECT category_id, name FROM procwh.m_category")
st.session_state.master_categories = [c["name"] for c in master_categories]



# ========== CUSTOM STYLE (Disesuaikan untuk st.radio) ==========
menu_items = {
    "Dashboard": "📊 Dashboard",
    "Inventori": "📦 Inventori",
    "Stok Masuk": "⬆️ Stok Masuk",
    "Stok Keluar": "⬇️ Stok Keluar",
    "Purchase Request": "📝 Purchase Request",
    "PR Approval": "✔️ Approval PR",
    "Purchase Order": "📄 Purchase Order",
    "PO Approval": "🛂 Approval PO",
    "Goods Receipt": "📦 GR / Barang Masuk",
    "Stock Movement": "📜 Stock Movement",
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



def ui_pr_approval():
    st.title("✔️ Approval Purchase Request (2 Level)")

    df_pr = pd.DataFrame(run_query("""
        SELECT pr_id, pr_date, status, remarks
        FROM procwh.t_pr_header
        WHERE status IN ('SUBMITTED','REVIEWED')
        ORDER BY pr_date DESC
    """))

    st.subheader("Daftar PR Pending")
    st.dataframe(df_pr, use_container_width=True)

    st.markdown("---")
    st.subheader("Form Approval")

    pr_list = ["(Pilih PR)"] + df_pr["pr_id"].tolist()
    selected = st.selectbox("Pilih PR", pr_list)

    if selected != "(Pilih PR)":
        pr_row = df_pr[df_pr["pr_id"] == selected].iloc[0]
        status = pr_row["status"]

        next_level = 1 if status == "SUBMITTED" else 2
        st.info(f"Status sekarang: **{status}** → Approval Level **{next_level}**")

        action = st.selectbox("Action", ["APPROVE", "REJECT"])
        notes = st.text_input("Notes")

        if st.button("Submit Approval PR"):
            run_exec("""
                INSERT INTO procwh.t_pr_approval (pr_id, level, action, action_at, notes)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (selected, next_level, action, notes))
            st.success(f"PR {selected} berhasil {action}")
            st.rerun()

def ui_po_approval():
    st.title("🛂 Approval Purchase Order (3 Level)")

    df_po = pd.DataFrame(run_query("""
        SELECT po_id, vendor_id, status
        FROM procwh.t_po_header
        WHERE status IN ('DRAFT','REVIEWED','VERIFIED')
        ORDER BY created_at DESC
    """))

    st.subheader("Daftar PO Pending")
    st.dataframe(df_po, use_container_width=True)

    st.markdown("---")
    st.subheader("Form Approval PO")

    po_list = ["(Pilih PO)"] + df_po["po_id"].tolist()
    selected = st.selectbox("Pilih PO", po_list)

    if selected != "(Pilih PO)":
        row = df_po[df_po["po_id"] == selected].iloc[0]
        status = row["status"]

        map_level = {"DRAFT": 1, "REVIEWED": 2, "VERIFIED": 3}
        next_level = map_level[status]

        st.info(f"Approval Level berikutnya: **{next_level}**")

        action = st.selectbox("Action", ["APPROVE", "REJECT"])
        notes = st.text_area("Notes")

        if st.button("Submit Approval PO"):
            run_exec("""
                INSERT INTO procwh.t_po_approval (po_id, level, action, action_at, notes)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (selected, next_level, action, notes))


            st.success(f"PO {selected} berhasil {action}")
            st.rerun()
def ui_gr():
    st.title("📦 Goods Receipt (GR)")

    df_po = pd.DataFrame(run_query("""
        SELECT po_id, vendor_id, status FROM procwh.t_po_header
        WHERE status = 'APPROVED'
    """))

    po_list = ["(Pilih PO)"] + df_po["po_id"].tolist()
    selected = st.selectbox("Pilih PO yang sudah APPROVED", po_list)

    if selected != "(Pilih PO)":
        df_detail = pd.DataFrame(run_query("""
            SELECT po_detail_id, item_id, qty_ordered
            FROM procwh.t_po_detail
            WHERE po_id = %s
        """, (selected,)))

        st.dataframe(df_detail, use_container_width=True)

        st.markdown("### Input Qty Received")
        qty_received = {}

        for _, row in df_detail.iterrows():
            qty_received[row["po_detail_id"]] = st.number_input(
                f"{row['item_id']} — Ordered {row['qty_ordered']}",
                min_value=0,
                max_value=row["qty_ordered"],
                value=row["qty_ordered"]
            )

        if st.button("Generate GR"):
            run_exec("SELECT procwh.fn_generate_gr_from_po(%s)", (selected,))
            st.success(f"GR berhasil dibuat untuk PO {selected}")
            st.balloons()
            st.rerun()

def ui_stock_movement():
    st.title("📜 Stock Movement")

    df = pd.DataFrame(run_query("""
        SELECT movement_id, item_id, qty_change, movement_type,
               location_id, ref_po_id, ref_gr_id, movement_date
        FROM procwh.t_stock_movement
        ORDER BY movement_date DESC
    """))

    st.dataframe(df, use_container_width=True)


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
# ========== HALAMAN PR (SAFE DB UPDATED) ======
# ===============================================
elif st.session_state.active_page == "Purchase Request":
    st.title("📝 Input Purchase Request")
    st.write("Silakan input setiap item barang satu per satu.")

    # ---------------------------
    # 0️⃣ Ambil Master Data dari DB
    # ---------------------------
    master_items = {row[1]: row[0] for row in run_query("SELECT item_id, name FROM procwh.m_item")}
    master_vendors = {row[1]: row[0] for row in run_query("SELECT vendor_id, name FROM procwh.m_vendor")}
    master_employees = {row[1]: row[0] for row in run_query("SELECT employee_id, name FROM procwh.m_employee")}

    st.session_state.master_vendors = list(master_vendors.keys())
    st.session_state.master_items = list(master_items.keys())
    st.session_state.master_employees = list(master_employees.keys())

    # ---------------------------
    # Ensure session keys
    # ---------------------------
    if "current_pr" not in st.session_state:
        st.session_state.current_pr = None
    if "pr_items" not in st.session_state:
        st.session_state.pr_items = []

    # ---------------------------
    # Button: Create new PR (generate PR id)
    # ---------------------------
    st.markdown("### 🔹 PR Header")
    colp1, colp2 = st.columns([3,1])
    with colp1:
        st.write("Buat dokumen PR baru sebelum menambahkan item.")
        if st.session_state.current_pr:
            st.success(f"PR Aktif: **{st.session_state.current_pr}**")
        else:
            st.info("Belum ada PR aktif.")
    with colp2:
        if st.button("➕ Buat PR Baru"):
            # ambil dari DB
            res = run_query("SELECT procwh.fn_next_pr_id()")
            # result handling: jika run_query kembali list of tuples
            if res and len(res) > 0:
                try:
                    new_pr = res[0][0]
                except Exception:
                    # fallback for dict-like
                    new_pr = list(res[0].values())[0]
                st.session_state.current_pr = new_pr
                st.success(f"Nomor PR berhasil dibuat: **{new_pr}**")
                st.rerun()
            else:
                st.error("Gagal generate PR ID. Cek koneksi atau fungsi DB procwh.fn_next_pr_id().")

    st.markdown("---")

    # ---------------------------
    # 1️⃣ Form Input Item PR (disabled if no PR header)
    # ---------------------------
    with st.expander("➕ Tambah Item Baru", expanded=True):
        if st.session_state.current_pr is None:
            st.warning("⚠️ Buat PR baru terlebih dahulu (klik tombol 'Buat PR Baru').")
        else:
            with st.form("form_add_item", clear_on_submit=True):
                col0, col1, col2, col3, col4 = st.columns([2, 3, 1.5, 1, 2.5])
                with col0:
                    # Nomor PR tidak bisa diedit
                    st.text_input("Nomor PR (otomatis)", value=st.session_state.current_pr, disabled=True, key="ui_pr_number")
                with col1:
                    description = st.selectbox("Deskripsi Barang/Jasa*", options=["(Pilih Item)"] + list(master_items.keys()), key="ui_item_desc")
                with col2:
                    qty = st.number_input("Qty*", min_value=1, value=1, key="ui_item_qty")
                with col3:
                    uom = st.text_input("UOM*", value="unit", key="ui_item_uom")
                with col4:
                    unit_price = st.number_input("Harga Satuan (Rp)*", min_value=0, format="%i", key="ui_item_price")

                col_vendor, col_dummy = st.columns(2)
                with col_vendor:
                    vendor = st.selectbox("Vendor*", options=["(Pilih Vendor)"] + list(master_vendors.keys()), key="ui_item_vendor")

                total_price = qty * unit_price
                st.info(f"Total Harga Estimasi: Rp {total_price:,.0f}")

                submitted_item = st.form_submit_button("Tambahkan ke Daftar PR")

            if submitted_item:
                if description != "(Pilih Item)" and vendor != "(Pilih Vendor)" and total_price > 0:
                    st.session_state.pr_items.append({
                        "PR Number": st.session_state.current_pr,
                        "Description": description,
                        "Qty": qty,
                        "UOM": uom,
                        "Unit Price (Est)": unit_price,
                        "Total Price (Est)": total_price,
                        "Vendor Recomendation": vendor
                    })
                    st.success(f"✅ Item '{description}' ditambahkan ke PR No. {st.session_state.current_pr}")
                    st.rerun()
                else:
                    st.error("Lengkapi semua kolom bertanda *.")

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

        for i, item in enumerate(st.session_state.pr_items):
            col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([1,4,1,1,2,2,3,2,1])
            with col1: st.write(i+1)
            with col2: st.markdown(f"**{item['Description']}**\nPR No: `{item['PR Number']}`")
            with col3: st.write(item["Qty"])
            with col4: st.write(item["UOM"])
            with col5: st.write(f"Rp {item['Unit Price (Est)']:,.0f}")
            with col6: st.write(f"Rp {item['Total Price (Est)']:,.0f}")
            with col7: st.write(item["Vendor Recomendation"])
            with col9:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.pr_items.pop(i)
                    st.rerun()

        st.subheader(f"💰 Grand Total Estimasi: Rp {total_all:,.0f}")
        st.markdown("---")

        # ---------------------------
        # 3️⃣ Form Submit PR Header ke DB
        # ---------------------------
        st.markdown("### Konfirmasi & Submit PR")
        with st.form("form_submit_pr"):
            colh1, colh2 = st.columns(2)
            with colh1:
                # Display PR number (read-only)
                st.text_input("Nomor PR", value=st.session_state.current_pr, disabled=True)
                employee_name = st.selectbox("Prepared By*", options=["(Pilih Employee)"] + st.session_state.master_employees, key="ui_pr_employee")
                pr_number_final = st.session_state.current_pr
            with colh2:
                reason = st.text_area("Alasan / Tujuan Pembelian*", key="ui_pr_reason")

            submitted_pr = st.form_submit_button("✅ Submit PR")

            if submitted_pr:
                if pr_number_final and employee_name != "(Pilih Employee)" and reason.strip() != "":
                    failed_items = []
                    employee_id = master_employees.get(employee_name)

                    # --- Insert header
                    run_exec("""
                        INSERT INTO procwh.t_pr_header (pr_id, employee_id, pr_date, remarks)
                        VALUES (%s, %s, CURRENT_DATE, %s)
                    """, (pr_number_final, employee_id, reason))

                    # --- Insert detail
                    for item in st.session_state.pr_items:
                        item_id = master_items.get(item["Description"])
                        vendor_id = master_vendors.get(item["Vendor Recomendation"])
                        if item_id is None or vendor_id is None:
                            failed_items.append(item["Description"])
                            continue

                        run_exec("""
                            INSERT INTO procwh.t_pr_detail
                            (pr_id, item_id, description, qty_requested, uom_id, unit_price, total_amount, vendor_id, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """, (
                            pr_number_final, item_id, item["Description"], item["Qty"], item["UOM"],
                            item["Unit Price (Est)"], item["Total Price (Est)"], vendor_id
                        ))

                    if failed_items:
                        st.warning(f"⚠️ Item gagal submit (tidak ada master data): {', '.join(failed_items)}")

                    st.success(f"🎉 PR {pr_number_final} berhasil diajukan dengan {len(st.session_state.pr_items) - len(failed_items)} item.")
                    st.balloons()
                    # reset state
                    st.session_state.pr_items = []
                    st.session_state.current_pr = None
                    st.rerun()
                else:
                    st.error("Lengkapi semua data header PR.")
    else:
        st.info("Belum ada item di PR. Tambahkan item setelah membuat PR header.")


elif st.session_state.active_page == "PR Approval":
    ui_pr_approval()

elif st.session_state.active_page == "PO Approval":
    ui_po_approval()

elif st.session_state.active_page == "Goods Receipt":
    ui_gr()

elif st.session_state.active_page == "Stock Movement":
    ui_stock_movement()

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
