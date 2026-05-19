import streamlit as st
import streamlit.components.v1 as components
import requests
import urllib.parse
import json

# ==========================================
# PAGE SETUP
# ==========================================

st.set_page_config(
    page_title="AI Flashcard Generator",
    page_icon="🎴",
    layout="centered"
)

st.title("🎴 AI Flashcard Generator")
st.caption("🌸 Bring Your Own Pollen (Flower Tier)")

# ==========================================
# CONFIG
# ==========================================

CLIENT_ID = "pk_AthVUCdXSHpixSqN"
APP_URL = "https://flashcardgenbychibbit.streamlit.app"

TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://image.pollinations.ai/prompt/"

# ==========================================
# GET api_key FROM URL FRAGMENT
# Pollinations returns:
# site.com/#api_key=sk_xxx
# ==========================================

fragment_value = components.html(
    """
<script>
const hash = window.parent.location.hash;

if(hash){

    const params = new URLSearchParams(
        hash.substring(1)
    );

    const key = params.get(
        "api_key"
    );

    if(key){
        document.write(key);
    }
}
</script>
""",
    height=0
)

# ==========================================
# LOAD KEY
# ==========================================

api_key = ""

query_key = st.query_params.get(
    "api_key",
    ""
)

if isinstance(query_key, list):
    query_key = query_key[0]

query_key = str(query_key)

if query_key:
    api_key = query_key

elif fragment_value:

    api_key = str(
        fragment_value
    ).strip()

# save login
if api_key:
    st.session_state[
        "api_key"
    ] = api_key

# restore login
if (
    not api_key
    and "api_key"
    in st.session_state
):
    api_key = st.session_state[
        "api_key"
    ]

# ==========================================
# LOGIN
# ==========================================

if not api_key:

    auth_params = {
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
            auth_params
        )
    )

    st.info(
        "Authenticate using your own Pollen account."
    )

    st.link_button(
        "🌸 Sign in with Pollinations",
        auth_url
    )

    st.caption(
        "Generation uses YOUR pollen balance."
    )

    st.stop()

# ==========================================
# SUCCESS
# ==========================================

st.success(
    "Logged in successfully"
)

if st.button(
    "Logout"
):

    if "api_key" in st.session_state:
        del st.session_state[
            "api_key"
        ]

    st.query_params.clear()

    st.rerun()

st.markdown("---")

# ==========================================
# INPUTS
# ==========================================

topic = st.text_input(
    "Study topic",
    "Neuroanatomy"
)

count = st.slider(
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

    headers = {
        "Authorization":
        f"Bearer {api_key}",

        "Content-Type":
        "application/json"
    }

    payload = {

        "model":
        "openai",

        "messages":[
            {
                "role":"system",

                "content":
"""
Return ONLY valid JSON:

[
{
"front":"",
"back":"",
"image_prompt":""
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

            cards = json.loads(
                raw
            )

            st.success(
                f"Generated {len(cards)} cards"
            )

            for i,card in enumerate(
                cards,
                1
            ):

                st.markdown(
                    f"## Card {i}"
                )

                st.subheader(
                    card["front"]
                )

                prompt = urllib.parse.quote(
                    card[
                        "image_prompt"
                    ]
                )

                image_url = (
                    f"{IMAGE_API_URL}"
                    f"{prompt}"
                    f"?width=600"
                    f"&height=350"
                    f"&nologo=true"
                )

                col1,col2=st.columns(
                    2
                )

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
                            card[
                                "back"
                            ]
                        )

                st.markdown(
                    "---"
                )

    except Exception as e:

        st.error(
            f"Error: {e}"
        )

        try:
            st.json(
                response.json()
            )

        except:
            pass
