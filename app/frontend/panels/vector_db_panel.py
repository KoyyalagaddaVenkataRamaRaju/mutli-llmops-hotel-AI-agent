import pandas as pd
import streamlit as st

from app.hotel.vector_db import HotelVectorDatabase
from app.config.settings import settings
from app.frontend.components.illustrations import get_undraw_cloud_svg
from app.frontend.components.icons import get_icon_img

def render_vector_db_panel(vdb: HotelVectorDatabase):
    """Renders Pinecone cloud configuration, hierarchical chunk inspector, and semantic search tester."""
    v_h1, v_h2 = st.columns([3, 1])
    with v_h1:
        st.markdown(f'### {get_icon_img("database", size=30)} Pinecone &amp; Vector Knowledge Database', unsafe_allow_html=True)
        st.caption("Hybrid Vector Store connecting Pinecone Cloud with in-code Semantic Hierarchical & Overlapping Window Chunking.")
    with v_h2:
        st.markdown(get_undraw_cloud_svg(width=220, height=120), unsafe_allow_html=True)

    with st.expander("⚙️ Pinecone Cloud Configuration (.env Storage)", expanded=not vdb.is_pinecone_connected):
        pc_c1, pc_c2 = st.columns([2, 1])
        with pc_c1:
            input_pc_key = st.text_input(
                "Pinecone API Key (pcsk_...):",
                value=settings.PINECONE_API_KEY or "",
                type="password"
            )
            input_pc_index = st.text_input(
                "Pinecone Index Name:",
                value=settings.PINECONE_INDEX_NAME or "stayease-hotel-apex"
            )
        with pc_c2:
            st.markdown("##### Connection Status")
            if vdb.is_pinecone_connected:
                st.success(f"🟢 **Connected to Pinecone**\n- Index: `{vdb.pinecone_index_name}`\n- Chunks Synced: **{len(vdb.documents)}**")
            else:
                st.warning("🟡 **In-Code Engine Active**\nPinecone cloud not yet connected. Using in-code vector cosine similarity.")

            btn_save_pc = st.button("💾 Save Key to .env & Connect Pinecone", use_container_width=True)
            if btn_save_pc:
                if not input_pc_key.strip():
                    st.error("Please enter a valid Pinecone API key.")
                else:
                    vdb.save_pinecone_api_key_to_env(input_pc_key, input_pc_index)
                    succ, msg = vdb.connect_pinecone(input_pc_key, input_pc_index)
                    if succ:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            if vdb.is_pinecone_connected:
                if st.button("🔄 Sync Chunks to Pinecone Index", use_container_width=True):
                    cnt = vdb.sync_vectors_to_pinecone()
                    st.success(f"Successfully synced {cnt} vector chunks to Pinecone index '{vdb.pinecone_index_name}'!")

    st.write("")
    vk_col1, vk_col2 = st.columns([1, 1], gap="large")

    with vk_col1:
        st.markdown("#### 🔍 Test Semantic Vector Query with Role Filter")
        test_query = st.text_input("Enter natural language query:", value="What are the housekeeping turnaround standards and staff allotment?")
        c_rf, c_topk = st.columns(2)
        with c_rf:
            role_filter = st.selectbox("Role Filter:", ["All Roles", "Receptionist", "General Manager", "Hotel Owner", "Housekeeping Staff", "Staff", "Support"])
        with c_topk:
            top_k_sel = st.slider("Top K Similar Chunks:", min_value=1, max_value=5, value=2)

        if st.button("Search Vector Database", type="primary", use_container_width=True):
            r_filt = None if role_filter == "All Roles" else role_filter
            matches = vdb.search(test_query, top_k=top_k_sel, role_filter=r_filt)
            active_engine = "🌲 Pinecone Cloud Index" if vdb.is_pinecone_connected else "🧠 In-Code Normalized Cosine Engine"
            st.markdown(f"**Found {len(matches)} Relevant Semantic Chunks ({active_engine}):**")
            for m in matches:
                doc = m["document"]
                score_pct = m["score"] * 100
                source_label = m.get("source", "Vector Store")
                st.markdown(f"""<div style="background:#ffffff; border:1px solid #e2e8f0; border-left:4px solid #0284c7; border-radius:8px; padding:12px 14px; margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
<div style="display:flex; justify-content:space-between; align-items:center;">
<span style="font-weight:700; color:#0f172a; font-size:14px;">{doc['title']}</span>
<span style="font-size:11px; padding:2px 8px; border-radius:12px; background:#eff6ff; color:#1d4ed8; font-weight:700;">{score_pct:.1f}% Match</span>
</div>
<div style="font-size:11px; color:#64748b; margin: 4px 0 6px 0;">Role: <span style="font-weight:700; color:#0284c7;">{doc.get('role', 'General')}</span> &bull; Category: {doc['category']} &bull; ID: {doc['id']} &bull; Source: <span style="color:#059669; font-weight:600;">{source_label}</span></div>
<div style="font-size:13px; color:#334155; line-height:1.5;">{doc['content']}</div>
</div>""", unsafe_allow_html=True)

    with vk_col2:
        st.markdown("#### 📑 Hierarchical Chunk Strategy Inspector")
        st.caption(f"Currently indexing {len(vdb.documents)} semantic chunks with 20-word overlapping windows across {len(vdb.vocabulary)} vocabulary dimensions.")

        v_summary = []
        for d in vdb.documents:
            v_summary.append({
                "ID": d["id"],
                "Role": d.get("role", "General"),
                "Category": d["category"],
                "Title": d["title"],
                "Preview": d["content"][:65] + "..."
            })
        st.dataframe(pd.DataFrame(v_summary), use_container_width=True, hide_index=True)

