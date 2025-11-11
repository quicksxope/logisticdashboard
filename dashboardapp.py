import streamlit as st
import pandas as pd
import requests
from datetime import date

# --- Konfigurasi dasar ---
st.set_page_config(page_title="Logistik Tambak Udang", layout="wide")

# --- Header ---
st.title("🦐 Sistem Logistik Penambakan Udang")
st.markdown("Kelola stok pakan, obat, dan alat dengan efisien menggunakan dashboard ini.")

# --- Tabs untuk navigasi ---
tab1, tab2, tab3 = st.tabs(["📥 Stok Masuk", "📤 Stok Keluar", "📊 Dashboard"])

# -------------------------------
# 1️⃣ Form Input Stok Masuk
# -------------------------------
with tab1:
    st.subheader("📦 Input Stok Masuk")
    with st.form("form_stok_masuk"):
        nama_barang = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah Masuk", min_value=0.0, step=0.1)
        satuan = st.selectbox("Satuan", ["kg", "liter", "pak", "unit"])
        supplier = st.text_input("Nama Supplier")
        tanggal = st.date_input("Tanggal Masuk", date.today())
        catatan = st.text_area("Catatan (opsional)")
        submitted = st.form_submit_button("✅ Simpan Stok Masuk")

        if submitted:
            data = {
                "nama_barang": nama_barang,
                "jumlah": jumlah,
                "satuan": satuan,
                "supplier": supplier,
                "tanggal": str(tanggal),
                "catatan": catatan
            }
            try:
                # Ganti URL sesuai endpoint FastAPI kamu
                res = requests.post("https://your-backend-url/stok_masuk", json=data)
                if res.status_code == 200:
                    st.success("✅ Data stok masuk berhasil disimpan!")
                else:
                    st.error("❌ Gagal menyimpan data ke server.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# -------------------------------
# 2️⃣ Form Input Stok Keluar
# -------------------------------
with tab2:
    st.subheader("📤 Input Stok Keluar")
    with st.form("form_stok_keluar"):
        nama_barang_out = st.text_input("Nama Barang")
        jumlah_out = st.number_input("Jumlah Keluar", min_value=0.0, step=0.1)
        satuan_out = st.selectbox("Satuan", ["kg", "liter", "pak", "unit"])
        kolam = st.text_input("Kolam (contoh: Kolam 3)")
        tanggal_out = st.date_input("Tanggal Keluar", date.today())
        catatan_out = st.text_area("Catatan (opsional)")
        submitted_out = st.form_submit_button("✅ Simpan Stok Keluar")

        if submitted_out:
            data = {
                "nama_barang": nama_barang_out,
                "jumlah": jumlah_out,
                "satuan": satuan_out,
                "kolam": kolam,
                "tanggal": str(tanggal_out),
                "catatan": catatan_out
            }
            try:
                res = requests.post("https://your-backend-url/stok_keluar", json=data)
                if res.status_code == 200:
                    st.success("✅ Data stok keluar berhasil disimpan!")
                else:
                    st.error("❌ Gagal menyimpan data ke server.")
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# -------------------------------
# 3️⃣ Dashboard Ringkasan
# -------------------------------
with tab3:
    st.subheader("📊 Ringkasan Stok")

    # --- Contoh data dummy (nanti diganti data real dari backend / Google Sheet) ---
    data_masuk = pd.DataFrame({
        "Nama Barang": ["Pakan Udang 40%", "Obat Air", "Pakan Udang 40%"],
        "Jumlah": [50, 10, 30],
        "Tanggal": ["2025-11-01", "2025-11-03", "2025-11-05"]
    })

    data_keluar = pd.DataFrame({
        "Nama Barang": ["Pakan Udang 40%", "Pakan Udang 40%", "Obat Air"],
        "Jumlah": [20, 10, 5],
        "Tanggal": ["2025-11-06", "2025-11-09", "2025-11-10"]
    })

    # Hitung stok tersisa per barang
    summary = (
        data_masuk.groupby("Nama Barang")["Jumlah"].sum()
        - data_keluar.groupby("Nama Barang")["Jumlah"].sum()
    ).reset_index()
    summary.columns = ["Nama Barang", "Sisa Stok"]

    st.dataframe(summary)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Stok Masuk", f"{data_masuk['Jumlah'].sum()} unit")
    with col2:
        st.metric("Total Stok Keluar", f"{data_keluar['Jumlah'].sum()} unit")

    st.markdown("📈 Visualisasi Stok Masuk & Keluar (dummy)")
    st.bar_chart({
        "Masuk": data_masuk.groupby("Tanggal")["Jumlah"].sum(),
        "Keluar": data_keluar.groupby("Tanggal")["Jumlah"].sum(),
    })
