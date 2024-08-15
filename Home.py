import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import streamlit_shadcn_ui as ui

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('cold-email-generator-137f6-0709e66e9bba.json')
    firebase_admin.initialize_app(cred)

def login(email, password):
    try:
        user = auth.get_user_by_email(email)
        # For demo purposes, assuming password validation here.
        if password:  # Replace this with actual password validation
            st.session_state.logged_in = True
            st.session_state.page = "Cold-email"  # Set the page to redirect
        else:
            st.warning('Invalid credentials')
    except Exception as e:
        st.warning(f'Login Failed: {e}')

def signup(username, email, password):
    try:
        auth.create_user(email=email, password=password, display_name=username)
        st.session_state.signup_successful = True
        st.session_state.page = "login"  # Set the page to show login form
    except Exception as e:
        st.error(f"Error creating account: {e}")

def main():
    # Initialize session state variables if not already present
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'signup_successful' not in st.session_state:
        st.session_state.signup_successful = False
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    # Check if the user is logged in and redirect if necessary
    if st.session_state.logged_in:
        if st.session_state.page != "Cold-email":
            st.session_state.page = "Cold-email"

    # Display the appropriate page based on session state
    if st.session_state.page == "Cold-email":
        if st.session_state.logged_in:
            st.success("Log in successful! Click on Cold-email on side-bar to start creating your mails.")
            st.markdown("""
            ### Welcome to the Cold Email Generator!
            
            You can now utilize our AI-powered tools to craft effective cold emails tailored to your industry and business needs.

            - Use the sidebar to navigate and fill out the necessary details.
            - Once you have filled in the details, click 'Generate Cold Email' to see the results.
            """)
            st.stop()  # Stop further processing to show the cold email page content

    if st.session_state.signup_successful:
        st.session_state.signup_successful = False
        st.info("Sign up successful! Please log in to access precisionReach.")

    st.title("Welcome to :blue[precisionReach]")
    st.markdown("#### The ultimate tool for generating effective cold emails using AI.")

    with st.container():
        st.image("assets/precisionReach.png", use_column_width=True)

    # Use Shadcn tabs for Login/Signup choice
    selected_tab = ui.tabs(['Login', 'Sign Up'], selected_index=0)

    if selected_tab == 'Login':
        with st.form(key='login_form', clear_on_submit=True):
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            submit_button = st.form_submit_button('Login')
            if submit_button:
                login(email, password)

    elif selected_tab == 'Sign Up':
        with st.form(key='signup_form', clear_on_submit=True):
            username = st.text_input('Username')
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            submit_button = st.form_submit_button('Sign Up')
            if submit_button:
                signup(username, email, password)

    # Additional CSS for styling
    st.markdown(
        """
        <style>
        .login-form, .signup-form {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin: 10px 0;
        }
        .stTabs [role="tablist"] {
            display: flex;
            justify-content: center;
            margin: 10px 0;
        }
        .stTabs [role="tab"] {
            padding: 10px 20px;
            margin: 0 5px;
            border: none;
            border-radius: 8px;
            background-color: #e0e0e0;
            cursor: pointer;
            font-size: 16px;
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background-color: #6200ee;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True
    )

def set_query_params_via_js(page):
    js_code = f"""
    <script>
    function setQueryParams() {{
        const url = new URL(window.location);
        url.searchParams.set('page', '{page}');
        window.history.pushState('', '', url);
    }}
    setQueryParams();
    window.location.reload();
    </script>
    """
    st.components.v1.html(js_code, height=0)

if __name__ == "__main__":
    main()
