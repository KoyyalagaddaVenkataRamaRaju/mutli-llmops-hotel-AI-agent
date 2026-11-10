from datetime import datetime
import streamlit as st
import requests

from app.hotel.services import HotelService
from app.hotel.vector_db import HotelVectorDatabase
from app.frontend.styles import apply_custom_styles
from app.frontend.components.navbar import render_top_navbar
from app.frontend.components.sidebar import render_sidebar
from app.frontend.components.kpi_metrics import render_kpi_cards
from app.frontend.components.floating_fab import render_floating_ai_fab

from app.frontend.panels.floor_plan import render_floor_plan_panel, render_room_folio_page
from app.frontend.panels.checkin import render_checkin_panel
from app.frontend.panels.checkout import render_checkout_panel
from app.frontend.panels.agent_terminal import render_agent_terminal_panel
from app.frontend.panels.housekeeping import render_housekeeping_panel
from app.frontend.panels.maintenance import render_maintenance_panel
from app.frontend.panels.room_service import render_room_service_panel
from app.frontend.panels.owner_analytics import render_owner_analytics_panel
from app.frontend.panels.vector_db_panel import render_vector_db_panel

BACKEND_URL = "http://127.0.0.1:8000"

# 1. Page Configuration
st.set_page_config(
    page_title="StayEase AI Agent OS | Hotel Apex Residency",
    page_icon="app/frontend/assets/icons/bot.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Apply Custom Styling Foundation
apply_custom_styles()

# 3. Service Singletons
@st.cache_resource
def get_hotel_service():
    return HotelService()

@st.cache_resource
def get_vector_db():
    return HotelVectorDatabase()

service = get_hotel_service()
vdb = get_vector_db()

def fetch_live_stats():
    try:
        r = requests.get(f"{BACKEND_URL}/stats", timeout=1.5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return service.get_hotel_stats()

stats = fetch_live_stats()
now_str = datetime.now().strftime("%d %b %Y | %H:%M:%S")

# 4. Render Sidebar Operations Console
selected_role, selected_panel, model_choice, enable_tavily = render_sidebar(
    stats=stats,
    is_pinecone_connected=vdb.is_pinecone_connected,
    pinecone_index_name=vdb.pinecone_index_name
)

# 5. Render Top Cockpit Navbar
render_top_navbar(
    selected_role=selected_role,
    is_pinecone_connected=vdb.is_pinecone_connected,
    pinecone_index_name=vdb.pinecone_index_name,
    now_str=now_str
)

# 6. Render Executive KPI Metric Cards
render_kpi_cards(stats=stats)

# 7. Check if user is inspecting a specific room card (Dedicated Full-Page Separate View)
if st.session_state.get("inspected_room_number"):
    render_room_folio_page(service=service, room_number=st.session_state.inspected_room_number)

# 8. Route to Active Management Cockpit
elif selected_panel == "🖥️ Autonomous Cockpit (Agent + Live Canvas)":
    agent_col, canvas_col = st.columns([1, 1], gap="large")

    with agent_col:
        render_agent_terminal_panel(
            selected_role=selected_role,
            model_choice=model_choice,
            enable_tavily=enable_tavily
        )

    with canvas_col:
        st.markdown("#### 🏨 Live Operations Canvas & Mirror")
        st.caption("Active property visualizer & live telemetry synchronized with StayEase AI operations.")

        tab_floor, tab_stays, tab_rev, tab_house, tab_pine = st.tabs([
            "🏢 60-Room Floor Plan",
            "🛎️ Live Stays & Checkout",
            "📊 Yield & Financials",
            "🧹 Housekeeping Queue",
            "🌲 Pinecone Knowledge Base"
        ])

        with tab_floor:
            render_floor_plan_panel(service=service)
        with tab_stays:
            render_checkout_panel(service=service)
        with tab_rev:
            render_owner_analytics_panel(service=service)
        with tab_house:
            render_housekeeping_panel(service=service)
        with tab_pine:
            render_vector_db_panel(vdb=vdb)

elif selected_panel == "🏢 60-Room Floor Plan & Folios":
    render_floor_plan_panel(service=service)

elif selected_panel == "💬 AI Operations Terminal":
    render_agent_terminal_panel(
        selected_role=selected_role,
        model_choice=model_choice,
        enable_tavily=enable_tavily
    )

elif selected_panel == "📊 Financial Yield & Night Audit":
    render_owner_analytics_panel(service=service)

elif selected_panel == "🌲 Pinecone Knowledge Base RAG":
    render_vector_db_panel(vdb=vdb)

# 9. Clean up any legacy injected elements safely
render_floating_ai_fab()
