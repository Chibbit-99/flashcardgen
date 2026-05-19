import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import json

# ==========================================
# CONFIG
# ==========================================

CLIENT_ID = "pk_AthVUCdXSHpixSqN"
APP_URL = "https://flashcardgenbychibbit.streamlit.app/"

TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

st.set_page_config(
    page_title="AI Flashcards",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 AI Flashcard Generator")

# ==========================================
# 🔥 CRITICAL FIX: FRAGMENT CAPTURE
# ==========================================

components.html(
"""
<script>
(function () {

    const hash = window.location.hash;

    if (!hash.includes("api_key=")) return;

    const params = new URLSearchParams(hash.slice(1));
    const key = params.get("api_key");

    if (!key) return;

    // store in real URL (this is what Streamlit can read)
    const url = new URL(window.location.href);

    url.hash = "";
    url.searchParams.set("api_key", key);

    // IMPORTANT: full reload so Streamlit re-runs Python
    window.location.href = url.toString();

})();
</script>
""",
height=0
)

# ==========================================
# READ KEY (ONLY QUERY PARAM)
# ==========================================

api_key = st.query_params.get("api_key", "")

if isinstance(api_key, list):
    api_key = api_key[0]

api_key = str(api_key).strip()

# ==========================================
# LOGIN
# ==========================================

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

if not api_key:

    st.info("Login required to use your Pollen balance.")

    st.link_button("🌸 Login with Pollinations", auth_url)

    st.stop()

# ==========================================
# APP
# ==========================================

st.success("Authenticated")

if st.button("Logout"):

    st.query_params.clear()

    components.html(
        """
        <script>
        const url = new URL(window.location.href);
        url.search = "";
        url.hash = "";
        window.location.href = url.toString();
        </script>
        """,
        height=0
    )

    st.stop()

st.markdown("---")

topic = st.text_input("Topic", "Neuroanatomy")
count = st.slider("Cards", 1, 10, 3)

# ==========================================
# GENERATE
# ==========================================

if st.button("Generate Deck ✨"):

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai",
        "messages": [
            {
                "role": "system",
                "content": """
Return ONLY JSON:

[
 {"front":"","back":"","image_prompt":""}
]
"""
            },
            {
                "role": "user",
                "content": f"Generate {count} flashcards about {topic}"
            }
        ]
    }

    try:
        with st.spinner("Generating..."):

            r = requests.post(
                TEXT_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            r.raise_for_status()

            data = r.json()

            raw = data["choices"][0]["message"]["content"]
            raw = raw.replace("```json", "").replace("```", "").strip()

            cards = json.loads(raw)

            for i, card in enumerate(cards, 1):

                st.subheader(f"Card {i}")
                st.write(card["front"])

                img = IMAGE_API_URL + urllib.parse.quote(card["image_prompt"])

                col1, col2 = st.columns(2)

                with col1:
                    st.image(img, use_container_width=True)

                with col2:
                    with st.expander("Answer"):
                        st.write(card["back"])

                st.markdown("---")

    except Exception as e:
        st.error(str(e))
