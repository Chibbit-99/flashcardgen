import json
import requests
import urllib.parse
import streamlit as st

# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 AI Flashcard Generator")
st.caption("🏵️ Bring Your Own Pollen Edition")

# ==========================================
# CONFIG
# ==========================================

POLLINATIONS_APP_KEY = "pk_athvucdxshpixsqn"

MY_APP_URL = "https://flashcardgenbychibbit.streamlit.app"

TEXT_API_URL = "https://text.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

# ==========================================
# AUTH
# ==========================================

params = st.query_params
user_token = params.get("token")

if not user_token:

    st.info(
        "Authenticate with Pollinations so generation uses YOUR pollen balance."
    )

    redirect = urllib.parse.quote(
        MY_APP_URL,
        safe=""
    )

    auth_url = (
        "https://auth.pollinations.ai/authorize?"
        f"app_key={POLLINATIONS_APP_KEY}"
        f"&redirect_url={redirect}"
    )

    st.link_button(
        "🔐 Sign in with Pollinations",
        auth_url
    )

    # temporary debug
    with st.expander("Debug URL"):
        st.code(auth_url)

    st.stop()

# ==========================================
# APP
# ==========================================

st.success("Authenticated via your Pollinations account")

if st.button("Logout"):
    st.query_params.clear()
    st.rerun()

topic = st.text_input(
    "Study topic",
    "Neuroanatomy"
)

count = st.slider(
    "Cards",
    1,
    10,
    3
)

if st.button(
    "Generate Deck ✨",
    type="primary"
):

    with st.spinner("Generating..."):

        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type":"application/json"
        }

        payload = {
            "model":"openai",
            "messages":[
                {
                    "role":"system",
                    "content":"""
Return ONLY a JSON array.

[
 {
   "front":"",
   "back":"",
   "image_prompt":""
 }
]
"""
                },
                {
                    "role":"user",
                    "content":
                    f"Generate exactly {count} flashcards about {topic}"
                }
            ]
        }

        try:

            r = requests.post(
                TEXT_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            r.raise_for_status()

            data = r.json()

            raw = (
                data["choices"][0]
                ["message"]["content"]
                .replace("```json","")
                .replace("```","")
                .strip()
            )

            cards = json.loads(raw)

            for i, card in enumerate(cards,1):

                st.subheader(
                    f"Card {i}: {card['front']}"
                )

                prompt = urllib.parse.quote(
                    card["image_prompt"]
                )

                image_url = (
                    f"{IMAGE_API_URL}{prompt}"
                    f"?key={user_token}"
                    f"&width=600"
                    f"&height=300"
                    f"&nologo=true"
                )

                col1,col2 = st.columns(2)

                with col1:

                    st.image(
                        image_url,
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

            st.error(str(e))

            try:
                st.json(r.json())
            except:
                st.write(r.text)
