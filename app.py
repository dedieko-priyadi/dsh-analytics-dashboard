"""DSH Analytics Dashboard — data perilaku & layanan DSH UGM.
Data: charts.db (r9_dsh_* tables dari collector collect_dsh.py).
Tab: Overview, Tren & Topik, Kualitas AI, Fasilitas, Pengguna."""
import streamlit as st, sqlite3, pandas as pd, plotly.express as px

st.set_page_config(page_title="DSH Analytics UGM", layout="wide")
DB = "/app/charts.db"

@st.cache_data(ttl=3600)
def load():
    con = sqlite3.connect(DB)
    ai = pd.read_sql("SELECT * FROM r9_dsh_ai_logs", con)
    sl = pd.read_sql("SELECT * FROM r9_dsh_search_log", con)
    fac = pd.read_sql("SELECT * FROM r9_dsh_facilities", con)
    kb = pd.read_sql("SELECT * FROM r9_dsh_kb_entities", con)
    con.close()
    return ai, sl, fac, kb

ai, sl, fac, kb = load()
ai["created_at"] = pd.to_datetime(ai["created_at"], errors="coerce")
sl["created_time"] = pd.to_datetime(sl["created_time"], errors="coerce")

st.title("🌐 DSH Analytics — Digital Services Hub UGM")

tab = st.sidebar.radio("Menu", ["Overview", "Tren & Topik", "Kualitas AI", "Fasilitas", "Pengguna"])
st.sidebar.caption(f"AI logs: {len(ai):,} · Search: {len(sl):,} · Fasilitas: {len(fac):,}")

# ═══════════ OVERVIEW ═══════════
if tab == "Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Query Chatbot (AI)", f"{len(ai):,}")
    c2.metric("Query Generator", f"{len(sl):,}")
    c3.metric("Fasilitas", f"{len(fac):,}")
    c4.metric("Unik Pengguna", f"{ai['ip_hash'].nunique():,}")
    c5.metric("Total Token AI", f"{ai['tokens_used'].sum():,}")

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Action Chatbot")
        vc = ai["action"].value_counts().reset_index()
        vc.columns = ["Action", "Jumlah"]
        st.plotly_chart(px.bar(vc, x="Action", y="Jumlah", color="Action"), use_container_width=True)
    with col_r:
        st.subheader("Model AI")
        vc = ai["model"].value_counts().reset_index()
        vc.columns = ["Model", "Jumlah"]
        st.plotly_chart(px.pie(vc, names="Model", values="Jumlah"), use_container_width=True)

    st.subheader("Knowledge Base Coverage")
    st.dataframe(kb.rename(columns={"entity_type": "Tipe", "total": "Jumlah"}), use_container_width=True, hide_index=True)

# ═══════════ TREN & TOPIK ═══════════
elif tab == "Tren & Topik":
    st.subheader("📈 Tren & Topik")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Query Chatbot per Bulan**")
        daily = ai.set_index("created_at").resample("ME").size().reset_index()
        daily.columns = ["Bulan", "Jumlah"]
        st.plotly_chart(px.line(daily, x="Bulan", y="Jumlah", markers=True), use_container_width=True)
    with col_r:
        st.markdown("**Query Generator per Bulan**")
        d2 = sl.set_index("created_time").resample("ME").size().reset_index()
        d2.columns = ["Bulan", "Jumlah"]
        st.plotly_chart(px.line(d2, x="Bulan", y="Jumlah", markers=True), use_container_width=True)

    st.subheader("Top 15 Query Chatbot (sinyal kebutuhan)")
    top = ai["query"].value_counts().head(15).reset_index()
    top.columns = ["Query", "Jumlah"]
    st.dataframe(top, use_container_width=True, hide_index=True)

# ═══════════ KUALITAS AI ═══════════
elif tab == "Kualitas AI":
    st.subheader("⚙️ Kualitas AI")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Error", f"{len(ai[ai['error_msg'] != '0']):,}")
    c2.metric("Cache Hit", f"{ai['cache_hit'].sum():,} ({ai['cache_hit'].mean()*100:.0f}%)")
    c3.metric("Rata2 Latency", f"{ai['latency_ms'].mean():.0f} ms")
    c4.metric("Rata2 Token/Query", f"{ai['tokens_used'].mean():.0f}")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Latency per Bulan**")
        lat = ai.set_index("created_at").resample("ME")["latency_ms"].mean().reset_index()
        lat.columns = ["Bulan", "Latency (ms)"]
        st.plotly_chart(px.line(lat, x="Bulan", y="Latency (ms)", markers=True), use_container_width=True)
    with col_r:
        st.markdown("**Token per Bulan (biaya)**")
        tok = ai.set_index("created_at").resample("ME")["tokens_used"].sum().reset_index()
        tok.columns = ["Bulan", "Token"]
        st.plotly_chart(px.line(tok, x="Bulan", y="Token", markers=True), use_container_width=True)

# ═══════════ FASILITAS ═══════════
elif tab == "Fasilitas":
    st.subheader("🗺️ Fasilitas")
    c1, c2 = st.columns(2)
    c1.metric("Total Fasilitas", f"{len(fac):,}")
    c2.metric("Kategori", f"{fac['category'].nunique():,}")

    vc = fac["category"].value_counts().head(20).reset_index()
    vc.columns = ["Kategori", "Jumlah"]
    st.plotly_chart(px.bar(vc, x="Jumlah", y="Kategori", orientation="h", color="Jumlah"), use_container_width=True)

    st.subheader("Fasilitas dengan Koordinat (map)")
    map_data = fac.dropna(subset=["latitude", "longitude"])
    map_data["lat"] = pd.to_numeric(map_data["latitude"], errors="coerce")
    map_data["lon"] = pd.to_numeric(map_data["longitude"], errors="coerce")
    map_data = map_data.dropna(subset=["lat", "lon"])
    if not map_data.empty:
        st.map(map_data[["lat", "lon"]])
    st.caption(f"{len(map_data)}/{len(fac)} punya koordinat")

# ═══════════ PENGGUNA ═══════════
else:
    st.subheader("👥 Pengguna")
    c1, c2, c3 = st.columns(3)
    c1.metric("Unik IP (AI)", f"{ai['ip_hash'].nunique():,}")
    c2.metric("Sesi", f"{ai['session_id'].nunique():,}")
    c3.metric("Query/Sesi", f"{len(ai)/max(ai['session_id'].nunique(),1):.1f}")

    st.subheader("Browser (User-Agent)")
    def browser(ua):
        ua = (ua or "").lower()
        if "chrome" in ua and "edg" not in ua: return "Chrome"
        if "edg" in ua: return "Edge"
        if "firefox" in ua: return "Firefox"
        if "safari" in ua: return "Safari"
        if "mobile" in ua: return "Mobile"
        return "Lainnya"
    ai["browser"] = ai["user_agent"].map(browser)
    br = ai["browser"].value_counts().reset_index()
    br.columns = ["Browser", "Jumlah"]
    st.plotly_chart(px.bar(br, x="Browser", y="Jumlah", color="Browser"), use_container_width=True)

    st.subheader("Pengirim Generator (email domain)")
    if "email" in sl.columns and len(sl):
        sl2 = sl[sl["email"].fillna("") != ""].copy()
        sl2["domain"] = sl2["email"].map(lambda e: str(e).split("@")[-1] if "@" in str(e) else "?")
        dom = sl2["domain"].value_counts().head(10).reset_index()
        dom.columns = ["Domain", "Jumlah"]
        st.dataframe(dom, use_container_width=True, hide_index=True)

st.caption("Data: charts.db (collector collect_dsh.py · cron harian 04:30)")
