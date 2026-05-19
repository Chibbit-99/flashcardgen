import json
import requests
import streamlit as st

# 1. Page Layout
st.set_page_config(page_title="AI Flashcard Generator", page_icon="🎴", layout="centered")

# ==========================================
# ⚙️ CONFIGURATION - SET THESE ONCE!
# ==========================================
POLLINATIONS_APP_KEY = "pk_athvucdxshpixsqn"  

# CRITICAL: Replace this string with your exact live deployed Streamlit URL
# Examples: "https://streamlit.app" or "http://localhost:8501" if testing locally
MY_APP_LIVE_URL = "https://flashcardgenbychibbit.streamlit.app/" 
# ==========================================

# Official Unified Pollinations V2 API Endpoints
TEXT_API_URL = "https://gen.pollinations.ai/v1/chat/completions"
IMAGE_API_URL = "https://gen.pollinations.ai/image/"

# Grab redirect token safely from query strings
query_params = st.query_params
user_token = query_params.get("token", None)

st.title("🎴 AI Flashcard Deck Generator")
st.caption("⚡ Powered by Pollinations.ai (Flower Tier BYOP Edition)")

if not user_token:
    # --- AUTHENTICATION SCREEN ---
    st.info("👋 Welcome! To protect server budgets, this application uses 'Bring Your Own Pollen'.")
    
    # Perfectly structured OAuth 2.0 URL using the correct query parameters
    auth_url = f"https://pollinations.ai{POLLINATIONS_APP_KEY}&redirect_uri={MY_APP_LIVE_URL}&response_type=token"
    
    st.markdown(
        f'<a href="{auth_url}" target="_self" style="display: inline-block; padding: 0.6em 1.2em; '
        f'color: white; background-color: #FF4B4B; border-radius: 6px; text-decoration: none; '
        f'font-weight: bold; text-align: center; box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">'
        f'🔑 Connect Your Pollinations Account</a>',
        unsafe_allow_html=True
    )
    st.stop()  # Halt execution until token lands

else:
    # --- ACTIVE GENERATOR APPLICATION ---
    st.success("🔒 Authenticated via visitor's Pollen account balance.")
    
    if st.button("🔄 Disconnect Session / Log Out"):
        st.query_params.clear()
        st.rerun()

    st.markdown("---")

    topic = st.text_input("Enter a study topic:", "Neuroanatomy")
    count = st.slider("Number of flashcards:", min_value=1, max_value=5, value=3)

    if st.button("Generate Deck ✨", type="primary"):
        with st.spinner("Generating flashcards and querying illustrations..."):
            
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            }
            
            system_prompt = (
                "You are an educational assistant. Output ONLY a valid JSON array. "
                "Do not use markdown backticks, code blocks, or introduction text. "
                "Each object inside the array must exactly have these string keys: 'front', 'back', 'image_prompt'."
            )
            user_prompt = f"Generate exactly {count} flashcards about '{topic}'. Make the 'image_prompt' descriptive and graphical."
            
            payload = {
                "model": "openai",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"}  
            }
            
            try:
                res = requests.post(TEXT_API_URL, json=payload, headers=headers)
                res.raise_for_status()
                
                response_json = res.json()
                raw_text = response_json['choices']['message']['content'].strip()
                
                # Cleanup any accidental code block backticks
                if raw_text.startswith("```json"):
                    raw_text = raw_text.split("```json").split("```").strip()
                elif raw_text.startswith("```"):
                    raw_text = raw_text.split("```").split("```").strip()
                
                flashcards = json.loads(raw_text)
                
                # Render results to the Streamlit UI dashboard
                for idx, card in enumerate(flashcards, 1):
                    with st.container():
                        st.markdown(f"### Card {idx}: {card['front']}")
                        
                        encoded_prompt = requests.utils.quote(card['image_prompt'])
                        full_img_url = f"{IMAGE_API_URL}{encoded_prompt}?width=500&height=300&nologo=true&key={user_token}"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(full_img_url, caption="AI Conceptual Diagram", use_container_width=True)
                        with col2:
                            with st.expander("Reveal Answer 🔍"):
                                st.write(card['back'])
                        st.markdown("---")
                        
            except Exception as e:
                st.error(f"Generation Engine Failure. Ensure your wallet has sufficient Pollen credits. Details: {e}")
