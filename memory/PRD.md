# ModulAI - PRD (Product Requirements Document)

## Project Overview
**ModulAI** adalah Generator Perangkat Ajar AI untuk Guru Indonesia dengan sistem token, pembayaran, dan admin panel.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI + KaTeX (math rendering) + html2pdf.js
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
- [x] SVG Physics Diagrams
- [x] No maxOutputTokens limit (AI generates freely)
- [x] **Chunked soal generation** for large question sets (>15 PG) — prevents proxy timeout
- [x] **Export: Excel** (.xlsx via @redoper1/xlsx-js-style)
- [x] **Export: Word** (.doc via Blob API + LaTeX→Unicode converter)
- [x] **Export: PDF** (via html2pdf.js + KaTeX pre-rendering)
- [x] **Print** (browser print dialog)

### Multi-Key Multi-Provider AI System
- [x] **3 Providers**: Google Gemini (4 models), Kimi/Moonshot (2 models), OpenAI (2 models)
- [x] **Fallback Chain**: Keys tried in priority order, auto-fallback on failure
- [x] **Admin CRUD**: Add/delete/toggle/reorder API keys from UI
- [x] **Pricing Info**: Per-provider pricing table in admin panel

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
├── tests/ (test_chunked_soal.py)
```

## Key Files
- `/app/frontend/src/utils/latexRenderer.js` — LaTeX→KaTeX rendering + LaTeX→Unicode converter
- `/app/frontend/src/utils/exportWord.js` — Word export with LaTeX→Unicode conversion
- `/app/frontend/src/utils/exportPdf.js` — PDF export with KaTeX pre-rendering
- `/app/frontend/src/utils/exportExcel.js` — Excel export
- `/app/backend/routes/generate_routes.py` — AI gen with chunking + save endpoint
- `/app/backend/prompts.py` — Prompts with section-specific builders

## API Credentials
- **Super Admin**: ipankpaul107@gmail.com / Kakiku5.
- **BCA Account**: 2470230889 / NAJMI ABUBAKAR BASUMBUL
- **Midtrans Sandbox**: SB-Mid-client-RlztC9s1e9UMUkE6

## Next Tasks / Backlog

### P1 (Important)
- [ ] Diagram untuk mata pelajaran lain (Chart.js, stock images)
- [ ] Ubah label "Token" → "Generate" di UI

### P2 (Nice to have)
- [ ] User upload gambar untuk soal
- [ ] Dynamic pricing (biaya bervariasi berdasarkan kompleksitas)
- [ ] Rate limiting per user

### P3 (Future)
- [ ] Real email integration (Mailketing)
- [ ] Production Midtrans keys
- [ ] Analytics dashboard with charts
