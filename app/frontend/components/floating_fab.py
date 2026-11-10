import streamlit as st

def render_floating_ai_fab(is_terminal_panel: bool = True):
    """
    Safely cleans up any legacy injected floating action buttons from the parent DOM.
    All navigation is now handled natively via the StayEase AI Operating System console.
    """
    st.html("""
    <script>
    try {
        const doc = window.parent && window.parent.document ? window.parent.document : document;
        const oldFab = doc.getElementById('stayease-luxury-floating-fab');
        if (oldFab) {
            oldFab.remove();
        }
    } catch (e) {
        // Safe silence
    }
    </script>
    """)
