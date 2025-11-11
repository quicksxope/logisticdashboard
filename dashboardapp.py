import streamlit as st
import pandas as pd
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Sistem Logistik Tambak Udang", layout="wide")

# --- STYLING (CSS CUSTOM) ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0e1117;
        }
        [data-testid="stSidebarNav"] {
            color: white;
        }
        .css-1d391kg {background-color: #0e1117;}
        .big-font {
            font-size: 22px !important;
            font-weight: bold;
        }
        .metric-box {
            background-color: #1c1e24;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR MENU ---
st.sidebar.title("🦐 Logistik Tambak Udang")
menu = st.sidebar.radio("Navigasi", ["📊 Dashboard Utama", "⬆️ Stok Masuk", "⬇️ Stok Keluar"])

# --- DATA SIMULASI ---
if "data_stok" not in st.session_state:
    st.session_state.data_stok = pd.DataFrame(columns=["Tanggal", "Jenis Barang", "Jumlah", "Tipe"])

# --- DASHBOARD ---
if menu == "📊 Dashboard Utama":
    st.title("📊 Dashboard Logistik Tambak Udang")

    total_masuk = st.session_state.data_stok[st.session_state.data_stok["Tipe"] == "Masuk"]["Jumlah"].sum()
    total_keluar = st.session_state.data_stok[st.session_state.data_stok["Tipe"] == "Keluar"]["Jumlah"].sum()
    stok_akhir = total_masuk - total_keluar

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-box"><p class="big-font">Stok Masuk</p>'
                    f'<h2>{int(total_masuk)}</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><p class="big-font">Stok Keluar</p>'
                    f'<h2>{int(total_keluar)}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><p class="big-font">Sisa Stok</p>'
                    f'<h2>{int(stok_akhir)}</h2></div>', unsafe_allow_html=True)

    st.subheader("📈 Riwayat Transaksi Stok")
    st.dataframe(st.session_state.data_stok, use_container_width=True)

# --- INPUT STOK MASUK ---
elif menu == "⬆️ Stok Masuk":
    st.title("⬆️ Input Stok Masuk")

    with st.form("form_masuk"):
        jenis = st.text_input("Jenis Barang")
        jumlah = st.number_input("Jumlah Barang", min_value=0, step=1)
        tanggal = st.date_input("Tanggal Masuk", datetime.date.today())
        submit = st.form_submit_button("Simpan")

    if submit and jenis:
        new_data = pd.DataFrame([[tanggal, jenis, jumlah, "Masuk"]],
                                columns=["Tanggal", "Jenis Barang", "Jumlah", "Tipe"])
        st.session_state.data_stok = pd.concat([st.session_state.data_stok, new_data], ignore_index=True)
        st.success("✅ Data stok masuk berhasil disimpan!")

# --- INPUT STOK KELUAR ---
elif menu == "⬇️ Stok Keluar":
    st.title("⬇️ Input Stok Keluar")

    with st.form("form_keluar"):
        jenis = st.text_input("Jenis Barang")
        jumlah = st.number_input("Jumlah Barang", min_value=0, step=1)
        tanggal = st.date_input("Tanggal Keluar", datetime.date.today())
        submit = st.form_submit_button("Simpan")

    if submit and jenis:
        new_data = pd.DataFrame([[tanggal, jenis, jumlah, "Keluar"]],
                                columns=["Tanggal", "Jenis Barang", "Jumlah", "Tipe"])
        st.session_state.data_stok = pd.concat([st.session_state.data_stok, new_data], ignore_index=True)
        st.success("✅ Data stok keluar berhasil disimpan!")
