import streamlit as st
import requests
import random 
from urllib.parse import quote

st.set_page_config(
    page_title="AI Image Studio"
)

st.title("MY AI IMAGE GENERATOR")
st.write("Generate AI images using Pollinations AI")

st.sidebar.header("Settings")

art_style = st.sidebar.selectbox(
    "Select Art Style",
    ["Photorealistic", "Anime", "Vintage Victorian", "Sketch", "3D Render", 
     "Cyberpunk", "Watercolor", "Oil Painting", "Pixar Style"]
)

width = st.sidebar.slider("Image Width", min_value=256, max_value=1024, value=512, step=64)
height = st.sidebar.slider("Image Height", min_value=256, max_value=1024, value=512, step=64)

# TASK 3: Added Magic Enhance Toggle
magic_enhance = st.sidebar.checkbox("Enable Magic Enhance")

# Prompt & Buttons
user_prompt = st.text_area("Describe the image", placeholder="Example: A futuristic city at sunset")

# TASK 4: Created a list of surprise prompts
surprise_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A cute golden retriever wearing steampunk goggles",
    "A majestic treehouse glowing in a bioluminescent forest",
    "A giant octopus playing chess with a submarine"
]

# Side-by-side buttons for a cleaner UI
col1, col2 = st.columns(2)
with col1:
    generate_btn = st.button("Generate Image")
with col2:
    surprise_btn = st.button("Surprise Me !!")

if surprise_btn:
    user_prompt = random.choice(surprise_prompts)

# Generation Logic
# Run generation if EITHER button is clicked
if generate_btn or surprise_btn:
    
    if user_prompt.strip() == "":
        st.warning("Please enter a prompt.")
        st.stop()

    with st.spinner("Generating image..."):
        
        full_prompt = f"{user_prompt}, high quality, {art_style}, masterpiece, detailed"
        
        # TASK 3: Append boost words if Magic Enhance is checked
        if magic_enhance:
            full_prompt += ", masterpiece, 8k resolution, highly detailed, trending on artstation, unreal engine 5 render"

        encoded_prompt = quote(full_prompt)

        # TASK 1: Injected width and height as URL parameters
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}"

        try:
            response = requests.get(url, timeout=90)

            if response.status_code == 200:
                st.success("✅ Image Generated Successfully!")
                st.image(response.content, caption=full_prompt, width='stretch')

                # TASK 2: Dynamic file naming and .png extension fix
                st.download_button(
                    label="⬇ Download Image",
                    data=response.content,
                    file_name=f"{art_style}_image.png",
                    mime="image/png"
                )
            else:
                st.error(f"API Error: {response.status_code}")

        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Unable to connect to Pollinations AI.")
        except Exception as e:
            st.error(f"Error: {e}")
