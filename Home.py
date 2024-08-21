import sqlite3
import streamlit as st
from hashlib import sha256
import streamlit_shadcn_ui as ui
from streamlit_extras.switch_page_button import switch_page
from streamlit_custom_notification_box import custom_notification_box


# Database connection function
def get_db_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Function to authenticate user
def authenticate_user(email, password):
    conn = get_db_connection()
    c = conn.cursor()
    password_hash = sha256(password.encode()).hexdigest()
    c.execute('SELECT id FROM users WHERE email = ? AND password_hash = ?', (email, password_hash))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Function to handle login
def login(email, password):
    user_id = authenticate_user(email, password)
    if user_id:
        st.session_state["logged_in"] = True
        st.session_state["email"] = email
        st.session_state["show_alert"] = True
        st.session_state["alert_message"] = "Logged in successfully!"
    else:
        st.session_state["show_alert"] = True
        st.session_state["alert_message"] = "Login failed"

# Function to handle signup
def signup(username, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    password_hash = sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', 
                  (username, email, password_hash))
        conn.commit()
        st.session_state["show_alert"] = True
        st.session_state["alert_message"] = "Account created successfully!"
        login(email, password)  # Automatically log in the user after signup
    except sqlite3.IntegrityError:
        st.session_state["show_alert"] = True
        st.session_state["alert_message"] = "Email or Username already exists!"
    conn.close()

# Streamlit app layout
def main():
    st.title("Welcome to :blue[precisionReach]")
    st.markdown("#### The ultimate tool for generating effective cold emails using AI.")
    st.image("assets/precisionReach.png", use_column_width=True)

    # Initialize session state variables
    if "show_alert" not in st.session_state:
        st.session_state["show_alert"] = False
    if "alert_message" not in st.session_state:
        st.session_state["alert_message"] = ""
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # Shadcn tabs for Login/Signup choice
    selected_tab = ui.tabs(['Login', 'Sign Up'], selected_index=0)

    if selected_tab == 'Login':
        with st.form(key='login_form', clear_on_submit=False):
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            if st.form_submit_button('Login'):
                if login(email,password):
                  switch_page('Cold-email')

    elif selected_tab == 'Sign Up':
        with st.form(key='signup_form', clear_on_submit=False):
            username = st.text_input('Username')
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            if st.form_submit_button('Sign Up'):
                if signup(username, email, password):
                    switch_page('Cold-email')

    # Show alert dialog if needed

   
    if st.session_state.get("show_alert", False):
      styles = {'material-icons':{'color': 'red'},
          'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
          'notification-text': {'':''},
          'close-button':{'':''},
          'link':{'':''}}
      custom_notification_box(
        icon='info',
        textDisplay='We are almost done with your registration...',
        externalLink='more info',
        url=switch_page('Cold-email'),
        styles=styles,
        key="foo"
    )
    st.session_state["show_alert"] = False  # Reset so the dialog doesn't show again

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

if __name__ == "__main__":
    main()
