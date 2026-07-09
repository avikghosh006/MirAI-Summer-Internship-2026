import streamlit as st

st.title("Echo Chamber 9000")
st.write("Welcome to the interface. Please enter your identity and the data you wish to transmit.")

user_name = st.text_input("Name:").strip()
user_message = st.text_input("Message:").strip()

if st.button("Send"):
    if not user_name:
        st.error("Please provide your name first.")
    elif not user_message:
        st.warning("Please type a message to transmit.")
    else:
        st.success(f'''Message sent successfully !!
                   Greetings, {user_name}. We received your message: {user_message}''')
        
        char_length = len(user_message)
        token_count = char_length / 4

        st.info(f"System Check: Your message will consume approximately {token_count} tokens from our context window.")
