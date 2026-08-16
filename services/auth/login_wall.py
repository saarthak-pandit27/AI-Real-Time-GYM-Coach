import streamlit as st
import re
from services.persistence.exercise_repository import authenticate_user, register_user


def clean_html(html_str: str) -> str:
    """Removes all leading whitespace from every line to prevent Markdown code block wrapping."""
    return re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    st.markdown(
        clean_html("""
        <style>
        .login-wrapper {
            padding: 10px 0;
            width: 100%;
        }
        .login-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 22px;
            border-radius: 24px;
            background: rgba(0, 255, 136, 0.15);
            border: 1px solid rgba(0, 255, 136, 0.4);
            color: #00FF88;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 14px;
            font-weight: 800;
            letter-spacing: 2px;
            margin-bottom: 18px;
            text-transform: uppercase;
            box-shadow: 0 0 25px rgba(0, 255, 136, 0.3);
        }
        .login-title {
            font-size: 54px;
            font-weight: 900;
            line-height: 1.15;
            background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, #00FF88 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 18px;
            letter-spacing: -1px;
        }
        .login-subtitle {
            color: #94A3B8;
            font-size: 20px;
            line-height: 1.6;
            margin-bottom: 32px;
        }
        .login-stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 24px;
            width: 100%;
        }
        .login-stat-card {
            background: linear-gradient(135deg, rgba(18, 26, 47, 0.85) 0%, rgba(10, 15, 29, 0.95) 100%);
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-radius: 22px;
            padding: 24px 22px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.4);
        }
        .login-stat-val {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 30px;
            font-weight: 900;
            color: #00E5FF;
            margin-bottom: 6px;
        }
        .login-stat-lbl {
            font-size: 14px;
            color: #94A3B8;
            font-weight: 600;
        }

        /* Scaled Up Athlete Access Portal Styling */
        .auth-header-title {
            font-size: 38px;
            font-weight: 900;
            color: #FFFFFF;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
            background: linear-gradient(135deg, #FFFFFF 0%, #00FF88 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .auth-header-sub {
            font-size: 18px;
            color: #94A3B8;
            margin-bottom: 24px;
            line-height: 1.5;
        }
        
        /* Larger Input Field Labels */
        .auth-input-label {
            color: #FFFFFF;
            font-weight: 800;
            font-size: 18px;
            margin-bottom: 8px;
            margin-top: 18px;
            letter-spacing: 0.5px;
        }
        </style>
        """),
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.markdown(
            clean_html("""
            <div class="login-wrapper">
                <div class="login-badge">🛡️ SECURE AI GYM ENGINE</div>
                <div class="login-title">Train Smarter with Real-Time AI Coaching</div>
                <div class="login-subtitle">
                    Experience state-of-the-art computer vision pose analysis, instant audio posture corrections, and encrypted workout telemetry tracking.
                </div>
                
                <div class="login-stats-grid">
                    <div class="login-stat-card">
                        <div class="login-stat-val">30 FPS</div>
                        <div class="login-stat-lbl">Real-time Joint Tracking</div>
                    </div>
                    <div class="login-stat-card">
                        <div class="login-stat-val">0.1s</div>
                        <div class="login-stat-lbl">Voice Audio Feedback</div>
                    </div>
                    <div class="login-stat-card">
                        <div class="login-stat-val">5 Exercises</div>
                        <div class="login-stat-lbl">Biomechanics AI Engine</div>
                    </div>
                    <div class="login-stat-card">
                        <div class="login-stat-val">256-bit</div>
                        <div class="login-stat-lbl">PBKDF2 Password Security</div>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            clean_html("""
            <div style="padding-top:10px;">
                <div class="auth-header-title">Athlete Access Portal</div>
                <div class="auth-header-sub">Sign in to your account or register to unlock AI telemetry tracking.</div>
            </div>
            """),
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_login:
            with st.form("signin_form", clear_on_submit=False):
                st.markdown("<div class='auth-input-label'>Username</div>", unsafe_allow_html=True)
                login_username = st.text_input("Username", placeholder="e.g. alex_fitness", key="login_user", label_visibility="collapsed")
                
                st.markdown("<div class='auth-input-label'>Password</div>", unsafe_allow_html=True)
                login_password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass", label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_signin = st.form_submit_button("🚀 SIGN IN & TRAIN", use_container_width=True)

            if submit_signin:
                user, err = authenticate_user(login_username, login_password)
                if err:
                    st.error(f"❌ {err}")
                else:
                    st.session_state["user_id"] = user["id"]
                    st.session_state["username"] = user["username"]
                    st.toast(f"Welcome back, {user['username']}!", icon="🔥")
                    st.rerun()

        with tab_register:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("<div class='auth-input-label'>Choose Username</div>", unsafe_allow_html=True)
                reg_username = st.text_input("Choose Username", placeholder="e.g. alex_fitness", key="reg_user", label_visibility="collapsed")
                
                st.markdown("<div class='auth-input-label'>Password (min 6 characters)</div>", unsafe_allow_html=True)
                reg_password = st.text_input("Password", type="password", placeholder="••••••••", key="reg_pass", label_visibility="collapsed")
                
                st.markdown("<div class='auth-input-label'>Confirm Password</div>", unsafe_allow_html=True)
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="reg_confirm", label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_signup = st.form_submit_button("✨ CREATE SECURE ACCOUNT", use_container_width=True)

            if submit_signup:
                if reg_password != reg_confirm:
                    st.error("❌ Passwords do not match. Please re-enter.")
                else:
                    user, err = register_user(reg_username, reg_password)
                    if err:
                        st.error(f"❌ {err}")
                    else:
                        st.session_state["user_id"] = user["id"]
                        st.session_state["username"] = user["username"]
                        st.success("🎉 Account created successfully! Launching coach...")
                        st.rerun()

    return False