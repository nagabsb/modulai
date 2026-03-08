# ModulAI - PRD (Product Requirements Document)

## Project Overview
**ModulAI** adalah Generator Perangkat Ajar AI untuk Guru Indonesia dengan sistem token, pembayaran, dan admin panel.

## Tech Stack
- **Frontend**: React + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + MongoDB
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

### Payment Integration
- [x] Midtrans Snap.js popup
- [x] Webhook handler untuk update token
- [x] Voucher system dengan diskon persentase/nominal

### Super Admin Panel
- [x] Dashboard: total users, revenue, documents, token circulation
- [x] User management: edit token balance, suspend/activate
- [x] Transaction monitoring dengan filter status
- [x] Voucher management: create, list
- [x] AI Settings: switch provider (Flash-Lite/Pro), update API key

## What's Been Implemented (Jan 2026)

### Backend
- FastAPI server with JWT auth
- MongoDB collections: users, transactions, generations, vouchers, settings
- Gemini AI integration with configurable provider
- Midtrans payment integration
- Webhook handler for payment notifications
- Admin endpoints for dashboard, users, transactions, vouchers, AI settings

### Frontend
- Landing page with hero, features, pricing, testimonials
- Auth pages: Login, Register, Forgot Password
- Dashboard with token balance, recent generations, quick actions
- Generate page: 3-step wizard with form, config, result
- Checkout page: 2-step wizard like SantaiScale reference
- History page with search/filter
- Super Admin panel with Dashboard, Users, Transactions, Vouchers, AI Settings
- SVG diagram components for physics (CircuitDiagram, MeterDiagram, PhysicsDiagram)
- Excel export utility with styling

## API Credentials
- **Super Admin**: ipankpaul107@gmail.com / Kakiku5.
- **Gemini API Key**: Configured in AI Settings (masked)
- **Midtrans Sandbox**: Client Key SB-Mid-client-RlztC9s1e9UMUkE6
- **Sample Voucher**: GURU2024 (20% discount)

## Next Tasks / Backlog

### P0 (Critical)
- [ ] Real email integration (Mailketing)
- [ ] Production Midtrans keys

### P1 (Important)
- [ ] Word/PDF export
- [ ] More physics diagram types (lens, waves, thermodynamics)
- [ ] KaTeX rendering for math formulas

### P2 (Nice to have)
- [ ] User profile settings page
- [ ] Password change functionality
- [ ] Analytics dashboard with charts
- [ ] Bulk document generation

## Design Guidelines
- Primary: #1E3A5F (Navy)
- Secondary: #F4820A (Orange)
- Success: #10B981 (Green)
- Font: Plus Jakarta Sans (headings), Inter (body)
