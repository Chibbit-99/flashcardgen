import json
import requests
import streamlit as st

# 1. Page Configuration
st.set_page_config(page_title="AI Flashcard Generator", page_icon="🎴", layout="centered")

# 2. Configuration Settings
# Replace this string with your real public App Key (starts with pk_)
POLLINATIONS_APP_KEY = "pk_AthVUCdXSHpixSqN"

TEXT_API_URL = "https://pollinations.ai"
IMAGE_API_URL = "https://pollinations.ai"

# 3. Check for User Authentication Token
# Pollinations redirects back to your site with '?token=sk_...' in the URL
query_params = st.query_params
user_token = query_params.get("token", None)

# 4. App Headers
st.title("🎴 AI Flashcard Deck Generator")
st.caption("Flower Tier BYOP (Bring Your Own Pollen) Edition")

if not user_token:
    # --- AUTHENTICATION SCREEN ---
    st.info("Welcome! To protect developer budgets, this app uses Pollinations 'Bring Your Own Pollen'.")
    
    # Dynamically find the current deployment URL to redirect users back correctly
    current_url = st.empty()
    # Fallback to local testing if not running on Streamlit Cloud
    base_url = "http://localhost:8501" 
    
    # Construct the secure Pollinations authentication link
    auth_url = f"https://pollinations.ai{POLLINATIONS_APP_KEY}&redirect_uri={base_url}&response_type=token"
    
    st.markdown(
        f'<a href="{auth_url}" target="_self" style="display: inline-block; padding: 0.5em 1em; '
        f'color: white; background-color: #FF4B4B; border-radius: 5px; text-decoration: none; '
        f'font-weight: bold;">🔑 Connect Your Pollinations Account</a>',
        unsafe_allow_html=True
    )
    st.stop() # Freeze the app here until they click and return with a token

else:
    # --- ACTIVE APPLICATION SCREEN ---
    st.success("🔒 Authenticated! Successfully utilizing your personal pollen balance.")
    
    if st.button("🔄 Log Out / Clear Session"):
        st.query_params.clear()
        st.rerun()

    st.markdown("---")

    # Inputs
    topic = st.text_input("Enter a study topic:", "Human Anatomy")
    count = st.slider("Number of flashcards:", min_value=1, max_value=5, value=3)

    if st.button("Generate Deck ✨", type="primary"):
        with st.spinner("Generating flashcards and custom illustrations..."):
            
            # Setup headers using the user's temporary secret key
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
                "model": "openai"
            }
            
            try:
                # Request text data
                res = requests.post(TEXT_API_URL, json=payload, headers=headers)
                res.raise_for_status()
                
                # Clean up formatting anomalies
                clean_text = res.text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                elif clean_text.startswith("```"):
                    clean_text = clean_text.split("```")[1].split("```")[0].strip()
                
                flashcards = json.loads(clean_text)
                
                # Render deck to interface
                for idx, card in enumerate(flashcards, 1):
                    with st.container():
                        st.markdown(f"### Card {idx}: {card['front']}")
                        
                        encoded_prompt = requests.utils.quote(card['image_prompt'])
                        full_img_url = f"{IMAGE_API_URL}{encoded_prompt}?width=500&height=300&nologo=true"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.image(full_img_url, caption="AI Visual Aid", use_container_width=True)
                        with col2:
                            with st.expander("Reveal Answer 🔍"):
                                st.write(card['back'])
                        st.markdown("---")
                        
            except Exception as e:
                st.error(f"Generation failed. Your key might be out of pollen or the response was malformed. Error: {e}")
