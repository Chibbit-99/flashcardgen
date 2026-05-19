import json
import requests
import streamlit as st

# Page Configuration
st.set_page_config(page_title="AI Flashcard Generator", page_icon="🎴", layout="centered")

# Configuration Settings
POLLINATIONS_APP_KEY = "pk_athvucdxshpixsqn"  # Your active App Key

# Modern Unified Pollinations Endpoints
TEXT_API_URL = "https://gen.pollinations.ai/text"
IMAGE_API_URL = "https://gen.pollinations.ai/image/"

# Check for User Authentication Token sent back via redirect parameters
query_params = st.query_params
user_token = query_params.get("token", None)

st.title("🎴 AI Flashcard Deck Generator")
st.caption("Flower Tier BYOP (Bring Your Own Pollen) Edition")

if not user_token:
    st.info("Welcome! To protect developer budgets, this app uses Pollinations 'Bring Your Own Pollen'.")
    
    # CRITICAL: Replace this string with your exact live deployed Streamlit URL
    # Leave it as http://localhost:8501 ONLY if you are testing on your local machine
    base_url = "https://flashcardgenbychibbit.streamlit.app/" 
    
    # Structured OAuth URL string pointing to the dedicated login engine
    auth_url = f"https://pollinations.ai{POLLINATIONS_APP_KEY}&redirect_uri={base_url}&response_type=token"
    
    st.markdown(
        f'<a href="{auth_url}" target="_self" style="display: inline-block; padding: 0.5em 1em; '
        f'color: white; background-color: #FF4B4B; border-radius: 5px; text-decoration: none; '
        f'font-weight: bold;">🔑 Connect Your Pollinations Account</a>',
        unsafe_allow_html=True
    )
    st.stop() 

else:
    st.success("🔒 Authenticated! Successfully utilizing your personal pollen balance.")
    
    if st.button("🔄 Log Out / Clear Session"):
        st.query_params.clear()
        st.rerun()

    st.markdown("---")

    topic = st.text_input("Enter a study topic:", "Human Anatomy")
    count = st.slider("Number of flashcards:", min_value=1, max_value=5, value=3)

    if st.button("Generate Deck ✨", type="primary"):
        with st.spinner("Generating flashcards and custom illustrations..."):
            
            headers = {
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "application/json"
            }
            
            system_prompt = (
                "You are an educational assistant. Output ONLY a valid JSON array. "
                "Do not use markdown backticks, code blocks, or introduction text. "
                "Each object inside the array must exactly have these string keys: 'front', 'back', 'image_prompt'."
            )
            user_prompt = f"Generate exactly {count} flashcards about '{topic}'. Make the 'image_prompt' highly visual."
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "model": "openai",
                "jsonMode": True # Tells Pollinations text engine to output raw JSON
            }
            
            try:
                res = requests.post(TEXT_API_URL, json=payload, headers=headers)
                res.raise_for_status()
                
                clean_text = res.text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                elif clean_text.startswith("```"):
                    clean_text = clean_text.split("```")[1].split("```")[0].strip()
                
                flashcards = json.loads(clean_text)
                
                for idx, card in enumerate(flashcards, 1):
                    with st.container():
                        st.markdown(f"### Card {idx}: {card['front']}")
                        
                        encoded_prompt = requests.utils.quote(card['image_prompt'])
                        # Image generation via authenticated key parameter passing
                        full_img_url = f"{IMAGE_API_URL}{encoded_prompt}?width=500&height=300&nologo=true&key={user_token}"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(full_img_url, caption="AI Visual Aid", use_container_width=True)
                        with col2:
                            with st.expander("Reveal Answer 🔍"):
                                st.write(card['back'])
                        st.markdown("---")
                        
            except Exception as e:
                st.error(f"Generation failed. Check your pollen balance or token validity. Error: {e}")
