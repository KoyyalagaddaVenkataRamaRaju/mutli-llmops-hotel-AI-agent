import pandas as pd
import streamlit as st

from app.hotel.services import HotelService
from app.frontend.components.illustrations import get_undraw_housekeeping_svg
from app.frontend.components.icons import get_icon_img

def render_housekeeping_panel(service: HotelService):
    """Renders housekeeping staff allotment, real-time cleaning queue, and daemon worker thread simulation."""
    st.markdown(f'### {get_icon_img("broom", size=30)} Housekeeping Operations &amp; Staff Allotment', unsafe_allow_html=True)
    st.caption("Allot cleaning staff to released rooms, monitor turnaround, and track thread lifecycle states.")

    service.reload_collections()
    clean_queue = list(service.collections["housekeeping_queue"])

    hq_c1, hq_c2 = st.columns([1, 1], gap="large")

    with hq_c1:
        st.markdown(f'#### {get_icon_img("user", size=22)} Allot Housekeeping Staff to Room', unsafe_allow_html=True)
        with st.form("staff_allotment_form"):
            staff_rm = st.number_input("Target Room Number:", min_value=101, max_value=325, value=103)
            staff_name = st.selectbox("Assign Cleaning Personnel:", ["Housekeeper Ramesh", "Housekeeper Sunita", "Housekeeper Anand", "Supervisor Anita"])
            staff_role = st.selectbox("Staff Role:", ["Housekeeper", "Inspector", "Sanitization Specialist", "Supervisor"])

            allot_btn = st.form_submit_button("Allot Staff Member", use_container_width=True)

        if allot_btn:
            asgn = service.assign_housekeeping_staff(staff_rm, staff_name, staff_role)
            st.success(f"✅ **Staff Allotted!** {asgn['staff_name']} ({asgn['staff_role']}) assigned to Room #{staff_rm}. Assignment ID: `{asgn['assignment_id']}`")
            st.rerun()

        st.write("---")
        st.markdown(f"#### 🧼 Active Cleaning Queue ({len(clean_queue)} Rooms)")
        if not clean_queue:
            st.success("✨ Housekeeping Queue is clear. All rooms are clean and available.")
        else:
            for item in clean_queue:
                cat_name = item.__class__.__name__.replace("Room", "")
                q_r1, q_r2, q_r3 = st.columns([2, 2, 1])
                with q_r1:
                    st.markdown(f"**Room #{item.room_number}** &bull; {cat_name} (Floor {item.floor})")
                with q_r2:
                    st.markdown("<span style='color:#d97706; font-weight:700;'>🟡 Cleaning Required</span>", unsafe_allow_html=True)
                with q_r3:
                    if st.button("Mark Clean", key=f"btn_clean_{item.room_number}"):
                        service.mark_room_cleaned(item.room_number)
                        st.success(f"Room #{item.room_number} marked AVAILABLE!")
                        st.rerun()

    with hq_c2:
        st.markdown(get_undraw_housekeeping_svg(width=260, height=140), unsafe_allow_html=True)
        st.markdown("#### 📋 Active Staff Allotment Ledger")
        assignments = service.get_housekeeping_assignments()
        if assignments:
            st.dataframe(pd.DataFrame(assignments), use_container_width=True, hide_index=True)
        else:
            st.info("No staff assignments recorded yet.")

        st.write("---")
        st.markdown("#### ⚙️ Background Daemon Worker Thread")
        if st.button("Launch Background Housekeeper Thread", use_container_width=True):
            launch_msg = service.start_housekeeping_thread_worker()
            st.info(launch_msg)

        thread_ref = service.housekeeper_thread
        if thread_ref and thread_ref.is_alive():
            st.success("Thread State: **RUNNABLE (Daemon)**")
            if hasattr(thread_ref, "activity_log") and thread_ref.activity_log:
                st.code("\n".join(thread_ref.activity_log[-5:]))
        else:
            st.info("Thread State: **INACTIVE / ON STANDBY**")

