import streamlit as st
import streamlit.components.v1 as components
from app.frontend.components.icons import get_icon_b64, get_icon_img

def render_top_navbar(selected_role: str, is_pinecone_connected: bool, pinecone_index_name: str, now_str: str):
    """
    Renders the Autonomous AI Agent Operating System Cockpit Navbar with live telemetry,
    real-time system status indicators, responsive mobile layout, and a 1-click Sidebar Toggle button.
    """
    pinecone_pill_class = "pill-green" if is_pinecone_connected else "pill-gold"
    pinecone_status_txt = f"Pinecone: {pinecone_index_name}" if is_pinecone_connected else "Vector DB: In-Memory"

    b64_logo = get_icon_b64("bot")
    ic_db = get_icon_img("database", size=14, margin_right=4)
    ic_cloud = get_icon_img("shield", size=14, margin_right=4)
    ic_persona = get_icon_img("manager", size=14, margin_right=4)
    ic_clock = get_icon_img("clock", size=14, margin_right=4)

    st.markdown(f"""
    <div class="official-navbar-light">
        <div class="brand-section">
            <div class="brand-left">
                <div class="brand-logo-badge" style="background:linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); border:2px solid #ffffff; border-radius:12px; width:42px; height:42px; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 14px rgba(79,70,229,0.35); flex-shrink:0;">
                    <img src="{b64_logo}" width="26" height="26" alt="StayEase AI Agent" style="display:block;"/>
                </div>
                <div style="min-width:0;">
                    <div class="brand-title">STAYEASE AUTONOMOUS AI AGENT OS</div>
                    <div class="brand-subtitle">Hotel Apex Residency &bull; 60 Premium Units</div>
                </div>
            </div>
            <div class="brand-toggle-wrapper">
                <div class="stayease-sidebar-toggle-pill" onclick="if(window.parent&&window.parent.stayeaseToggleSidebar){{window.parent.stayeaseToggleSidebar();}}else if(window.stayeaseToggleSidebar){{window.stayeaseToggleSidebar();}}" title="Click to toggle Operations Console">
                    <span style="font-size:14px; font-weight:900;">☰</span>
                    <span class="toggle-pill-text">Console</span>
                </div>
            </div>
        </div>
        <div class="system-status-pills">
            <div class="status-pill pill-green" style="font-weight:800; background:#ecfdf5; border:1px solid #10b981; color:#047857;">
                ● AI Agent: Armed
            </div>
            <div class="status-pill pill-green">{ic_db} SQLite: Synced</div>
            <div class="status-pill {pinecone_pill_class}">{ic_cloud} {pinecone_status_txt}</div>
            <div class="status-pill pill-purple">{ic_persona} Persona: {selected_role}</div>
            <div class="status-pill pill-blue">{ic_clock} {now_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Infallible Sidebar Controller via Component Script
    components.html("""
    <script>
    (function() {
        function getDoc() {
            try {
                return window.parent && window.parent.document ? window.parent.document : document;
            } catch(e) {
                return document;
            }
        }

        function toggleSidebar() {
            try {
                const doc = getDoc();
                const expandBtn = doc.querySelector('[data-testid="stExpandSidebarButton"]') || 
                                  doc.querySelector('button[aria-label="Expand sidebar"]') ||
                                  doc.querySelector('[data-testid="collapsedControl"]');
                const collapseBtn = doc.querySelector('[data-testid="stSidebarCollapseButton"]') || 
                                    doc.querySelector('button[aria-label="Collapse sidebar"]');
                if (expandBtn) {
                    expandBtn.click();
                } else if (collapseBtn) {
                    collapseBtn.click();
                }
            } catch(e) {
                console.warn('Sidebar toggle error:', e);
            }
        }

        try {
            if (window.parent) {
                window.parent.stayeaseToggleSidebar = toggleSidebar;
            }
            window.stayeaseToggleSidebar = toggleSidebar;
        } catch(e) {}

        function bindAllPills() {
            try {
                const doc = getDoc();
                const pills = doc.querySelectorAll('.stayease-sidebar-toggle-pill');
                pills.forEach(function(p) {
                    if (!p.dataset.bound) {
                        p.dataset.bound = "true";
                        p.style.cursor = "pointer";
                        p.onclick = function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            toggleSidebar();
                        };
                    }
                });

                // Auto-expand on desktop if viewport is large enough and currently collapsed
                if (window.innerWidth > 768) {
                    const expandBtn = doc.querySelector('[data-testid="stExpandSidebarButton"]');
                    if (expandBtn) {
                        expandBtn.click();
                    }
                }
            } catch(e) {}
        }

        bindAllPills();
        setTimeout(bindAllPills, 100);
        setTimeout(bindAllPills, 350);
        setTimeout(bindAllPills, 800);
    })();
    </script>
    """, height=0)
