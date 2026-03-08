# ModulAI - PRD (Product Requirements Document)

## Project Overview
**ModulAI** adalah Generator Perangkat Ajar AI untuk Guru Indonesia dengan sistem token, pembayaran, dan admin panel.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB (modular architecture)
- **AI**: Google Gemini API (2.5-flash / 2.5-pro)
- **Payment**: Midtrans (Sandbox)
- **Email**: Mailketing (MOCKED)

## User Personas
1. **Guru** - Pengguna utama yang membuat perangkat ajar
2. **Super Admin** - Mengelola users, transaksi, voucher, dan AI settings

## Core Requirements

### Authentication
- [x] Register dengan email/password
- [x] Login dengan JWT token (7 days expiry)
- [x] Forgot password flow (mocked email)
- [x] Role-based access (user / super_admin)

### Token System
- [x] 4 paket token: Starter (Rp99K/100), Pro (Rp249K/300), Guru (Rp399K/750), Sekolah (Rp899K/2000)
- [x] Token tidak expired (lifetime)
- [x] 1 token = 1 dokumen generated

### Document Generator
- [x] 5 jenis dokumen: Modul Ajar, RPP, LKPD, Bank Soal, Rubrik Asesmen
- [x] Form input: Jenjang, Kelas, Kurikulum, Semester, Fase, Mata Pelajaran, Topik
- [x] Soal config: PG, Isian, Essay, Tingkat Kesulitan, Pembahasan
- [x] Physics custom values: Resistor, Voltage untuk soal Fisika
- [x] SVG Diagrams: CircuitDiagram, MeterDiagram, PhysicsDiagram
- [x] Export Excel dengan styling header #1E3A5F
- [x] Multi-document generation (generate beberapa dokumen sekaligus)
- [x] Format soal baru: semua soal dulu, kunci jawaban & pembahasan di akhir
- [x] Daftar Pustaka di Modul Ajar dengan sumber resmi pemerintah

### Payment Integration
- [x] Midtrans Snap.js popup
- [x] Webhook handler untuk update token
- [x] Voucher system dengan diskon persentase/nominal

### Super Admin Panel
- [x] Dashboard: total users, revenue, documents, token circulation
- [x] User management: edit token balance, suspend/activate
- [x] Transaction monitoring dengan filter status
- [x] Voucher management: create, list, toggle active/inactive, delete
- [x] AI Settings: switch provider (Flash/Pro), update API key

## Backend Architecture (Refactored Mar 2026)
```
/app/backend/
├── server.py          (slim app entry, startup, CORS)
├── database.py        (MongoDB connection)
├── config.py          (config constants, TOKEN_PACKAGES)
├── models.py          (all Pydantic models)
├── auth.py            (JWT helpers, auth dependencies)
├── prompts.py         (AI prompt building functions)
├── routes/
│   ├── auth_routes.py     (auth endpoints)
│   ├── generate_routes.py (document generation + packages)
│   ├── payment_routes.py  (payment + voucher apply + transactions)
│   └── admin_routes.py    (admin panel endpoints)
```

## API Credentials
- **Super Admin**: ipankpaul107@gmail.com / Kakiku5.
- **Gemini API Key**: Configured in AI Settings (masked)
- **Midtrans Sandbox**: Client Key SB-Mid-client-RlztC9s1e9UMUkE6
- **Sample Voucher**: GURU2024 (20% discount)

## Next Tasks / Backlog

### P1 (Important)
- [ ] Word export yang lebih baik (sudah dibahas user)
- [ ] Diagram untuk mata pelajaran lain (Chart.js untuk Matematika, gambar stock untuk Biologi/Kimia)
- [ ] Ubah label "Token" menjadi "Generate" di UI

### P2 (Nice to have)
- [ ] User upload gambar untuk soal
- [ ] KaTeX rendering untuk rumus matematika
- [ ] User profile settings page
- [ ] Password change functionality

### P3 (Future)
- [ ] Real email integration (Mailketing)
- [ ] Production Midtrans keys
- [ ] Analytics dashboard with charts

## Design Guidelines
- Primary: #1E3A5F (Navy)
- Secondary: #F4820A (Orange)
- Success: #10B981 (Green)
- Font: Plus Jakarta Sans (headings), Inter (body)
