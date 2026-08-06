# DSH Analytics Dashboard

Streamlit dashboard untuk analisis Digital Services Hub UGM (search.ugm.ac.id) — perilaku pengguna, kualitas AI, knowledge base, fasilitas. Data: `charts.db` (collection engine), di-populate oleh `collect_dsh.py` dari **database `ugm_dsh`** (sumber benar).

## URL
- **Public**: https://nuc-nuc7i5bnh-1.tail758353.ts.net/dsh-analytics/
- **Local**: http://127.0.0.1:8541/dsh-analytics/

## ⚠️ Pelajaran Penting: Sumber Database yang BENAR (2026-08-07)

Koreksi setelah RCA: **`store_ai.search_log` (9.158) BUKAN data DSH** — itu tabel aplikasi lain. Aplikasi DSH (`/var/www/html/search/search&dsh/`, config/db.php) menulis ke **`ugm_dsh`**:
- `ugm_dsh.search_history` (3.812) — riwayat pencarian web
- `ugm_dsh.ai_search_logs` (2.362) — log chatbot RAG
- `ugm_dsh.ai_qa_knowledge` (338) — Q&A knowledge base
- `ugm_dsh.ai_feedback` (41) — rating pengguna
- `ugm_dsh.ai_conversations` (229) — percakapan multi-turn
- `ugm_dsh.ai_search_analytics` (48) — agregat harian (request/token/latency/error)
- `ugm_dsh.popular_searches` (40) + `search_trends` (135) — query populer + analitik entity
- `ugm_dsh.search_index` (89.774) — knowledge base pencarian

**Pitfall**: `search_trends` = analitik per **entity type** (entity_type, total_items_created, clicked_items_30d), BUKAN query populer. Query populer ada di `popular_searches`.

## Arsitektur
```
MySQL production (10.17.104.219, ugm_dsh)
  → SSH tunnel 127.0.0.1:13307 (systemd dsh-tunnel)
  → collect_dsh.py (cron harian 04:30, job 185ce216edec)
  → charts.db (r9_dsh_* tables)
  → dsh-analytics (Streamlit :8541, subpath /dsh-analytics/)
```

## 6 Tab
1. **Overview** — KPI, action/model, entity trends (search_index)
2. **Tren & Topik** — query per bulan, top query chatbot, query populer
3. **Kualitas AI** — agregat harian: request, token, latency, error rate
4. **Knowledge & Feedback** — Q&A KB top, rating pengguna, feedback negatif, percakapan
5. **Fasilitas** — kategori, map koordinat
6. **Pengguna** — unik IP, sesi, mode pencarian, browser

## Insight terverifikasi (2026-08-07)
- 2.362 query chatbot (Mar–Agt 2026), 1.147.769 token, model qwen2.5:0.5b (65%) + gpt-4o-mini (32%)
- 3.812 pencarian web, mode fulltext dominan (3.192)
- Q&A KB: "penelitian hantavirus" paling dipakai (17×); total use 459
- Feedback: 36 positif / 5 negatif — negatif: "jawaban tidak sesuai", "informasi rancu", "text terputus"
- Knowledge base: publication 68.756, patent 9.246, people 5.412, news 5.018 (90.500 total)
- Entity clicks 30d: service 20, news 11, publication 8

## Deploy
```bash
cd ~/dsh-analytics-dashboard
sg docker -c "docker compose up -d --build"
sudo tailscale funnel --bg --set-path /dsh-analytics/ http://localhost:8541/dsh-analytics/
```

## Repo
https://github.com/dedieko-priyadi/dsh-analytics-dashboard
