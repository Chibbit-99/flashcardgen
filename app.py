import streamlit as st
import requests
import json
import urllib.parse

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

# ==========================================
# CONFIG
# ==========================================

CLIENT_ID = "pk_AthVUCdXSHpixSqN"

APP_URL = "https://flashcardgenbychibbit.streamlit.app"

TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

st.title("🎴 AI Flashcard Generator")
st.caption("🌸 Bring Your Own Pollen Edition")

# ==========================================
# FRAGMENT HANDLING
# ==========================================

st.markdown("""
<script>
const hash = window.location.hash.substring(1);
const params = new URLSearchParams(hash);

const apiKey = params.get("api_key");

if(apiKey){

    const url=new URL(window.location);

    url.searchParams.set(
        "api_key",
        apiKey
    );

    window.location=url;
}
</script>
""", unsafe_allow_html=True)

api_key = st.query_params.get("api_key")

# ==========================================
# LOGIN
# ==========================================

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
        "Sign in to use your own Pollen balance."
    )

    st.link_button(
        "🌸 Sign in with Pollinations",
        auth_url
    )

    st.code(auth_url)

    st.stop()

# ==========================================
# APP
# ==========================================

st.success("Authenticated")

if st.button("Logout"):
    st.query_params.clear()
    st.rerun()

topic = st.text_input(
    "Topic",
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
Return only valid JSON:

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
                f"Generate {count} flashcards about {topic}"
            }
        ]
    }

    try:

        with st.spinner(
            "Generating..."
        ):

            r = requests.post(
                TEXT_API_URL,
                headers=headers,
                json=payload
            )

            r.raise_for_status()

            data=r.json()

            text=(
                data["choices"][0]
                ["message"]["content"]
                .replace("```json","")
                .replace("```","")
                .strip()
            )

            cards=json.loads(text)

            for i,card in enumerate(cards,1):

                st.subheader(
                    f"Card {i}: {card['front']}"
                )

                prompt=urllib.parse.quote(
                    card["image_prompt"]
                )

                img=(
                    f"{IMAGE_API_URL}{prompt}"
                    f"?width=600"
                    f"&height=300"
                    f"&nologo=true"
                )

                col1,col2=st.columns(2)

                with col1:
                    st.image(
                        img,
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
