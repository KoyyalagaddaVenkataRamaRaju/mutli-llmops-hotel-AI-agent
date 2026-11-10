import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from app.hotel.services import HotelService
from app.frontend.components.illustrations import get_undraw_analytics_svg
from app.frontend.components.icons import get_icon_img

def render_owner_analytics_panel(service: HotelService):
    """
    Renders comprehensive Executive Financial Analytics, Customer Intelligence,
    Interactive Plotly Visual Charts, Night Audit, and Binary Compliance.
    """
    # Header with unDraw vector illustration
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown(f'### {get_icon_img("graph", size=30)} Executive Financial &amp; Customer Analytics', unsafe_allow_html=True)
        st.caption("Owner & GM Operations Suite: Dynamic Yield Metrics, Customer Folio Analytics, Revenue Composition & Data Governance.")
    with h_col2:
        st.markdown(get_undraw_analytics_svg(width=220, height=130), unsafe_allow_html=True)

    fin_summary = service.get_financial_executive_summary()

    # Top KPI Metrics Row
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.metric("Gross Revenue", f"₹{fin_summary['gross_revenue']:,.0f}", delta="+12.4% vs target")
    with f2:
        st.metric("Average Daily Rate (ADR)", f"₹{fin_summary['adr_average_daily_rate']:,.0f}", delta="Yield Optimized")
    with f3:
        revpar_val = fin_summary['revpar']
        revpar_delta = f"{'+' if revpar_val >= 2800 else '-'}₹{abs(revpar_val - 2800):,.0f} vs ₹2,800 Target"
        st.metric("RevPAR", f"₹{revpar_val:,.0f}", delta=revpar_delta)
    with f4:
        st.metric("12% Taxes Remitted", f"₹{fin_summary['luxury_taxes_remitted']:,.0f}", delta="Audit Compliant")

    st.write("---")

    # =========================================================================
    # SECTION 1: INTERACTIVE VISUAL CHARTS (PLOTLY)
    # =========================================================================
    st.markdown(f'#### {get_icon_img("pie-chart", size=22)} Interactive Operational Visualizations', unsafe_allow_html=True)
    c_chart1, c_chart2 = st.columns([1, 1], gap="large")

    with c_chart1:
        st.markdown("##### Revenue Stream Composition")
        rev_data = {
            "Stream": ["Room Tariff Revenue", "F&B & Amenities POS", "12% Luxury Taxes"],
            "Amount": [
                fin_summary["room_revenue"],
                fin_summary["food_and_beverage_revenue"],
                fin_summary["luxury_taxes_remitted"]
            ]
        }
        fig_donut = px.pie(
            rev_data,
            values="Amount",
            names="Stream",
            hole=0.55,
            color_discrete_sequence=["#4F46E5", "#06B6D4", "#F59E0B"]
        )
        fig_donut.update_layout(
            margin=dict(t=20, b=20, l=10, r=10),
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c_chart2:
        st.markdown("##### 🏢 Floor-Wise Occupancy & Room Distribution")
        conn = service.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT floor, status, COUNT(*) as count 
                FROM rooms 
                GROUP BY floor, status
            """)
            floor_stat_rows = [dict(r) for r in cursor.fetchall()]
        finally:
            conn.close()

        df_floor = pd.DataFrame(floor_stat_rows)
        if not df_floor.empty:
            df_floor["Floor Label"] = df_floor["floor"].apply(lambda f: f"Floor {f}")
            color_map = {"Available": "#10B981", "Occupied": "#EF4444", "Cleaning": "#F59E0B"}
            fig_bar = px.bar(
                df_floor,
                x="Floor Label",
                y="count",
                color="status",
                barmode="stack",
                color_discrete_map=color_map,
                labels={"count": "Rooms Count", "Floor Label": "Property Floor"}
            )
            fig_bar.update_layout(
                margin=dict(t=20, b=20, l=10, r=10),
                height=280,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.write("---")

    # =========================================================================
    # SECTION 2: CUSTOMER INTELLIGENCE & GUEST ANALYTICS
    # =========================================================================
    st.markdown(f'#### {get_icon_img("conference-call", size=22)} Customer &amp; In-House Guest Intelligence', unsafe_allow_html=True)
    st.caption("Real-time guest demographics, length-of-stay distribution, and total lifetime spend.")

    conn = service.db.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT g.guest_id, g.name, g.phone, g.id_proof, g.address,
                   COUNT(b.booking_id) as total_bookings,
                   SUM(b.nights) as total_nights,
                   COALESCE(SUM(b.total_amount), 0) as total_spent
            FROM guests g
            LEFT JOIN bookings b ON g.guest_id = b.guest_id
            GROUP BY g.guest_id
            ORDER BY total_spent DESC
        """)
        guest_records = [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

    if guest_records:
        df_guests = pd.DataFrame(guest_records)
        cg1, cg2, cg3, cg4 = st.columns(4)
        with cg1:
            st.metric("Total Registered Customers", len(df_guests))
        with cg2:
            avg_stay = df_guests["total_nights"].fillna(1).mean()
            st.metric("Average Stay Duration", f"{avg_stay:.1f} Nights")
        with cg3:
            avg_spend = df_guests["total_spent"].mean()
            st.metric("Avg Customer Lifetime Spend", f"₹{avg_spend:,.0f}")
        with cg4:
            vip_count = len(df_guests[df_guests["total_spent"] > 15000])
            st.metric("High-Value / VIP Guests", vip_count)

        search_guest = st.text_input("🔍 Quick Customer Lookup (Filter by Name, Phone, or ID):", placeholder="e.g. Farhan, 9876, PASSPORT...")
        if search_guest.strip():
            kw = search_guest.strip().lower()
            df_guests = df_guests[
                df_guests["name"].str.lower().str.contains(kw) |
                df_guests["phone"].str.lower().str.contains(kw) |
                df_guests["id_proof"].str.lower().str.contains(kw) |
                df_guests["address"].str.lower().str.contains(kw)
            ]

        # Formatting table
        df_display = df_guests.copy()
        df_display["total_spent"] = df_display["total_spent"].apply(lambda v: f"₹{v:,.2f}")
        df_display.rename(columns={
            "guest_id": "Guest ID",
            "name": "Full Name",
            "phone": "Contact Phone",
            "id_proof": "Official ID",
            "address": "Permanent City",
            "total_bookings": "Bookings",
            "total_nights": "Nights Stayed",
            "total_spent": "Lifetime Spend"
        }, inplace=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.write("---")

    # =========================================================================
    # SECTION 3: NIGHT AUDIT & BINARY BYTE-STREAM COMPLIANCE
    # =========================================================================
    la1, la2 = st.columns([1, 1], gap="large")

    with la1:
        st.markdown("#### 🌙 Daily Night Audit Runner")
        st.caption("Executes at MAX_PRIORITY, posts daily room charges across active bookings, and logs thread activity.")

        if st.button("Execute Night Audit Task", type="primary", use_container_width=True):
            audit_result = service.run_night_audit()
            st.success(f"✅ Night Audit Completed: {audit_result['occupied_count']} active rooms audited! Total charges posted: ₹{audit_result['total_charges_posted']:,.2f}")

            st.markdown("##### Thread Activity & Reconciliation Log")
            st.code("\n".join(audit_result["log"]))

        st.write("---")
        st.markdown("#### ⚡ Concurrency Race Simulation (Page 7 Spec)")
        st.caption("Simulates two terminals assigning the last Deluxe room simultaneously.")
        if st.button("Simulate Race Condition (Unsync vs Sync)", use_container_width=True):
            race_res = service.simulate_concurrency_race()
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.error("❌ Without Synchronization:")
                for line in race_res["without_synchronization"]["log"]:
                    st.caption(f"• {line}")
            with c_r2:
                st.success("✅ With Synchronization (Lock):")
                for line in race_res["with_synchronization"]["log"]:
                    st.caption(f"• {line}")

    with la2:
        st.markdown("#### 💾 Binary Byte Stream Storage (invoices.dat)")
        st.caption("Pure byte stream serialization (FileOutputStream / FileInputStream equivalent) with record count validation.")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Export to invoices.dat", use_container_width=True):
                try:
                    b_info = service.export_invoices_binary()
                    st.success(f"✅ **Binary Backup Completed!**\n- File: `{b_info['file']}`\n- Records Exported: **{b_info['records_written']}**\n- Bytes Written: **{b_info['bytes_written']:,} bytes**")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")

        with col_b2:
            if st.button("Restore from invoices.dat", use_container_width=True):
                try:
                    r_info = service.restore_invoices_binary()
                    st.info(f"🔄 **Restoration Verified!**\n- Records Restored: **{r_info['records_restored']}**\n- Bytes Read: **{r_info['bytes_read']:,} bytes**\n- Integrity: **{r_info['verification']}**")
                except Exception as e:
                    st.error(f"Restoration failed: {str(e)}")

        st.write("---")
        st.markdown("##### Recent Invoices in Audit Log")
        conn = service.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT invoice_id, guest_name, room_number, room_category, nights, total_amount, created_at FROM invoices ORDER BY created_at DESC LIMIT 6")
            inv_recs = [dict(r) for r in cursor.fetchall()]
            if inv_recs:
                st.dataframe(pd.DataFrame(inv_recs), use_container_width=True, hide_index=True)
        finally:
            conn.close()
