# ModulAI - PRD (Product Requirements Document)

## Project Overview
**ModulAI** adalah Generator Perangkat Ajar AI untuk Guru Indonesia dengan sistem token, pembayaran, dan admin panel.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI + KaTeX (math rendering)
- **Backend**: FastAPI (Python) + MongoDB (modular architecture)
- **AI**: Google Gemini API (2.5-flash / 2.5-pro)
- **Payment**: Midtrans (Sandbox) + Bank Transfer Manual (BCA)
- **Email**: Mailketing (MOCKED)

## Core Requirements

### Authentication
- [x] Register, Login, Forgot password, Role-based access (user/super_admin)

### Token System
- [x] 4 paket: Starter (Rp99K/100), Pro (Rp249K/300), Guru (Rp399K/750), Sekolah (Rp899K/2000)

### Document Generator
- [x] 5 jenis: Modul Ajar, RPP, LKPD, Bank Soal, Rubrik Asesmen
- [x] Multi-document generation with tabbed results
- [x] LaTeX/KaTeX rendering, HTML terstruktur, Daftar Pustaka
- [x] SVG Physics Diagrams, Excel Export

### Payment Integration
- [x] **E-Wallet/QRIS**: Midtrans Snap.js popup, auto-confirm via webhook
- [x] **Bank Transfer**: Manual ke BCA 2470230889 (Najmi Abubakar Basumbul)
  - User upload bukti transfer
  - Admin verifikasi/tolak dari dashboard
  - Kode unik (1-999) untuk identifikasi transfer
  - Auto-refresh halaman transfer setiap 15 detik
- [x] Voucher system (create, toggle, delete)

### Super Admin Panel
- [x] Dashboard, User management, Transaction monitoring
- [x] Voucher management, AI Settings
- [x] Bank transfer verification: view proof, approve/reject, filter by status

## Backend Architecture
```
/app/backend/
├── server.py, database.py, config.py, models.py, auth.py, prompts.py
├── routes/ (auth_routes, generate_routes, payment_routes, admin_routes)
├── uploads/ (proof of payment images)
```

## API Credentials
- **Super Admin**: ipankpaul107@gmail.com / Kakiku5.
- **BCA Account**: 2470230889 / NAJMI ABUBAKAR BASUMBUL
- **Midtrans Sandbox**: SB-Mid-client-RlztC9s1e9UMUkE6
- **Sample Voucher**: GURU2024 (20% discount)

## Next Tasks / Backlog

### P1 (Important)
- [ ] Multi-provider AI system (Gemini + OpenAI + Claude)
- [ ] Word export yang lebih baik
- [ ] Diagram untuk mata pelajaran lain
- [ ] Ubah label "Token" → "Generate" di UI

### P2 (Nice to have)
- [ ] User upload gambar untuk soal
- [ ] Rate limiting per user
- [ ] User profile settings page

### P3 (Future)
- [ ] Real email integration (Mailketing)
- [ ] Production Midtrans keys
- [ ] Analytics dashboard with charts
