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
<h2 style="background-color:#1E3A5F;color:white;padding:10px;margin-top:30px;">PEMBAHASAN</h2>
<p><em>(Untuk setiap soal, berikan penjelasan detail dengan rumus dan langkah penyelesaian)</em></p>
<div style="margin-left:10px;">
<p><strong>1.</strong> [Pembahasan lengkap soal 1]</p>
<p><strong>2.</strong> [Pembahasan lengkap soal 2]</p>
</div>
... dst untuk semua soal""" if data.sertakan_pembahasan else ""

        total_soal = data.jumlah_pg + data.jumlah_isian + data.jumlah_essay

        return f"""Buatkan Bank Soal dengan spesifikasi:
{base_info}
Tingkat Kesulitan: {data.tingkat_kesulitan} - {difficulty_map.get(data.tingkat_kesulitan, '')}

{physics_diagram_instruction}

JUMLAH SOAL YANG HARUS DIBUAT (WAJIB TEPAT, TIDAK BOLEH KURANG):
- Pilihan Ganda (PG): TEPAT {data.jumlah_pg} soal (nomor 1 sampai {data.jumlah_pg})
- Isian Singkat: TEPAT {data.jumlah_isian} soal (nomor 1 sampai {data.jumlah_isian})
- Essay/Uraian: TEPAT {data.jumlah_essay} soal (nomor 1 sampai {data.jumlah_essay})
TOTAL: {total_soal} soal. PASTIKAN SEMUA {total_soal} SOAL DITULIS LENGKAP TANPA DISINGKAT.

SANGAT PENTING - OUTPUT HARUS BERUPA HTML YANG TERSTRUKTUR DENGAN BAIK.
Gunakan tag HTML berikut secara WAJIB:
- <h2> untuk judul section (dengan style background-color:#1E3A5F;color:white;padding:10px)
- <div> untuk setiap soal (dengan margin-bottom:20px)
- <p> untuk teks soal
- <div> dengan margin-left untuk pilihan jawaban, SETIAP PILIHAN di baris terpisah menggunakan <p>
- <strong> untuk nomor soal
- <hr> untuk pemisah antar section

Untuk rumus matematika, gunakan LaTeX: $formula$ untuk inline atau $$formula$$ untuk display.
Contoh: $F = m \\times a$, $v = \\frac{{s}}{{t}}$, $E_k = \\frac{{1}}{{2}}mv^2$

FORMAT HTML OUTPUT HARUS PERSIS SEPERTI INI:

<h2 style="background-color:#1E3A5F;color:white;padding:10px;text-align:center;">BANK SOAL {data.mata_pelajaran.upper()}</h2>
<p style="text-align:center;"><strong>Kelas {data.kelas} {data.jenjang} | {data.kurikulum} | Semester {data.semester}</strong></p>

<h2 style="background-color:#1E3A5F;color:white;padding:10px;margin-top:30px;">I. SOAL PILIHAN GANDA</h2>

<div style="margin-bottom:20px;">
<p><strong>1.</strong> [Teks soal pertama lengkap]</p>
<div style="margin-left:30px;">
<p>A. [Pilihan jawaban A]</p>
<p>B. [Pilihan jawaban B]</p>
<p>C. [Pilihan jawaban C]</p>
<p>D. [Pilihan jawaban D]</p>
<p>E. [Pilihan jawaban E]</p>
</div>
</div>

<div style="margin-bottom:20px;">
<p><strong>2.</strong> [Teks soal kedua lengkap]</p>
<div style="margin-left:30px;">
<p>A. ...</p>
<p>B. ...</p>
<p>C. ...</p>
<p>D. ...</p>
<p>E. ...</p>
</div>
</div>

(Lanjutkan pola yang SAMA PERSIS untuk setiap soal sampai {data.jumlah_pg} soal PG selesai)

<h2 style="background-color:#1E3A5F;color:white;padding:10px;margin-top:30px;">II. SOAL ISIAN SINGKAT</h2>

<div style="margin-bottom:15px;">
<p><strong>1.</strong> [Teks soal isian] _______________</p>
</div>
<div style="margin-bottom:15px;">
<p><strong>2.</strong> [Teks soal isian] _______________</p>
</div>
(Lanjutkan sampai {data.jumlah_isian} soal isian selesai)

<h2 style="background-color:#1E3A5F;color:white;padding:10px;margin-top:30px;">III. SOAL ESSAY/URAIAN</h2>

<div style="margin-bottom:20px;">
<p><strong>1.</strong> [Teks soal essay lengkap]</p>
</div>
<div style="margin-bottom:20px;">
<p><strong>2.</strong> [Teks soal essay lengkap]</p>
</div>
(Lanjutkan sampai {data.jumlah_essay} soal essay selesai)

<hr style="border:2px solid #1E3A5F;margin:30px 0;">

<h2 style="background-color:#1E3A5F;color:white;padding:10px;">KUNCI JAWABAN</h2>

<table style="width:100%;border-collapse:collapse;margin:15px 0;">
<tr style="background-color:#1E3A5F;color:white;">
<th style="padding:8px;border:1px solid #ccc;">No</th>
<th style="padding:8px;border:1px solid #ccc;">PG</th>
<th style="padding:8px;border:1px solid #ccc;">No</th>
<th style="padding:8px;border:1px solid #ccc;">PG</th>
</tr>
<tr><td style="padding:8px;border:1px solid #ccc;">1</td><td style="padding:8px;border:1px solid #ccc;">[Huruf]</td><td style="padding:8px;border:1px solid #ccc;">6</td><td style="padding:8px;border:1px solid #ccc;">[Huruf]</td></tr>
</table>

<h3 style="margin-top:20px;"><strong>Isian Singkat:</strong></h3>
<div style="margin-left:10px;">
<p><strong>1.</strong> [Jawaban]</p>
<p><strong>2.</strong> [Jawaban]</p>
</div>

<h3 style="margin-top:20px;"><strong>Essay:</strong></h3>
<div style="margin-left:10px;">
<p><strong>1.</strong> [Jawaban lengkap]</p>
<p><strong>2.</strong> [Jawaban lengkap]</p>
</div>
{pembahasan_instruction}

CATATAN PENTING:
- OUTPUT WAJIB HTML! Gunakan tag <h2>, <p>, <div>, <table>, <strong> dll
- JUMLAH SOAL WAJIB TEPAT: {data.jumlah_pg} PG + {data.jumlah_isian} Isian + {data.jumlah_essay} Essay = {total_soal} soal total. JANGAN KURANG!
- SEMUA {total_soal} SOAL harus ditulis LENGKAP satu per satu dari nomor 1 sampai selesai
- JANGAN skip, JANGAN tulis "dst", JANGAN tulis "lanjutkan pola yang sama"
- KUNCI JAWABAN ditulis SETELAH semua soal selesai
- PEMBAHASAN (jika ada) ditulis PALING AKHIR setelah kunci jawaban
- Setiap pilihan jawaban (A, B, C, D, E) HARUS pada baris terpisah (gunakan <p> tag)
- Setiap soal HARUS dipisahkan dengan spacing yang cukup (gunakan <div> dengan margin-bottom)
- Untuk rumus Matematika/Fisika, gunakan LaTeX: $formula$ untuk inline atau $$formula$$ untuk display
- JANGAN gunakan emoji
- JANGAN output sebagai plain text, HARUS HTML terstruktur
- Variasikan topik dan tipe soal supaya tidak monoton"""

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
