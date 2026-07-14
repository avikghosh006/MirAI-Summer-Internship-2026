import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

PERSONALITIES = [
    "Common Indian Man",
    "Crazy Salman Khan Fan",
    "Little Boy",
    "Motivational Coach",
    "Software Engineer",
    "College Professor",
    "Stand-up Comedian",
    "Entrepreneur",
    "Friendly Teacher",
    "AI Assistant"
]

def init_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("API Key not found. Please ensure it is set in your .env file.")
        st.stop()
    return genai.Client(api_key=api_key)

def main():
    st.set_page_config(page_title="AI Multiverse", layout="centered")
    client = init_gemini_client()
    
    with st.sidebar:
        st.title("Multiverse Controls")
        
        selected_persona = st.selectbox(
            "Choose Personality",
            options=PERSONALITIES
        )
        
        st.divider()
        # Manual clear button works exactly as intended
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            
    # Task 1: Initialize the Memory Vault
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_persona" not in st.session_state:
        st.session_state.current_persona = selected_persona
        
    if st.session_state.current_persona != selected_persona:
        st.session_state.current_persona = selected_persona
        st.toast(f"Switched universe to: {selected_persona}")

    st.title("AI Multiverse")
    st.caption(f"Currently talking to: **{selected_persona}**")
    st.divider()

    # Task 2: Render Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Task 3: Upgrade Input UI
    if prompt := st.chat_input(f"Say something to the {selected_persona}..."):
        
        # Task 4: Save User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        formatted_history = []
        for msg in st.session_state.messages:
            api_role = "user" if msg["role"] == "user" else "model"
            formatted_history.append(
                types.Content(role=api_role, parts=[types.Part.from_text(text=msg["content"])])
            )

        system_instruction = (
            f"You are acting as {selected_persona}. "
            "Always stay in character. "
            "Reply strictly according to that personality. "
            "Keep your answers interesting, natural, and highly conversational."
        )

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=formatted_history,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.7 
                        )
                    )
                    
                    answer = response.text
                    st.markdown(answer)
                    
                    # Task 4: Save AI Message
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Communication error: {e}")

if __name__ == "__main__":
    main()
