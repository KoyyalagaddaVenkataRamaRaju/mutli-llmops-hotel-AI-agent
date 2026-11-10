import requests
import streamlit as st

from app.core.ai_agent import get_response_from_ai_agents

BACKEND_URL = "http://127.0.0.1:8000"

def render_agent_terminal_panel(selected_role: str, model_choice: str, enable_tavily: bool):
    """
    Renders the Multi-Role AI Agent terminal with quick command chips at top,
    clean natural Streamlit chat messages, and resilient execution.
    """
    st.markdown("### 🤖 StayEase AI Operations & Multi-Role Agent Terminal")
    st.caption("Active Guardrails Protected • Automatic Tool Calling across Receptionist, Manager, Owner, Housekeeping & Concierge")

    st.markdown(f"""
    <div style="background:#f1f5f9; border-left:4px solid #0284c7; padding:10px 16px; border-radius:8px; margin-bottom:14px;">
        <span style="font-weight:700; color:#0f172a;">Active Authority:</span> 
        <span style="background:#0284c7; color:#ffffff; padding:2px 8px; border-radius:4px; font-weight:700; font-size:12px;">{selected_role} Mode</span>
        <span style="color:#64748b; font-size:12px; margin-left:10px;">Security Guardrails: Enforced | 12 Operational Tools Armed</span>
    </div>
    """, unsafe_allow_html=True)

    # 1. Initialize Terminal Messages
    if "terminal_messages" not in st.session_state:
        st.session_state.terminal_messages = [
            {
                "role": "assistant",
                "content": f"Welcome to Hotel Apex Residency! I am StayEase AI operating in **{selected_role} Mode**. How may I assist you with room allocations, guest folios, housekeeping dispatch, or owner financials today?"
            }
        ]

    # 2. Quick Action Commands (Positioned Cleanly at Top - Never Overlaps Chat)
    st.markdown(f'<div class="agent-quick-actions-anchor"></div>**⚡ Quick Action Commands ({selected_role}):**', unsafe_allow_html=True)
    rc1, rc2, rc3, rc4, rc5 = st.columns(5)
    selected_action = None

    if selected_role == "Receptionist":
        if rc1.button("🛏️ Check Availability", key="btn_q_avail", use_container_width=True):
            selected_action = "Check availability for Deluxe rooms and quote price for 3 nights."
        if rc2.button("📋 Hotel Status", key="btn_q_status", use_container_width=True):
            selected_action = "What is the current hotel occupancy, available rooms, and occupied rooms?"
        if rc3.button("📝 Book Deluxe Room", key="btn_q_book", use_container_width=True):
            selected_action = "Book Deluxe room for Farhan, phone 9876543210, ID PASSPORT-A9901 for 2 nights."
        if rc4.button("💳 Checkout Rm 203", key="btn_q_co", use_container_width=True):
            selected_action = "Check out Room 203 and generate the final invoice."
        if rc5.button("📜 Check-In SOP", key="btn_q_sop", use_container_width=True):
            selected_action = "Search knowledge base for Front Desk Check-in protocol."

    elif selected_role == "General Manager":
        if rc1.button("📈 Peak Surcharge Audit", key="btn_q_peak", use_container_width=True):
            selected_action = "What is the current occupancy percentage, and should the 20% Peak Surcharge be activated?"
        if rc2.button("🧹 Allot Ramesh Rm 103", key="btn_q_allot", use_container_width=True):
            selected_action = "Allot Housekeeper Ramesh to clean Room 103."
        if rc3.button("🛠️ Check Maintenance", key="btn_q_maint", use_container_width=True):
            selected_action = "Check all open engineering maintenance tickets."
        if rc4.button("🌙 Daily Night Audit", key="btn_q_audit", use_container_width=True):
            selected_action = "Execute the daily night audit task and post room charges."
        if rc5.button("📑 Yield Management", key="btn_q_yield", use_container_width=True):
            selected_action = "Search knowledge base for General Manager yield management guidelines."

    elif selected_role == "Hotel Owner":
        if rc1.button("💰 Executive Financials", key="btn_q_fin", use_container_width=True):
            selected_action = "Generate the executive financial summary with ADR, RevPAR, gross revenue, and tax remittances."
        if rc2.button("📊 Occupancy & ADR", key="btn_q_adr", use_container_width=True):
            selected_action = "What is our current ADR (Average Daily Rate) and RevPAR compared to our ₹2,800 target?"
        if rc3.button("💾 Binary Backup Status", key="btn_q_bak", use_container_width=True):
            selected_action = "Verify the binary backup compliance of invoices.dat against database records."
        if rc4.button("💵 Tax Collections", key="btn_q_tax", use_container_width=True):
            selected_action = "What is the total 12% luxury tax collected across all rooms and F&B?"
        if rc5.button("📑 Owner Data Policy", key="btn_q_pol", use_container_width=True):
            selected_action = "Search knowledge base for Hotel Owner financial and data governance rules."

    elif selected_role == "Housekeeping":
        if rc1.button("🧼 Cleaning Queue", key="btn_q_queue", use_container_width=True):
            selected_action = "What rooms are currently in the Housekeeping Cleaning Queue?"
        if rc2.button("🧹 Allot Sunita Rm 212", key="btn_q_sunita", use_container_width=True):
            selected_action = "Allot Housekeeper Sunita to Room 212."
        if rc3.button("✨ Mark Rm 103 Clean", key="btn_q_clean103", use_container_width=True):
            selected_action = "Mark Room 103 as cleaned and inspected by housekeeping."
        if rc4.button("🛠️ Report AC Leak Rm 207", key="btn_q_leak", use_container_width=True):
            selected_action = "Report an engineering maintenance issue for Room 207: AC is leaking water."
        if rc5.button("📑 Cleaning SOP", key="btn_q_clnsop", use_container_width=True):
            selected_action = "Search knowledge base for Housekeeping 20-minute turnaround SOP."

    elif selected_role == "Guest Support":
        if rc1.button("🍽️ Order Biryani Rm 208", key="btn_q_food208", use_container_width=True):
            selected_action = "Order Hyderabadi Dum Biryani Feast for Room 208."
        if rc2.button("🚗 Airport Chauffeur", key="btn_q_car", use_container_width=True):
            selected_action = "What are the rates and travel time for the luxury Mercedes airport chauffeur to BLR airport?"
        if rc3.button("🐕 Pet & Smoke Rules", key="btn_q_pet", use_container_width=True):
            selected_action = "What is the hotel pet policy and smoking policy?"
        if rc4.button("💆 Ayurvedic Spa", key="btn_q_spa", use_container_width=True):
            selected_action = "What are the timings and cost for the Luxury Ayurvedic Spa?"
        if rc5.button("🧺 Express Laundry", key="btn_q_laundry", use_container_width=True):
            selected_action = "Add Express Laundry (₹350) to Room 102."

    else:  # General
        if rc1.button("🛏️ Book Room", key="btn_q_book_gen", use_container_width=True):
            selected_action = "Book Deluxe room for Farhan, phone 9876543210, ID PASSPORT-A9901 for 2 nights."
        if rc2.button("🍽️ Order Food", key="btn_q_food_gen", use_container_width=True):
            selected_action = "Order Hyderabadi Dum Biryani Feast for Room 208."
        if rc3.button("🧹 Clean Room", key="btn_q_clean_gen", use_container_width=True):
            selected_action = "Allot Housekeeper Ramesh to clean Room 103."
        if rc4.button("📊 Financials", key="btn_q_fin_gen", use_container_width=True):
            selected_action = "Provide the executive financial summary with gross revenue, ADR, and RevPAR."
        if rc5.button("🌙 Night Audit", key="btn_q_audit_gen", use_container_width=True):
            selected_action = "Execute the daily night audit task and post room charges."

    st.write("---")

    # 3. Clean Natural Chat Messages Display (Contained Viewport, No Overlap)
    chat_container = st.container(height=520)
    with chat_container:
        for message in st.session_state.terminal_messages:
            avatar = "🤖" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    # 4. Standard Bottom Chat Input
    user_typed = st.chat_input("Command StayEase AI (e.g., 'Book Room 310', 'Order biryani to Room 208', 'Check occupancy')...")
    action_prompt = selected_action or user_typed

    # 5. Execution & Response
    if action_prompt:
        st.session_state.terminal_messages.append({"role": "user", "content": action_prompt})
        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(action_prompt)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner(f"StayEase AI ({selected_role} Mode) executing hotel operations..."):
                    reply = ""
                    history_payload = st.session_state.terminal_messages[-8:]
                    try:
                        payload = {
                            "model_name": model_choice,
                            "system_prompt": "",
                            "messages": history_payload,
                            "allow_search": enable_tavily,
                            "active_role": selected_role
                        }
                        res = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=40)
                        if res.status_code == 200:
                            reply = res.json().get("response", "")
                        else:
                            reply = get_response_from_ai_agents(model_choice, history_payload, enable_tavily, active_role=selected_role)
                    except Exception:
                        try:
                            reply = get_response_from_ai_agents(model_choice, history_payload, enable_tavily, active_role=selected_role)
                        except Exception as err:
                            reply = f"⚠️ Operational alert: {str(err)}"

                    st.markdown(reply)
                    st.session_state.terminal_messages.append({"role": "assistant", "content": reply})

        st.rerun()

    # 6. Clear Conversation
    st.write("")
    if st.button("🗑️ Clear Terminal Conversation", key="btn_clear_terminal"):
        st.session_state.terminal_messages = [
            {"role": "assistant", "content": f"Chat history cleared. StayEase AI ({selected_role} Mode) on standby."}
        ]
        st.rerun()
