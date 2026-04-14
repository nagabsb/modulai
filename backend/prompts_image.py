"""
Prompts khusus untuk Mode Bergambar (soal + gambar sekaligus).
File terpisah dari prompts.py agar tidak mengganggu prompt text biasa.
Dipakai oleh Gemini 2.5 Flash Image yang bisa output text + image interleaved.
"""


def build_bergambar_prompt(data) -> str:
    """
    Prompt untuk Gemini 2.5 Flash Image — generate soal bergambar.
    Output: interleaved text (HTML) + images.
    """

    jumlah_pg = getattr(data, 'jumlah_pg', 0) or 0
    jumlah_isian = getattr(data, 'jumlah_isian', 0) or 0
    jumlah_essay = getattr(data, 'jumlah_essay', 0) or 0
    sertakan_pembahasan = getattr(data, 'sertakan_pembahasan', True)

    soal_lines = []
    if jumlah_pg > 0:
        soal_lines.append(f"{jumlah_pg} soal Pilihan Ganda (5 opsi: A-E)")
    if jumlah_isian > 0:
        soal_lines.append(f"{jumlah_isian} soal Isian Singkat")
    if jumlah_essay > 0:
        soal_lines.append(f"{jumlah_essay} soal Essay")
    soal_spec = ", ".join(soal_lines)

    pembahasan_instruction = ""
    if sertakan_pembahasan:
        pembahasan_instruction = """

Setelah semua soal selesai, tulis bagian KUNCI JAWABAN DAN PEMBAHASAN dalam format HTML:
<h2 style="background-color:#1E3A5F;color:white;padding:10px;border-radius:8px;">KUNCI JAWABAN DAN PEMBAHASAN</h2>
Untuk setiap soal:
<p><strong>1. Jawaban: [huruf]</strong></p>
<p><strong>Pembahasan:</strong> [penjelasan detail]</p>
Bagian kunci jawaban TIDAK perlu gambar."""

    return f"""Buat {soal_spec} untuk mata pelajaran {data.mata_pelajaran}, topik "{data.topik}", kelas {data.kelas} {data.jenjang}, Kurikulum {data.kurikulum}.

ATURAN OUTPUT:
1. Tulis soal dalam format HTML. Gunakan tag <p>, <strong>, <ol>, <li>.
2. Header judul soal pakai: <h2 style="background-color:#1E3A5F;color:white;padding:10px;border-radius:8px;">BANK SOAL {data.mata_pelajaran.upper()}</h2>
3. Untuk rumus matematika gunakan LaTeX: $formula$ (inline) atau $$formula$$ (block).

ATURAN GAMBAR (SANGAT PENTING):
1. Untuk SETIAP nomor soal, generate 1 gambar ilustrasi.
2. Gambar harus SPESIFIK menggambarkan konsep yang ditanyakan di soal itu:
   - Soal tentang pertumbuhan → gambar tahap pertumbuhan organisme
   - Soal tentang fotosintesis → gambar tumbuhan dengan cahaya matahari
   - Soal tentang gaya → gambar benda yang didorong/ditarik
   - Soal tentang penguapan → gambar air mendidih/uap
   - Soal tentang pembekuan → gambar es batu/freezer
3. Gambar TIDAK BOLEH mengandung teks, huruf, angka, label, atau tulisan.
4. Gaya gambar: ilustrasi sederhana, warna cerah, gaya buku pelajaran anak.
5. Letakkan gambar SEBELUM teks soal.
6. DILARANG KERAS: Jangan pernah membuat gambar yang berisi layout ujian, tabel soal, daftar pilihan ganda, atau tampilan dokumen. Gambar harus HANYA berisi ilustrasi objek/pemandangan/proses saja.
7. Setiap gambar harus BERBEDA dan spesifik untuk konsep soal masing-masing.

STRUKTUR PER SOAL:
<p><strong>[nomor].</strong></p>
[GAMBAR ILUSTRASI]
<p>Perhatikan gambar di atas! [teks soal...]</p>
<p>A. [opsi]</p>
<p>B. [opsi]</p>
<p>C. [opsi]</p>
<p>D. [opsi]</p>
<p>E. [opsi]</p>
{pembahasan_instruction}

PENTING:
- Langsung mulai dengan HTML soal, JANGAN tulis kalimat pembuka seperti "Tentu" atau "Baik".
- Bahasa Indonesia yang baik dan benar.
- JANGAN gunakan emoji."""


def build_fallback_image_prompts(soal_text_list: list, mata_pelajaran: str, topik: str) -> list:
    """
    Fallback: buat prompt gambar spesifik per soal untuk Imagen API.
    """
    prompts = []
    for soal in soal_text_list:
        clean = soal.strip()[:200]
        prompt = (
            f"Simple colorful illustration for an Indonesian school exam question about {mata_pelajaran}, topic: {topik}. "
            f"The question asks about: {clean}. "
            f"Style: children educational book, bright colors, simple flat design. "
            f"ABSOLUTE RULE: NO text, NO letters, NO numbers, NO labels, NO words in the image."
        )
        prompts.append(prompt)
    return prompts
