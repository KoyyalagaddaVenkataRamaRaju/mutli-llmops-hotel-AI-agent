import pandas as pd
import streamlit as st

from app.hotel.services import HotelService
from app.frontend.components.illustrations import get_undraw_maintenance_svg
from app.frontend.components.icons import get_icon_img

def render_maintenance_panel(service: HotelService):
    """Renders engineering & maintenance tickets dispatch and resolution."""
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f'### {get_icon_img("wrench", size=30)} Hotel Engineering &amp; Maintenance Tickets', unsafe_allow_html=True)
        st.caption("Report and resolve room engineering tickets (AC, Plumbing, Electrical, Carpentry) to maintain 5-star standards.")
    with h_col2:
        st.markdown(get_undraw_maintenance_svg(width=220, height=120), unsafe_allow_html=True)

    m_col1, m_col2 = st.columns([1, 1], gap="large")

    with m_col1:
        st.markdown(f'#### {get_icon_img("wrench", size=22)} Report Maintenance Issue', unsafe_allow_html=True)
        with st.form("maintenance_form"):
            m_room = st.number_input("Room Number with Issue:", min_value=101, max_value=325, value=207)
            m_cat = st.selectbox("Issue Category:", ["Air Conditioning (HVAC)", "Plumbing & Bath", "Electrical & Lighting", "Carpentry & Furniture", "Electronics / TV"])
            m_desc = st.text_area("Issue Description:", value="AC unit not cooling effectively, slight water leakage from vent.")
            m_by = st.selectbox("Reported By:", ["Housekeeping Staff", "Front Desk Receptionist", "Guest Complaint", "Maintenance Inspection"])

            report_btn = st.form_submit_button("Log Maintenance Ticket", use_container_width=True)

        if report_btn:
            t = service.report_maintenance_ticket(m_room, m_cat, m_desc, m_by)
            st.success(f"✅ **Ticket Logged!** Ticket ID: `{t['ticket_id']}` for Room #{t['room_number']}. Status: Open.")
            st.rerun()

    with m_col2:
        st.markdown("#### 📋 Open Maintenance Tickets")
        tickets = service.get_maintenance_tickets()
        if tickets:
            df_t = pd.DataFrame(tickets)
            st.dataframe(df_t[["ticket_id", "room_number", "category", "description", "status"]], use_container_width=True, hide_index=True)

            st.write("---")
            st.markdown("##### Resolve Ticket")
            open_tickets = [t["ticket_id"] for t in tickets if t["status"] == "Open"]
            if open_tickets:
                res_tid = st.selectbox("Select Ticket to Mark Resolved:", open_tickets)
                if st.button("Mark Ticket Resolved", type="primary", use_container_width=True):
                    service.resolve_maintenance_ticket(res_tid)
                    st.success(f"Ticket `{res_tid}` marked RESOLVED!")
                    st.rerun()
            else:
                st.success("✨ All maintenance tickets are resolved!")
        else:
            st.info("No maintenance tickets on record.")

