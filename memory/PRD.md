# ModulAI - PRD (Product Requirements Document)

## Project Overview
**ModulAI** adalah Generator Perangkat Ajar AI untuk Guru Indonesia dengan sistem token, pembayaran, dan admin panel.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI + KaTeX (math rendering)
- **Backend**: FastAPI (Python) + MongoDB (modular architecture)
- **AI**: Multi-provider (Gemini, Kimi/Moonshot, OpenAI) with fallback chain
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
- [x] No maxOutputTokens limit (AI generates freely)

### Multi-Key Multi-Provider AI System
- [x] **3 Providers**: Google Gemini (4 models), Kimi/Moonshot (2 models), OpenAI (2 models)
- [x] **Fallback Chain**: Keys tried in priority order, auto-fallback on failure
- [x] **Admin CRUD**: Add/delete/toggle/reorder API keys from UI
- [x] **Pricing Info**: Per-provider pricing table in admin panel
- [x] **Models supported**:
  - Gemini: 2.5 Flash, 2.5 Flash-Lite, 2.5 Pro, 2.0 Flash
  - Kimi: K2.5, K2.5 Instant
  - OpenAI: GPT-4o Mini, GPT-4o

### Payment Integration
- [x] E-Wallet/QRIS via Midtrans
- [x] Bank Transfer to BCA 2470230889 (Najmi Abubakar Basumbul) with proof upload
- [x] Voucher system

### Super Admin Panel
- [x] Dashboard, User management, Transaction monitoring (with verify/reject bank transfers)
- [x] Voucher management, AI Settings (multi-key management)

## Backend Architecture
```
/app/backend/
├── server.py, database.py, config.py, models.py, auth.py, prompts.py
├── routes/ (auth_routes, generate_routes, payment_routes, admin_routes)
├── uploads/ (proof of payment images)
├── tests/ (test_ai_keys.py)
```

## API Credentials
- **Super Admin**: ipankpaul107@gmail.com / Kakiku5.
- **BCA Account**: 2470230889 / NAJMI ABUBAKAR BASUMBUL
- **Midtrans Sandbox**: SB-Mid-client-RlztC9s1e9UMUkE6

## Next Tasks / Backlog

### P1 (Important)
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
