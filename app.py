import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import json

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴"
)

CLIENT_ID="pk_AthVUCdXSHpixSqN"
APP_URL="https://flashcardgenbychibbit.streamlit.app"

# Run JS in iframe and read fragment
fragment = components.html(
"""
<script>
const hash = window.parent.location.hash;
const params = new URLSearchParams(hash.slice(1));
const key = params.get("api_key");

if(key){
    document.write(key);
}
</script>
""",
height=0
)

# fallback
api_key = st.query_params.get("api_key")

if not api_key and fragment:
    api_key = fragment

if not api_key:

    auth_url=(
        "https://enter.pollinations.ai/authorize?"
        + urllib.parse.urlencode({
            "redirect_uri":APP_URL,
            "client_id":CLIENT_ID
        })
    )

    st.link_button(
        "🌸 Sign in",
        auth_url
    )

    st.stop()

st.success("Logged in")
st.write(api_key[:15] + "...")
