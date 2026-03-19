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
        return f"""Buatkan Modul Ajar Kurikulum Merdeka yang LENGKAP dan DETAIL dengan format berikut:
{base_info}

Struktur Modul Ajar:

1. INFORMASI UMUM
   - Identitas Modul (satuan pendidikan, mata pelajaran, kelas/fase, semester, alokasi waktu, penyusun)
   - Kompetensi Awal (pengetahuan/keterampilan prasyarat yang harus dimiliki peserta didik)
   - Profil Pelajar Pancasila: Sebutkan MINIMAL 2 dimensi spesifik yang dikembangkan beserta penjelasannya (pilih dari: Beriman/Bertakwa, Berkebhinekaan Global, Bergotong Royong, Mandiri, Bernalar Kritis, Kreatif)
   - Sarana Prasarana (alat, bahan, media yang dibutuhkan)
   - Target Peserta Didik (reguler, peserta didik dengan kesulitan belajar, peserta didik dengan pencapaian tinggi)
   - Model Pembelajaran (PBL/Discovery Learning/Project Based Learning/dll, jelaskan alasan pemilihan)

2. KOMPONEN INTI

   a. Capaian Pembelajaran (CP):
      Tulis 1 narasi CP sesuai standar BSKAP untuk Fase {data.fase} mata pelajaran {data.mata_pelajaran}.
      CP berupa paragraf utuh yang mendeskripsikan kompetensi yang harus dicapai di akhir fase.

   b. Tujuan Pembelajaran (TP):
      Rumuskan MINIMAL 3 Tujuan Pembelajaran yang diturunkan dari CP di atas.
      Setiap TP harus menggunakan format ABCD:
      - A (Audience): Peserta didik
      - B (Behavior): Kata kerja operasional spesifik (mengidentifikasi, menganalisis, menerapkan, dll.)
      - C (Condition): Kondisi/cara pencapaian
      - D (Degree): Tingkat keberhasilan yang diharapkan

      Format penulisan:
      TP 1: [TP paling sederhana/dasar - level mengingat/memahami]
      TP 2: [TP menengah - level menerapkan/menganalisis]
      TP 3: [TP paling kompleks - level mengevaluasi/mencipta]
      (Tambahkan TP 4, TP 5 jika topik memerlukan)

   c. Alur Tujuan Pembelajaran (ATP):
      Susun urutan linier dari semua TP di atas, dari yang paling sederhana menuju paling kompleks.
      Tampilkan dalam bentuk tabel/diagram alur:
      TP 1 (dasar) --> TP 2 (menengah) --> TP 3 (kompleks) --> Menuju CP

      Jelaskan mengapa urutan ini dipilih dan bagaimana setiap TP membangun fondasi untuk TP berikutnya.

   d. Pemahaman Bermakna:
      Tuliskan konsep-konsep kunci yang akan dipahami peserta didik secara mendalam.

   e. Pertanyaan Pemantik:
      Tuliskan 2-3 pertanyaan terbuka yang memicu rasa ingin tahu dan berpikir kritis peserta didik.

   f. Kegiatan Pembelajaran:
      Rinci per pertemuan (sesuaikan dengan alokasi waktu {data.alokasi_waktu} menit):
      - Pendahuluan ({int(data.alokasi_waktu * 0.15)} menit): Apersepsi, motivasi, penyampaian TP
      - Kegiatan Inti ({int(data.alokasi_waktu * 0.7)} menit): Langkah-langkah detail sesuai model pembelajaran yang dipilih
      - Penutup ({int(data.alokasi_waktu * 0.15)} menit): Refleksi, kesimpulan, tindak lanjut

   g. Asesmen:
      - Diagnostik: Asesmen awal untuk mengidentifikasi kesiapan belajar peserta didik (berikan contoh soal/instrumen)
      - Formatif: Asesmen selama proses pembelajaran (observasi, tugas, kuis - berikan contoh instrumen)
      - Sumatif: Asesmen akhir untuk mengukur pencapaian TP (berikan contoh soal/rubrik)

   h. Pengayaan dan Remedial:
      - Pengayaan: Kegiatan untuk peserta didik yang sudah mencapai TP
      - Remedial: Kegiatan untuk peserta didik yang belum mencapai TP

3. LAMPIRAN
   - Lembar Kerja Peserta Didik (LKPD) dengan instruksi dan ruang jawaban
   - Bahan Bacaan ringkas
   - Glosarium istilah penting

4. DAFTAR PUSTAKA
   Wajib sertakan referensi resmi berikut (sesuaikan dengan mata pelajaran dan jenjang):
   - Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi. (2024). Panduan Pembelajaran dan Asesmen Kurikulum Merdeka. Jakarta: Kemendikbudristek. Tersedia di: kurikulum.kemendikdasmen.go.id
   - Badan Standar, Kurikulum, dan Asesmen Pendidikan. (2022). Capaian Pembelajaran {data.mata_pelajaran} Fase {data.fase}. Jakarta: BSKAP.
   - Pusat Perbukuan. (2024). Buku Panduan Guru {data.mata_pelajaran} Kelas {data.kelas} {data.jenjang}. Jakarta: Kemendikdasmen. Tersedia di: buku.kemendikdasmen.go.id
   - Tambahkan 2-3 sumber relevan lainnya (buku teks, jurnal pendidikan, atau sumber resmi pemerintah)

CATATAN PENTING:
- TP WAJIB minimal 3, masing-masing dengan format ABCD yang jelas
- ATP WAJIB menunjukkan urutan linier dari semua TP
- Setiap bagian harus DETAIL dan LENGKAP, bukan hanya judul/label
- Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). Gunakan LaTeX untuk rumus matematika ($formula$ untuk inline, $$formula$$ untuk block). JANGAN gunakan emoji."""

    elif data.doc_type == "rpp":
        if data.kurikulum.lower() in ["merdeka", "kurikulum merdeka"]:
            return f"""Buatkan RPP (Rencana Pelaksanaan Pembelajaran) format Kurikulum Merdeka dengan format:
{base_info}

Struktur RPP Kurikulum Merdeka:

1. IDENTITAS
   - Satuan Pendidikan, Mata Pelajaran, Kelas/Semester, Fase, Materi Pokok, Alokasi Waktu: {data.alokasi_waktu} menit

2. CAPAIAN PEMBELAJARAN (CP)
   Tulis 1 narasi CP sesuai standar BSKAP untuk Fase {data.fase} mata pelajaran {data.mata_pelajaran}.
   CP berupa paragraf utuh yang mendeskripsikan kompetensi akhir fase.

3. TUJUAN PEMBELAJARAN (TP)
   Rumuskan MINIMAL 3 Tujuan Pembelajaran dari CP dengan format ABCD:
   - A (Audience): Peserta didik
   - B (Behavior): Kata kerja operasional spesifik
   - C (Condition): Kondisi/cara pencapaian
   - D (Degree): Tingkat keberhasilan

   TP 1: [Level dasar - mengingat/memahami]
   TP 2: [Level menengah - menerapkan/menganalisis]
   TP 3: [Level tinggi - mengevaluasi/mencipta]

4. ALUR TUJUAN PEMBELAJARAN (ATP)
   Susun urutan linier: TP 1 --> TP 2 --> TP 3 --> Menuju CP
   Jelaskan progres dari sederhana ke kompleks.

5. PROFIL PELAJAR PANCASILA
   Sebutkan minimal 2 dimensi yang dikembangkan beserta implementasinya dalam pembelajaran.

6. MATERI PEMBELAJARAN
   Uraikan materi pokok: fakta, konsep, prinsip, dan prosedur.

7. MODEL DAN METODE PEMBELAJARAN
   - Model: (PBL/Discovery/Project Based/dll.)
   - Metode: (Diskusi, Tanya Jawab, Presentasi, Praktik, dll.)

8. KEGIATAN PEMBELAJARAN
   a. Pendahuluan ({int(data.alokasi_waktu * 0.15)} menit):
      - Salam, doa, presensi
      - Apersepsi (mengaitkan materi sebelumnya)
      - Motivasi dan penyampaian TP
      - Pertanyaan pemantik

   b. Kegiatan Inti ({int(data.alokasi_waktu * 0.7)} menit):
      - Langkah-langkah detail sesuai sintak model pembelajaran
      - Diferensiasi untuk kebutuhan belajar yang berbeda
      - Aktivitas kolaboratif dan mandiri

   c. Penutup ({int(data.alokasi_waktu * 0.15)} menit):
      - Refleksi peserta didik
      - Kesimpulan bersama
      - Asesmen formatif singkat
      - Tindak lanjut/tugas

9. ASESMEN
   - Diagnostik: (instrumen awal)
   - Formatif: (observasi/tugas proses)
   - Sumatif: (tes/proyek akhir)

10. SUMBER DAN MEDIA PEMBELAJARAN
    - Buku teks, media digital, alat peraga, dll.

CATATAN PENTING:
- TP WAJIB minimal 3, format ABCD
- ATP WAJIB urutan linier dari semua TP
- Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). Gunakan LaTeX untuk rumus matematika ($formula$ untuk inline, $$formula$$ untuk block). JANGAN gunakan emoji."""
        else:
            return f"""Buatkan RPP (Rencana Pelaksanaan Pembelajaran) format Kurikulum 2013 (K13) dengan format:
{base_info}

Struktur RPP Kurikulum 2013:

1. IDENTITAS
   - Satuan Pendidikan, Mata Pelajaran, Kelas/Semester, Materi Pokok, Alokasi Waktu: {data.alokasi_waktu} menit

2. KOMPETENSI INTI (KI)
   Tuliskan 4 Kompetensi Inti lengkap:
   - KI-1 (Sikap Spiritual): Menghayati dan mengamalkan ajaran agama yang dianutnya
   - KI-2 (Sikap Sosial): Menghayati dan mengamalkan perilaku jujur, disiplin, tanggung jawab, peduli, santun, responsif dan pro-aktif...
   - KI-3 (Pengetahuan): Memahami, menerapkan, menganalisis pengetahuan faktual, konseptual, prosedural berdasarkan rasa ingin tahunya tentang {data.mata_pelajaran}
   - KI-4 (Keterampilan): Mengolah, menalar, dan menyaji dalam ranah konkret dan ranah abstrak terkait {data.mata_pelajaran}

3. KOMPETENSI DASAR (KD) DAN INDIKATOR PENCAPAIAN KOMPETENSI
   Tuliskan KD dari KI-3 dan KI-4 yang relevan dengan topik {data.topik}, lengkap dengan:
   - Nomor KD (misal: 3.1, 4.1)
   - Rumusan KD
   - Indikator Pencapaian Kompetensi (minimal 3 indikator per KD, menggunakan kata kerja operasional)

   Tampilkan dalam bentuk tabel:
   | KD | Indikator Pencapaian Kompetensi |
   |---|---|

4. TUJUAN PEMBELAJARAN
   Rumuskan tujuan berdasarkan KD dan indikator di atas (setiap indikator menjadi 1 tujuan).

5. MATERI PEMBELAJARAN
   Uraikan materi: fakta, konsep, prinsip, dan prosedur yang relevan.

6. METODE PEMBELAJARAN
   - Pendekatan: Saintifik (5M: Mengamati, Menanya, Mengumpulkan Informasi, Mengasosiasi, Mengkomunikasikan)
   - Model: (Discovery Learning/Problem Based Learning/dll.)
   - Metode: (Ceramah, Diskusi, Tanya Jawab, Penugasan, dll.)

7. MEDIA DAN SUMBER BELAJAR
   - Media: alat peraga, LCD, buku, dll.
   - Sumber: buku teks, internet, dll.

8. LANGKAH-LANGKAH KEGIATAN PEMBELAJARAN
   a. Pendahuluan ({int(data.alokasi_waktu * 0.15)} menit):
      - Salam, doa, presensi
      - Apersepsi (mengaitkan materi sebelumnya)
      - Motivasi
      - Penyampaian tujuan dan cakupan materi

   b. Kegiatan Inti ({int(data.alokasi_waktu * 0.7)} menit):
      Langkah-langkah sesuai pendekatan Saintifik (5M):
      - Mengamati: ...
      - Menanya: ...
      - Mengumpulkan Informasi: ...
      - Mengasosiasi: ...
      - Mengkomunikasikan: ...

   c. Penutup ({int(data.alokasi_waktu * 0.15)} menit):
      - Kesimpulan bersama
      - Refleksi
      - Penugasan/tindak lanjut
      - Salam penutup

9. PENILAIAN HASIL BELAJAR
   a. Penilaian Sikap (Observasi): Instrumen lembar observasi
   b. Penilaian Pengetahuan (Tes Tertulis): Contoh soal + kunci jawaban
   c. Penilaian Keterampilan (Unjuk Kerja/Proyek): Rubrik penilaian

   Sertakan tabel rubrik penilaian.

Format output: HTML dengan tabel berformat (header #1E3A5F, teks putih). Gunakan LaTeX untuk rumus matematika ($formula$ untuk inline, $$formula$$ untuk block). JANGAN gunakan emoji."""

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

        # Handle chunked soal generation
        if data.soal_section == "pg":
            return _build_pg_chunk_prompt(data, base_info, difficulty_map, physics_diagram_instruction)
        elif data.soal_section == "non_pg":
            return _build_non_pg_chunk_prompt(data, base_info, difficulty_map)

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


def _build_pg_chunk_prompt(data, base_info, difficulty_map, physics_diagram_instruction):
    """Build prompt for a PG-only chunk (used for chunked large soal generation)"""
    start_num = data.pg_numbering_start
    count = data.jumlah_pg
    end_num = start_num + count - 1

    return f"""Buatkan HANYA soal Pilihan Ganda dengan spesifikasi:
{base_info}
Tingkat Kesulitan: {data.tingkat_kesulitan} - {difficulty_map.get(data.tingkat_kesulitan, '')}

{physics_diagram_instruction}

INSTRUKSI: Buat TEPAT {count} soal Pilihan Ganda, dinomori dari {start_num} sampai {end_num}.

OUTPUT HANYA berisi soal PG dan kunci jawaban PG. JANGAN buat soal isian atau essay.

Format setiap soal WAJIB seperti ini:
<div style="margin-bottom:20px;">
<p><strong>{start_num}.</strong> [Teks soal lengkap]</p>
<div style="margin-left:30px;">
<p>A. [Pilihan A]</p>
<p>B. [Pilihan B]</p>
<p>C. [Pilihan C]</p>
<p>D. [Pilihan D]</p>
<p>E. [Pilihan E]</p>
</div>
</div>

Setelah semua {count} soal, tulis kunci jawaban:
<h3 style="margin-top:20px;"><strong>Kunci Jawaban PG No. {start_num}-{end_num}:</strong></h3>
<table style="width:100%;border-collapse:collapse;margin:15px 0;">
<tr style="background-color:#1E3A5F;color:white;">
<th style="padding:8px;border:1px solid #ccc;">No</th>
<th style="padding:8px;border:1px solid #ccc;">Jawaban</th>
</tr>
(satu baris per soal)
</table>

Untuk rumus matematika, gunakan LaTeX: $formula$ untuk inline atau $$formula$$ untuk display.

CATATAN PENTING:
- WAJIB TEPAT {count} soal PG dari nomor {start_num} sampai {end_num}
- JANGAN kurang, JANGAN skip, JANGAN tulis "dst"
- SETIAP soal harus ditulis LENGKAP
- Setiap pilihan jawaban (A-E) HARUS pada baris terpisah
- Output WAJIB HTML terstruktur
- JANGAN gunakan emoji
- Variasikan topik dan tipe soal"""


def _build_non_pg_chunk_prompt(data, base_info, difficulty_map):
    """Build prompt for non-PG section (isian + essay + pembahasan)"""
    pembahasan_instruction = ""
    if data.sertakan_pembahasan:
        pembahasan_instruction = """
Setelah kunci jawaban, tambahkan PEMBAHASAN DETAIL:
<h3 style="margin-top:20px;"><strong>Pembahasan Isian Singkat:</strong></h3>
<div style="margin-left:10px;">
(Pembahasan untuk setiap soal isian)
</div>

<h3 style="margin-top:20px;"><strong>Pembahasan Essay:</strong></h3>
<div style="margin-left:10px;">
(Pembahasan untuk setiap soal essay)
</div>
"""

    sections = []
    if data.jumlah_isian > 0:
        sections.append(f"""
<h2 style="background-color:#1E3A5F;color:white;padding:10px;margin-top:30px;">II. SOAL ISIAN SINGKAT</h2>
Buat TEPAT {data.jumlah_isian} soal isian singkat (nomor 1 sampai {data.jumlah_isian}).
Format:
<div style="margin-bottom:15px;">
<p><strong>1.</strong> [Teks soal isian] _______________</p>
</div>
""")

    if data.jumlah_essay > 0:
        sections.append(f"""
<h2 style="background-color:#1E3A5F;color:white;padding:10px;margin-top:30px;">III. SOAL ESSAY/URAIAN</h2>
Buat TEPAT {data.jumlah_essay} soal essay (nomor 1 sampai {data.jumlah_essay}).
Format:
<div style="margin-bottom:20px;">
<p><strong>1.</strong> [Teks soal essay lengkap]</p>
</div>
""")

    section_text = "\n".join(sections)

    return f"""Buatkan soal Isian Singkat dan Essay dengan spesifikasi:
{base_info}
Tingkat Kesulitan: {data.tingkat_kesulitan} - {difficulty_map.get(data.tingkat_kesulitan, '')}

INSTRUKSI: Buat HANYA soal Isian Singkat dan Essay. JANGAN buat soal Pilihan Ganda.

{section_text}

Setelah semua soal, tulis kunci jawaban:
<hr style="border:2px solid #1E3A5F;margin:30px 0;">
<h3 style="margin-top:20px;"><strong>Kunci Jawaban Isian Singkat:</strong></h3>
<div style="margin-left:10px;">
(Jawaban untuk setiap soal isian)
</div>

<h3 style="margin-top:20px;"><strong>Kunci Jawaban Essay:</strong></h3>
<div style="margin-left:10px;">
(Jawaban lengkap untuk setiap soal essay)
</div>

{pembahasan_instruction}

Untuk rumus matematika, gunakan LaTeX: $formula$ untuk inline atau $$formula$$ untuk display.

CATATAN PENTING:
- JUMLAH SOAL WAJIB TEPAT: {data.jumlah_isian} Isian + {data.jumlah_essay} Essay
- JANGAN buat soal PG
- JANGAN kurang, JANGAN skip
- Output WAJIB HTML terstruktur
- JANGAN gunakan emoji"""
