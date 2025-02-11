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

def get_linkedin_auth_url():
    """Construct the LinkedIn authorization URL."""
    params = {
        "response_type": "code",
        "client_id": LINKEDIN_CLIENT_ID,
        "redirect_uri": LINKEDIN_REDIRECT_URI,
        "scope": " ".join(LINKEDIN_SCOPE),
        "state": "random_state_string"  # In production, generate a secure random state
    }
    return f"{LINKEDIN_AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code):
    """Exchange authorization code for an access token."""
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

def get_linkedin_user_info(access_token):
    """Fetch user profile and email from LinkedIn using the access token."""
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

def linkedin_callback():
    """
    Process the OAuth callback. If a 'code' parameter exists in the URL,
    exchange it for an access token and retrieve the user's information.
    """
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        try:
            token = exchange_code_for_token(code)
            user_info = get_linkedin_user_info(token)
            return user_info
        except Exception as e:
            st.error(f"LinkedIn authentication failed: {e}")
            return None
    return None

def authenticate_linkedin():
    """
    Main function to handle LinkedIn authentication.
    
    Returns a user info dict if successful, or None otherwise.
    """
    # Check if we are on the OAuth callback
    user_info = linkedin_callback()
    if user_info:
        st.success(f"Welcome, {user_info['firstName']} {user_info['lastName']}")
    return user_info

# Placeholder for Google authentication (to be implemented with Firebase)
def authenticate_google():
    """
    Placeholder for Google authentication using Firebase.
    Replace this with your actual Google/Firebase authentication logic.
    """
    # TODO: Implement Firebase authentication and user data storage
    return {"username": "GoogleUser", "provider": "Google"}
