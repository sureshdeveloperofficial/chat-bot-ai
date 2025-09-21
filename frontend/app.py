import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = None

def make_authenticated_request(method, endpoint, **kwargs):
    headers = kwargs.get("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    kwargs["headers"] = headers
    
    url = f"{GATEWAY_URL}{endpoint}"
    return requests.request(method, url, **kwargs)

def login(username, password):
    try:
        response = requests.post(
            f"{GATEWAY_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            st.session_state.authenticated = True
            return True, "Login successful!"
        else:
            return False, response.json().get("detail", "Login failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def register(username, email, password):
    try:
        response = requests.post(
            f"{GATEWAY_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            st.session_state.authenticated = True
            return True, "Registration successful!"
        else:
            return False, response.json().get("detail", "Registration failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def send_message(message):
    try:
        response = make_authenticated_request(
            "POST",
            "/chat",
            json={"message": message, "session_id": st.session_state.session_id}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            return True, data["response"]
        else:
            return False, response.json().get("detail", "Chat failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def upload_document(uploaded_file):
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        response = make_authenticated_request(
            "POST",
            f"/documents/upload?username={st.session_state.username}",
            files=files
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Upload failed")
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def get_chat_history():
    try:
        response = make_authenticated_request(
            "GET",
            "/chat/history"
        )
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def logout():
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.messages = []
    st.session_state.session_id = None

def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        st.title("🤖 AI Chatbot - Login")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login to your account")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", key="login_button"):
                if username and password:
                    success, message = login(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
        
        with tab2:
            st.subheader("Create a new account")
            reg_username = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            
            if st.button("Register", key="register_button"):
                if reg_username and reg_email and reg_password:
                    success, message = register(reg_username, reg_email, reg_password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    else:
        st.title("🤖 AI Chatbot")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Welcome, **{st.session_state.username}**!")
        with col2:
            if st.button("Logout"):
                logout()
                st.rerun()
        
        st.sidebar.title("📚 Document Management")
        
        uploaded_file = st.sidebar.file_uploader(
            "Upload a document",
            type=['txt', 'pdf', 'docx'],
            help="Upload documents to enhance chat responses with relevant context"
        )
        
        if uploaded_file is not None:
            if st.sidebar.button("Upload Document"):
                with st.sidebar.spinner("Uploading and processing..."):
                    success, result = upload_document(uploaded_file)
                    if success:
                        st.sidebar.success(f"Document uploaded successfully! Created {result.get('chunks_created', 0)} chunks.")
                    else:
                        st.sidebar.error(f"Upload failed: {result}")
        
        st.sidebar.subheader("💬 Chat History")
        history = get_chat_history()
        
        if history:
            for session in history[-5:]:
                session_id = session['session_id'][:8]
                message_count = len(session['messages'])
                if st.sidebar.button(f"Session {session_id} ({message_count} msgs)"):
                    st.session_state.session_id = session['session_id']
                    st.session_state.messages = []
                    for msg in session['messages']:
                        st.session_state.messages.append({
                            "role": "user",
                            "content": msg['user_message']
                        })
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": msg['ai_response']
                        })
                    st.rerun()
        
        if st.sidebar.button("New Chat"):
            st.session_state.messages = []
            st.session_state.session_id = None
            st.rerun()
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("What would you like to know?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    success, response = send_message(prompt)
                    if success:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        error_msg = f"Error: {response}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

if __name__ == "__main__":
    main()