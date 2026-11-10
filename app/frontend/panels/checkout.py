import pandas as pd
import streamlit as st

from app.hotel.services import HotelService
from app.hotel.models import PaymentPendingException
from app.frontend.components.illustrations import get_undraw_checkout_svg
from app.frontend.components.icons import get_icon_img

def render_checkout_panel(service: HotelService):
    """Renders in-house guest folios, settlement verification, and itemized invoice generation."""
    c_h1, c_h2 = st.columns([3, 1])
    with c_h1:
        st.markdown(f'### {get_icon_img("bill", size=30)} In-House Guest Directory &amp; Checkout Folios', unsafe_allow_html=True)
        st.caption("Active guest folios with 1-click invoice settlement and departure processing.")
    with c_h2:
        st.markdown(get_undraw_checkout_svg(width=220, height=120), unsafe_allow_html=True)

    conn = service.db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, b.room_number, r.category, g.guest_id, g.name AS guest_name,
                   b.check_in, b.check_out, b.nights
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            JOIN rooms r ON b.room_number = r.room_number
            WHERE b.status = 'Active'
            ORDER BY b.room_number ASC
        """)
        inhouse_data = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

    if not inhouse_data:
        st.info("No guests currently in-house.")
    else:
        table_rows = []
        for r in inhouse_data:
            table_rows.append({
                "Room": f"#{r['room_number']}",
                "Category": r['category'],
                "Guest Name": r['guest_name'],
                "Nights": r['nights'],
                "Check-In": r['check_in']
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        st.write("---")
        st.markdown(f'#### {get_icon_img("money-bag", size=22)} Process Departure &amp; Generate Final Invoice', unsafe_allow_html=True)
        c_out1, c_out2 = st.columns([1, 1], gap="large")
        with c_out1:
            checkout_room_pick = st.selectbox(
                "Select Room for Departure:",
                [r['room_number'] for r in inhouse_data],
                format_func=lambda x: f"Room #{x}"
            )
            settled_check = st.checkbox("Mark Folio Balance as Settled at Front Desk", value=True)

            if st.button("Generate Invoice & Depart Guest", type="primary", use_container_width=True):
                try:
                    out_res = service.checkout_guest(checkout_room_pick, payment_settled=settled_check)
                    st.success(f"✅ Check-out recorded for Room #{checkout_room_pick}! Room sent to Housekeeping Queue.")
                    st.session_state["last_invoice"] = out_res
                except PaymentPendingException as ppe:
                    st.error(f"🛑 **SETTLEMENT BLOCKED:** {str(ppe)}")
                except Exception as e:
                    st.error(f"Checkout error: {str(e)}")

        with c_out2:
            if "last_invoice" in st.session_state:
                inv = st.session_state["last_invoice"]
                st.markdown("##### 📄 Official Check-Out Invoice")
                st.markdown(f'<div class="invoice-box-light">{inv["invoice_text"]}</div>', unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Official Invoice (.txt)",
                    data=inv["invoice_text"],
                    file_name=f"Invoice_{inv['invoice_id']}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

