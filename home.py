import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# Check if the Firebase app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('cold-email-generator-137f6-11c68d6eb9b6.json')
    firebase_admin.initialize_app(cred)

def login(email, password):
    try:
        user = auth.get_user_by_email(email)
        # For demo purposes, assuming password validation here.
        st.session_state.logged_in = True
        st.experimental_set_query_params(page="cold-email")  # Set query param for redirection
        st.experimental_set_query_params(reload=True)
    except Exception as e:
        st.warning(f'Login Failed: {e}')

def signup(username, email, password):
    try:
        auth.create_user(email=email, password=password, display_name=username)
        st.success("Account created successfully")
        st.markdown("Please login using email and password")
    except Exception as e:
        st.error(f"Error creating account: {e}")

def main():
    # Check query parameters
    query_params = st.experimental_get_query_params()
    page = query_params.get("page", ["home"])[0]

    if page == "cold-email" and st.session_state.get("logged_in", False):
        st.experimental_set_query_params(page="cold-email")
        st.stop()  # Stop the script here to avoid further processing and display the current page

    st.title("Welcome to :blue[precisionReach]")
    st.markdown("#### The ultimate tool for generating effective cold emails using AI.")

    with st.container():
        st.image("https://via.placeholder.com/800x200.png?text=Cold+Email+Generator", use_column_width=True)

    choice = st.selectbox('Login/Signup', ['Login', 'Sign Up'], index=0)

    if choice == 'Login':
        with st.form(key='login_form'):
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            submit_button = st.form_submit_button('Login')
            if submit_button:
                login(email, password)

    elif choice == 'Sign Up':
        with st.form(key='signup_form'):
            username = st.text_input('Username')
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            submit_button = st.form_submit_button('Sign Up')
            if submit_button:
                signup(username, email, password)

if __name__ == "__main__":
    main()
