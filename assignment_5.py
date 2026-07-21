import streamlit as st
import os, json, requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from gtts import gTTS

load_dotenv()
st.title("AI Visual Novel Engine")

@st.cache_resource
def gen_ai_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = gen_ai_client()

st.sidebar.header("Story Settings")
genre = st.sidebar.selectbox("Story Genre", ["Fantasy", "Sci-Fi", "Horror", "Mystery", "Cyberpunk"])
art_style = st.sidebar.selectbox("Art Style", ["Anime", "Watercolor", "Pixel Art", "Photorealistic", "Comic Book"])

for key, default in [("messages", []), ("gemini_chat", None), ("story", None)]:
    if key not in st.session_state:
        st.session_state[key] = default

SYSTEM_PROMPT = (
    "You are a visual novel narrator. Every reply MUST be a single JSON object with exactly three keys: "
    "'story_text' (a short narrative paragraph), 'image_prompt' (a detailed, vivid text-to-image prompt "
    "describing the current scene), and 'options' (a list of 2-3 short strings for what the user can do next). "
    "No text outside the JSON."
)

def start_story():
    st.session_state.gemini_chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )
    st.session_state.messages = []
    send_turn(f"Start a {genre} story, illustrated in {art_style} style. Set the opening scene.")

def parse_story_json(raw_text):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        cleaned = raw_text.strip().strip("`").replace("json\n", "", 1)
        return json.loads(cleaned)  
    
def fetch_image(prompt):
    try:
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=768&height=512&nologo=true"
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return resp.content
    except Exception:
        st.toast("Image server is busy, skipping visual...")
        return None

def synthesize_audio(text):
    try:
        tts = gTTS(text=text)
        path = "narration.mp3"
        tts.save(path)
        return path
    except Exception:
        st.toast("TTS service is busy, skipping narration...")
        return None

def send_turn(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    try:
        with st.spinner("The story unfolds..."):
            response = st.session_state.gemini_chat.send_message(user_input)
        data = parse_story_json(response.text)
    except Exception as e:
        st.toast(f"Story engine hiccup: {e}")
        return

    image_bytes = fetch_image(data.get("image_prompt", ""))
    audio_path = synthesize_audio(data.get("story_text", ""))

    st.session_state.story = {
        "story_text": data.get("story_text", ""),
        "options": data.get("options", []),
        "image_bytes": image_bytes,
        "audio_path": audio_path,
    }
    st.session_state.messages.append({"role": "narrator", "content": data.get("story_text", "")})

if st.sidebar.button("Start New Story"):
    start_story()

if len(st.session_state.messages) > 1:
    with st.expander("View Story History"):
        for msg in st.session_state.messages[:-1]: # We use [:-1] to exclude the current scene
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

if st.session_state.story:
    story = st.session_state.story
    st.write(story["story_text"])

    if story["image_bytes"]:
        st.image(story["image_bytes"])
    if story["audio_path"]:
        st.audio(story["audio_path"])

    st.subheader("What do you do?")
    cols = st.columns(len(story["options"]) or 1)
    for i, option in enumerate(story["options"]):
        if cols[i].button(option, key=f"opt_{i}_{len(st.session_state.messages)}"):
            send_turn(option)
            st.rerun()
else:
    st.info("Choose your Genre and Art Style, then click **Start New Story** in the sidebar.")

if st.session_state.messages:
    output = "CHAT HISTORY:\n"
    for msg in st.session_state.messages:
        output += f"{msg['role']}: {msg['content']}\n"
    st.sidebar.download_button("Download Story Log", data=output, file_name="story_log.txt", mime="text/plain")
