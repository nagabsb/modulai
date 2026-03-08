from models import GenerateRequest


def build_prompt(data: GenerateRequest) -> str:
    """Build prompt based on document type"""
    base_info = f"""
Jenjang: {data.jenjang}
Kelas: {data.kelas}
Kurikulum: {data.kurikulum}
Semester: {data.semester}
Fase: {data.fase}
Mata Pelajaran: {data.mata_pelajaran}
Topik/Materi: {data.topik}
Alokasi Waktu: {data.alokasi_waktu} menit
"""

    physics_diagram_instruction = ""
    if data.mata_pelajaran.lower() in ["fisika", "ipa"] and data.doc_type == "soal":
        custom_values = ""
        if data.use_custom_values and data.resistor1 and data.voltage:
            custom_values = f"""
NILAI CUSTOM YANG HARUS DIGUNAKAN:
- Resistor 1: {data.resistor1} Ohm
- Resistor 2: {data.resistor2 or data.resistor1} Ohm
- Tegangan: {data.voltage} Volt
"""

        physics_diagram_instruction = f"""
INSTRUKSI KHUSUS UNTUK SOAL FISIKA:
{custom_values}

Untuk soal tentang RANGKAIAN LISTRIK, tambahkan tag berikut SEBELUM teks soal:
[DIAGRAM:circuit,type=series,R1=2,R2=3,V=12]
atau
[DIAGRAM:circuit,type=parallel,R1=4,R2=6,V=24]

Untuk soal tentang PENGUKURAN (ammeter/voltmeter), tambahkan tag:
[DIAGRAM:meter,type=ammeter,needle=70,range=0.5 A]
atau
[DIAGRAM:meter,type=voltmeter,needle=45,range=10 V]

Untuk soal tentang BIDANG MIRING, tambahkan tag:
[DIAGRAM:physics,scene=inclined-plane,angle=30,mass=5]

Untuk soal tentang GERAK PARABOLA, tambahkan tag:
[DIAGRAM:physics,scene=projectile,angle=45,v0=20]

Untuk soal tentang KATROL, tambahkan tag:
[DIAGRAM:physics,scene=pulley,m1=5,m2=3]

Tag diagram WAJIB ada untuk setiap soal yang relevan dengan topik di atas.
"""

    if data.doc_type == "modul":
        return f"""Buatkan Modul Ajar lengkap dengan format berikut:
{base_info}

Struktur Modul Ajar:
1. INFORMASI UMUM
   - Identitas Modul
   - Kompetensi Awal
   - Profil Pelajar Pancasila
   - Sarana Prasarana
   - Target Peserta Didik
   - Model Pembelajaran

2. KOMPONEN INTI
   - Capaian Pembelajaran (CP)
   - Tujuan Pembelajaran (TP)
   - Alur Tujuan Pembelajaran (ATP)
   - Pemahaman Bermakna
   - Pertanyaan Pemantik
   - Kegiatan Pembelajaran (Pendahuluan, Inti, Penutup)
   - Asesmen (Diagnostik, Formatif, Sumatif)
   - Pengayaan dan Remedial

3. LAMPIRAN
   - Lembar Kerja Peserta Didik
   - Bahan Bacaan
   - Glosarium

4. DAFTAR PUSTAKA
   Wajib sertakan referensi resmi berikut (sesuaikan dengan mata pelajaran dan jenjang):
   - Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi. (2024). Panduan Pembelajaran dan Asesmen Kurikulum Merdeka. Jakarta: Kemendikbudristek. Tersedia di: kurikulum.kemendikdasmen.go.id
   - Badan Standar, Kurikulum, dan Asesmen Pendidikan. (2022). Capaian Pembelajaran {data.mata_pelajaran} Fase {data.fase}. Jakarta: BSKAP.
   - Pusat Perbukuan. (2024). Buku Panduan Guru {data.mata_pelajaran} Kelas {data.kelas} {data.jenjang}. Jakarta: Kemendikdasmen. Tersedia di: buku.kemendikdasmen.go.id
   - Tambahkan 2-3 sumber relevan lainnya (buku teks, jurnal pendidikan, atau sumber resmi pemerintah)

Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). Gunakan LaTeX untuk rumus matematika ($formula$ untuk inline, $$formula$$ untuk block). JANGAN gunakan emoji."""

    elif data.doc_type == "rpp":
        return f"""Buatkan RPP (Rencana Pelaksanaan Pembelajaran) dengan format:
{base_info}

Struktur RPP:
1. Identitas RPP
2. Kompetensi Inti (KI) / Capaian Pembelajaran (CP)
3. Kompetensi Dasar (KD) / Tujuan Pembelajaran (TP)
4. Indikator Pencapaian Kompetensi
5. Materi Pembelajaran
6. Metode Pembelajaran
7. Kegiatan Pembelajaran:
   - Pendahuluan ({int(data.alokasi_waktu * 0.15)} menit)
   - Inti ({int(data.alokasi_waktu * 0.7)} menit)
   - Penutup ({int(data.alokasi_waktu * 0.15)} menit)
8. Penilaian
9. Sumber dan Media Pembelajaran

Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). JANGAN gunakan emoji."""

    elif data.doc_type == "lkpd":
        return f"""Buatkan LKPD (Lembar Kerja Peserta Didik) dengan format:
{base_info}

Struktur LKPD:
1. Judul LKPD
2. Identitas Siswa (nama, kelas, tanggal)
3. Petunjuk Pengerjaan
4. Kompetensi yang Dicapai
5. Ringkasan Materi (singkat)
6. Kegiatan 1: [Aktivitas eksplorasi]
7. Kegiatan 2: [Aktivitas diskusi/praktik]
8. Kegiatan 3: [Aktivitas penerapan]
9. Kesimpulan (isian untuk siswa)
10. Refleksi Diri

Buat dengan desain menarik, ada kotak isian untuk jawaban siswa (gunakan <u>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</u> untuk garis isian). Format: HTML dengan tabel. JANGAN gunakan emoji."""

    elif data.doc_type == "soal":
        difficulty_map = {
            "Mudah": "C1-C2 (Mengingat, Memahami)",
            "Sedang": "C3-C4 (Menerapkan, Menganalisis)",
            "Sulit": "C5-C6 (Mengevaluasi, Mencipta)",
            "Campuran": "C1-C6 (bervariasi)"
        }

        pembahasan_instruction = """

PEMBAHASAN

(Untuk setiap soal, berikan penjelasan detail dengan rumus dan langkah penyelesaian)
1. [Pembahasan lengkap soal 1]
2. [Pembahasan lengkap soal 2]
... dst""" if data.sertakan_pembahasan else ""

        return f"""Buatkan Bank Soal dengan spesifikasi:
{base_info}
Tingkat Kesulitan: {data.tingkat_kesulitan} - {difficulty_map.get(data.tingkat_kesulitan, '')}

{physics_diagram_instruction}

Jumlah Soal:
- Pilihan Ganda (PG): {data.jumlah_pg} soal
- Isian Singkat: {data.jumlah_isian} soal
- Essay/Uraian: {data.jumlah_essay} soal

PENTING - FORMAT OUTPUT HARUS SEPERTI INI:

BANK SOAL {data.mata_pelajaran.upper()}
Kelas {data.kelas} {data.jenjang} | {data.kurikulum} | Semester {data.semester}

I. SOAL PILIHAN GANDA

1. [Soal pertama dengan rumus LaTeX jika perlu]
   A. [Pilihan jawaban]
   B. [Pilihan jawaban]
   C. [Pilihan jawaban]
   D. [Pilihan jawaban]
   E. [Pilihan jawaban]

2. [Soal kedua]
   A. ...
   B. ...
   C. ...
   D. ...
   E. ...

(Lanjutkan sampai {data.jumlah_pg} soal PG selesai)

II. SOAL ISIAN SINGKAT

1. [Soal isian] _______________
2. [Soal isian] _______________
(Lanjutkan sampai {data.jumlah_isian} soal isian selesai)

III. SOAL ESSAY/URAIAN

1. [Soal essay lengkap]
2. [Soal essay lengkap]
(Lanjutkan sampai {data.jumlah_essay} soal essay selesai)

KUNCI JAWABAN

I. Pilihan Ganda
1. [Huruf]    6. [Huruf]    11. [Huruf]
2. [Huruf]    7. [Huruf]    12. [Huruf]
3. [Huruf]    8. [Huruf]    13. [Huruf]
4. [Huruf]    9. [Huruf]    14. [Huruf]
5. [Huruf]   10. [Huruf]    15. [Huruf]
(Sesuaikan dengan jumlah soal)

II. Isian Singkat
1. [Jawaban]
2. [Jawaban]
... dst

III. Essay
1. [Jawaban lengkap]
2. [Jawaban lengkap]
... dst
{pembahasan_instruction}

CATATAN PENTING:
- SEMUA SOAL harus ditulis LENGKAP terlebih dahulu
- KUNCI JAWABAN ditulis SETELAH semua soal selesai
- PEMBAHASAN (jika ada) ditulis PALING AKHIR setelah kunci jawaban
- Untuk Matematika/Fisika, gunakan LaTeX: $formula$ untuk inline atau $$formula$$ untuk display
- Format output: HTML dengan pemisah yang jelas. JANGAN gunakan emoji."""

    elif data.doc_type == "rubrik":
        return f"""Buatkan Rubrik Asesmen dengan format:
{base_info}

Struktur Rubrik:
1. Judul Asesmen
2. Tujuan Asesmen
3. Kriteria Penilaian
4. Tabel Rubrik dengan:
   - Aspek yang Dinilai
   - Kriteria per Level (4 = Sangat Baik, 3 = Baik, 2 = Cukup, 1 = Kurang)
   - Deskripsi per Level
   - Bobot/Skor
5. Cara Penggunaan Rubrik
6. Contoh Penghitungan Nilai

Format: HTML dengan tabel rubrik yang jelas. Header tabel: background #1E3A5F, teks putih. JANGAN gunakan emoji."""

    return f"Buatkan dokumen pendidikan tentang: {data.topik}"
