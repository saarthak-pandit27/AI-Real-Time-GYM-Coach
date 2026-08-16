# 🏋️‍♂️ AI Real-Time GYM Coach

> **Next-Gen Computer Vision & Proactive AI Voice Guidance Engine**  
> Train Smarter with Real-Time Joint Tracking, PBKDF2 Password Security, and Full-Screen Cyberpunk HUD Telemetry.

---

## 🌟 Key Features

- **🛡️ Secure User Authentication**:
  - Encrypted account registration & login using **PBKDF2 HMAC SHA-256** with unique 16-byte random salts.
  - SQLite persistence storing password hashes and user workout history safely.

- **👁️ Real-Time Computer Vision Pose Estimation**:
  - 30+ FPS joint tracking powered by **MediaPipe** and **OpenCV**.
  - Precise biomechanics & angle calculations for **5 key exercises**:
    - 🏋️ **Squats**: Knee angle, back inclination, depth checks.
    - 🧘 **Push-ups**: Elbow angle, body alignment, sagging/piked hip detection.
    - 💪 **Biceps Curls**: Elbow drift detection, torso swing alerts.
    - 🏋️‍♂️ **Shoulder Press**: Arm extension, excessive back arch tracking.
    - 🏃 **Lunges**: Front knee angle, torso balance posture checks.

- **🎙️ Crash-Proof AI Voice Coaching**:
  - Dual-layer voice synthesis engine using **Groq Llama 3.3 70B** LLM + **gTTS** (Google Text-to-Speech).
  - Automatic fallback to high-energy rule-based AI prompts + **Browser Web Speech API** (`window.speechSynthesis`), ensuring voice guidance **never crashes** even when offline or without an API key.

- **✨ Futuristic Sci-Fi HUD Interface**:
  - Full-screen edge-to-edge dark theme (`layout="wide"`).
  - Ambient laser scanline animations, glassmorphism telemetry panels, and glowing audio feedback visualizers.

- **📈 Workout History & Telemetry**:
  - Automatic session logging (Reps, Sets, Active Training Seconds).
  - Aggregate workout dashboard tracking lifetime reps, sets, and active workout time.

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: Streamlit (Full-Screen Layout, WebRTC Streamer)
- **Computer Vision & Pose Tracking**: MediaPipe Pose, OpenCV
- **AI LLM & Speech**: Groq API (Llama 3.3 70B Versatile), gTTS, Web Speech API Fallback
- **Database & Security**: SQLite3, `hashlib` PBKDF2 HMAC SHA-256
- **Styling**: Custom CSS3, Glassmorphism, Google Fonts (`Outfit`, `Space Grotesk`, `Inter`)

---

## ⚡ Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/saarthak-pandit27/AI-Real-Time-GYM-Coach.git
cd AI-Real-Time-GYM-Coach
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables (Optional for Groq LLM)
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```
> *Note: If no API key is provided, the application automatically uses its built-in fail-safe rule-based AI voice engine.*

### 4. Launch the AI Coach
```bash
streamlit run main.py
```

Open your browser at **`http://localhost:8501`**.

---

## 📁 Repository Architecture

```
AI-Real-Time-GYM-Coach/
├── main.py                          # Application entry point & full-screen UI layout
├── requirements.txt                 # Dependencies
├── data.db                          # SQLite database (auto-created)
├── static/
│   ├── style.css                    # Futuristic Sci-Fi HUD Theme & laser animations
│   └── AdobeClean.otf               # Custom font asset
├── services/
│   ├── auth/
│   │   ├── security.py              # PBKDF2 password hashing & verification
│   │   └── login_wall.py            # Glassmorphic Sign In & Create Account wall
│   ├── coaching/
│   │   ├── llm.py                   # Groq LLM coach with fallback feedback
│   │   ├── tts.py                   # Text-To-Speech engine
│   │   └── voice_pipeline.py        # Voice pipeline & Web Speech JS fallback
│   ├── persistence/
│   │   └── exercise_repository.py   # SQLite CRUD operations
│   ├── tracking/
│   │   └── metrics.py               # Live rep/set counter & telemetry sync
│   └── vision/
│       └── exercise_video_processor.py # MediaPipe pose analysis processor
└── detectors/                       # Exercise angle calculations
```

---

## 👤 Author

**Saarthak Pandit**  
B.Tech CSE (AI & ML)  
Amity University Mohali  
🔗 GitHub: [@saarthak-pandit27](https://github.com/saarthak-pandit27)
