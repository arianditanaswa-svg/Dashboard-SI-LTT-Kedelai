import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN & CUSTOM CSS (DARK MODE)
# ---------------------------------------------------------
st.set_page_config(
    page_title="SI LTT Kedelai - Monitoring 38 Provinsi (2020-2026)",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
    <style>
    /* Background Utama App */
    .stApp {
        background-color: #062319 !important; /* Hijau Botol/Gelap */
        color: #ecfdf5 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    /* Header Utama */
    .main-header {
        background: linear-gradient(135deg, #0d3b2e 0%, #062319 100%);
        color: #ffffff;
        padding: 22px 26px;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid #165b46;
    }
    /* Kartu KPI Ringkasan */
    .kpi-card {
        background-color: #0d3b2e;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #165b46;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .kpi-label {
        color: #a7f3d0 !important;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-val {
        color: #34d399 !important; /* Hijau Terang */
        font-size: 1.8rem;
        font-weight: 800;
        margin: 4px 0;
    }
    .kpi-sub {
        font-size: 0.82rem;
        color: #6ee7b7 !important;
        font-weight: 600;
    }
    /* Box Grafik / Konten */
    .card-box {
        background-color: #0d3b2e;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #165b46;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    .card-box h3, .card-box h4, .card-box p, .card-box span {
        color: #ecfdf5 !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. MASTER KOORDINAT PROVINSI INDONESIA
# ---------------------------------------------------------
PROVINSI_COORDS = {
    'ACEH': (4.6951, 96.7494),
    'SUMATERA UTARA': (2.1154, 99.5451),
    'SUMATERA BARAT': (-0.7399, 100.8000),
    'RIAU': (0.2933, 101.7068),
    'KEPULAUAN RIAU': (3.9456, 108.1428),
    'JAMBI': (-1.6101, 103.6131),
    'SUMATERA SELATAN': (-3.3199, 104.9147),
    'BENGKULU': (-3.8004, 102.2655),
    'LAMPUNG': (-4.5586, 105.4068),
    'KEPULAUAN BANGKA BELITUNG': (-2.7410, 106.4406),
    'DKI JAKARTA': (-6.2088, 106.8456),
    'JAWA BARAT': (-6.9175, 107.6191),
    'JABAR': (-6.9175, 107.6191),
    'JAWA TENGAH': (-7.1509, 110.1403),
    'JATENG': (-7.1509, 110.1403),
    'DI YOGYAKARTA': (-7.7956, 110.3695),
    'JAWA TIMUR': (-7.5360, 112.2384),
    'JATIM': (-7.5360, 112.2384),
    'BANTEN': (-6.4058, 106.0640),
    'BALI': (-8.4095, 115.1889),
    'NUSA TENGGARA BARAT': (-8.6529, 117.3616),
    'NTB': (-8.6529, 117.3616),
    'NUSA TENGGARA TIMUR': (-8.6574, 121.0794),
    'NTT': (-8.6574, 121.0794),
    'KALIMANTAN BARAT': (-0.2787, 111.4753),
    'KALBAR': (-0.2787, 111.4753),
    'KALIMANTAN TENGAH': (-1.6815, 113.3823),
    'KALTENG': (-1.6815, 113.3823),
    'KALIMANTAN SELATAN': (-3.0926, 115.2838),
    'KALSEL': (-3.0926, 115.2838),
    'KALIMANTAN TIMUR': (0.5387, 116.4194),
    'KALTIM': (0.5387, 116.4194),
    'KALIMANTAN UTARA': (3.0731, 116.0414),
    'KALTARA': (3.0731, 116.0414),
    'SULAWESI UTARA': (0.6246, 123.9750),
    'SULUT': (0.6246, 123.9750),
    'SULAWESI TENGAH': (-1.4300, 121.4456),
    'SULTENG': (-1.4300, 121.4456),
    'SULAWESI SELATAN': (-3.6687, 119.9740),
    'SULSEL': (-3.6687, 119.9740),
    'SULAWESI TENGGARA': (-4.1449, 122.1746),
    'SULTRA': (-4.1449, 122.1746),
    'GORONTALO': (0.6999, 122.4467),
    'SULAWESI BARAT': (-2.8441, 119.2321),
    'SULBAR': (-2.8441, 119.2321),
    'MALUKU': (-3.2385, 130.1453),
    'MALUKU UTARA': (1.5709, 127.8087),
    'PAPUA': (-2.5000, 140.0000),
    'PAPUA BARAT': (-1.3361, 133.1747),
    'PAPUA SELATAN': (-7.5000, 139.0000),
    'PAPUA TENGAH': (-3.5000, 136.0000),
    'PAPUA PEGUNUNGAN': (-4.2000, 138.8000),
    'PAPUA BARAT DAYA': (-1.1500, 131.2500)
}

# ---------------------------------------------------------
# 3. KONEKSI GOOGLE SHEETS API KEY & PEMBERSIHAN DATA
# ---------------------------------------------------------
SPREADSHEET_ID = "1LyZkf9mdttT51mFx6qcBhvAzE2U7nk9BWwSgkhop6fs"
SHEET_NAME = "MASTERPROVITAS"
API_KEY = "AIzaSyBjaWo-DUl-Xm1fWkgCJmCNiWEEnKffn8o"

def process_and_clean_data(df):
    df.columns = [str(col).upper().strip() for col in df.columns]

    required_cols = [
        'TAHUN', 'BULAN', 'KODE PROVINSI', 'PROVINSI', 
        'KODE KABUPATEN/KOTA', 'KABUPATEN/KOTA', 
        'LUAS TANAM (HA)', 'LUAS PANEN (HA)', 'PRODUKSI (TON)', 
        'PRODUKTIVITAS (KU/HA)', 'CATATAN'
    ]
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0

    df['PROVINSI'] = df['PROVINSI'].astype(str).str.upper().str.strip()
    df['KABUPATEN/KOTA'] = df['KABUPATEN/KOTA'].astype(str).str.upper().str.strip()

    numeric_cols = ['LUAS TANAM (HA)', 'LUAS PANEN (HA)', 'PRODUKSI (TON)', 'PRODUKTIVITAS (KU/HA)']
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace('-', '0', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['TARGET (HA)'] = df['LUAS TANAM (HA)'] * 1.1
    df['CAPAIAN TARGET (%)'] = np.where(
        df['TARGET (HA)'] > 0, 
        (df['LUAS TANAM (HA)'] / df['TARGET (HA)']) * 100, 
        0
    )

    # Pemetaan koordinat cepat tanpa geocoding external
    if 'LAT' not in df.columns or 'LON' not in df.columns:
        df['LAT'] = df['PROVINSI'].map(lambda x: PROVINSI_COORDS.get(x, (-2.5489, 118.0149))[0])
        df['LON'] = df['PROVINSI'].map(lambda x: PROVINSI_COORDS.get(x, (-2.5489, 118.0149))[1])

    return df

@st.cache_data(ttl=300)
def load_datasource():
    RANGE_NAME = f"{SHEET_NAME}!A:K"
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/{RANGE_NAME}?key={API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "values" in data:
            values = data["values"]
            if len(values) > 0:
                header = [str(h).upper().strip() for h in values[0]]
                rows = values[1:]
                
                num_cols = len(header)
                adjusted_rows = [
                    (r + [''] * (num_cols - len(r))) if len(r) < num_cols else r[:num_cols] 
                    for r in rows
                ]
                
                df = pd.DataFrame(adjusted_rows, columns=header)
                return process_and_clean_data(df)
        elif "error" in data:
            st.error(f"Google Sheets API Error: {data['error']['message']}")
    except Exception as e:
        st.error(f"Gagal terhubung ke Google Sheets API: {e}")

    return pd.DataFrame(columns=[
        'TAHUN', 'BULAN', 'KODE PROVINSI', 'PROVINSI', 
        'KODE KABUPATEN/KOTA', 'KABUPATEN/KOTA', 
        'LUAS TANAM (HA)', 'LUAS PANEN (HA)', 'PRODUKSI (TON)', 
        'PRODUKTIVITAS (KU/HA)', 'CATATAN', 'TARGET (HA)', 'CAPAIAN TARGET (%)', 'LAT', 'LON'
    ])

# Load Data Utama
df_raw = load_datasource()

# ---------------------------------------------------------
# 4. SIDEBAR & FILTER DATA
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/606/606200.png", width=45)
    st.title("SI LTT KEDELAI")
    st.caption("Sistem Monitoring 38 Provinsi (Real-Time API Key)")
    st.divider()

    st.subheader("📌 Navigasi Menu")
    menu = st.radio(
        "Pilih Tampilan:",
        ["Dashboard Utama", "Data Wilayah", "Analitik & Produktivitas", "Peta Persebaran 38 Provinsi"],
        index=0
    )
    st.divider()

    st.subheader("🔍 Filter Data")
    tahun_opt = ["Semua Tahun"] + sorted(list(df_raw['TAHUN'].unique())) if not df_raw.empty else ["Semua Tahun"]
    sel_tahun = st.selectbox("Pilih Tahun", tahun_opt)

    prov_opt = ["Semua 38 Provinsi"] + sorted(list(df_raw['PROVINSI'].unique())) if not df_raw.empty else ["Semua 38 Provinsi"]
    sel_prov = st.selectbox("Pilih Provinsi", prov_opt)

    if not df_raw.empty:
        if sel_prov != "Semua 38 Provinsi":
            kab_list = sorted(list(df_raw[df_raw['PROVINSI'] == sel_prov]['KABUPATEN/KOTA'].unique()))
        else:
            kab_list = sorted(list(df_raw['KABUPATEN/KOTA'].unique()))
    else:
        kab_list = []

    sel_kab = st.selectbox("Pilih Kabupaten/Kota", ["Semua Kabupaten/Kota"] + kab_list)

    min_capaian, max_capaian = st.slider(
        "Filter Capaian Target (%)",
        min_value=0, max_value=200, value=(0, 200), step=5
    )

# Filter Dataset
df_filtered = df_raw.copy()

if not df_filtered.empty:
    if sel_tahun != "Semua Tahun":
        df_filtered = df_filtered[df_filtered['TAHUN'] == sel_tahun]
    if sel_prov != "Semua 38 Provinsi":
        df_filtered = df_filtered[df_filtered['PROVINSI'] == sel_prov]
    if sel_kab != "Semua Kabupaten/Kota":
        df_filtered = df_filtered[df_filtered['KABUPATEN/KOTA'] == sel_kab]

    df_filtered = df_filtered[
        (df_filtered['CAPAIAN TARGET (%)'] >= min_capaian) & 
        (df_filtered['CAPAIAN TARGET (%)'] <= max_capaian)
    ]

# ---------------------------------------------------------
# HEADER UTAMA
# ---------------------------------------------------------
st.markdown("""
    <div class="main-header">
        <h2 style="margin:0; font-weight:800;">🌱 Dashboard Monitoring Kedelai - 38 Provinsi Indonesia</h2>
        <p style="margin:4px 0 0 0; opacity:0.85; font-size:0.95rem;">
            Data Real-Time via Google Sheets API Key | Monitoring Luas Tanam, Luas Panen, Produksi, dan Produktivitas
        </p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LAYAR 1: DASHBOARD UTAMA
# ---------------------------------------------------------
if menu == "Dashboard Utama":
    tot_tanam = df_filtered['LUAS TANAM (HA)'].sum() if not df_filtered.empty else 0
    tot_panen = df_filtered['LUAS PANEN (HA)'].sum() if not df_filtered.empty else 0
    tot_produksi = df_filtered['PRODUKSI (TON)'].sum() if not df_filtered.empty else 0
    avg_provitas = df_filtered['PRODUKTIVITAS (KU/HA)'].mean() if not df_filtered.empty else 0
    avg_prod_per_ha = (tot_produksi / tot_panen) if tot_panen > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Luas Tanam</div>
                <div class="kpi-val">{tot_tanam:,.0f} <span style="font-size:1rem;">Ha</span></div>
                <div class="kpi-sub">Total Akumulasi Tanam</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Luas Panen</div>
                <div class="kpi-val">{tot_panen:,.0f} <span style="font-size:1rem;">Ha</span></div>
                <div class="kpi-sub">Capaian Panen Riil</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Produksi</div>
                <div class="kpi-val">{tot_produksi:,.0f} <span style="font-size:1rem;">Ton</span></div>
                <div class="kpi-sub">Rata-rata: {avg_prod_per_ha:.2f} Ton/Ha</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Rata-rata Produktivitas</div>
                <div class="kpi-val">{avg_provitas:.2f} <span style="font-size:1rem;">Ku/Ha</span></div>
                <div class="kpi-sub">Provitas Nasional / Wilayah</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    col_a, col_b = st.columns([1.6, 1.4])
    with col_a:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("📈 Tren Luas Tanam vs Produksi")
        if not df_raw.empty:
            df_trend = df_raw.groupby('TAHUN')[['LUAS TANAM (HA)', 'PRODUKSI (TON)']].sum().reset_index()
            fig_trend = px.line(df_trend, x='TAHUN', y=['LUAS TANAM (HA)', 'PRODUKSI (TON)'], markers=True, template="plotly_dark")
            fig_trend.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Data belum tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("🏆 Peringkat Top 5 Provinsi Produksi Tertinggi")
        if not df_filtered.empty:
            df_rank_prov = df_filtered.groupby('PROVINSI')['PRODUKSI (TON)'].sum().reset_index().sort_values(by='PRODUKSI (TON)', ascending=False).head(5)
            fig_rank = px.bar(df_rank_prov, x='PRODUKSI (TON)', y='PROVINSI', orientation='h', color='PRODUKSI (TON)', color_continuous_scale='Greens', template="plotly_dark")
            fig_rank.update_layout(height=320, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'}, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_rank, use_container_width=True)
        else:
            st.info("Data belum tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# LAYAR 2: DATA WILAYAH
# ---------------------------------------------------------
elif menu == "Data Wilayah":
    st.subheader("📊 Analisis Data Wilayah Per Kabupaten")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("Luas Tanam (Ha) Per Kabupaten")
        if not df_filtered.empty:
            df_kab_tanam = df_filtered.groupby('KABUPATEN/KOTA')['LUAS TANAM (HA)'].sum().reset_index()
            fig_kab = px.bar(df_kab_tanam, x='KABUPATEN/KOTA', y='LUAS TANAM (HA)', color='LUAS TANAM (HA)', template="plotly_dark")
            fig_kab.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_kab, use_container_width=True)
        else:
            st.info("Data belum tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card-box">', unsafe_allow_html=True)
        st.subheader("Produksi (Ton) Per Kabupaten")
        if not df_filtered.empty:
            df_kab_prod = df_filtered.groupby('KABUPATEN/KOTA')['PRODUKSI (TON)'].sum().reset_index()
            fig_prod = px.bar(df_kab_prod, x='KABUPATEN/KOTA', y='PRODUKSI (TON)', color='PRODUKSI (TON)', color_continuous_scale='Blues', template="plotly_dark")
            fig_prod.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_prod, use_container_width=True)
        else:
            st.info("Data belum tersedia.")
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📄 Membuka Data Real-Time Google Sheets"):
        st.dataframe(df_filtered, use_container_width=True, height=400)

# ---------------------------------------------------------
# LAYAR 3: ANALITIK & PRODUKTIVITAS
# ---------------------------------------------------------
elif menu == "Analitik & Produktivitas":
    st.subheader("⚡ Analitik Produktivitas (Provitas)")

    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("📈 Grafik Produktivitas (Ku/Ha) Per Tahun")
    if not df_raw.empty:
        df_prov_nat = df_raw.groupby('TAHUN')['PRODUKTIVITAS (KU/HA)'].mean().reset_index()
        fig_nat = px.bar(df_prov_nat, x='TAHUN', y='PRODUKTIVITAS (KU/HA)', text_auto='.2f', color='PRODUKTIVITAS (KU/HA)', color_continuous_scale='Viridis', template="plotly_dark")
        fig_nat.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_nat, use_container_width=True)
    else:
        st.info("Data belum tersedia.")
    st.markdown('</div>', unsafe_allow_html=True)

    col_max, col_min = st.columns(2)
    if not df_filtered.empty and df_filtered['PRODUKTIVITAS (KU/HA)'].sum() > 0:
        max_row = df_filtered.loc[df_filtered['PRODUKTIVITAS (KU/HA)'].idxmax()]
        min_row = df_filtered.loc[df_filtered['PRODUKTIVITAS (KU/HA)'].idxmin()]

        with col_max:
            st.markdown(f"""
                <div class="card-box" style="border-left: 6px solid #10b981;">
                    <h4 style="color:#059669; margin:0;">🥇 Produktivitas TERTINGGI</h4>
                    <h2 style="margin:8px 0; color:#38bdf8;">{max_row['PRODUKTIVITAS (KU/HA)']} Ku/Ha</h2>
                    <p style="margin:0; color:#94a3b8;">
                        <b>Kabupaten:</b> {max_row['KABUPATEN/KOTA']}<br>
                        <b>Provinsi:</b> {max_row['PROVINSI']} ({max_row['TAHUN']})
                    </p>
                </div>
            """, unsafe_allow_html=True)

        with col_min:
            st.markdown(f"""
                <div class="card-box" style="border-left: 6px solid #ef4444;">
                    <h4 style="color:#dc2626; margin:0;">🔻 Produktivitas TERENDAH</h4>
                    <h2 style="margin:8px 0; color:#ef4444;">{min_row['PRODUKTIVITAS (KU/HA)']} Ku/Ha</h2>
                    <p style="margin:0; color:#94a3b8;">
                        <b>Kabupaten:</b> {min_row['KABUPATEN/KOTA']}<br>
                        <b>Provinsi:</b> {min_row['PROVINSI']} ({min_row['TAHUN']})
                    </p>
                </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# LAYAR 4: PETA PERSEBARAN 38 PROVINSI
# ---------------------------------------------------------
elif menu == "Peta Persebaran 38 Provinsi":
    st.subheader("🗺️ Peta Persebaran Kedelai 38 Provinsi Indonesia")
    st.caption("Menampilkan titik lokasi Provinsi berdasarkan Luas Tanam, Luas Panen, Produksi, dan Produktivitas.")

    if not df_filtered.empty:
        map_df = df_filtered.groupby(['PROVINSI', 'LAT', 'LON'], as_index=False).agg({
            'LUAS TANAM (HA)': 'mean',
            'LUAS PANEN (HA)': 'mean',
            'PRODUKSI (TON)': 'mean',
            'PRODUKTIVITAS (KU/HA)': 'mean'
        })

        fig_map_full = px.scatter_map(
            map_df,
            lat="LAT",
            lon="LON",
            size="PRODUKSI (TON)",
            color="PRODUKTIVITAS (KU/HA)",
            color_continuous_scale="Reds",
            hover_name="PROVINSI",
            hover_data={
                "LUAS TANAM (HA)": ":,.0f",
                "LUAS PANEN (HA)": ":,.0f",
                "PRODUKSI (TON)": ":,.0f",
                "PRODUKTIVITAS (KU/HA)": ":.2f",
                "LAT": False, "LON": False
            },
            zoom=4.2,
            center={"lat": -2.5, "lon": 118.0},
            height=620,
            map_style="carto-darkmatter"
        )
        fig_map_full.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_map_full, use_container_width=True)
    else:
        st.info("Data tidak ditemukan untuk koneksi Google Sheets saat ini.")