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
# CONVERT:
# #api_key=...
# →
# ?api_key=...
#
# Streamlit cannot read fragments
# ==========================================

components.html(
"""
<script>

const hash = window.parent.location.hash;

if(hash && hash.includes("api_key=")){

    const params = new URLSearchParams(
        hash.substring(1)
    );

    const key=params.get(
        "api_key"
    );

    if(key){

        const url =
            new URL(
                window.parent.location.href
            );

        url.hash="";

        url.searchParams.set(
            "api_key",
            key
        );

        window.parent.location.replace(
            url.toString()
        );
    }

}

</script>
""",
height=0
)

# ==========================================
# GET KEY
# ==========================================

api_key = st.query_params.get(
    "api_key",
    ""
)

if isinstance(api_key,list):
    api_key=api_key[0]

api_key=str(api_key).strip()

# ==========================================
# LOGIN PAGE
# ==========================================

if not api_key:

    params = {

        "redirect_uri":
        APP_URL,

        "client_id":
        CLIENT_ID,

        "scope":
        "usage",

        "budget":
        "10",

        "expiry":
        "7"
    }

    auth_url = (
        "https://enter.pollinations.ai/authorize?"
        + urllib.parse.urlencode(
            params
        )
    )

    st.info(
        "Authenticate with Pollinations using your own Pollen balance."
    )

    st.link_button(
        "🌸 Sign in with Pollinations",
        auth_url
    )

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

    const url=
        new URL(
            window.parent.location.href
        );

    url.hash="";

    url.search="";

    window.parent.location.replace(
        url.toString()
    );

    </script>
    """,
    height=0
    )

    st.stop()

st.markdown("---")

# ==========================================
# INPUTS
# ==========================================

topic=st.text_input(
    "Study topic",
    "Neuroanatomy"
)

count=st.slider(
    "Flashcards",
    1,
    10,
    3
)

# ==========================================
# GENERATE
# ==========================================

if st.button(
    "Generate Deck ✨",
    type="primary"
):

    headers={

        "Authorization":
        f"Bearer {api_key}",

        "Content-Type":
        "application/json"
    }

    payload={

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

No markdown
No code blocks
No explanations
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
            "Generating..."
        ):

            response=requests.post(
                TEXT_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            response.raise_for_status()

            data=response.json()

            raw=(
                data["choices"][0]
                ["message"]["content"]
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )

            cards=json.loads(
                raw
            )

            st.success(
                f"Generated {len(cards)} cards"
            )

            for i,card in enumerate(
                cards,
                1
            ):

                st.subheader(
                    f"Card {i}"
                )

                st.write(
                    f"**Question:** {card['front']}"
                )

                image_url=(
                    IMAGE_API_URL
                    + urllib.parse.quote(
                        card["image_prompt"]
                    )
                )

                col1,col2=st.columns(2)

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
            str(e)
        )

        try:
            st.json(
                response.json()
            )
        except:
            pass
