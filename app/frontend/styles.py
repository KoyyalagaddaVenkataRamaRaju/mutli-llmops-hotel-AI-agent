import streamlit as st

def apply_custom_styles():
    """Applies the executive light luxury styling system and custom typography."""
    st.markdown("""<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* =========================================================================
       1. GLOBAL LIGHT THEME FOUNDATION
       ========================================================================= */
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* =========================================================================
       1. STREAMLIT HEADER & SIDEBAR TOGGLE BUTTONS
       ========================================================================= */
    [data-testid="stHeader"] {
        background: transparent !important;
        pointer-events: none !important;
        z-index: 100000 !important;
        height: 3.5rem !important;
    }

    [data-testid="stHeader"] * {
        pointer-events: auto !important;
    }

    /* Streamlit Sidebar Expand Toggle Button (When Sidebar is Collapsed) */
    [data-testid="stExpandSidebarButton"],
    [data-testid="collapsedControl"],
    button[aria-label="Expand sidebar"] {
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        border: 2px solid #ffffff !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 16px rgba(79, 70, 229, 0.45) !important;
        padding: 6px 12px !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        z-index: 9999999 !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stExpandSidebarButton"]:hover,
    [data-testid="collapsedControl"]:hover,
    button[aria-label="Expand sidebar"]:hover {
        background: #4338ca !important;
        color: #ffffff !important;
        transform: scale(1.08) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.55) !important;
    }

    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="collapsedControl"] svg,
    button[aria-label="Expand sidebar"] svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    [data-testid="stExpandSidebarButton"]:hover svg,
    [data-testid="collapsedControl"]:hover svg,
    button[aria-label="Expand sidebar"]:hover svg {
        fill: #ffffff !important;
        stroke: #ffffff !important;
    }

    /* Streamlit Sidebar Collapse Button (When Sidebar is Open) */
    [data-testid="stSidebarCollapseButton"],
    button[aria-label="Collapse sidebar"] {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #f1f5f9 !important;
        border: 1.5px solid #cbd5e1 !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        z-index: 100003 !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover,
    button[aria-label="Collapse sidebar"]:hover {
        background: #fee2e2 !important;
        border-color: #ef4444 !important;
        color: #dc2626 !important;
        transform: scale(1.05) !important;
    }

    [data-testid="stSidebarCollapseButton"] svg,
    button[aria-label="Collapse sidebar"] svg {
        fill: #334155 !important;
    }

    [data-testid="stSidebarCollapseButton"]:hover svg,
    button[aria-label="Collapse sidebar"]:hover svg {
        fill: #dc2626 !important;
    }

    /* Ensure Sidebar Header is Always Displayed with Collapse Button */
    [data-testid="stSidebarHeader"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
        padding: 10px 14px 0 14px !important;
        background: transparent !important;
        z-index: 100002 !important;
    }

    /* =========================================================================
       2. EXECUTIVE SIDEBAR STYLING
       ========================================================================= */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
        box-shadow: 4px 0 24px rgba(15, 23, 42, 0.04) !important;
        z-index: 100001 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span {
        color: #0f172a !important;
    }

    /* Sidebar Radio Navigation Tiles */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 6px !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: #f1f5f9 !important;
        border-color: #cbd5e1 !important;
        transform: translateX(2px) !important;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: #eff6ff !important;
        border-color: #3b82f6 !important;
        color: #1d4ed8 !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.12) !important;
    }

    /* =========================================================================
       3. INPUTS, SELECTBOXES, DATEPICKERS & FORMS (NO DARK BOXES)
       ========================================================================= */
    /* Force All Inputs, Selectboxes, Dropdowns & Popovers to Crisp Light Theme */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="input"] input,
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] > div,
    div[data-baseweb="base-input"] input,
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stTextInput"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stDateInput"] > div,
    div[role="combobox"],
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-color: #cbd5e1 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    div[data-baseweb="select"] svg {
        fill: #0f172a !important;
    }

    input::placeholder, textarea::placeholder {
        color: #64748b !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] > div,
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }

    div[data-baseweb="select"] > div:hover,
    .stTextInput input:hover,
    .stNumberInput input:hover,
    .stTextArea textarea:hover {
        border-color: #94a3b8 !important;
    }

    div[data-baseweb="select"] > div:focus-within,
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus {
        border-color: #4f46e5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    }

    /* Dropdown Menus / Popovers */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.12) !important;
    }

    ul[role="listbox"] li,
    ul[role="listbox"] li * {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 13px !important;
    }

    ul[role="listbox"] li:hover,
    ul[role="listbox"] li:hover *,
    ul[role="listbox"] li[aria-selected="true"],
    ul[role="listbox"] li[aria-selected="true"] * {
        background-color: #eff6ff !important;
        color: #1d4ed8 !important;
        font-weight: 600 !important;
    }

    /* Input Labels - High Contrast */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span,
    .stSelectbox label,
    .stSelectbox label p,
    .stTextInput label,
    .stTextInput label p,
    .stNumberInput label,
    .stNumberInput label p,
    .stDateInput label,
    .stDateInput label p,
    .stTextArea label,
    .stTextArea label p {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        margin-bottom: 4px !important;
    }

    /* =========================================================================
       4. TOP EXECUTIVE NAVBAR (PERMANENTLY STICKY TO TOP)
       ========================================================================= */
    /* Ensure Streamlit containers do not clip or break sticky behavior */
    .main,
    [data-testid="stAppViewContainer"],
    .block-container,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stVerticalBlockBorderWrapper"] {
        overflow: visible !important;
    }

    /* Reduce Streamlit default top padding so content docks cleanly */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Clean Top Navbar Container */
    .official-navbar-light {
        position: relative !important;
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 14px !important;
        padding: 14px 22px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05) !important;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        width: 100% !important;
    }
    .brand-section {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-logo-badge {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f59e0b;
        width: 44px;
        height: 44px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 800;
        border: 2px solid #f59e0b;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
    }
    .brand-title {
        font-size: 20px;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.4px;
        line-height: 1.15;
    }
    .brand-subtitle {
        font-size: 11px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
        margin-top: 3px;
    }
    .system-status-pills {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-green {
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
    }
    .pill-gold {
        background: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
    }
    .pill-blue {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    .pill-purple {
        background: #faf5ff;
        color: #7e22ce;
        border: 1px solid #e9d5ff;
    }

    /* =========================================================================
       5. EXECUTIVE KPI CARDS
       ========================================================================= */
    .kpi-container-light {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin-bottom: 22px;
    }
    .kpi-card-light {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card-light:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px -3px rgba(15, 23, 42, 0.08);
        border-color: #cbd5e1;
    }
    .kpi-card-light::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
    }
    .kpi-accent-gold::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .kpi-accent-green::before { background: linear-gradient(90deg, #10b981, #059669); }
    .kpi-accent-red::before { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .kpi-accent-amber::before { background: linear-gradient(90deg, #f59e0b, #b45309); }
    .kpi-accent-cyan::before { background: linear-gradient(90deg, #0284c7, #0369a1); }
    .kpi-accent-blue::before { background: linear-gradient(90deg, #3b82f6, #1d4ed8); }

    .kpi-label-light {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 700;
        color: #64748b;
        margin-bottom: 4px;
    }
    .kpi-value-light {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        line-height: 1.1;
    }
    .kpi-subtext-light {
        font-size: 11px;
        color: #64748b;
        margin-top: 5px;
        font-weight: 500;
    }

    /* =========================================================================
       6. 60-ROOM LUXURY KEYCARD GRID MATRIX
       ========================================================================= */
    .room-grid-light {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 12px;
        margin-top: 10px;
        margin-bottom: 22px;
    }
    .room-card-light {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px 12px;
        text-align: center;
        box-shadow: 0 2px 8px -1px rgba(15, 23, 42, 0.04);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        position: relative;
    }
    .room-card-light:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px -3px rgba(15, 23, 42, 0.09);
        border-color: #3b82f6;
    }
    .room-card-light-available { border-top: 4px solid #10b981; }
    .room-card-light-occupied { border-top: 4px solid #ef4444; background: #fffbfb; }
    .room-card-light-cleaning { border-top: 4px solid #f59e0b; background: #fffdf7; }

    .room-number-light {
        font-size: 17px;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 3px;
    }
    .room-cat-tag-light {
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        background: #f1f5f9;
        color: #475569;
        display: inline-block;
        margin-bottom: 6px;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }
    .room-tariff-light {
        font-size: 12px;
        color: #475569;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .room-status-badge-light {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        padding: 3px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    .status-light-available {
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
    }
    .status-light-occupied {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    .status-light-cleaning {
        background: #fffbeb;
        color: #d97706;
        border: 1px solid #fde68a;
    }

    /* =========================================================================
       7. BUTTONS, CARDS, INVOICE & TABS (CRISP LIGHT LUXURY STYLING)
       ========================================================================= */
    /* Primary buttons: Royal Indigo */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 8px 18px !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.35) !important;
        background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%) !important;
    }

    /* Standard / Secondary buttons: Crisp Light Cards (NO PITCH BLACK) */
    div.stButton > button:first-child,
    div.stButton > button[kind="secondary"],
    div.stButton > button {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover,
    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button:hover {
        background: #f8fafc !important;
        border-color: #4f46e5 !important;
        color: #4f46e5 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.12) !important;
    }

    /* Official Action Card */
    .official-action-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        margin-bottom: 16px;
    }

    /* Official Invoice Box */
    .invoice-box-light {
        font-family: 'JetBrains Mono', monospace !important;
        background: #0f172a;
        color: #38bdf8;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #1e293b;
        font-size: 13px;
        line-height: 1.6;
        white-space: pre;
        overflow-x: auto;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
    }

    /* =========================================================================
       8. STREAMLIT CHAT MESSAGES (CLEAN LIGHT CARD FOUNDATION)
       ========================================================================= */
    [data-testid="stChatMessage"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px -1px rgba(15, 23, 42, 0.04) !important;
    }

    /* Distinguish User & Assistant messages cleanly */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #f8faff !important;
        border: 1.5px solid #dbeafe !important;
        border-left: 5px solid #6366f1 !important;
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #ffffff !important;
        border: 1.5px solid #e2e8f0 !important;
        border-left: 5px solid #0284c7 !important;
    }

    [data-testid="stChatMessage"] p {
        color: #0f172a !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }

    [data-testid="stChatMessage"] table {
        border-collapse: separate !important;
        border-spacing: 0 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        width: 100% !important;
        margin: 10px 0 !important;
    }

    [data-testid="stChatMessage"] th {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        padding: 8px 12px !important;
        border-bottom: 1px solid #cbd5e1 !important;
    }

    [data-testid="stChatMessage"] td {
        padding: 8px 12px !important;
        border-bottom: 1px solid #f1f5f9 !important;
        font-size: 13px !important;
        color: #334155 !important;
    }

    [data-testid="stChatMessage"] code {
        background: #f1f5f9 !important;
        color: #0f172a !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        border: 1px solid #cbd5e1 !important;
    }

    /* Quick Action Directive Buttons in Agent Terminal */
    div[data-testid="stColumn"]:has(button[key^="btn_q_"]) button {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-size: 12.5px !important;
        font-weight: 700 !important;
        padding: 6px 10px !important;
        min-height: 40px !important;
        height: 40px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(button[key^="btn_q_"]) button:hover {
        background: #eff6ff !important;
        border-color: #3b82f6 !important;
        color: #1d4ed8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.16) !important;
    }

    /* Back to Floor Plan Navigation Button */
    div[data-testid="stColumn"]:has(button[key*="btn_back_to_floorplan"]) button,
    button[key*="btn_back_to_floorplan"] {
        min-height: 42px !important;
        height: 42px !important;
        background: #0F172A !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 13.5px !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stColumn"]:has(button[key*="btn_back_to_floorplan"]) button:hover,
    button[key*="btn_back_to_floorplan"]:hover {
        background: #1E293B !important;
        color: #FFFFFF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.22) !important;
    }

    /* Floor Plan Interactive Room Card Buttons (SCOPED STRICTLY TO FLOOR PLAN) */
    div[data-testid="stColumn"]:has(.hotel-room-card) button,
    div[data-testid="stElementContainer"]:has(.hotel-room-card) + div[data-testid="stElementContainer"] button {
        min-height: 125px !important;
        height: 125px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 10px 4px !important;
        text-align: center !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: pre-line !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    div[data-testid="stColumn"]:has(.hotel-room-card) button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.12) !important;
        border-color: #6366F1 !important;
    }

    /* Status Accent Borders */
    div[data-testid="stColumn"]:has(.hotel-room-card.room-available) button,
    div[data-testid="stElementContainer"]:has(.hotel-room-card.room-available) + div[data-testid="stElementContainer"] button {
        border-top: 5px solid #10B981 !important;
    }
    div[data-testid="stColumn"]:has(.hotel-room-card.room-occupied) button,
    div[data-testid="stElementContainer"]:has(.hotel-room-card.room-occupied) + div[data-testid="stElementContainer"] button {
        border-top: 5px solid #EF4444 !important;
    }
    div[data-testid="stColumn"]:has(.hotel-room-card.room-cleaning) button,
    div[data-testid="stElementContainer"]:has(.hotel-room-card.room-cleaning) + div[data-testid="stElementContainer"] button {
        border-top: 5px solid #F59E0B !important;
    }

    /* Paragraph inside room button: ensure multi-line vertical layout without ellipsis */
    div[data-testid="stColumn"]:has(.hotel-room-card) button div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stColumn"]:has(.hotel-room-card) button p {
        white-space: pre-line !important;
        line-height: 1.45 !important;
        margin: 0 !important;
        font-size: 13px !important;
        color: #0f172a !important;
        font-weight: 600 !important;
        text-align: center !important;
    }

    /* Hide the zero-height anchor element */
    div[data-testid="stElementContainer"]:has(.hotel-room-card),
    div.element-container:has(.hotel-room-card) {
        height: 0px !important;
        min-height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
        opacity: 0 !important;
        pointer-events: none !important;
        overflow: hidden !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 700;
        font-size: 13px;
        color: #475569;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.08) !important;
    }

    /* Sidebar Toggle Pill in Top Navbar */
    .stayease-sidebar-toggle-pill {
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        text-decoration: none !important;
        padding: 6px 14px !important;
        border-radius: 20px !important;
        font-weight: 800 !important;
        font-size: 11.5px !important;
        box-shadow: 0 3px 10px rgba(79, 70, 229, 0.35) !important;
        border: 1.5px solid #ffffff !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    .stayease-sidebar-toggle-pill:hover {
        transform: translateY(-1px) scale(1.04) !important;
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.5) !important;
        color: #ffffff !important;
    }

    /* =========================================================================
       9. ADVANCED RESPONSIVE MEDIA QUERIES (TABLET & MOBILE)
       ========================================================================= */
    /* Medium & Tablet Screens (<= 992px) */
    @media (max-width: 992px) {
        .block-container {
            padding-top: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Stack side-by-side columns into single column on narrower screens */
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 16px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }

        /* KPI Cards in 3 columns on tablet */
        .kpi-container-light {
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 10px !important;
        }
    }

    /* Mobile Screens (<= 768px) */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 0.75rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }

        /* Compact Header Navbar */
        .official-navbar-light {
            padding: 10px 14px !important;
            border-radius: 10px !important;
            margin-bottom: 12px !important;
            gap: 10px !important;
        }
        .brand-section {
            gap: 10px !important;
        }
        .brand-section > div:first-child {
            width: 38px !important;
            height: 38px !important;
        }
        .brand-section img {
            width: 24px !important;
            height: 24px !important;
        }
        .brand-title {
            font-size: 15px !important;
            line-height: 1.2 !important;
        }
        .brand-subtitle {
            font-size: 10px !important;
            letter-spacing: 0.4px !important;
        }
        .system-status-pills {
            gap: 6px !important;
            width: 100% !important;
            justify-content: flex-start !important;
        }
        .status-pill {
            font-size: 10px !important;
            padding: 4px 8px !important;
        }

        /* Mobile KPI Cards: Crisp 2x3 Grid */
        .kpi-container-light {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
            margin-bottom: 14px !important;
        }
        .kpi-card-light {
            padding: 10px 12px !important;
            border-radius: 10px !important;
        }
        .kpi-label-light {
            font-size: 9.5px !important;
        }
        .kpi-value-light {
            font-size: 18px !important;
        }
        .kpi-subtext-light {
            font-size: 9px !important;
        }
        .kpi-card-light > div > div:last-child {
            width: 34px !important;
            height: 34px !important;
        }
        .kpi-card-light img {
            width: 20px !important;
            height: 20px !important;
        }

        /* Responsive Floor Plan Matrix: 2 Cards per Row */
        div[data-testid="stHorizontalBlock"]:has(.hotel-room-card) {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 8px !important;
        }
        div[data-testid="stHorizontalBlock"]:has(.hotel-room-card) > div[data-testid="stColumn"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        div[data-testid="stElementContainer"]:has(.hotel-room-card) + div[data-testid="stElementContainer"] button {
            min-height: 95px !important;
            height: 95px !important;
            padding: 6px 2px !important;
        }
        div[data-testid="stElementContainer"]:has(.hotel-room-card) + div[data-testid="stElementContainer"] button p {
            font-size: 11.5px !important;
            line-height: 1.35 !important;
        }

        /* Scrollable Tabs without ugly pagination bar */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            padding: 4px !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px !important;
            font-size: 11px !important;
            white-space: nowrap !important;
            flex-shrink: 0 !important;
        }

        /* Quick Action Directive Buttons in Agent Terminal */
        div[data-testid="stColumn"]:has(button[key^="btn_q_"]) {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        div[data-testid="stColumn"]:has(button[key^="btn_q_"]) button {
            font-size: 11.5px !important;
            min-height: 36px !important;
            height: 36px !important;
            padding: 4px 8px !important;
        }

        /* Floating Sidebar Toggle Button for Mobile */
        [data-testid="stExpandSidebarButton"],
        [data-testid="collapsedControl"],
        button[aria-label="Expand sidebar"] {
            position: fixed !important;
            top: 10px !important;
            left: 10px !important;
            z-index: 99999999 !important;
            display: inline-flex !important;
            padding: 6px 10px !important;
            font-size: 12px !important;
        }
        [data-testid="stSidebar"] {
            z-index: 10000000 !important;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.3) !important;
        }
    }
</style>""", unsafe_allow_html=True)
