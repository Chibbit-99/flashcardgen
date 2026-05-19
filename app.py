import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import json

# ==========================================
# CONFIG
# ==========================================

CLIENT_ID = "pk_AthVUCdXSHpixSqN"
APP_URL = "https://flashcardgenbychibbit.streamlit.app"

TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 AI Flashcard Generator")
st.caption("🌸 Bring Your Own Pollen")

# ==========================================
# 🔥 JS: convert #api_key → ?api_key
# ==========================================

components.html(
"""
<script>
(function () {

    const hash = window.location.hash;

    if (hash.includes("api_key=")) {

        const params = new URLSearchParams(hash.slice(1));
        const key = params.get("api_key");

        if (key) {
            const url = new URL(window.location.href);

            url.hash = "";
            url.searchParams.set("api_key", key);

            // reload into Streamlit-friendly URL
            window.location.replace(url.toString());
        }
    }

})();
</script>
""",
height=0
)

# ==========================================
# READ KEY (Streamlit side)
# ==========================================

api_key = st.query_params.get("api_key", "")

if isinstance(api_key, list):
    api_key = api_key[0]

api_key = str(api_key).strip()

# ==========================================
# LOGIN SCREEN
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

    st.info("Sign in with Pollinations to use your own Pollen")

    st.link_button("🌸 Login", auth_url)

    st.stop()

# ==========================================
# LOGGED IN
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
        window.location.replace(url.toString());
        </script>
        """,
        height=0
    )

    st.stop()

st.markdown("---")

# ==========================================
# INPUTS
# ==========================================

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
Return ONLY valid JSON:

[
 {"front":"","back":"","image_prompt":""}
]

No markdown, no explanation.
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

            raw = (
                data["choices"][0]["message"]["content"]
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            cards = json.loads(raw)

            st.success(f"Generated {len(cards)} cards")

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

        try:
            st.json(r.json())
        except:
            pass
