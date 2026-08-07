# Peta Project DSH — Pemetaan Lengkap (2026-08-07)

**Tujuan**: menghilangkan kebingungan karena banyaknya project DSH. Satu dokumen yang memetakan semua.

## 1. DSH = Apa? (wajah publik, dari crawl langsung)

**"Search & Digital Services Universitas Gadjah Mada"** — portal pencarian terpadu di **https://search.ugm.ac.id/ai/** untuk sivitas + publik menemukan & mengakses layanan digital UGM.

- **89.740 entitas terindeks**: Layanan 112, Berita 4.965, Produk 596, Dosen 5.385, Publikasi 68.692, HKI/Paten 9.233, Produk Hukum 149, Pidato 24, Fasilitas 404, Agenda 180, Tech4disaster 31, Video
- **3 pilar (Dharma)**: Pendidikan, Penelitian, Pengabdian
- **Fitur**: Search box, Informasi Terbaru (37 berita/7 hari), FAQ, Peta Fasilitas, Tools AI, Dashboard
- **API publik** (12 action): smart_search, get_trending, get_database_stats, browse, faq_list, detect_intent, search_external, trigger_scraping, get_scraping_jobs, get_filter_options, facility_categories, get_acadstaff_photo

## 2. Semua Project DSH (folder → repo → fungsi)

| # | Folder | Repo GitHub | Fungsi | Container/Port | Status |
|---|---|---|---|---|---|
| 1 | `dsh-ugm` | [dsh-ugm](https://github.com/dedieko-priyadi/dsh-ugm) | Web DSH asli (PHP, dari search.ugm.ac.id) | dsh-ugm-web/nginx :8585, dsh-ugm-db | 🟢 jalan |
| 2 | `dsh-aitool` | [dsh-aitool](https://github.com/dedieko-priyadi/dsh-aitool) | AI tool (chat, generator berita) | dsh-aitool :8590, dsh-aitool-db | 🟢 jalan |
| 3 | `dsh-dashboard` | [dsh-dashboard](https://github.com/dedieko-priyadi/dsh-dashboard) | Dashboard DSH lama (Streamlit, baca charts.db) | dsh-dashboard :8528 /dsh-dash/ | 🟢 jalan |
| 4 | `dsh_chatbot` | [dsh-chatbot](https://github.com/dedieko-priyadi/dsh-chatbot) | Chatbot DSH (Node.js + Streamlit + API) | :8516, streamlit+api | 🟢 jalan |
| 5 | `dsh-mcp` | [dsh-mcp](https://github.com/dedieko-priyadi/dsh-mcp) | MCP server DSH (7 tools, query production MySQL) | — | 🟢 MCP aktif |
| 6 | `dsh-analytics-dashboard` | [dsh-analytics-dashboard](https://github.com/dedieko-priyadi/dsh-analytics-dashboard) | **Dashboard analytics DSH (BARU)** — perilaku pengguna, AI quality, KB | dsh-analytics :8541 /dsh-analytics/ | 🟢 jalan |
| 7 | `dsh_super_app` | [dsh-super-app](https://github.com/dedieko-priyadi/dsh-super-app) | DSH Super App (Flutter/APK mobile) | — | 🟢 repo |
| 8 | `dsh-apk` | (belum repo) | Build APK DSH | — | ⚪ draft |
| 9 | `ugmdsh-mcp` | (belum repo) | MCP DSH alternatif (draft) | — | ⚪ draft |

## 3. Arsitektur Data Pipeline (yang benar)

```
search.ugm.ac.id (VPS 10.17.104.219)
├── ugm_dsh DB (production) — sumber data BENAR
│   ├── search_history (3.812) — perilaku pencarian
│   ├── ai_search_logs (2.362) — chatbot AI
│   ├── ai_qa_knowledge (338) — Q&A KB
│   ├── ai_feedback (41) — rating
│   ├── ai_conversations (229)
│   ├── ai_search_analytics (48) — agregat harian
│   ├── popular_searches (40) + search_trends (135)
│   └── search_index (89.774) — knowledge base
├── store_ai DB — ⚠️ BUKAN sumber DSH (app lain)
└── search&dsh/ (kode aplikasi) — config/db.php → ugm_dsh

→ SSH tunnel 127.0.0.1:13307 (systemd dsh-tunnel)
→ collect_dsh.py (cron 04:30) → charts.db (r9_dsh_*)
→ dsh-analytics-dashboard (:8541) + strategic-dashboard (:8542)
```

## 4. Dashboard Analytics DSH (yang aktif direkomendasikan)

**dsh-analytics-dashboard** :8541 → https://nuc-nuc7i5bnh-1.tail758353.ts.net/dsh-analytics/
- 6 tab: Overview, Tren & Topik, Kualitas AI, Knowledge & Feedback, Fasilitas, Pengguna + Cross-Domain EA

**dsh-dashboard** :8528 (lama) → https://nuc-nuc7i5bnh-1.tail758353.ts.net/dsh-dash/
- Dashboard DSH generasi pertama (baca snapshot charts.db)

## 5. Pelajaran Kunci (agar tidak salah lagi)

1. **Sumber data DSH = `ugm_dsh`**, BUKAN `store_ai` (store_ai = app lain, 9.158 search_log itu bukan DSH)
2. `search_trends` = analitik per entity type; query populer ada di `popular_searches`
3. Kode aplikasi di VPS: `/var/www/html/search/search&dsh/` — config/db.php = konfigurasi DB asli
4. JS & API di `/ai/search&dsh/js/` & `/ai/search&dsh/api/api.php`
5. **Wajib pahami wajah publik dulu** (crawl search.ugm.ac.id) sebelum analisis data — konteks menentukan makna data
