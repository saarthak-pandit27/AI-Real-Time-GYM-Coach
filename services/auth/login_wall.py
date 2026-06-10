import streamlit as st
from services.persistence.exercise_repository import get_or_create_user


def render_login_wall():

    if st.session_state.get("user_id") is not None:
        return True

    st.markdown("""
    <style>
    .login-card {
        max-width: 550px;
        margin: auto;
        padding: 40px;
        border-radius: 20px;
        background: rgba(22,27,34,0.85);
        border: 1px solid rgba(255,255,255,0.1);
        text-align: center;
    }

    .logo {
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 10px;
        color: white;
    }

    .subtitle {
        color: #F8FAFC;
        letter-spacing: 1px;
    }

        .feature {
            color: white;
            margin: 8px 0;
            font-size: 15px;
        }
        </style>
        """, unsafe_allow_html=True)


    st.markdown("""
    <style>
    ...
    </style>

    <div class="logo">
        🏋️ AI GYM COACH
    </div>

    <div class="subtitle">
        Train Smarter. Move Better.
    </div>

    <div class="feature">✓ Real-time Pose Detection</div>
    <div class="feature">✓ AI Voice Coaching</div>

""", unsafe_allow_html=True)


    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):

        st.markdown(
    """
    <div style="
        color:white;
        font-size:16px;
        font-weight:600;
        margin-bottom:8px;
        margin-top:20px;
    ">
        Username
    </div>
    """,
    unsafe_allow_html=True
)

        username = st.text_input(
            "",
            placeholder="👤 Enter your username e.g.shashwat",
            label_visibility="collapsed"
        )

        submit_button = st.form_submit_button(
            "🚀 START TRAINING",
            use_container_width=True
        )

    if submit_button:

        if not username:
            st.error("Please enter a username.")
            return False

        user = get_or_create_user(username)

        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]

        st.rerun()

    return False