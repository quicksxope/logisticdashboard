import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Sistem Logistik Tambak Udang", layout="wide")

# ========== CUSTOM STYLE ==========
st.markdown("""
<style>
/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #111827;
    padding-top: 2rem;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] li, [data-testid="stSidebar"] div {
    color: #E5E7EB !important;
}
.sidebar-title {
    color: white;
    font-weight: bold;
    font-size: 20px;
    text-align: center;
}

/* Metric cards */
.metric-card {
    background-color: #1F2937;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
}
.metric-label {
    font-size: 14px;
    color: #9CA3AF;
}

/* Table styling */
thead tr th {
    background-color: #374151 !important;
    color: white !important;
    text-align: center !important;
}
tbody tr td {
    text-align: center !important;
}

/* Main background */
.stApp {
    background-color: #F9FAFB;
}
</style>
""", unsafe_allow_html=True)

# ========== SIDEBAR ==========
st.sidebar.markdown("<h2 class='sidebar-title'>🦐 Tambak Logistik</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigasi", ["📊 Dashboard", "⬆️ Stok Masuk", "⬇️ Stok Keluar", "⚙️ Setting"])

# ========== DUMMY DATA ==========
shipment_data = pd.DataFrame({
    "Order ID": ["BA92123", "KH92129", "SD92123", "BA92124", "SD92125"],
    "Type of Goods": ["Pakan Udang", "Obat Air", "Benur Vaname", "Vitamin Tambak", "Alat Aerator"],
    "Place of Discharge": ["Situbondo", "Probolinggo", "Lamongan", "Sidoarjo", "Gresik"],
    "Date": ["2025-10-12", "2025-10-15", "2025-10-18", "2025-10-19", "2025-10-20"],
    "Status": ["On Delivery", "Complete", "Pending", "On Delivery", "Pending"]
})

# ========== DASHBOARD ==========
if menu == "📊 Dashboard":
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

# ========== STOK MASUK ==========
elif menu == "⬆️ Stok Masuk":
    st.title("⬆️ Input Stok Masuk")
    with st.form("form_masuk"):
        jenis = st.text_input("Jenis Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        tanggal = st.date_input("Tanggal")
        submitted = st.form_submit_button("Simpan")
    if submitted:
        st.success(f"✅ Data stok masuk '{jenis}' sejumlah {jumlah} berhasil disimpan!")

# ========== STOK KELUAR ==========
elif menu == "⬇️ Stok Keluar":
    st.title("⬇️ Input Stok Keluar")
    with st.form("form_keluar"):
        jenis = st.text_input("Jenis Barang")
        jumlah = st.number_input("Jumlah", min_value=1)
        tanggal = st.date_input("Tanggal")
        submitted = st.form_submit_button("Simpan")
    if submitted:
        st.success(f"✅ Data stok keluar '{jenis}' sejumlah {jumlah} berhasil disimpan!")

# ========== SETTINGS ==========
elif menu == "⚙️ Setting":
    st.title("⚙️ Pengaturan Sistem")
    st.write("Tempat untuk konfigurasi API Key, database, dan backup data.")
