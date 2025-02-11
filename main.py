# main.py
import streamlit as st
from src.llm import initialize_llm, generate_response
from src.auth import get_linkedin_auth_url, authenticate_linkedin, authenticate_google

# Initialize session state for navigation, authentication, and chat history
if "page" not in st.session_state:
    st.session_state.page = "home"  # pages: home, login, chat
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def home_page():
    st.title("Welcome to Yukti")
    st.markdown("""
    **Yukti** is your Research Assistant that uses advanced AI, web surfing, and more to provide up-to-date answers.
    """)
    if st.button("Get Started"):
        st.session_state.page = "login"
        st.experimental_rerun()

def login_page():
    st.title("Login")
    st.markdown("Choose your preferred login method:")

    # Check for LinkedIn OAuth callback using st.query_params
    query_params = st.query_params
    if "code" in query_params:
        user_info = authenticate_linkedin()
        if user_info:
            st.session_state.user_info = user_info
            st.session_state.authenticated = True
            st.session_state.page = "chat"
            st.experimental_rerun()
        else:
            st.error("LinkedIn authentication failed. Please try again.")

    # Provide login options for LinkedIn and Google
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign in with LinkedIn"):
            # Provide a clickable link to redirect the user to LinkedIn for authentication
            auth_url = get_linkedin_auth_url()
            st.markdown(f"[Click here to authenticate with LinkedIn]({auth_url})", unsafe_allow_html=True)
    with col2:
        if st.button("Sign in with Google"):
            # Simulate Google authentication (replace with your Firebase integration)
            user_info = authenticate_google()
            if user_info:
                st.session_state.user_info = user_info
                st.session_state.authenticated = True
                st.session_state.page = "chat"
                st.experimental_rerun()
            else:
                st.error("Google authentication failed. Please try again.")

def chat_page():
    if not st.session_state.authenticated:
        st.error("You must be logged in to access the chat page.")
        st.session_state.page = "login"
        st.experimental_rerun()
        return

    # Determine the user's name; adjust keys based on your LinkedIn user info structure
    username = st.session_state.user_info.get("firstName") or st.session_state.user_info.get("username", "User")
    st.title(f"Namashkar {username}, welcome to Yukti")
    
    # Initialize the LLM client
    try:
        llm_client = initialize_llm()
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        return

    # Layout: main chat area and sidebar for previous searches
    main_col, sidebar_col = st.columns([3, 1])
    
    with main_col:
        chat_container = st.container()
        # Display conversation history
        if st.session_state.chat_history:
            for chat in st.session_state.chat_history:
                st.markdown(f"**You:** {chat['user']}")
                st.markdown(f"**Yukti:** {chat['ai']}")
        else:
            st.info("Start your conversation with Yukti!")
        
        # Input area for new query
        user_input = st.text_area("Enter your query:", key="user_input", height=100)
        if st.button("Send"):
            if user_input.strip():
                with chat_container:
                    st.markdown("**You:**")
                    st.markdown(f"```{user_input}```")
                with st.spinner("Yukti is thinking..."):
                    try:
                        response = generate_response(llm_client, user_input)
                        if response:
                            with chat_container:
                                st.markdown("**Yukti:**")
                                st.markdown(response)
                            # Save conversation history for memory/tracking
                            st.session_state.chat_history.append({
                                "user": user_input,
                                "ai": response
                            })
                        else:
                            st.error("Failed to generate a response. Please try again.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
    
    with sidebar_col:
        st.sidebar.header("Previous Searches")
        if st.session_state.chat_history:
            for idx, chat in enumerate(st.session_state.chat_history, start=1):
                st.sidebar.markdown(f"**{idx}.** {chat['user']}")
        else:
            st.sidebar.info("No previous searches yet.")

def main():
    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "chat":
        chat_page()
    else:
        st.error("Page not found.")

if __name__ == "__main__":
    main()
