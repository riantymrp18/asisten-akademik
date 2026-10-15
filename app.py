import streamlit as st
from groq import Groq

# 1. Judul dan Tampilan Header
st.set_page_config(page_title="Asisten Informasi Akademik", page_icon="🤖")

# Sembunyikan Header bawaan Streamlit (Share, GitHub icon, Main Menu) & Footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🤖 Asisten Informasi Akademik")
st.caption("Tanyakan informasi seputar perkuliahan, jadwal, dan administrasi akademik.")

# 2. Ambil Groq API Key secara otomatis dari Secrets Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Groq API Key belum diatur di Streamlit Secrets. Harap atur terlebih dahulu di menu pengaturan deployment.")
    st.stop()

# Inisialisasi Klien Groq
try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"Gagal menginisialisasi Groq API: {e}")
    st.stop()

# 3. SETTING BAHAN / KNOWLEDGE BASE AI (System Prompt)
KNOWLEDGE_BASE = """
Kamu adalah Asisten Informasi Akademik Universitas Buana Perjuangan (UBP) Karawang.
Berikut adalah data/bahan informasi resmi dan lengkap yang harus kamu gunakan untuk menjawab pertanyaan:

- Nama Kampus: Universitas Buana Perjuangan (UBP) Karawang
- Program Studi Utama: Sistem Informasi (S1)
- Syarat Pengajuan Judul Skripsi (Program Studi Sistem Informasi):
  1. Telah menempuh minimal 120 SKS.
  2. IPK minimal 2.75.
  3. Lulus mata kuliah Metodologi Penelitian dan Pemrograman Web.
  4. Proposal judul harus disetujui oleh dosen PA (Pembimbing Akademik).

- Jadwal Kuliah & Jam Operasional Umum:
  - Perkuliahan aktif Senin s.d. Jumat pukul 08.00 - 17.00 WIB (serta hari Sabtu untuk kelas/program tertentu).
  - Kartu Rencana Studi (KRS) diisi melalui portal akademik masing-masing mahasiswa setiap awal semester.
- Layanan Akademik: Hubungi bagian tata usaha prodi atau cek portal web kampus untuk informasi surat aktif kuliah dan cuti.

- DETAIL JADWAL PERKULIAHAN PRODI SISTEM INFORMASI (SEMESTER GANJIL TA 2026/2027):

  1. SEMESTER 1 (Angkatan 2026, Ruang: A.307-A.308):
     - Senin:
       * Pendidikan Pancasila (2 SKS, Dr. Erwin Susanto, S.Pd., M.Pd) | Kelas A: 07.00-08.40 (A.307), Kelas B: 09.00-10.40 (A.307), Kelas C: 20.00-21.40 (A.307).
       * Percakapan Bahasa Inggris (2 SKS, Hilda Tri Yulianti, M.Pd) | Kelas A: 09.00-10.40 (A.308), Kelas B: 11.00-12.40 (A.308), Kelas C: 18.15-19.55 (A.308).
       * Bahasa Indonesia (2 SKS, Lisa Mariam, M.Pd) | Kelas A: 09.00-10.40 (A.307), Kelas B: 07.00-08.40 (A.307), Kelas C: 18.15-19.55 (A.307).
     - Rabu:
       * Dasar-Dasar Akuntansi dan Keuangan (2 SKS, Dhea Imroatul Fatihah, SE., M.Ak) | Kelas A: 07.00-08.40 (A.308), Kelas B: 09.00-10.40 (A.308), Kelas C: 18.15-19.55 (A.308).
       * Pengantar Sistem Informasi (3 SKS, Agustia Hananto, M.Kom) | Kelas A: 07.00-08.40 (A.307), Kelas B: 09.00-10.40 (A.307), Kelas C: 20.00-21.40 (A.307).
     - Kamis:
       * Algoritma dan Pemrograman (Teori) (3 SKS, Dr. Tukino, S.Kom, MMSI) | Kelas A: 07.00-08.40 & 09.00-10.40 (A.307), Kelas B: 13.00-14.40 & 15.00-16.40 (A.307), Kelas C: 18.15-19.55 & 20.00-21.40 (A.307).
     - Jumat:
       * Matematika Diskrit (3 SKS, Fitria Nurapriani, S.Pd., M.Pd) | Kelas A: 07.00-08.40 (A.307), Kelas B: 09.00-10.40 (A.307), Kelas C: 20.00-21.40 (A.307).
       * Pengantar Manajemen dan Bisnis (2 SKS, Rieke Retnosari, Ph.D) | Kelas A: 09.00-10.40 (A.308), Kelas B: 07.00-08.40 (A.308), Kelas C: 18.15-19.55 (A.308).

  2. SEMESTER 3 (Angkatan 2025, Ruang: A.407-A.408 / Lab.Kom):
     - Senin:
       * Analisa dan Perancangan Sistem Informasi (T/P) (3 SKS, Dr. Tukino, S.Kom, MMSI) | Kelas A: 07.00-08.40 (A.408), Kelas B: 09.00-10.40 (A.408), Kelas C: 18.15-19.55 (A.408).
       * Arsitektur Enterprise (3 SKS, Prof. April Lia Hananto, M.Kom., Ph.D) | Kelas A: 09.00-10.40 (A.407), Kelas B: 07.00-08.40 (A.407), Kelas C: 20.00-21.40 (A.407).
     - Selasa:
       * Desain dan Manajemen Jaringan Komputer (Teori & Praktik) (3 SKS, Agustia Hananto, M.Kom) | Kelas A: Teori 07.00-08.40 / Praktik 09.00-10.40 (A.408 & Lab.Kom), Kelas B: Teori 13.00-14.40 / Praktik 15.00-16.40 (A.408 & Lab.Kom), Kelas C: Teori 18.15-19.55 / Praktik 20.00-21.40 (A.408 & Lab.Kom).
       * Jati Diri Bangsa (2 SKS, Dr. Yogi Nugraha, M.Pd) | Kelas A: 11.00-12.40 (A.407), Kelas B: 13.00-14.40 (A.407), Kelas C: 20.00-21.40 (A.407).
     - Rabu:
       * Sistem Basis Data (2 SKS, Elfina Novalia, M.Kom) | Kelas A: 09.00-10.40 (A.408), Kelas B: 07.00-08.40 (A.408), Kelas C: 18.15-19.55 (A.408).
       * Digital dan Media Baru (3 SKS, Dr. Shofa Shofia H, S.Kom., M.Kom) | Kelas A: 07.00-08.40 (A.407), Kelas B: 09.00-10.40 (A.407), Kelas C: 18.15-19.55 (A.407).
     - Kamis:
       * Statistik Probabilitas (2 SKS, Fitria Nurapriani, S.Pd., M.Pd) | Kelas A: 09.00-10.40 (A.408), Kelas B: 07.00-08.40 (A.408), Kelas C: 20.00-21.40 (A.408).
     - Jumat:
       * Desain UI-UX (Teori & Praktik) (Teori 2 SKS oleh Baenil Huda, ST., M.Kom; Praktik 2 SKS) | Kelas A: Teori 07.00-08.40 / Praktik 09.00-10.40 (A.408 & Lab.Kom), Kelas B: Teori 13.00-14.40 / Praktik 15.00-16.40 (A.408 & Lab.Kom), Kelas C: Teori 18.15-19.55 / Praktik 20.00-21.40 (A.408 & Lab.Kom).

  3. SEMESTER 5 (Angkatan 2024, Ruang: A.407-A.410 / Lab.Kom):
     - Senin:
       * Integrasi Aplikasi Perusahaan (Teori & Praktik) (3 SKS, Bayu Priyatna, M.Kom, Ph.D) | Kelas A: Teori 07.00-08.40 / Praktik 09.00-10.40 (A.408 & Lab.Kom), Kelas B: Teori 13.00-14.40 / Praktik 15.00-16.40 (A.408 & Lab.Kom), Kelas C: Teori 18.15-19.55 / Praktik 20.00-21.40 (A.408 & Lab.Kom).
       * Manajemen Proyek Sistem Informasi (2 SKS, Elfina Novalia, M.Kom) | Kelas A: 07.00-08.40 (A.408), Kelas B: 09.00-10.40 (A.408), Kelas C: 18.15-19.55 (A.408).
     - Selasa:
       * Etika Profesi Teknologi Informasi (3 SKS, Sutan Faisal, M.Kom) | Kelas A: 09.00-10.40 (A.410A), Kelas B: 07.00-08.40 (A.404B), Kelas C: 20.00-21.40 (A.308C).
       * Sistem Pendukung Keputusan (3 SKS, Dr. Shofa Shofia H., S.Kom., M.Kom) | Kelas A: 07.00-08.40 (A.407), Kelas B: 09.00-10.40 (A.407), Kelas C: 18.15-19.55 (A.407).
     - Rabu:
       * Manajemen Proses Bisnis (3 SKS, Kiki Ahmad Baihaqi, M.Kom) | Kelas A: 09.00-10.40 (A.409), Kelas B: 07.00-08.40 (A.409), Kelas C: 20.00-21.40 (A.408C).
     - Kamis:
       * Keamanan Teknologi Informasi dan Manajemen Resiko (3 SKS, Baenil Huda, ST., M.Kom) | Kelas A: 07.00-08.40 (A.407C), Kelas B: 09.00-10.40 (A.409), Kelas C: 18.15-19.55 (A.409).
     - Jumat:
       * Tata Kelola dan Manajemen Teknologi Informasi (3 SKS, Prof. April Lia Hananto, M.Kom., Ph.D) | Kelas A: 07.00-08.40 (A.408C), Kelas B: 09.00-10.40 (A.407BC), Kelas C: 18.15-19.55 (A.407BC).

  4. SEMESTER 7 (Angkatan 2023, Ruang: A.305-A.409 / Lab.Kom):
     - Senin:
       * Big Data Analysis & Business Intelligence (Teori & Praktik) (3 SKS, Agustia Hananto, M.Kom) | Kelas A: Teori 09.00-10.40 / Praktik 11.00-12.40 (A.409A & Lab), Kelas B: Teori 13.00-14.40 / Praktik 15.00-16.40 (A.408B & Lab), Kelas C: Teori 18.15-19.55 / Praktik 20.00-21.40 (A.407C & Lab).
     - Selasa:
       * Inovasi Digital (Teori & Praktik) (3 SKS, Dr. Shofa Shofia H., S.Kom., M.Kom) | Kelas A: Teori 07.00-08.40 / Praktik 09.00-10.40 (A.308 & Lab), Kelas B: Teori 13.00-14.40 / Praktik 15.00-16.40 (A.308 & Lab), Kelas C: Teori 18.15-19.55 / Praktik 20.00-21.40 (A.310C & Lab).
     - Rabu:
       * Kewirausahaan (3 SKS, Rieke Retnosari, MM., Ph.D & Baenil Huda, M.Kom) | Kelas A: 09.00-10.40 (A.308), Kelas B: 13.00-14.40 (A.308), Kelas C: 18.15-19.55 (A.308).
       * Bahasa Jepang (2 SKS, Rahmat, S.Pd., M.Pd / Ray Andriana, S) | Kelas A: 11.00-12.40 (A.305), Kelas B: 09.00-10.40 (A.305), Kelas C: 20.00-21.40 (A.307C).
     - Kamis:
       * Sistem Informasi Penjualan Online (Teori & Praktik) (3 SKS, Bayu Priyatna, M.Kom, Ph.D) | Kelas A: Teori 07.00-08.40 / Praktik 09.00-10.40 (A.308 & Lab), Kelas B: Teori 13.00-14.40 / Praktik 15.00-16.40 (A.308 & Lab), Kelas C: Teori 18.15-19.55 / Praktik 20.00-21.40 (A.308 & Lab).
     - Jumat:
       * Proposal Tugas Akhir (2 SKS, Elfina Novalia, M.Kom / Fitria Nurapriani, M.Pd) | Kelas A: 11.00-12.40, Kelas B: 09.00-10.40, Kelas C: 18.15-19.55.
     - Sabtu:
       * Kuliah Kerja Nyata (KKN) (3 SKS, Dr. Tukino, S.Kom, MMSI) | Kelas A: 09.00-10.40, Kelas B: 11.00-12.40, Kelas C: 18.15-19.55.

- TAMBAHAN DATA PRODI & FAKULTAS LAINNYA DI UBP KARAWANG:
  1. Program Studi Magister Manajemen (S2):
     - Contoh Jadwal Semester I (Kelas MM26A): Etika Profesi & Tata Kelola Organisasi (Sabtu 08.00 oleh Dr. H. Sihabudin), Inovasi & Kewirausahaan Digital (Sabtu 10.00 oleh Prof. Dr. H. Dedi Mulyadi), dll.
  2. Program Studi S1 Teknik Industri:
     - Menyediakan kelas paralel T126A-L (Semester 1), T125A-J (Semester 3), T124A-H (Semester 5), dan T123A-H (Semester 7) dengan mata kuliah seperti Pendidikan Pancasila, Kalkulus I, Pengantar Teknik Industri, dll.
  3. Program Studi S1 Teknik Mesin:
     - Menyediakan kelas pagi dan malam (TM 26A-E untuk Semester 1, TM 25A-D untuk Semester 3, TM 24A-C untuk Semester 5, serta konsentrasi Konversi Energi & Manufaktur untuk Semester 7).
  4. Program Studi S1 Ilmu Hukum:
     - Menyediakan kelas reguler dan malam (HK26A-E untuk Semester 1, HK25A-D untuk Semester 3, HK24A-D untuk Semester 5, dan HK23A-E untuk Semester 7) dengan mata kuliah seperti Pengantar Ilmu Hukum, Hukum Adat, Moot Court, dll.
  5. Program Studi S1 Farmasi:
     - Menyediakan kelas dari semester 1 hingga semester 7 (FM26, FM25, FM24, FM23). Mata kuliah mencakup Kalkulasi Farmasi, Farmakologi Molekuler, Farmasi Klinik, Fitoterapi, dll.
  6. Program Studi S1 PPKn:
     - Menyediakan kelas untuk semester 1 (PK26A), semester 3 (PK25A-B), semester 5 (PK24A-B), dan semester 7 (PK23A-B). Mata kuliah mencakup Pendidikan Pancasila, Kurikulum & Pembelajaran PPKn, Seminar PPKn, KKN, dll.
  7. Program Studi S1 Teknik Informatika:
     - Menyediakan kelas paralel dari semester 1 hingga semester 7 (IF26, IF25, IF24, IF23). Mata kuliah mencakup Algoritma, Basis Data, Pemrograman Web, Pembelajaran Mendalam, Visi Komputer, dll.

Aturan Menjawab:
- Jawablah pertanyaan mahasiswa secara ramah, sopan, dan gunakan format tabel yang rapi apabila mereka menanyakan jadwal mata kuliah.
- Pastikan informasi hari, jam, dosen, ruang, dan kelas merujuk tepat pada data di atas.
- Jika informasi tidak ada di dalam data di atas, arahkan mahasiswa untuk bertanya langsung ke bagian administrasi prodi masing-masing di UBP Karawang.
"""

# 4. Simpan Riwayat Percakapan
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu terkait informasi akademik perkuliahanmu hari ini?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. Kolom Input Pesan Pengguna
if user_input := st.chat_input("Ketik pertanyaan akademikmu di sini..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    groq_messages = [{"role": "system", "content": KNOWLEDGE_BASE}]
    for m in st.session_state.messages:
        groq_messages.append({"role": m["role"], "content": m["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses jawaban..."):
            try:
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=groq_messages,
                    temperature=0.3,
                    max_tokens=1024
                )
                
                bot_reply = completion.choices[0].message.content
                st.write(bot_reply)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"Terjadi kesalahan pada Groq API: {e}")
