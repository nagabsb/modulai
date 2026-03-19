# ModulAI - PRD (Product Requirements Document)

## Project Overview
**ModulAI** adalah Generator Perangkat Ajar AI untuk Guru Indonesia dengan sistem token, pembayaran, dan admin panel.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI + KaTeX (math rendering) + html2pdf.js
- **Backend**: FastAPI (Python) + MongoDB + python-docx + latex2mathml + lxml
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
- [x] No maxOutputTokens limit
- [x] **Chunked soal generation** for large question sets (>15 PG)
- [x] **Export: Excel** (.xlsx via @redoper1/xlsx-js-style)
- [x] **Export: Word (.docx)** — Backend python-docx with OMML native math equations
- [x] **Export: PDF** (html2pdf.js + KaTeX pre-rendering)
- [x] **Print** (browser print dialog)

### Math Rendering Pipeline
- [x] **In-app**: KaTeX renders $..$ and $$...$$ LaTeX delimiters
- [x] **Word DOCX export**: LaTeX → MathML → OMML → proper Word equations
- [x] **PDF export**: KaTeX pre-render → html2pdf.js visual capture

### Multi-Key Multi-Provider AI System
- [x] **3 Providers**: Google Gemini, Kimi/Moonshot, OpenAI
- [x] **Fallback Chain**: Priority-based key selection
- [x] **Admin CRUD**: Add/delete/toggle/reorder API keys

### Payment Integration
- [x] E-Wallet/QRIS via Midtrans
- [x] Bank Transfer to BCA with proof upload
- [x] Voucher system

### Super Admin Panel
- [x] Dashboard, User management, Transaction monitoring
- [x] Voucher management, AI Settings
- [x] **Delete Users** (with cascade delete of related generations & transactions)
- [x] **Delete Transactions**
- [x] **Delete Generations** (individual + bulk delete all)
- [x] **Delete AI Keys**
- [x] **Generations management tab** — view & manage all generated documents

### Security
- [x] **Security Headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, Permissions-Policy, Content-Security-Policy, HSTS, Cache-Control
- [x] **XSS Input Sanitization**: sanitize_string for user inputs (name, phone, school)
- [x] **Auth bypass protection**: All admin endpoints require valid JWT with super_admin role (returns 401)

## Key Files
- `/app/backend/docx_export.py` — HTML→DOCX converter with OMML math
- `/app/backend/security.py` — XSS sanitization utilities
- `/app/backend/routes/admin_routes.py` — Admin CRUD + DELETE endpoints
- `/app/backend/routes/generate_routes.py` — /export/docx endpoint, chunked generation
- `/app/frontend/src/pages/SuperAdmin.js` — Full admin panel UI
- `/app/frontend/src/utils/latexRenderer.js` — KaTeX rendering
- `/app/frontend/src/utils/exportPdf.js` — PDF export

## API Credentials
- **Super Admin**: ipankpaul107@gmail.com / Kakiku5.

## Next Tasks / Backlog

### P1
- [ ] Diagram untuk mata pelajaran lain (Chart.js, stock images)
- [ ] Ubah label "Token" → "Generate" di UI

### P2
- [ ] User upload gambar untuk soal
- [ ] Dynamic pricing

### P3
- [ ] Real email integration (Mailketing)
- [ ] Production Midtrans keys
- [ ] Analytics dashboard
