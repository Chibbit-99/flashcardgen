import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import json

st.set_page_config(page_title="AI Flashcards", page_icon="🎴")

CLIENT_ID = "pk_AthVUCdXSHpixSqN"
APP_URL = "https://flashcardgenbychibbit.streamlit.app"

TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

st.title("🎴 AI Flashcard Generator")

# ==========================================
# 🔥 PROPER FRAGMENT → STREAMLIT PIPE
# ==========================================

components.html("""
<script>
(function () {
    const hash = window.location.hash;

    if (hash.includes("api_key=")) {

        const params = new URLSearchParams(hash.slice(1));
        const key = params.get("api_key");

        if (key) {
            // send to Streamlit parent
            window.parent.postMessage(
                {
                    type: "pollinations_key",
                    key: key
                },
                "*"
            );
        }
    }
})();
</script>
""", height=0)

# ==========================================
# RECEIVE KEY (via query param fallback)
# ==========================================

# Streamlit cannot directly receive postMessage,
# so we ALSO store via query param fallback redirect

api_key = st.query_params.get("api_key", "")

if isinstance(api_key, list):
    api_key = api_key[0]

api_key = str(api_key).strip()

# ==========================================
# LOGIN
# ==========================================

if not api_key:

    auth_url = (
        "https://enter.pollinations.ai/authorize?"
        + urllib.parse.urlencode({
            "redirect_uri": APP_URL,
            "client_id": CLIENT_ID,
            "scope": "usage",
            "budget": "10",
            "expiry": "7"
        })
    )

    st.info("Login required")

    st.link_button("🌸 Sign in", auth_url)

    st.stop()

# ==========================================
# APP WORKS HERE
# ==========================================

st.success("Authenticated")

st.write(f"Key loaded: {api_key[:12]}...")
