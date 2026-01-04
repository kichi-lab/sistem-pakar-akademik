import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Pakar Akademik", layout="wide")

# --- BASIS PENGETAHUAN ---
GRADE_BOBOT = {
    "A": 4.0, "A-": 3.75, "B+": 3.5, "B": 3.25, "B-": 3.0,
    "C+": 2.75, "C": 2.5, "C-": 2.25,
    "D+": 2.0, "D": 1.75, "D-": 1.5,
    "E+": 1.25, "E": 1.0
}

def hitung_rekomendasi_sks(ipk):
    if ipk >= 3.5: return 24
    elif ipk >= 3.0: return 22
    elif ipk >= 2.5: return 18
    else: return 15

def get_saran(ipk):
    if ipk >= 3.5: return "Luar biasa! Pertahankan prestasimu dan ikuti program beasiswa atau magang."
    elif ipk >= 3.0: return "Prestasi bagus. Tingkatkan konsistensi belajarmu."
    else: return "Perlu evaluasi strategi belajar. Konsultasikan dengan dosen wali Anda."

# --- UI UTAMA ---
st.title("🎓 SISTEM PAKAR KONSULTASI AKADEMIK")

# 1. Input Jumlah Semester di Sidebar
with st.sidebar:
    st.header("Konfigurasi")
    jml_semester = st.number_input("Jumlah semester yang telah ditempuh:", min_value=1, max_value=14, value=1)

# 2. Area Input Data per Semester
st.subheader("📝 Input Data Mata Kuliah")
st.info("Klik tombol '+' di bawah tabel setiap semester untuk menambah mata kuliah.")

# List untuk menampung semua dataframe dari setiap semester
all_semester_data = []

for i in range(1, jml_semester + 1):
    with st.expander(f"📘 Semester {i}", expanded=(i == jml_semester)):
        # Template tabel input
        df_template = pd.DataFrame([{"Nama MK": "", "SKS": 3, "Grade": "A"}])
        
        # Tabel interaktif (Data Editor)
        edited_df = st.data_editor(
            df_template,
            key=f"editor_sem_{i}",
            num_rows="dynamic", # Memungkinkan pengguna tambah/hapus baris
            column_config={
                "SKS": st.column_config.NumberColumn(min_value=1, max_value=6, step=1),
                "Grade": st.column_config.SelectboxColumn(options=list(GRADE_BOBOT.keys()))
            },
            use_container_width=True
        )
        edited_df['Sem'] = i # Tandai semester
        all_semester_data.append(edited_df)

# 3. Tombol Proses Analisis
if st.button("Analisis Akademik", type="primary"):
    # Gabungkan semua data
    df_total = pd.concat(all_semester_data, ignore_index=True)
    
    # Bersihkan data (hapus baris jika Nama MK kosong)
    df_total = df_total[df_total['Nama MK'] != ""]
    
    if not df_total.empty:
        # Perhitungan Nilai
        df_total['Bobot'] = df_total['Grade'].map(GRADE_BOBOT)
        df_total['Poin'] = df_total['SKS'] * df_total['Bobot']
        
        # Hitung IP per Semester untuk Grafik
        summary_sem = df_total.groupby('Sem').apply(lambda x: x['Poin'].sum() / x['SKS'].sum()).reset_index()
        summary_sem.columns = ['Semester', 'IP']
        
        # Hitung IPK Akhir
        total_sks = df_total['SKS'].sum()
        total_poin = df_total['Poin'].sum()
        ipk_akhir = total_poin / total_sks

        # --- TAMPILAN HASIL ---
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("IPK Akhir", f"{ipk_akhir:.2f}")
            st.write(f"**Total SKS ditempuh:** {total_sks}")
            st.write(f"**Rekomendasi SKS Semester Depan:** {hitung_rekomendasi_sks(ipk_akhir)}")

        with col2:
            st.subheader("🧠 Saran Pakar")
            st.success(get_saran(ipk_akhir))

        # Grafik Tren
        st.subheader("📈 Tren IP per Semester")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(summary_sem['Semester'], summary_sem['IP'], marker='o', linestyle='-', color='blue')
        ax.set_xticks(summary_sem['Semester'])
        ax.set_ylim(0, 4.2)
        ax.set_xlabel("Semester")
        ax.set_ylabel("IP Semester")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        # Detail MK Bermasalah
        mk_rendah = df_total[df_total['Bobot'] < 2.75]
        if not mk_rendah.empty:
            st.subheader("⚠️ Mata Kuliah Perlu Perhatian")
            st.warning("Mata kuliah dengan grade di bawah C+:")
            st.table(mk_rendah[['Sem', 'Nama MK', 'Grade']])
    else:
        st.error("Silakan isi data mata kuliah terlebih dahulu!")