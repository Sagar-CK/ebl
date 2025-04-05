import streamlit as st
import requests
import json
import uuid


st.set_page_config(page_title="AI Planner", layout="centered")

st.title("🏋️ Muscle AI Chat Plan")

# Session state to persist messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "What is your goal?"}
    ]
    

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# Input form
with st.form(key="chat_form"):
    user_message = st.text_input("Your message", key="message_input")
    photo_urls = st.text_area("Photo URLs (one per line)", height=100)
    submitted = st.form_submit_button("Send")

# Submit and stream response
if submitted and user_message.strip():
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Build request body
    data = {
        #based on time random session id
        "session_id": st.session_state.session_id,
        "focus": "muscle",
        "messages": st.session_state.messages,
        "photo_urls": [url.strip() for url in photo_urls.splitlines() if url.strip()],
    }

    # Stream response using SSE
    response_placeholder = st.empty()
    full_response = ""
    try:
        # Sending the POST request to FastAPI endpoint with stream=True
        with requests.post("http://localhost:1337/chat/plan", json=data, stream=True) as resp:
            full_response = resp.content.decode("utf-8")

        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(f"Error during stream: {e}")

# Show chat history
st.markdown("### Chat History")
for msg in st.session_state.messages:
    role = "🧍‍♂️ You" if msg["role"] == "user" else "🤖 AI"
    st.markdown(f"**{role}:** {msg['content']}")