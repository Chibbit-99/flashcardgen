import json
import requests
import urllib.parse
import streamlit as st

# ==========================================
# PAGE SETUP
# ==========================================

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

# ==========================================
# CONFIG
# ==========================================

POLLINATIONS_APP_KEY = "pk_athvucdxshpixsqn"

# no trailing slash
MY_APP_LIVE_URL = "https://flashcardgenbychibbit.streamlit.app"

# actual endpoints
TEXT_API_URL = "https://text.pollinations.ai/openai"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

# ==========================================
# GET AUTH TOKEN
# ==========================================

query_params = st.query_params
user_token = query_params.get("token")

st.title("🎴 AI Flashcard Deck Generator")
st.caption("⚡ Powered by Pollinations.ai")

# ==========================================
# LOGIN SCREEN
# ==========================================

if not user_token:

    st.info(
        "👋 Welcome! Authenticate using your Pollinations account."
    )

    auth_url = (
        "https://pollinations.ai/auth?"
        f"key={POLLINATIONS_APP_KEY}"
        f"&redirect_uri={urllib.parse.quote(MY_APP_LIVE_URL)}"
        "&response_type=token"
    )

    st.link_button(
        "🔐 Authenticate with Pollinations",
        auth_url
    )

    st.stop()

# ==========================================
# APP
# ==========================================

st.success("Authenticated")

if st.button("Disconnect Session"):
    st.query_params.clear()
    st.rerun()

st.markdown("---")

topic = st.text_input(
    "Enter a study topic:",
    "Neuroanatomy"
)

count = st.slider(
    "Number of flashcards",
    min_value=1,
    max_value=10,
    value=3
)

# ==========================================
# GENERATE
# ==========================================

if st.button(
    "Generate Deck ✨",
    type="primary"
):

    with st.spinner("Generating..."):

        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }

        system_prompt = """
Return ONLY valid JSON.

Format:

[
 {
   "front":"question",
   "back":"answer",
   "image_prompt":"description"
 }
]

No markdown.
No explanations.
No code blocks.
"""

        user_prompt = (
            f"Generate exactly {count} flashcards "
            f"about {topic}"
        )

        payload = {
            "model": "openai",
            "messages": [
                {
                    "role":"system",
                    "content":system_prompt
                },
                {
                    "role":"user",
                    "content":user_prompt
                }
            ]
        }

        try:

            response = requests.post(
                TEXT_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            data = response.json()

            # safer extraction
            raw_text = (
                data
                .get("choices",[{}])[0]
                .get("message",{})
                .get("content","")
                .strip()
            )

            # remove accidental markdown wrappers
            raw_text = (
                raw_text
                .replace("```json","")
                .replace("```","")
                .strip()
            )

            flashcards = json.loads(raw_text)

            if not isinstance(
                flashcards,
                list
            ):
                raise Exception(
                    "AI did not return a list"
                )

            st.success(
                f"Generated {len(flashcards)} cards"
            )

            for i,card in enumerate(
                flashcards,
                start=1
            ):

                st.markdown(
                    f"## Card {i}"
                )

                st.subheader(
                    card["front"]
                )

                encoded = urllib.parse.quote(
                    card["image_prompt"]
                )

                img_url = (
                    f"{IMAGE_API_URL}"
                    f"{encoded}"
                    "?width=500"
                    "&height=300"
                    "&nologo=true"
                )

                col1,col2 = st.columns(2)

                with col1:
                    st.image(
                        img_url,
                        caption="Concept Image",
                        use_container_width=True
                    )

                with col2:
                    with st.expander(
                        "Reveal Answer"
                    ):
                        st.write(
                            card["back"]
                        )

                st.markdown("---")

        except Exception as e:

            st.error(
                f"Error:\n\n{str(e)}"
            )
