import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from supabase_client import get_supabase

st.set_page_config(page_title="PrecisionReach", page_icon="assets/scaletific_icon.png", layout="centered")

# ── Hide Streamlit branding ──
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

def login(email: str, password: str) -> bool:
    try:
        sb = get_supabase()
        response = sb.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state["user"] = response.user
        st.session_state["logged_in"] = True
        return True
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def signup(username: str, email: str, password: str) -> bool:
    try:
        sb = get_supabase()
        response = sb.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"username": username}}
        })
        if response.user:
            # Create user profile manually (more reliable than DB trigger)
            try:
                sb.table("user_profiles").upsert({
                    "id": response.user.id,
                    "run_count": 0,
                    "is_paid": False
                }).execute()
            except Exception:
                pass  # Profile creation is non-blocking
            st.session_state["user"] = response.user
            st.session_state["logged_in"] = True
            return True
        return False
    except Exception as e:
        st.error(f"Sign up failed: {str(e)}")
        return False

def main():
    # Already logged in — go straight to app
    if st.session_state.get("logged_in"):
        switch_page("Cold-Email")
        return

    st.title("Welcome to :blue[precisionReach]")
    st.markdown("#### AI-powered cold email generation for smarter outreach.")

    try:
        st.image("assets/precisionReach.png", use_container_width=True)
    except Exception:
        pass

    tab = st.tabs(["Login", "Sign Up"])

    with tab[0]:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                if login(email, password):
                    switch_page("Cold-Email")

    with tab[1]:
        with st.form("signup_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            st.caption("Password must be at least 6 characters.")
            if st.form_submit_button("Create Account", use_container_width=True):
                if signup(username, email, password):
                    st.success("Account created! Redirecting...")
                    switch_page("Cold-Email")

if __name__ == "__main__":
    main()
