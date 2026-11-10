from typing import Dict, Any
import streamlit as st
from app.frontend.components.icons import get_icon_b64

def render_kpi_cards(stats: Dict[str, Any]):
    """
    Renders executive KPI metric cards with prominent, luxury 44px Icons8 badge icons
    and high-contrast status values matching top-tier hospitality management suites.
    """
    tot_rooms = stats.get('total_rooms', 60)
    avail_cnt = stats.get('available_count', 0)
    occ_cnt = stats.get('occupied_count', 0)
    clean_cnt = stats.get('cleaning_count', 0)
    occ_pct = stats.get('occupancy_rate', 0.0)
    tot_rev = stats.get('total_revenue', 0.0)

    b64_inventory = get_icon_b64("building")
    b64_bed = get_icon_b64("bed")
    b64_user = get_icon_b64("user")
    b64_broom = get_icon_b64("broom")
    b64_graph = get_icon_b64("graph")
    b64_bill = get_icon_b64("money-bag")

    st.markdown(f"""<div class="kpi-container-light">

<!-- 1. Total Inventory -->
<div class="kpi-card-light kpi-accent-gold">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
    <div>
      <div class="kpi-label-light">TOTAL INVENTORY</div>
      <div class="kpi-value-light">{tot_rooms}</div>
      <div class="kpi-subtext-light">60 Units &bull; Floors 1, 2 &amp; 3</div>
    </div>
    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:12px; width:44px; height:44px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(245,158,11,0.15); flex-shrink:0;">
      <img src="{b64_inventory}" width="28" height="28" alt="Inventory"/>
    </div>
  </div>
</div>

<!-- 2. Vacant / Ready -->
<div class="kpi-card-light kpi-accent-green">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
    <div>
      <div class="kpi-label-light">VACANT / READY</div>
      <div class="kpi-value-light" style="color:#059669;">{avail_cnt}</div>
      <div class="kpi-subtext-light">Ready for Check-In</div>
    </div>
    <div style="background:#ecfdf5; border:1px solid #a7f3d0; border-radius:12px; width:44px; height:44px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(16,185,129,0.15); flex-shrink:0;">
      <img src="{b64_bed}" width="28" height="28" alt="Ready Bed"/>
    </div>
  </div>
</div>

<!-- 3. Occupied Stays -->
<div class="kpi-card-light kpi-accent-red">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
    <div>
      <div class="kpi-label-light">OCCUPIED STAYS</div>
      <div class="kpi-value-light" style="color:#dc2626;">{occ_cnt}</div>
      <div class="kpi-subtext-light">In-House Guests</div>
    </div>
    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:12px; width:44px; height:44px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(239,68,68,0.15); flex-shrink:0;">
      <img src="{b64_user}" width="28" height="28" alt="Guest"/>
    </div>
  </div>
</div>

<!-- 4. Housekeeping Queue -->
<div class="kpi-card-light kpi-accent-amber">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
    <div>
      <div class="kpi-label-light">HOUSEKEEPING</div>
      <div class="kpi-value-light" style="color:#d97706;">{clean_cnt}</div>
      <div class="kpi-subtext-light">Sanitization in Progress</div>
    </div>
    <div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:12px; width:44px; height:44px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(245,158,11,0.15); flex-shrink:0;">
      <img src="{b64_broom}" width="28" height="28" alt="Housekeeping"/>
    </div>
  </div>
</div>

<!-- 5. Live Occupancy -->
<div class="kpi-card-light kpi-accent-cyan">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
    <div>
      <div class="kpi-label-light">LIVE OCCUPANCY</div>
      <div class="kpi-value-light" style="color:#0284c7;">{occ_pct:.1f}%</div>
      <div class="kpi-subtext-light">{"Normal" if occ_pct < 90 else "⚠️ Peak"}</div>
    </div>
    <div style="background:#f0f9ff; border:1px solid #bae6fd; border-radius:12px; width:44px; height:44px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(2,132,199,0.15); flex-shrink:0;">
      <img src="{b64_graph}" width="28" height="28" alt="Occupancy Graph"/>
    </div>
  </div>
</div>

<!-- 6. Realized Revenue -->
<div class="kpi-card-light kpi-accent-blue">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:10px;">
    <div>
      <div class="kpi-label-light">REALIZED REVENUE</div>
      <div class="kpi-value-light" style="color:#2563eb;">₹{tot_rev:,.0f}</div>
      <div class="kpi-subtext-light">Invoiced to Date</div>
    </div>
    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; width:44px; height:44px; display:flex; align-items:center; justify-content:center; box-shadow:0 3px 8px rgba(37,99,235,0.15); flex-shrink:0;">
      <img src="{b64_bill}" width="28" height="28" alt="Revenue Folio"/>
    </div>
  </div>
</div>

</div>""", unsafe_allow_html=True)
