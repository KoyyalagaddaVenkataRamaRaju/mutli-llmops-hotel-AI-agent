import pandas as pd
import streamlit as st

from app.hotel.services import HotelService
from app.frontend.components.illustrations import get_undraw_dining_svg
from app.frontend.components.icons import get_icon_img

def render_room_service_panel(service: HotelService):
    """Renders 24/7 in-room dining, POS amenities catalog, and folio posting."""
    st.markdown(f'### {get_icon_img("restaurant", size=30)} Point of Sale &amp; In-Room Amenities', unsafe_allow_html=True)
    st.caption("Post charges for dining, beverages, express laundry, and wellness directly to guest folios.")

    service.reload_collections()
    srv_catalog = service.collections["service_prices"]

    sp1, sp2 = st.columns([1, 1], gap="large")

    with sp1:
        st.markdown(f'#### {get_icon_img("bill", size=22)} Post Service Charge to Room', unsafe_allow_html=True)
        conn = service.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT b.room_number, g.name AS guest_name
                FROM bookings b
                JOIN guests g ON b.guest_id = g.guest_id
                WHERE b.status = 'Active'
                ORDER BY b.room_number ASC
            """)
            active_guests = cursor.fetchall()
        finally:
            conn.close()

        if not active_guests:
            st.info("No active guests currently checked in.")
        else:
            room_map = {f"Room #{r['room_number']} - {r['guest_name']}": r['room_number'] for r in active_guests}
            pos_room_label = st.selectbox("Select Target Room:", list(room_map.keys()))
            pos_room = room_map[pos_room_label]

            srv_options = list(srv_catalog.keys()) + ["Custom Amenity / Special Request"]
            pos_service_name = st.selectbox("Amenity / Item:", srv_options)
            default_rate = srv_catalog.get(pos_service_name, 500.0)
            pos_cost = st.number_input("Amount to Post (₹):", min_value=50.0, max_value=50000.0, value=float(default_rate))

            if st.button("Post Charge to Folio", type="primary", use_container_width=True):
                try:
                    p_res = service.add_room_service(pos_room, pos_service_name, pos_cost)
                    st.success(f"✅ Posted **{p_res['service_name']}** (₹{p_res['cost']:,.2f}) to Room #{pos_room}!")
                except Exception as e:
                    st.error(f"Failed to post service charge: {str(e)}")

    with sp2:
        st.markdown(get_undraw_dining_svg(width=260, height=140), unsafe_allow_html=True)
        st.markdown("#### 📋 Standard Amenity Catalog")
        amenity_df = pd.DataFrame([
            {"Amenity Name": k, "Standard Rate": f"₹{v:,.2f}"}
            for k, v in srv_catalog.items()
        ])
        st.dataframe(amenity_df, use_container_width=True, hide_index=True)

