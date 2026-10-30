import json
import os
import re
import streamlit as st
import pdfplumber

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOC_DIR = os.path.join(BASE_DIR, "data", "dokumen")
CATALOG_PATH = os.path.join(BASE_DIR, "data", "katalog_dokumen.json")

with open(CATALOG_PATH, encoding="utf-8") as f:
    KATALOG = json.load(f)

KATA_FILE = ["file", "pdf", "unduh", "download", "lampiran", "berkas", "salinan"]
KATA_JADWAL = ["jadwal", "kuliah", "kelas"]


def cocok(kata: str, teks: str) -> bool:
    return re.search(r"\b" + re.escape(kata) + r"\b", teks) is not None


def ada_permintaan_file(pertanyaan: str) -> bool:
    q = pertanyaan.lower()
    return any(cocok(k, q) for k in KATA_FILE)


def cari_lampiran(pertanyaan: str) -> list:
    q = pertanyaan.lower()
    minta_file = ada_permintaan_file(pertanyaan)
    bahas_jadwal = any(cocok(k, q) for k in KATA_JADWAL)
    if not (minta_file or bahas_jadwal):
        return []
    hasil = []
    for doc in KATALOG:
        if any(cocok(k, q) for k in doc.get("kecuali", [])):
            continue
        if not any(cocok(k, q) for k in doc["kata_kunci"]):
            continue
        if minta_file or doc.get("jenis") == "jadwal":
            hasil.append(doc)
    return hasil


def cari_teks(pertanyaan: str) -> list:
    q = pertanyaan.lower()
    hasil = []
    for doc in KATALOG:
        if any(cocok(k, q) for k in doc.get("kecuali", [])):
            continue
        if any(cocok(k, q) for k in doc["kata_kunci"]):
            hasil.append(doc)
    return hasil


@st.cache_data
def teks_dari_pdf(nama_file: str) -> str:
    path = os.path.join(DOC_DIR, nama_file)
    if not os.path.exists(path):
        return ""
    halaman = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            halaman.append(p.extract_text() or "")
    return "\n".join(halaman)


def ambil_teks(docs: list, maks: int = 2) -> str:
    bagian = []
    for doc in docs:
        isi = ""
        if doc.get("teks"):
            path = os.path.join(BASE_DIR, doc["teks"])
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    isi = f.read()
        if not isi and doc.get("jenis") == "jadwal":
            isi = teks_dari_pdf(doc["file"])
        if isi:
            bagian.append(f"--- {doc['judul']} ---\n{isi}")
        if len(bagian) >= maks:
            break
    return "\n\n".join(bagian)


@st.cache_data
def baca_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def render_lampiran(docs: list, key_prefix: str):
    for i, doc in enumerate(docs):
        path = os.path.join(DOC_DIR, doc["file"])
        if not os.path.exists(path):
            continue
        st.download_button(
            label=f"⬇️ {doc['judul']} (update {doc['tanggal']})",
            data=baca_file(path),
            file_name=doc["file"],
            mime="application/pdf",
            key=f"{key_prefix}_{i}",
        )
