"""DSH Analytics Dashboard — data perilaku & layanan DSH UGM.
Data: charts.db (r9_dsh_* dari collect_dsh.py — sumber BENAR: ugm_dsh).
Tab: Overview, Tren & Topik, Kualitas AI, Knowledge & Feedback, Fasilitas, Pengguna."""
import streamlit as st, sqlite3, pandas as pd, plotly.express as px

st.set_page_config(page_title="DSH Analytics UGM", layout="wide")
DB = "/app/charts.db"

@st.cache_data(ttl=3600)
def load():
    con = sqlite3.connect(DB)
    ai = pd.read_sql("SELECT * FROM r9_dsh_ai_logs", con)
    sh = pd.read_sql("SELECT * FROM r9_dsh_search_history", con)
    qa = pd.read_sql("SELECT * FROM r9_dsh_qa_knowledge", con)
    fb = pd.read_sql("SELECT * FROM r9_dsh_ai_feedback", con)
    conv = pd.read_sql("SELECT * FROM r9_dsh_ai_conversations", con)
    an = pd.read_sql("SELECT * FROM r9_dsh_ai_analytics", con)
    pop = pd.read_sql("SELECT * FROM r9_dsh_popular", con)
    tr = pd.read_sql("SELECT * FROM r9_dsh_entity_trends", con)
    fac = pd.read_sql("SELECT * FROM r9_dsh_facilities", con)
    # EA tables (cross-domain)
    try:
        ea_el = pd.read_sql("SELECT Object_ID, Name, Stereotype, Status, Package_ID FROM r9_ea_elements", con)
        ea_pkg = pd.read_sql("SELECT Package_ID, Name FROM r9_ea_packages", con)
    except Exception:
        ea_el, ea_pkg = pd.DataFrame(), pd.DataFrame()
    con.close()
    return ai, sh, qa, fb, conv, an, pop, tr, fac, ea_el, ea_pkg

ai, sh, qa, fb, conv, an, pop, tr, fac, ea_el, ea_pkg = load()
ai["created_at"] = pd.to_datetime(ai["created_at"], errors="coerce")
sh["search_timestamp"] = pd.to_datetime(sh["search_timestamp"], errors="coerce")

st.title("🌐 DSH Analytics — Digital Services Hub UGM")

tab = st.sidebar.radio("Menu", ["Overview", "Tren & Topik", "Kualitas AI", "Knowledge & Feedback", "Fasilitas", "Pengguna", "Cross-Domain EA"])
st.sidebar.caption(f"AI: {len(ai):,} · Search: {len(sh):,} · Q&A: {len(qa):,} · Index: {tr['total_items_created'].sum():,}")

# ═══════════ OVERVIEW ═══════════
if tab == "Overview":
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Query Chatbot", f"{len(ai):,}")
    c2.metric("Pencarian Web", f"{len(sh):,}")
    c3.metric("Q&A Knowledge", f"{len(qa):,}")
    c4.metric("Feedback", f"{len(fb):,}")
    c5.metric("Unik Pengguna", f"{ai['ip_hash'].nunique():,}")
    c6.metric("Token AI", f"{ai['tokens_used'].sum():,}")

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

    st.subheader("Knowledge Base — Entity Trends (search_index)")
    agg = tr.groupby("entity_type")[["total_items_created", "clicked_items_30d"]].sum().reset_index()
    agg.columns = ["Entity", "Total", "Klik 30d"]
    st.dataframe(agg.sort_values("Total", ascending=False), use_container_width=True, hide_index=True)

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
        st.markdown("**Pencarian Web per Bulan**")
        d2 = sh.set_index("search_timestamp").resample("ME").size().reset_index()
        d2.columns = ["Bulan", "Jumlah"]
        st.plotly_chart(px.line(d2, x="Bulan", y="Jumlah", markers=True), use_container_width=True)

    st.subheader("Top 15 Query Chatbot (sinyal kebutuhan)")
    top = ai["query"].value_counts().head(15).reset_index()
    top.columns = ["Query", "Jumlah"]
    st.dataframe(top, use_container_width=True, hide_index=True)

    st.subheader("Query Populer (search_trends)")
    st.dataframe(pop.sort_values("search_count", ascending=False).head(15)
                 [["query", "search_count", "avg_results", "search_date"]]
                 .rename(columns={"query": "Query", "search_count": "Jumlah", "avg_results": "Rata2 Hasil", "search_date": "Tanggal"}),
                 use_container_width=True, hide_index=True)

# ═══════════ KUALITAS AI ═══════════
elif tab == "Kualitas AI":
    st.subheader("⚙️ Kualitas AI (ai_search_analytics — agregat harian)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Request", f"{an['total_requests'].sum():,}")
    c2.metric("Error Rate", f"{an['error_rate_pct'].mean():.1f}%")
    c3.metric("Avg Latency", f"{an['avg_latency_ms'].mean():.0f} ms")
    c4.metric("Total Token", f"{an['total_tokens'].sum():,}")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("**Request per Hari**")
        a2 = an.groupby("search_date")["total_requests"].sum().reset_index()
        st.plotly_chart(px.line(a2, x="search_date", y="total_requests", markers=True), use_container_width=True)
    with col_r:
        st.markdown("**Token per Hari**")
        t2 = an.groupby("search_date")["total_tokens"].sum().reset_index()
        st.plotly_chart(px.line(t2, x="search_date", y="total_tokens", markers=True), use_container_width=True)

    st.subheader("Detail per Hari-Action")
    st.dataframe(an.sort_values("search_date", ascending=False), use_container_width=True, hide_index=True)

# ═══════════ KNOWLEDGE & FEEDBACK ═══════════
elif tab == "Knowledge & Feedback":
    st.subheader("🧠 Knowledge Base & Feedback")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Q&A Knowledge", f"{len(qa):,}")
    c2.metric("Feedback", f"{len(fb):,}")
    c3.metric("Total Use (KB)", f"{qa['use_count'].sum():,}")
    c4.metric("Perc. Approved", f"{qa['is_approved'].mean()*100:.0f}%")

    st.subheader("Top 15 Q&A Paling Dipakai")
    top = qa.nlargest(15, "use_count")[["query_original", "use_count", "positive_feedback", "negative_feedback", "quality_score"]]
    top.columns = ["Pertanyaan", "Dipakai", "Positif", "Negatif", "Skor"]
    st.dataframe(top, use_container_width=True, hide_index=True)

    st.subheader("Feedback Pengguna (rating)")
    if not fb.empty:
        vc = fb["rating"].value_counts().sort_index().reset_index()
        vc.columns = ["Rating", "Jumlah"]
        st.plotly_chart(px.bar(vc, x="Rating", y="Jumlah", color="Rating"), use_container_width=True)
        fb_txt = fb[fb["feedback_text"].notna() & (fb["feedback_text"] != "")][["query", "rating", "feedback_text"]].head(10)
        if not fb_txt.empty:
            st.dataframe(fb_txt, use_container_width=True, hide_index=True)

    st.subheader("Percakapan (ai_conversations)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Percakapan", f"{len(conv):,}")
    c2.metric("Rata2 Turn", f"{conv['turn_count'].mean():.1f}" if not conv.empty else "-")
    c3.metric("Kontribusi KB", f"{conv['contributed_kb'].sum():,}")

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
    map_data = fac.dropna(subset=["latitude", "longitude"]).copy()
    map_data["lat"] = pd.to_numeric(map_data["latitude"], errors="coerce")
    map_data["lon"] = pd.to_numeric(map_data["longitude"], errors="coerce")
    map_data = map_data.dropna(subset=["lat", "lon"])
    if not map_data.empty:
        st.map(map_data[["lat", "lon"]])
    st.caption(f"{len(map_data)}/{len(fac)} punya koordinat")

# ═══════════ PENGGUNA ═══════════
elif tab == "Pengguna":
    st.subheader("👥 Pengguna")
    c1, c2, c3 = st.columns(3)
    c1.metric("Unik IP (AI)", f"{ai['ip_hash'].nunique():,}")
    c2.metric("Sesi", f"{ai['session_id'].nunique():,}")
    c3.metric("Query/Sesi", f"{len(ai)/max(ai['session_id'].nunique(),1):.1f}")

    st.subheader("Mode Pencarian Web (search_history)")
    if not sh.empty:
        vc = sh["search_mode"].value_counts().reset_index()
        vc.columns = ["Mode", "Jumlah"]
        st.plotly_chart(px.bar(vc, x="Mode", y="Jumlah", color="Mode"), use_container_width=True)

    st.subheader("Browser (User-Agent AI)")
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

# ═══════════ CROSS-DOMAIN EA ═══════════
elif tab == "Cross-Domain EA":
    st.subheader("🔗 Cross-Domain — EA (blueprint) × DSH (realita)")
    if ea_el.empty:
        st.warning("Data EA tidak tersedia di charts.db — jalankan collect_ea_ugm.py dulu")
    else:
        # 1. Layanan EA vs entity service DSH
        c1, c2, c3 = st.columns(3)
        ea_lay = ea_el[ea_el["Stereotype"].isin(["Layanan", "ApplicationService", "ApplicationComponent", "ServiceCategory"])]
        dsh_serv = tr[tr["entity_type"] == "service"]["total_items_created"].sum() if not tr.empty else 0
        c1.metric("EA: Layanan/Aplikasi", f"{len(ea_lay):,}")
        c2.metric("DSH: Entity Service", f"{int(dsh_serv):,}")
        c3.metric("Query 'layanan' DSH", f"{len(sh[sh['query'].str.contains('layanan|simaster|portal', case=False, na=False)]):,}")

        # 2. EA Layanan per package (unit)
        st.subheader("EA: Layanan per Unit (package)")
        if not ea_lay.empty and not ea_pkg.empty:
            pkg_name = ea_pkg.rename(columns={"Name": "PkgName"})
            merged = ea_lay.merge(pkg_name, on="Package_ID", how="left")
            top = merged["PkgName"].fillna("(tanpa package)").value_counts().head(15).reset_index()
            top.columns = ["Unit", "Jumlah Layanan"]
            st.plotly_chart(px.bar(top, x="Jumlah Layanan", y="Unit", orientation="h", color="Jumlah Layanan"), use_container_width=True)

        # 3. DSH entity clicks vs EA (kebutuhan publik)
        st.subheader("DSH: Entity Diklik 30d (kebutuhan publik)")
        if not tr.empty:
            agg = tr.groupby("entity_type")[["total_items_created", "clicked_items_30d"]].sum().reset_index()
            agg.columns = ["Entity", "Total", "Klik 30d"]
            agg["rasio_klik"] = (agg["Klik 30d"] / agg["Total"].replace(0, 1) * 100).round(1)
            st.dataframe(agg.sort_values("Klik 30d", ascending=False), use_container_width=True, hide_index=True)

        # 4. Insight gap
        st.subheader("💡 Insight Gap (otomatis)")
        if not tr.empty:
            agg = tr.groupby("entity_type")[["total_items_created", "clicked_items_30d"]].sum().reset_index()
            agg = agg[agg["clicked_items_30d"] > 0]
            if not agg.empty:
                top_ent = agg.sort_values("clicked_items_30d", ascending=False).iloc[0]
                ent_name = str(top_ent.get("entity_type", "?"))
                klik = int(top_ent.get("clicked_items_30d", 0) or 0)
                total = int(top_ent.get("total_items_created", 0) or 0)
                st.info(f"Entity **{ent_name}** paling diklik publik (30d: {klik} klik dari {total} item) — kebutuhan publik tertinggi, pastikan proses EA terkait sudah digital.")
            gaps = sh[sh["query"].str.contains("layanan|simaster|portal", case=False, na=False)]
            st.write(f"**{len(gaps):,} pencarian layanan** di DSH → bandingkan dengan **{len(ea_lay):,} layanan/aplikasi** di EA: proses mana yang dicari publik tapi belum ada di arsitektur?")

st.caption("Data: charts.db r9_dsh_* (collect_dsh.py — sumber ugm_dsh /var/www/html/search/search&dsh · cron harian 04:30)")
