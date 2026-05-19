import streamlit as st
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
st.caption("🌸 Bring Your Own Pollen (Streamlit-safe version)")

# ==========================================
# AUTH LINK
# ==========================================

auth_url = (
    "https://enter.pollinations.ai/authorize?"
    + urllib.parse.urlencode({
        "redirect_uri": APP_URL,   # MUST be clean URL (no #)
        "client_id": CLIENT_ID,
        "scope": "usage",
        "budget": "10",
        "expiry": "7"
    })
)

# ==========================================
# READ KEY (ONLY QUERY PARAMS)
# ==========================================

api_key = st.query_params.get("api_key")

if isinstance(api_key, list):
    api_key = api_key[0]

api_key = (api_key or "").strip()

# ==========================================
# LOGIN SCREEN
# ==========================================

if not api_key:

    st.info("Sign in to use your own Pollen balance.")

    st.link_button(
        "🌸 Login with Pollinations",
        auth_url
    )

    st.stop()

# ==========================================
# LOGGED IN
# ==========================================

st.success("Authenticated")

if st.button("Logout"):

    # clear URL + rerun clean
    st.query_params.clear()
    st.rerun()

st.markdown("---")

# ==========================================
# INPUTS
# ==========================================

topic = st.text_input("Study topic", "Neuroanatomy")
count = st.slider("Flashcards", 1, 10, 3)

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
  {
    "front": "",
    "back": "",
    "image_prompt": ""
  }
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

            st.success(f"Generated {len(cards)} cards")

            for i, card in enumerate(cards, 1):

                st.subheader(f"Card {i}")
                st.write(card["front"])

                img_url = (
                    IMAGE_API_URL +
                    urllib.parse.quote(card["image_prompt"])
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.image(img_url, use_container_width=True)

                with col2:
                    with st.expander("Answer"):
                        st.write(card["back"])

                st.markdown("---")

    except Exception as e:
        st.error(f"Error: {e}")

        try:
            st.json(r.json())
        except:
            pass
