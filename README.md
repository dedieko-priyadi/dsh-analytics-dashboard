# DSH Analytics Dashboard

Streamlit dashboard untuk analisis Digital Services Hub UGM (search.ugm.ac.id) — perilaku pengguna, kualitas AI, fasilitas, dan knowledge base. Data: `charts.db` (collection engine), di-populate oleh `collect_dsh.py`.

## URL
- **Public**: https://nuc-nuc7i5bnh-1.tail758353.ts.net/dsh-analytics/
- **Local**: http://127.0.0.1:8541/dsh-analytics/

## Arsitektur
```
MySQL production (10.17.104.219, store_ai + ugm_dsh)
  → SSH tunnel 127.0.0.1:13307 (systemd dsh-tunnel)
  → collect_dsh.py (cron harian 04:30)
  → charts.db (r9_dsh_* tables)
  → dsh-analytics (Streamlit :8541, subpath /dsh-analytics/)
```

## Data (charts.db)
| Tabel | Isi | Jumlah |
|---|---|---|
| `r9_dsh_search_log` | Query AI generator (BERITAUGM dll) + email pengirim | 9.158 |
| `r9_dsh_ai_logs` | Query chatbot RAG: action, model, tokens, latency, cache, ip_hash, session | 2.362 |
| `r9_dsh_facilities` | Fasilitas kampus + kategori + koordinat | 404 |
| `r9_dsh_kb_entities` | Coverage knowledge base per tipe (publication 68K, patent 9.2K...) | 10 |

## 5 Tab
1. **Overview** — KPI, action/model distribution, KB coverage
2. **Tren & Topik** — query per bulan (chatbot + generator), top 15 query
3. **Kualitas AI** — error, cache hit, latency, token per bulan
4. **Fasilitas** — kategori, map koordinat
5. **Pengguna** — unik IP, sesi, browser, email domain

## Insight terverifikasi (2026-08-07)
- 2.362 query chatbot (Mar–Agt 2026), 1.147.769 token total, 0 error
- 9.158 query generator; 2.444 email @ugm.ac.id (1.467 ugm.ac.id + 977 mail.ugm.ac.id)
- Top kebutuhan: rektor UGM (26), hantavirus (22), peraturan rektor (18), beasiswa (16), red tape (15)
- 404 fasilitas, 100% punya koordinat (siap map)
- Cache hit 459/2.362 (19%) — potensi penghematan token

## Deploy
```bash
cd ~/dsh-analytics-dashboard
sg docker -c "docker compose up -d --build"
sudo tailscale funnel --bg --set-path /dsh-analytics/ http://localhost:8541/dsh-analytics/
```

## Repo
https://github.com/dedieko-priyadi/dsh-analytics-dashboard
