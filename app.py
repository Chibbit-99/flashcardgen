import streamlit as st
import requests
import urllib.parse
import json

# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 AI Flashcard Generator")
st.caption("🌸 Bring Your Own Pollen Edition")

# ==========================================
# CONFIG
# ==========================================

CLIENT_ID = "pk_AthVUCdXSHpixSqN"

APP_URL = "https://flashcardgenbychibbit.streamlit.app"

TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

# ==========================================
# MOVE #api_key TO ?api_key
# Streamlit cannot read fragments
# ==========================================

st.markdown("""
<script>
(function(){

    const hash = window.location.hash.slice(1);

    if(!hash) return;

    const params = new URLSearchParams(hash);

    const apiKey = params.get("api_key");

    if(apiKey){

        const url = new URL(window.location);

        url.searchParams.set(
            "api_key",
            apiKey
        );

        window.location.href=url;
    }

})();
</script>
""", unsafe_allow_html=True)

# ==========================================
# AUTH
# ==========================================

api_key = st.query_params.get("api_key")

if not api_key:

    auth_params = {
        "redirect_uri": APP_URL,
        "client_id": CLIENT_ID,
        "scope":"usage",
        "budget":"10",
        "expiry":"7"
    }

    auth_url = (
        "https://enter.pollinations.ai/authorize?"
        + urllib.parse.urlencode(auth_params)
    )

    st.info(
        "Authenticate using your own Pollen balance."
    )

    st.link_button(
        "🌸 Sign in with Pollinations",
        auth_url
    )

    st.caption(
        "Usage is charged to your own account."
    )

    st.stop()

# ==========================================
# AUTH SUCCESS
# ==========================================

st.success(
    "Authenticated"
)

if st.button("Logout"):

    st.query_params.clear()

    st.rerun()

st.markdown("---")

# ==========================================
# INPUTS
# ==========================================

topic = st.text_input(
    "Study topic",
    value="Neuroanatomy"
)

count = st.slider(
    "Flashcards",
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

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type":"application/json"
    }

    payload = {
        "model":"openai",
        "messages":[
            {
                "role":"system",
                "content":
"""
Return ONLY valid JSON.

[
 {
   "front":"question",
   "back":"answer",
   "image_prompt":"description"
 }
]

No markdown.
No code blocks.
No explanations.
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

        with st.spinner(
            "Generating flashcards..."
        ):

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

            cards = json.loads(raw)

            st.success(
                f"Generated {len(cards)} cards"
            )

            for i,card in enumerate(cards,1):

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
                    f"{IMAGE_API_URL}{encoded}"
                    f"?width=600"
                    f"&height=350"
                    f"&nologo=true"
                    f"&seed={i}"
                )

                col1,col2 = st.columns(2)

                with col1:

                    st.image(
                        image_url,
                        use_container_width=True
                    )

                with col2:

                    with st.expander(
                        "Reveal Answer 🔍"
                    ):

                        st.write(
                            card["back"]
                        )

                st.markdown("---")

    except Exception as e:

        st.error(
            f"Generation failed:\n{str(e)}"
        )

        try:
            st.json(
                response.json()
            )
        except:
            pass
