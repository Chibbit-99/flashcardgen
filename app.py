import json
import urllib.parse
import requests
import streamlit as st

# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 AI Flashcard Deck Generator")
st.caption("⚡ Powered by Pollinations")

# ==========================================
# CONFIG
# ==========================================

# your publishable key
API_KEY = "pk_athvucdxshpixsqn"

# OpenAI-compatible endpoint
TEXT_API_URL = "https://text.pollinations.ai/v1/chat/completions"

IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

# ==========================================
# UI
# ==========================================

topic = st.text_input(
    "Study topic",
    value="Neuroanatomy"
)

count = st.slider(
    "Number of flashcards",
    1,
    10,
    3
)

# ==========================================
# GENERATE
# ==========================================

if st.button("Generate Deck ✨", type="primary"):

    with st.spinner("Generating flashcards..."):

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        system_prompt = """
Return ONLY a valid JSON array.

Format:

[
 {
   "front":"question",
   "back":"answer",
   "image_prompt":"image description"
 }
]

No markdown.
No explanation.
No code fences.
"""

        payload = {
            "model": "openai",
            "messages": [
                {
                    "role":"system",
                    "content":system_prompt
                },
                {
                    "role":"user",
                    "content":
                    f"Generate exactly {count} flashcards about {topic}"
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

            raw = (
                data["choices"][0]
                ["message"]["content"]
                .replace("```json","")
                .replace("```","")
                .strip()
            )

            flashcards = json.loads(raw)

            for i, card in enumerate(
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

                image_url = (
                    f"{IMAGE_API_URL}"
                    f"{encoded}"
                    f"?width=600"
                    f"&height=350"
                    f"&nologo=true"
                    f"&key={API_KEY}"
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

            st.error(
                f"Error:\n{e}"
            )

            st.write(
                "Raw response:"
            )

            try:
                st.json(response.json())
            except:
                st.write(response.text)
