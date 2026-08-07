# Referensi Arsitektur — Dashboard BTD (Payung Besar)

Dashboard DSH analytics ini adalah **sub-menu** dari BTD MAIN DASHBOARD (payung besar).
Konsep lengkap: `~/strategic-dashboard/ARSITEKTUR-DASHBOARD-BTD.md` + repo strategic-dashboard.

## Posisi DSH di arsitektur

```
BTD MAIN DASHBOARD (strategic-dashboard :8542 /strategic/)
├── Overview
├── Sub-menu per dataset
│   ├── DSH → dsh-analytics-dashboard (:8541 /dsh-analytics/) ← INI
│   └── ...
└── Cross-Domain (menghubungkan semua dataset)
```

## Peta project DSH

Lihat `PETA-PROJECT-DSH.md` di repo ini — 9 project DSH (dsh-ugm, dsh-aitool, dsh-dashboard,
dsh_chatbot, dsh-mcp, dsh-analytics-dashboard, dsh_super_app, dsh-apk, ugmdsh-mcp).

## Pipeline data DSH (sumber benar)

```
search.ugm.ac.id → ugm_dsh (BUKAN store_ai!)
  → SSH tunnel 127.0.0.1:13307 → collect_dsh.py (cron 04:30)
  → charts.db (r9_dsh_*) → dsh-analytics-dashboard
```
