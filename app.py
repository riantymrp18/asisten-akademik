import streamlit as st
from groq import Groq
from lampiran import cari_lampiran, render_lampiran, ada_permintaan_file

# 1. Judul dan Tampilan Header
st.set_page_config(page_title="Asisten Informasi Akademik", page_icon="🤖")

tampilan = """
<style>
#MainMenu, footer, header {visibility: hidden;}
.stApp {
    background: linear-gradient(160deg, #E8F4FF 0%, #F3EEFF 50%, #FFF6E5 100%);
}
.block-container { max-width: 860px; padding-top: 2rem; }
.kepala {
    background: linear-gradient(135deg, #1565C0 0%, #7E57C2 100%);
    color: #FFFFFF;
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(21,101,192,0.25);
}
.kepala h2 { color: #FFFFFF; margin: 0 0 0.3rem 0; font-size: 1.7rem; }
.kepala p { color: #E3ECFF; margin: 0; font-size: 0.95rem; }
.lencana {
    display: inline-block;
    background: #FFC93C;
    color: #3B2A00;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    margin-bottom: 0.6rem;
}
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 0.8rem 1rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    border: none;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {
    background-color: #FFFFFF;
}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {
    background-color: #DCEBFF;
}
[data-testid="stChatInput"] textarea {
    border-radius: 14px;
    border: 2px solid #7E57C2;
}
.stButton > button {
    background: #FFFFFF;
    color: #1565C0;
    border: 2px solid #1565C0;
    border-radius: 999px;
    font-weight: 600;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: #1565C0;
    color: #FFFFFF;
}
.banner-prototipe {
    background-color: #FFF1C2;
    border-left: 6px solid #F9A825;
    padding: 0.7rem 1rem;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #5C4300;
    margin-bottom: 1rem;
}
</style>
"""
st.markdown(tampilan, unsafe_allow_html=True)

st.markdown("""
<div class="kepala">
    <span class="lencana">PROTOTIPE TUGAS AKHIR</span>
    <h2>Asisten Informasi Akademik</h2>
    <p>Tanyakan jadwal perkuliahan, daftar dosen pengampu, dan kalender akademik semester ganjil 2026/2027.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner-prototipe">
    <b>Prototipe penelitian Tugas Akhir.</b> Ini bukan layanan resmi Universitas Buana Perjuangan Karawang
    dan belum terintegrasi dengan SIPT. Untuk informasi resmi, cek dokumen asli atau hubungi bagian administrasi prodi.
</div>
""", unsafe_allow_html=True)

# Tombol contoh pertanyaan
contoh = [
    "Jadwal kuliah Sistem Informasi semester 3",
    "Kapan UTS semester ganjil?",
    "Minta file kalender akademik",
]
kolom = st.columns(len(contoh))
for i, teks in enumerate(contoh):
    if kolom[i].button(teks, key=f"contoh_{i}", use_container_width=True):
        st.session_state["pending"] = teks

# 2. Ambil Groq API Key dari Secrets Streamlit
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Groq API Key belum diatur di Streamlit Secrets. Harap atur terlebih dahulu di menu pengaturan deployment.")
    st.stop()

try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"Gagal menginisialisasi Groq API: {e}")
    st.stop()

# 3. KNOWLEDGE BASE AI (System Prompt)
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

- Layanan Akademik:
  - Kartu Rencana Studi (KRS) diisi melalui portal akademik masing-masing mahasiswa setiap awal semester.
  - Untuk informasi surat aktif kuliah dan cuti, hubungi bagian tata usaha prodi atau cek portal web kampus.

- KALENDER AKADEMIK SEMESTER GASAL 2026/2027 (sumber: SK Rektor Nomor 142/R/SK/2026):
  - Perwalian dan pengisian KRS: 18 Agustus s.d. 20 September 2026.
  - Modifikasi KRS: 21 s.d. 26 September 2026.
  - Perkuliahan tengah semester: 21 September s.d. 7 November 2026.
  - Pekan UTS: 9 s.d. 14 November 2026.
  - Batas input nilai UTS: 16 s.d. 29 November 2026.
  - Perkuliahan akhir semester: 16 November 2026 s.d. 2 Januari 2027.
  - Pekan UAS: 11 s.d. 16 Januari 2027.
  - Pengolahan KHS: 17 s.d. 31 Januari 2027.
  - Batas sidang gelombang 1 semester gasal: 19 September 2026.
  - Kegiatan wisuda ke-13: 24 November 2026.

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

- PRODI LAIN DI UBP KARAWANG (jadwal lengkapnya ada sebagai file resmi, lihat aturan di bawah):
  - S2 Magister Manajemen, S1 Teknik Industri, S1 Teknik Mesin, S1 Ilmu Hukum, S1 Farmasi, S1 PPKn, S1 Pendidikan Agama Islam, S1 Psikologi, S1 Akuntansi, S1 Teknik Informatika, S1 PGSD, S1 Manajemen.

Aturan Menjawab:
- Jawab dengan ramah, sopan, dan singkat.
- Jangan membuat file CSV, jangan membuat tabel panjang, dan jangan menyalin seluruh jadwal ke dalam jawaban. Jawab hanya bagian yang ditanyakan, misalnya satu mata kuliah atau satu hari.
- Jika ada catatan sistem tentang file resmi, sebut bahwa file tersebut bisa diunduh lewat tombol di bawah jawaban. Jangan menyebut nama file atau tautan.
- Jika mahasiswa menanyakan jadwal tanpa menyebut program studi, tanyakan dulu program studinya.
- Pastikan hari, jam, dosen, ruang, dan kelas sesuai dengan data di atas.
- Jika informasi tidak ada di dalam data di atas, arahkan mahasiswa untuk bertanya langsung ke bagian administrasi prodi masing-masing di UBP Karawang.
"""

# 4. Riwayat percakapan (termasuk tombol lampiran)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Halo! Ada yang bisa saya bantu terkait informasi akademik perkuliahanmu hari ini?", "lampiran": []}
    ]

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("lampiran"):
            render_lampiran(msg["lampiran"], key_prefix=f"hist_{idx}")

# 5. Input pesan pengguna (dari kolom ketik atau tombol contoh)
user_input = st.chat_input("Ketik pertanyaan akademikmu di sini...") or st.session_state.pop("pending", None)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "lampiran": []})
    with st.chat_message("user"):
        st.write(user_input)

    lampiran = cari_lampiran(user_input)

    catatan = ""
    if lampiran:
        catatan = ("Catatan sistem: file resmi yang relevan tersedia sebagai tombol unduh di bawah jawaban. "
                   "Jangan menuliskan ulang seluruh jadwal atau membuat CSV. Cukup sebut bahwa file bisa diunduh, "
                   "tanpa menyebut nama file.")
    elif ada_permintaan_file(user_input):
        catatan = ("Catatan sistem: file yang diminta tidak tersedia. Sampaikan dengan sopan bahwa file tersebut "
                   "belum tersedia dan arahkan mahasiswa ke bagian administrasi prodi.")

    system_content = KNOWLEDGE_BASE + ("\n\n" + catatan if catatan else "")
    groq_messages = [{"role": "system", "content": system_content}]
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
                if lampiran:
                    render_lampiran(lampiran, key_prefix=f"new_{len(st.session_state.messages)}")
                st.session_state.messages.append({"role": "assistant", "content": bot_reply, "lampiran": lampiran})
            except Exception as e:
                st.error(f"Terjadi kesalahan pada Groq API: {e}")
