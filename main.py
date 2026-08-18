import streamlit as st
import os
import time
import re
from dotenv import load_dotenv
import pandas as pd
from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import load_css, inject_local_font, inject_webrtc_styles, suppress_injected_script_text
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.exercise_repository import (
    get_users_exercises,
    add_exercise
)
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio

load_dotenv()


def clean_html(html_str: str) -> str:
    """Removes all leading whitespace from every line to prevent Markdown code block wrapping."""
    return re.sub(r'^\s+', '', html_str, flags=re.MULTILINE)


def main():
    st.set_page_config(
        page_icon="🏋️‍♂️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="wide"
    )

    load_css(os.path.join(os.getcwd(), "static", "style.css"))
    inject_local_font(os.path.join(os.getcwd(), "static", "AdobeClean.otf"), "AdobeClean")
    suppress_injected_script_text()

    init_db()

    if not render_login_wall():
        return

    initial_session_defaults()

    # Initialize Voice Pipeline safely with fallback
    if "voice_pipeline" not in st.session_state:
        try:
            api_key = os.environ.get("GROQ_API_KEY", "").strip()
            groq_client = Groq(api_key=api_key) if api_key else None
            llm_coach = LLMCoach(groq_client)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)
        except Exception:
            llm_coach = LLMCoach(None)
            tts = TextToSpeech()
            st.session_state.voice_pipeline = VoicePipeline(llm_coach, tts)

    workout_started = st.session_state.get("workout_started", False)

    # Sidebar Navigation & Workout Configuration
    with st.sidebar:
        user_name = st.session_state.get("username", "Athlete")
        avatar_letter = user_name[0].upper() if user_name else "👤"

        st.markdown(
            clean_html(f"""
            <div class="user-profile-badge">
                <div class="user-avatar">{avatar_letter}</div>
                <div>
                    <div class="user-info-name">{user_name}</div>
                    <div class="user-info-status">🟢 Active Athlete</div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

        if st.button("🚪 Logout Account", use_container_width=True, type="secondary"):
            st.session_state.pop("user_id", None)
            st.session_state.pop("username", None)
            st.session_state.workout_started = False
            st.rerun()

        st.divider()
        st.markdown("### 🎯 Workout Plan")

        if not workout_started:
            plan_exercise = st.selectbox("Select Exercise", options=EXERCISE_OPTIONS, key="plan_exercise")
            plan_sets = st.number_input("Sets", min_value=1, max_value=50, key="plan_sets", step=1)
            plan_reps = st.number_input("Reps per Set", min_value=1, max_value=100, key="plan_reps", step=1)

            st.markdown("<br>", unsafe_allow_html=True)
            start_session_button = st.button("🚀 START WORKOUT", use_container_width=True, key="start_session_button")

            if start_session_button:
                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)
                st.session_state.reps = 0
                st.session_state.sets_completed = 0
                st.session_state.current_set_reps = 0
                st.session_state.workout_started = True
                st.session_state.set_cycle_started_at = time.time()
                st.session_state.last_saved_sets_completed = 0
                st.session_state.reset_requested = True

                if st.session_state.get("voice_pipeline"):
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_started",
                        exercise=plan_exercise,
                        metrics={}
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.session_state.last_notified_sets_completed = 0
                st.session_state.last_notified_workout_complete = False
                st.rerun()
        else:
            exercise = st.session_state.get("exercise_type")
            sets = st.session_state.get("target_sets")
            reps = st.session_state.get("reps_per_set")

            st.info(f"🏋️ **{exercise}**\n\n🎯 Target: {sets} Sets × {reps} Reps")

            end_session_button = st.button("🛑 END WORKOUT", key="end_session_button", use_container_width=True, type="secondary")

            if end_session_button:
                st.session_state.workout_started = False
                user_id = st.session_state.get("user_id")

                if user_id:
                    add_exercise(
                        user_id=user_id,
                        exercise_name=exercise,
                        reps=st.session_state.get("reps", 0),
                        sets=st.session_state.get("sets_completed", 0),
                        time=int(
                            time.time() - st.session_state.get("set_cycle_started_at", time.time())
                        )
                    )

                if st.session_state.get("voice_pipeline"):
                    result = st.session_state.voice_pipeline.process_event(
                        event="workout_completed",
                        exercise=exercise,
                        metrics={}
                    )
                    if result:
                        st.session_state.audio_to_play, st.session_state.coach_feedback = result

                st.rerun()

        if workout_started:
            st.divider()
            exercise = st.session_state.get("exercise_type")
            total_reps = st.session_state.get("reps", 0)
            current_set_reps = st.session_state.get("current_set_reps", 0)
            reps_per_set = st.session_state.get("reps_per_set", 1)
            sets_completed = st.session_state.get("sets_completed", 0)
            target_sets = st.session_state.get("target_sets", 1)

            st.markdown("### 📊 Progress Telemetry")
            st.metric("Total Reps", f"{total_reps}")
            st.metric("Current Set Reps", f"{current_set_reps} / {reps_per_set}")
            st.metric("Sets Completed", f"{sets_completed} / {target_sets}")

            st.divider()
            st.markdown("### 🔍 Live Biometrics")

            if exercise == "Squats":
                st.metric("Knee Angle", f"{st.session_state.get('knee_angle', 0)}°")
                st.metric("Back Angle", f"{st.session_state.get('back_angle', 0)}°")
                st.metric("Depth Status", st.session_state.get("depth_status", "N/A"))

            elif exercise == "Push-ups":
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}°")
                st.metric("Body Alignment", st.session_state.get("body_alignment", "N/A"))
                st.metric("Hip Position", st.session_state.get("hip_status", "N/A"))

            elif exercise == "Biceps Curls (Dumbbell)":
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}°")
                st.metric("Shoulder Stability", st.session_state.get("shoulder_status", "N/A"))
                st.metric("Swing Detection", st.session_state.get("swing_status", "N/A"))

            elif exercise == "Shoulder Press":
                st.metric("Elbow Angle", f"{st.session_state.get('elbow_angle', 0)}°")
                st.metric("Arm Extension", st.session_state.get("extension_status", "N/A"))
                st.metric("Back Arch", st.session_state.get("back_arch_status", "N/A"))

            elif exercise == "Lunges":
                st.metric("Front Knee Angle", f"{st.session_state.get('front_knee_angle', 0)}°")
                st.metric("Torso Angle", f"{st.session_state.get('torso_angle', 0)}°")
                st.metric("Balance Status", st.session_state.get("balance_status", "N/A"))

    # Main Dashboard Header
    st.markdown(
        clean_html("""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
            <div>
                <h1 style="margin:0; font-size:34px;">🏋️‍♂️ AI Real-time GYM Coach</h1>
                <p style="color:#94A3B8; margin:4px 0 0 0; font-size:15px;">Next-Gen Computer Vision & Proactive AI Voice Guidance</p>
            </div>
            <div style="background:rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.4); color:#00FF88; padding:8px 18px; border-radius:24px; font-size:12px; font-weight:800; letter-spacing:1px; box-shadow:0 0 20px rgba(0,255,136,0.25);">
                ⚡ LIVE AI VISION
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

    # Voice Feedback Component
    audio_bytes = st.session_state.get("audio_to_play")
    coach_feedback = st.session_state.get("coach_feedback")

    if audio_bytes or coach_feedback:
        autoplay_audio(audio_bytes, text_fallback=coach_feedback)

    if coach_feedback:
        st.markdown(
            clean_html(f"""
            <div class="coach-visualizer-card">
                <div class="coach-avatar">🤖</div>
                <div class="coach-text-container">
                    <div class="coach-label">⚡ AI COACH AUDIO FEEDBACK</div>
                    <div class="coach-feedback-text">"{coach_feedback}"</div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )

    # Hero / Live Camera Mode
    if not workout_started:
        st.markdown(
            clean_html("""
            <div class="hero-container">
                <div class="hero-badge">⚡ ATHLETIC AI ENGINE</div>
                <div class="hero-title">Start Your AI-Guided Workout</div>
                <div class="hero-description">
                    Configure your workout plan in the sidebar and click <strong>START WORKOUT</strong> to activate real-time pose tracking and dynamic AI voice audio coaching.
                </div>
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon-wrapper">👁️</div>
                        <div class="feature-title">Pose Analysis</div>
                        <div class="feature-desc">Real-time joint angle and biomechanics calculation via camera.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon-wrapper">🎙️</div>
                        <div class="feature-title">Proactive Voice</div>
                        <div class="feature-desc">Instant audio form corrections and motivational feedback.</div>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon-wrapper">📈</div>
                        <div class="feature-title">Telemetry Sync</div>
                        <div class="feature-desc">Automatic tracking of reps, sets, and active workout time.</div>
                    </div>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
    else:
        context = webrtc_streamer(
            key="exercise-analysis",
            mode=WebRtcMode.SENDRECV,
            video_processor_factory=VideoProcessorClass,
            rtc_configuration={
                "iceServers": [
                    {"urls": ["stun:stun.l.google.com:19302", "stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"]},
                    {"urls": ["stun:stun.services.mozilla.com"]},
                    {"urls": ["stun:global.stun.twilio.com:3478"]}
                ]
            },
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:
            time.sleep(0.25)
            st.rerun()

        inject_webrtc_styles()

    st.divider()

    # Workout History Telemetry Section
    st.markdown("### 📈 Workout History & Telemetry")

    user_id = st.session_state.get("user_id", 0)

    if isinstance(user_id, int) and user_id > 0:
        history_rows = get_users_exercises(user_id)

        if history_rows:
            arr = [
                {
                    "Exercise": row['exercise_name'],
                    "Reps": row['reps'],
                    "Sets": row['sets'],
                    "Time (sec)": row['time'],
                    "Date": row['created_at']
                }
                for row in history_rows
            ]

            df = pd.DataFrame(arr)

            # Summary Metrics Row
            total_reps_all = df["Reps"].sum()
            total_sets_all = df["Sets"].sum()
            total_time_min = round(df["Time (sec)"].sum() / 60, 1)

            col_h1, col_h2, col_h3 = st.columns(3)
            col_h1.metric("Lifetime Reps", f"{total_reps_all}")
            col_h2.metric("Lifetime Sets", f"{total_sets_all}")
            col_h3.metric("Total Active Time", f"{total_time_min} mins")

            st.markdown("<br>", unsafe_allow_html=True)

            df["Date"] = pd.to_datetime(df["Date"]).dt.date
            agg_df = df.groupby(["Exercise", "Date"]).agg({
                "Reps": 'sum',
                "Sets": "sum",
                "Time (sec)": "sum"
            }).reset_index()
            agg_df.index += 1
            st.table(agg_df)
        else:
            st.info("💡 No workout records found for this account yet. Complete a session to see your stats here!")


if __name__ == "__main__":
    main()