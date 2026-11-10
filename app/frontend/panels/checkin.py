from datetime import datetime, timedelta
import streamlit as st

from app.hotel.services import HotelService
from app.frontend.components.illustrations import get_undraw_booking_svg
from app.frontend.components.icons import get_icon_img
from app.hotel.models import (
    LUXURY_TAX_RATE, WEEKEND_SURCHARGE_RATE, LONG_STAY_DISCOUNT_RATE,
    RoomNotAvailableException, InvalidStayPeriodException, BlacklistedGuestException
)

def render_checkin_panel(service: HotelService):
    """Renders Front Desk express check-in, dynamic tariff computation, and atomic room allotment."""
    st.markdown(f'### {get_icon_img("service-bell", size=30)} Express Guest Registration &amp; Check-In', unsafe_allow_html=True)
    st.caption("Atomic room allocation prevents double-booking. Security blacklist validation enforced.")

    col_in1, col_in2 = st.columns([1, 1], gap="large")

    with col_in1:
        with st.form("light_checkin_form"):
            st.markdown(f'#### {get_icon_img("user", size=22)} Guest Folio Registration', unsafe_allow_html=True)
            ci_name = st.text_input("Guest Full Name*", value="", placeholder="Enter guest full name (e.g., Rajesh Kumar)")
            c_p, c_id = st.columns(2)
            with c_p:
                ci_phone = st.text_input("Phone Number*", value="", placeholder="10-digit mobile (e.g., 9876543210)")
            with c_id:
                ci_idproof = st.text_input("Official ID Proof*", value="", placeholder="e.g. AADHAAR-1234-5678 or PASSPORT")

            ci_addr = st.text_input("Permanent Address / City", value="", placeholder="e.g. Bangalore, Karnataka")

            c_cat, c_nt = st.columns(2)
            with c_cat:
                ci_category = st.selectbox("Room Category:", ["Standard", "Deluxe", "Suite"], index=1)
            with c_nt:
                ci_nights = st.number_input("Stay Duration (Nights):", min_value=1, max_value=30, value=3)

            c_d1, c_d2 = st.columns(2)
            t_today = datetime.now().date()
            with c_d1:
                ci_checkin = st.date_input("Check-In Date:", value=t_today)
            with c_d2:
                ci_checkout = st.date_input("Check-Out Date:", value=t_today + timedelta(days=ci_nights))

            has_wknd = any((ci_checkin + timedelta(days=i)).weekday() in (5, 6) for i in range(ci_nights))
            base_rate = 2500.0 if ci_category == "Standard" else (4200.0 if ci_category == "Deluxe" else 7800.0)
            wknd_multiplier = (1.0 + WEEKEND_SURCHARGE_RATE) if has_wknd else 1.0
            calc_room = base_rate * wknd_multiplier * ci_nights
            if ci_nights >= 7:
                calc_room *= (1.0 - LONG_STAY_DISCOUNT_RATE)
            tax_val = calc_room * LUXURY_TAX_RATE
            total_preview = calc_room + tax_val

            st.markdown(f"""<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; margin: 12px 0;">
<div style="font-size:11px; color:#64748b; font-weight:700; text-transform:uppercase;">Rate Calculation Summary</div>
<div style="font-size:13px; color:#0f172a; margin-top:4px;">
Base Rate: <b>₹{base_rate:,.0f}</b>/night &bull; Weekend Surcharge: <b>{'+15%' if has_wknd else 'No'}</b><br>
Room Charges: <b>₹{calc_room:,.2f}</b> &bull; Luxury Tax (12%): <b>₹{tax_val:,.2f}</b><br>
<span style="font-size:16px; font-weight:800; color:#0284c7;">Estimated Total: ₹{total_preview:,.2f}</span>
</div>
</div>""", unsafe_allow_html=True)

            checkin_submit = st.form_submit_button("Confirm Reservation & Issue Room", use_container_width=True)

        if checkin_submit:
            try:
                b_res = service.book_and_checkin(
                    guest_name=ci_name,
                    phone=ci_phone,
                    id_proof=ci_idproof,
                    category=ci_category,
                    check_in=str(ci_checkin),
                    check_out=str(ci_checkout),
                    address=ci_addr
                )
                st.success(f"🎉 **Check-In Confirmed!** Room **#{b_res['room_number']}** ({b_res['category']}) allotted to **{b_res['guest_name']}**. Booking ID: `{b_res['booking_id']}`")
                st.rerun()
            except BlacklistedGuestException as bge:
                st.error(f"🛑 **SECURITY BLOCK:** {str(bge)}")
            except RoomNotAvailableException as rne:
                st.warning(f"⚠️ {str(rne)}")
            except InvalidStayPeriodException as ispe:
                st.error(f"⚠️ {str(ispe)}")
            except Exception as e:
                st.error(f"Check-In failure: {str(e)}")

    with col_in2:
        st.markdown(get_undraw_booking_svg(width=260, height=140), unsafe_allow_html=True)
        st.markdown("#### 📜 Room Category Guidelines")
        st.markdown("""<div class="official-action-card">
<h5 style="color:#0f172a; margin:0 0 8px 0;">Standard Room (₹2,500/night)</h5>
<p style="font-size:12px; color:#64748b; margin:0 0 14px 0;">Queen bed, ensuite bathroom, high-speed Wi-Fi, writing desk. Floors 1 &amp; 2.</p>

<h5 style="color:#0f172a; margin:0 0 8px 0;">Deluxe Room (₹4,200/night)</h5>
<p style="font-size:12px; color:#64748b; margin:0 0 14px 0;">King-size bed, private scenic balcony, minibar &amp; 24/7 room service capability. Floors 2 &amp; 3.</p>

<h5 style="color:#0f172a; margin:0 0 8px 0;">Presidential Suite (₹7,800/night)</h5>
<p style="font-size:12px; color:#64748b; margin:0;">Master bedroom, executive living lounge, jacuzzi bath &amp; dedicated 24/7 butler service. Floor 3.</p>
</div>""", unsafe_allow_html=True)

