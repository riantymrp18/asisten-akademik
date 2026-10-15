import streamlit as st
from groq import Groq

# 1. Judul dan Tampilan Header
st.set_page_config(page_title="Asisten Informasi Akademik", page_icon="🤖")
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
Berikut adalah data/bahan informasi resmi yang harus kamu gunakan untuk menjawab pertanyaan:

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

- TAMBAHAN DATA JADWAL PERKULIAHAN & PRODI LAIN (Semester Ganjil TA 2026/2027):
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
- Jawablah pertanyaan mahasiswa secara ramah, sopan, dan berdasarkan data di atas.
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
