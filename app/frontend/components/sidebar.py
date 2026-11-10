from typing import Dict, Any, Tuple
import streamlit as st
from app.config.settings import settings
from app.frontend.components.illustrations import get_undraw_sidebar_svg
from app.frontend.components.icons import get_icon_img

def render_sidebar(stats: Dict[str, Any], is_pinecone_connected: bool, pinecone_index_name: str) -> Tuple[str, str, str, bool]:
    """
    Renders the StayEase AI Agent OS sidebar console:
    - Agent persona authority switch
    - Cockpit display mode switch (Default: Dual-Cockpit Agent + Live Property Canvas)
    - Safety guardrails telemetry
    - Live property metrics & LLM model architecture
    Returns: (selected_role, selected_panel, model_choice, enable_tavily)
    """
    with st.sidebar:
        ic_bot = get_icon_img("bot", size=44, margin_right=0, extra_style="margin-bottom:6px; filter:drop-shadow(0 2px 4px rgba(79,70,229,0.3));")
        st.markdown(f"""
        <div style="text-align:center; padding: 6px 0 12px 0; border-bottom: 1px solid #e2e8f0; margin-bottom: 12px;">
            {ic_bot}
            <div style="font-size:18px; font-weight:800; color:#0f172a; letter-spacing:-0.3px;">StayEase Agent OS</div>
            <div style="font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:1px;">Hotel Apex Residency</div>
            <div style="font-size:10px; color:#4f46e5; font-weight:700; margin-top:3px;">● Autonomous Operations Engine &bull; 60 Units</div>
        </div>
        """, unsafe_allow_html=True)

        # Embedded Authentic unDraw Vector Banner
        st.markdown(f"""
        <div style="display:flex; justify-content:center; margin-bottom:12px; border-radius:10px; overflow:hidden; border:1px solid #e2e8f0; background:#f8fafc; padding:8px; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
            {get_undraw_sidebar_svg(width=220, height=110)}
        </div>
        """, unsafe_allow_html=True)

        # 1. Multi-Persona Role Switcher
        ic_mgr = get_icon_img("manager", size=18, margin_right=6)
        st.markdown(f"##### {ic_mgr} Agent Operating Authority", unsafe_allow_html=True)
        selected_role = st.selectbox(
            "Current Authority / Persona:",
            ["General", "Receptionist", "General Manager", "Hotel Owner", "Housekeeping", "Guest Support"],
            index=0,
            help="Switches the AI agent persona, authorization level, and specialized operational tools."
        )

        # Guardrails Indicator
        ic_shd = get_icon_img("shield", size=16, margin_right=6)
        st.markdown(f"""
        <div style="background:#ecfdf5; border:1.5px solid #a7f3d0; border-radius:8px; padding:8px 12px; margin: 8px 0 14px 0;">
            <div style="font-size:11px; font-weight:700; color:#047857; display:flex; align-items:center;">
                {ic_shd}
                <span>AI SAFETY GUARDRAILS: ENFORCED</span>
            </div>
            <div style="font-size:10px; color:#065f46; margin-top:3px; line-height:1.4;">
                Rate Floor &bull; Blacklist &bull; Settlement &bull; Pinecone RAG
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Cockpit Operating View Mode
        ic_rm = get_icon_img("room", size=18, margin_right=6)
        st.markdown(f"##### {ic_rm} Cockpit Operating View", unsafe_allow_html=True)
        nav_panels = [
            "🖥️ Autonomous Cockpit (Agent + Live Canvas)",
            "🏢 60-Room Floor Plan & Folios",
            "💬 AI Operations Terminal",
            "📊 Financial Yield & Night Audit",
            "🌲 Pinecone Knowledge Base RAG"
        ]
        if "main_nav_radio" not in st.session_state or st.session_state.main_nav_radio not in nav_panels:
            st.session_state.main_nav_radio = "🖥️ Autonomous Cockpit (Agent + Live Canvas)"

        selected_panel = st.radio(
            "Select Display Workspace:",
            nav_panels,
            key="main_nav_radio"
        )

        st.write("---")

        # Live Property Snapshot Card
        ic_grp = get_icon_img("graph", size=18, margin_right=6)
        st.markdown(f"##### {ic_grp} Live Property Telemetry", unsafe_allow_html=True)
        occ_val = stats.get('occupancy_rate', 0.0)
        st.progress(min(1.0, max(0.0, occ_val / 100.0)))
        st.caption(f"**Occupancy:** {occ_val:.1f}% ({stats.get('occupied_count', 0)} / {stats.get('total_rooms', 60)} Units)")

        s_c1, s_c2 = st.columns(2)
        with s_c1:
            st.metric("Ready Units", stats.get('available_count', 0))
        with s_c2:
            st.metric("Cleaning Queue", stats.get('cleaning_count', 0))

        st.write("---")

        # AI Agent Controls
        st.markdown(f"##### {get_icon_img('bot', size=18, margin_right=6)} LLM Model Architecture", unsafe_allow_html=True)
        model_choice = st.selectbox("Model Engine:", settings.ALLOWED_MODEL_NAMES, index=0)
        enable_tavily = st.checkbox("🌐 Tavily Live Web Search", value=False)

        if is_pinecone_connected:
            st.success(f"🌲 **Pinecone Connected**\nIndex: `{pinecone_index_name}`")
        else:
            st.info("🧠 **Vector DB:** In-Memory Active")

    return selected_role, selected_panel, model_choice, enable_tavily
