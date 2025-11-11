import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="Tambak Logistik", layout="wide")

# --- SIDEBAR STYLING ---
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            padding: 2rem 1rem;
        }
        .sidebar-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: white;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .menu-item {
            color: #d1d5db;
            font-size: 1rem;
            padding: 0.6rem 0.8rem;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: background 0.2s ease;
        }
        .menu-item:hover {
            background-color: #1e293b;
            color: white;
        }
        .menu-item.active {
            background-color: #2563eb;
            color: white;
        }
        hr {
            border: 1px solid #1e293b;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTENT ---
st.sidebar.markdown('<div class="sidebar-title">🦐 Tambak Logistik</div>', unsafe_allow_html=True)
st.sidebar.markdown("<hr>", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Navigasi",
    ["Dashboard", "Stok Masuk", "Stok Keluar", "Setting"],
    label_visibility="collapsed",
    index=0
)

# --- MAIN CONTENT ---
if menu == "Dashboard":
    st.title("📊 Dashboard Logistik")
    st.write("Tampilkan ringkasan stok, tren pemakaian, dan status gudang di sini.")

elif menu == "Stok Masuk":
    st.title("⬆️ Stok Masuk")
    st.write("Input data barang yang baru masuk ke sistem logistik.")

elif menu == "Stok Keluar":
    st.title("⬇️ Stok Keluar")
    st.write("Catat pengeluaran stok untuk kegiatan penambakan udang.")

elif menu == "Setting":
    st.title("⚙️ Pengaturan")
    st.write("Atur preferensi sistem atau koneksi Google Sheet di sini.")
