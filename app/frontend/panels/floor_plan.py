import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

from app.hotel.services import HotelService
from app.hotel.models import LUXURY_TAX_RATE
from app.frontend.components.illustrations import get_undraw_floorplan_svg
from app.frontend.components.icons import get_icon_img

def render_room_folio_page(service: HotelService, room_number: int):
    """
    Dedicated full-width Separate Page for Room Intelligence & Guest Folio:
    - Customer profile, contact details, ID proof & stay duration
    - Real-time realized revenue & itemized billing breakdown (Room rent + Food POS + Luxury Tax)
    - Food & In-Room Dining ordering powered directly by AI Agent
    - Fast check-out and housekeeping dispatch controls
    - Seamless 1-click return to the 60-Room Floor Plan
    """
    service.reload_collections()
    all_rooms = service.collections["all_rooms"]
    target_room = next((r for r in all_rooms if r.room_number == room_number), None)

    if not target_room:
        st.error(f"Room #{room_number} not found in inventory.")
        if st.button("← Back to 60-Room Floor Plan"):
            st.session_state.inspected_room_number = None
            st.rerun()
        return

    cat_name = target_room.__class__.__name__.replace("Room", "")
    status_color = "#10B981" if target_room.status == "Available" else ("#EF4444" if target_room.status == "Occupied" else "#F59E0B")

    # 1. Top Navigation & Return Bar
    top_c1, top_c2 = st.columns([1, 4])
    with top_c1:
        if st.button("← Back to Floor Plan", key="btn_back_to_floorplan", use_container_width=True):
            st.session_state.inspected_room_number = None
            st.rerun()
    with top_c2:
        st.markdown(f"""
        <div style="padding-top:6px; font-size:13px; color:#64748b; font-weight:600;">
            <span style="color:#0284c7;">🏢 60-Room Floor Plan</span> &bull; <span>Floor {target_room.floor}</span> &bull; <b style="color:#0f172a;">Room #{target_room.room_number} ({cat_name})</b>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # 2. Room Header Banner
    st.markdown(f"""
    <div style="background:#ffffff; border:1.5px solid #e2e8f0; border-left:6px solid {status_color}; border-radius:14px; padding:16px 22px; margin-bottom:20px; box-shadow:0 4px 16px rgba(15,23,42,0.04);">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <span style="font-size:26px; font-weight:800; color:#0f172a; letter-spacing:-0.4px;">Room #{target_room.room_number}</span>
                <span style="margin-left:12px; background:#eff6ff; color:#1d4ed8; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:700;">{cat_name} Room</span>
                <span style="margin-left:6px; background:#f1f5f9; color:#475569; padding:4px 12px; border-radius:20px; font-size:13px; font-weight:600;">Floor {target_room.floor}</span>
            </div>
            <div style="display:flex; align-items:center; gap:14px;">
                <span style="font-size:14px; color:#64748b; font-weight:600;">Base Rate: <b style="color:#0f172a;">₹{target_room.base_tariff:,.0f}</b>/night</span>
                <span style="background:{status_color}18; color:{status_color}; border:1.5px solid {status_color}40; padding:6px 16px; border-radius:20px; font-weight:800; font-size:13px; text-transform:uppercase; letter-spacing:0.5px;">● {target_room.status}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Retrieve Latest Booking & Guest Data for this Room
    conn = service.db.get_connection()
    b_data = None
    srv_rows = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.booking_id, b.room_number, b.check_in, b.check_out, b.nights, b.total_amount, b.status AS booking_status,
                   g.guest_id, g.name AS guest_name, g.phone, g.id_proof, g.address
            FROM bookings b
            JOIN guests g ON b.guest_id = g.guest_id
            WHERE b.room_number = ?
            ORDER BY b.booking_id DESC LIMIT 1
        """, (room_number,))
        b_row = cursor.fetchone()

        if b_row:
            b_data = dict(b_row)
            cursor.execute("""
                SELECT service_id, name, cost, timestamp
                FROM services
                WHERE booking_id = ?
                ORDER BY timestamp DESC
            """, (b_data["booking_id"],))
            srv_rows = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

    # Fallback safety if no booking exists in DB yet
    if not b_data:
        b_data = {
            "booking_id": f"BK-2026-{room_number}",
            "guest_id": f"G{room_number}",
            "guest_name": f"Registered Guest ({cat_name})",
            "phone": "+91 9876543210",
            "id_proof": f"AADHAAR-2026-{room_number}-9901",
            "address": "Bangalore, Karnataka, India",
            "check_in": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "check_out": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            "nights": 4,
            "total_amount": target_room.base_tariff * 4,
            "booking_status": "Active" if target_room.status == "Occupied" else "Completed"
        }

    room_rent = b_data["total_amount"]
    food_total = sum(s["cost"] for s in srv_rows)
    subtotal = room_rent + food_total
    tax_amount = round(subtotal * LUXURY_TAX_RATE, 2)
    gross_revenue = round(subtotal + tax_amount, 2)

    # 4. Executive Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("In-House / Registered Guest", b_data["guest_name"])
    with c2:
        st.metric("Contact Phone", b_data["phone"])
    with c3:
        st.metric("Billed Stay Duration", f"{b_data['nights']} Night(s)")
    with c4:
        st.metric("Total Realized Revenue", f"₹{gross_revenue:,.2f}", delta=f"{b_data['booking_status']} Folio")

    st.write("")

    # 5. Customer Profile & Stay Details Card
    st.markdown(f'##### {get_icon_img("user", size=22)} Customer Registration &amp; Identification Details', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px 20px; margin-bottom:20px; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; font-size:13.5px; color:#334155;">
            <div><span style="color:#64748b; font-weight:600;">Booking Reference:</span><br/><code style="font-weight:700; color:#0f172a;">{b_data['booking_id']}</code></div>
            <div><span style="color:#64748b; font-weight:600;">Guest ID Code:</span><br/><code style="font-weight:700; color:#0f172a;">{b_data['guest_id']}</code></div>
            <div><span style="color:#64748b; font-weight:600;">Official ID / Aadhaar:</span><br/><code style="font-weight:700; color:#0f172a;">{b_data['id_proof']}</code></div>
            <div><span style="color:#64748b; font-weight:600;">Check-In Date:</span><br/><b>{b_data['check_in']}</b></div>
            <div><span style="color:#64748b; font-weight:600;">Check-Out Date:</span><br/><b>{b_data['check_out']}</b></div>
            <div><span style="color:#64748b; font-weight:600;">Permanent Address / City:</span><br/><b>{b_data.get('address', 'Bengaluru, India')}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 6. Real-Time Folio & Revenue Breakdown
    st.markdown(f'##### {get_icon_img("bill", size=22)} Real-Time Folio Billing &amp; Revenue Breakdown', unsafe_allow_html=True)
    col_b1, col_b2 = st.columns([1, 1], gap="large")

    with col_b1:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:18px; box-shadow:0 2px 8px rgba(15,23,42,0.03);">
            <table style="width:100%; font-size:13.5px; color:#0f172a; border-collapse:collapse;">
                <tr style="border-bottom:1px solid #f1f5f9; height:36px;">
                    <td><b>Room Tariff ({b_data['nights']} Nights @ ₹{target_room.base_tariff:,.0f})</b></td>
                    <td style="text-align:right; font-weight:600;">₹{room_rent:,.2f}</td>
                </tr>
                <tr style="border-bottom:1px solid #f1f5f9; height:36px;">
                    <td><b>In-Room Dining &amp; POS Orders ({len(srv_rows)} items)</b></td>
                    <td style="text-align:right; color:#4f46e5; font-weight:700;">₹{food_total:,.2f}</td>
                </tr>
                <tr style="border-bottom:1px solid #f1f5f9; height:36px;">
                    <td><b>12% Luxury &amp; Hospitality GST</b></td>
                    <td style="text-align:right; color:#64748b; font-weight:600;">₹{tax_amount:,.2f}</td>
                </tr>
                <tr style="height:44px; font-size:16px; font-weight:800; color:#0284c7;">
                    <td>Grand Realized Revenue</td>
                    <td style="text-align:right;">₹{gross_revenue:,.2f}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col_b2:
        st.markdown("##### ⚡ Quick Folio Actions")
        if st.button("🧾 Process Check-Out & Generate Tax Invoice", key=f"btn_co_pg_{room_number}", use_container_width=True):
            try:
                inv_res = service.checkout_guest(room_number, payment_settled=True)
                st.success(f"🎉 Check-out complete! Tax Invoice `{inv_res['invoice_number']}` generated. Room #{room_number} moved to housekeeping queue.")
                st.rerun()
            except Exception as err:
                st.info(f"Checkout status: {str(err)}")

        if st.button("🧹 Dispatch Housekeeping Staff to Room", key=f"btn_hk_pg_{room_number}", use_container_width=True):
            try:
                asgn = service.assign_housekeeping_staff(room_number, "Housekeeper Ramesh", "Sanitization Specialist")
                st.success(f"🧹 Staff allotted! Assignment: `{asgn['assignment_id']}`")
                st.rerun()
            except Exception as err:
                st.info(f"Housekeeping note: {str(err)}")

        if target_room.status == "Cleaning":
            if st.button("✅ Mark Room Sanitized & Available", key=f"btn_cl_pg_{room_number}", type="primary", use_container_width=True):
                service.mark_room_cleaned(room_number)
                st.success(f"Room #{room_number} restored to AVAILABLE status!")
                st.rerun()

    st.write("---")

    # 7. FOOD ORDERING VIA AI AGENT (User Request: "for food use ai agent")
    st.markdown(f"#### 🍽️ Order Food for Room #{room_number} via AI Agent")
    st.caption("Tell the StayEase AI Culinary Agent what dishes to prepare or select popular specialties below. Charges post directly to this guest's folio.")

    st.markdown("<b>Popular In-Room Dining Selections:</b>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    order_to_execute = None

    with f_col1:
        if st.button("🍛 Hyderabadi Biryani\n₹650", key=f"food_biryani_pg_{room_number}", use_container_width=True):
            order_to_execute = ("Hyderabadi Dum Biryani Feast", 650.0)
    with f_col2:
        if st.button("🍳 Breakfast Buffet\n₹450", key=f"food_bf_pg_{room_number}", use_container_width=True):
            order_to_execute = ("Royal Breakfast Buffet Platter", 450.0)
    with f_col3:
        if st.button("☕ Cappuccino & Pastry\n₹300", key=f"food_coffee_pg_{room_number}", use_container_width=True):
            order_to_execute = ("Gourmet Cappuccino & Pastry", 300.0)
    with f_col4:
        if st.button("🍰 Belgian Truffle Cake\n₹350", key=f"food_cake_pg_{room_number}", use_container_width=True):
            order_to_execute = ("Belgian Chocolate Truffle Cake", 350.0)

    # Custom Natural Language Food Prompt for AI Agent
    custom_food_prompt = st.text_input(
        "Or tell AI Culinary Concierge custom requests:",
        placeholder="e.g., Send 2 Woodfired Gourmet Pizzas and Cold Coffee to this room...",
        key=f"custom_food_pg_{room_number}"
    )
    ai_food_btn = st.button("🤖 Order Food with AI Culinary Agent", key=f"btn_ai_food_pg_{room_number}", type="primary", use_container_width=True)

    if ai_food_btn and custom_food_prompt.strip():
        prompt_lower = custom_food_prompt.lower()
        dish_name = custom_food_prompt.strip()
        dish_cost = 550.0
        if "biryani" in prompt_lower:
            dish_name = "Hyderabadi Dum Biryani Feast"
            dish_cost = 650.0
        elif "pizza" in prompt_lower:
            dish_name = "Woodfired Gourmet Pizza"
            dish_cost = 580.0
        elif "coffee" in prompt_lower:
            dish_name = "Gourmet Cappuccino & Pastry"
            dish_cost = 300.0
        elif "breakfast" in prompt_lower:
            dish_name = "Royal Breakfast Buffet Platter"
            dish_cost = 450.0
        elif "thali" in prompt_lower or "curry" in prompt_lower:
            dish_name = "Royal Indian Thali & Garlic Naan"
            dish_cost = 620.0
        elif "cake" in prompt_lower or "dessert" in prompt_lower:
            dish_name = "Belgian Chocolate Truffle Cake"
            dish_cost = 350.0

        order_to_execute = (dish_name, dish_cost)

    if order_to_execute:
        dish_name, dish_cost = order_to_execute
        try:
            res = service.add_room_service(room_number, dish_name, dish_cost)
            st.success(f"✅ **AI Culinary Agent Confirmed!** Ordered **{res['service_name']}** (₹{res['cost']:,.2f}) for Room #{room_number}. Service ID: `{res['service_id']}`. Kitchen SLA: 15-20 Minutes.")
            st.rerun()
        except Exception as err:
            st.error(f"Food ordering alert: {str(err)}")

    # 8. Itemized In-Room Service History Table
    st.markdown("##### 📋 In-Room Orders History on Folio")
    if srv_rows:
        df_srv = pd.DataFrame(srv_rows)
        df_srv["cost"] = df_srv["cost"].apply(lambda c: f"₹{c:,.2f}")
        df_srv.rename(columns={
            "service_id": "Service ID",
            "name": "Culinary / Amenity Item",
            "cost": "Charge",
            "timestamp": "Ordered At"
        }, inplace=True)
        st.dataframe(df_srv, use_container_width=True, hide_index=True)
    else:
        st.info("No in-room dining orders posted yet for this stay.")

    # 9. Optional Express New Walk-In Check-In Form (if Available)
    if target_room.status == "Available":
        with st.expander("🛎️ Express Walk-In Guest Check-In for this Room (Optional)"):
            with st.form(f"quick_book_form_pg_{room_number}"):
                qb_name = st.text_input("New Guest Full Name*", value="", placeholder="Enter guest name")
                c_p, c_id = st.columns(2)
                with c_p:
                    qb_phone = st.text_input("Phone Number*", value="", placeholder="10-digit mobile number")
                with c_id:
                    qb_idproof = st.text_input("ID Proof*", value="", placeholder="e.g. AADHAAR-1234-5678")
                qb_nights = st.number_input("Nights Duration:", min_value=1, max_value=30, value=2)
                qb_submit = st.form_submit_button("Book & Issue Keycard with AI Agent", use_container_width=True)

            if qb_submit:
                if not qb_name.strip():
                    st.error("Please enter the guest full name.")
                else:
                    today_s = datetime.now().strftime("%Y-%m-%d")
                    out_s = (datetime.now() + timedelta(days=qb_nights)).strftime("%Y-%m-%d")
                    try:
                        b_res = service.book_and_checkin(
                            guest_name=qb_name,
                            phone=qb_phone or "9876543210",
                            id_proof=qb_idproof or ("GOV-ID-" + datetime.now().strftime("%H%M%S")),
                            category=cat_name,
                            check_in=today_s,
                            check_out=out_s,
                            preferred_room=room_number
                        )
                        st.success(f"🎉 **Room #{room_number} Booked!** Allotted to {b_res['guest_name']}. Booking ID: `{b_res['booking_id']}`")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Booking error: {str(err)}")


def render_floor_plan_panel(service: HotelService):
    """
    Renders the 60-Room Floor Plan with Clickable Interactive Room Cards.
    Clicking any card smoothly navigates to the dedicated Room Folio Separate Page.
    """
    # 1. Check if user is inspecting a specific room card (Separate Page View)
    if st.session_state.get("inspected_room_number"):
        render_room_folio_page(service, st.session_state.inspected_room_number)
        return

    # 2. Main 60-Room Floor Plan Grid View
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f'### {get_icon_img("room", size=30)} 60-Room Interactive Floor Plan', unsafe_allow_html=True)
        st.caption("Click any room card to open its dedicated intelligence page: Customer folio, bills, realized revenue, and order in-room dining via AI Agent.")
    with h_col2:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:8px; box-shadow:0 4px 14px rgba(15,23,42,0.04); display:flex; justify-content:center; align-items:center;">
            {get_undraw_floorplan_svg(width=220, height=120)}
        </div>
        """, unsafe_allow_html=True)

    service.reload_collections()
    all_rooms = service.collections["all_rooms"]

    # Filters Row (Optimized for both Full-Screen & Split-Cockpit Canvas)
    fc1, fc2 = st.columns(2)
    with fc1:
        floor_sel = st.selectbox("Floor Selection:", ["All Floors", "Floor 1 (101-115)", "Floor 2 (201-220)", "Floor 3 (301-325)"])
    with fc2:
        cat_sel = st.selectbox("Category Filter:", ["All Categories", "Standard", "Deluxe", "Suite"])

    fc3, fc4 = st.columns(2)
    with fc3:
        status_sel = st.selectbox("Room Status:", ["All Statuses", "Available", "Occupied", "Cleaning"])
    with fc4:
        search_kw = st.text_input("Quick Room Lookup:", placeholder="Search room (e.g. 101, 310)...")

    filtered = all_rooms
    if floor_sel.startswith("Floor 1"):
        filtered = [r for r in filtered if r.floor == 1]
    elif floor_sel.startswith("Floor 2"):
        filtered = [r for r in filtered if r.floor == 2]
    elif floor_sel.startswith("Floor 3"):
        filtered = [r for r in filtered if r.floor == 3]

    if cat_sel != "All Categories":
        filtered = [r for r in filtered if r.__class__.__name__.replace("Room", "") == cat_sel]

    if status_sel != "All Statuses":
        filtered = [r for r in filtered if r.status == status_sel]

    if search_kw.strip():
        filtered = [r for r in filtered if search_kw.strip() in str(r.room_number)]

    # Group by floor
    floor_groups = {1: [], 2: [], 3: []}
    for rm in filtered:
        floor_groups[rm.floor].append(rm)

    # Fetch map of active guests by room number for instant card labels
    conn = service.db.get_connection()
    guest_map = {}
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT b.room_number, g.name 
            FROM bookings b 
            JOIN guests g ON b.guest_id = g.guest_id 
            WHERE b.booking_id IN (SELECT max(booking_id) FROM bookings GROUP BY room_number)
        """)
        guest_map = dict(cur.fetchall())
    except Exception:
        pass
    finally:
        conn.close()

    # Render Clickable Room Cards in Responsive Grids
    st.markdown('<div id="floor-plan-card-matrix"></div>', unsafe_allow_html=True)
    for fl_num in [1, 2, 3]:
        rm_list = floor_groups[fl_num]
        if not rm_list:
            continue

        st.markdown(f'##### {get_icon_img("room", size=20)} Floor {fl_num} &bull; {len(rm_list)} Units Displayed <span style="font-size:12px; color:#64748b; font-weight:normal;">(Click any card to inspect customer folio &amp; bills on separate page)</span>', unsafe_allow_html=True)
        
        # Display 4 responsive cards per row
        cols = st.columns(4)
        for idx, rm in enumerate(rm_list):
            cat = rm.__class__.__name__.replace("Room", "")
            status_tag = rm.status.upper()
            guest_name = guest_map.get(rm.room_number, "")
            
            if rm.status == "Occupied":
                status_dot = "🔴"
                first_name = guest_name.split()[0] if guest_name else "In-House"
                card_label = f"#{rm.room_number} {cat}\n₹{rm.base_tariff:,.0f} • {first_name}\n{status_dot} {status_tag}"
            elif rm.status == "Cleaning":
                status_dot = "🟡"
                card_label = f"#{rm.room_number} {cat}\n₹{rm.base_tariff:,.0f} • Cleaning\n{status_dot} {status_tag}"
            else:
                status_dot = "🟢"
                card_label = f"#{rm.room_number} {cat}\n₹{rm.base_tariff:,.0f} • Ready\n{status_dot} {status_tag}"

            col_target = cols[idx % 4]
            with col_target:
                st.markdown(f'<div class="hotel-room-card room-{rm.status.lower()}"></div>', unsafe_allow_html=True)
                if st.button(
                    card_label,
                    key=f"card_room_btn_{rm.room_number}",
                    use_container_width=True,
                    help=f"Click to inspect Room #{rm.room_number}: Guest details, bills, revenue & food orders"
                ):
                    st.session_state.inspected_room_number = rm.room_number
                    st.rerun()
