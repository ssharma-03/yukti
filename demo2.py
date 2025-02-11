import streamlit as st
import requests
from urllib.parse import urlencode

# LinkedIn OAuth2 credentials
LINKEDIN_CLIENT_ID = "77idt0ydijr0p9"
LINKEDIN_CLIENT_SECRET = "WPL_AP1.Ec8yJNfmo0QLkYcY.3bJvNw=="
LINKEDIN_REDIRECT_URI = "http://localhost:8501/auth/linkedin/callback"
LINKEDIN_SCOPE = ["openid", "profile", "email"]

# LinkedIn OAuth2 URLs
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USER_INFO_URL = "https://api.linkedin.com/v2/me"
LINKEDIN_EMAIL_URL = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"

st.set_page_config(page_title="LinkedIn OAuth App")

# Authentication Helper Functions
def get_authorization_url():
    """Construct the LinkedIn authorization URL."""
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "scope": " ".join(LINKEDIN_SCOPE),
        "state": "random_state_string"  # Use a secure random value in production
    }
    return f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code):
    """Exchange authorization code for access token."""
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "client_id": LINKEDIN_CLIENT_ID,
        "client_secret": LINKEDIN_CLIENT_SECRET,
    }
    response = requests.post(LINKEDIN_TOKEN_URL, data=token_data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_user_info(access_token):
    """Fetch user profile and email from LinkedIn."""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    profile_response = requests.get(LINKEDIN_USER_INFO_URL, headers=headers)
    email_response = requests.get(LINKEDIN_EMAIL_URL, headers=headers)
    
    profile_response.raise_for_status()
    email_response.raise_for_status()
    
    profile_data = profile_response.json()
    email_data = email_response.json()
    
    user_info = {
        "id": profile_data.get("id"),
        "firstName": profile_data.get("localizedFirstName"),
        "lastName": profile_data.get("localizedLastName"),
        "email": email_data.get("elements", [{}])[0].get("handle~", {}).get("emailAddress"),
    }
    return user_info

# UI Logic
st.title("LinkedIn OAuth2 Authentication")

# Login Section
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None

if st.session_state["user_info"]:
    st.success(f"Welcome, {st.session_state['user_info']['firstName']} {st.session_state['user_info']['lastName']}")
    st.write(f"Email: {st.session_state['user_info']['email']}")
    if st.button("Logout"):
        st.session_state["user_info"] = None
        st.experimental_rerun()
else:
    st.write("Click the button below to log in with LinkedIn.")
    auth_url = get_authorization_url()
    if st.button("Login with LinkedIn"):
        st.markdown(f"[Authenticate Here]({auth_url})")

# Handle Redirect Callback
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"][0]
    try:
        token = exchange_code_for_token(code)
        user_info = get_user_info(token)
        st.session_state["user_info"] = user_info
        st.success("Login Successful!")
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Authentication failed: {e}")