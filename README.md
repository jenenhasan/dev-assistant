# 🎤 Diva — AI Voice Assistant

Diva is a fully modular, voice-activated personal assistant built in Python. It uses Voice Activity Detection (VAD), gTTS for text-to-speech, and Google Speech Recognition to let you control your computer hands-free. Diva can manage your emails, schedule calendar events, browse GitHub, search Google, scaffold new projects, track hand gestures, generate AI-powered creative ideas, and log terminal errors to Notion — all through natural voice commands.

A PyQt5 desktop UI is included for a polished visual experience.

---

## 📁 Project Structure

```
diva/
│
├── main.py                      # Core VoiceAssistant class — VAD loop, command routing, all handlers
├── app.py                        # PyQt5 desktop GUI — animated chat bubbles, voice indicator, waveform
│
├── gemini.py                     # Gemini 2.0 Flash API wrapper — fallback LLM for general queries
├── speech.py                     # VoiceControl — TTS (gTTS/espeak), speech recognition, Vosk offline mode
│
├── googleterminal.py             # Google search via SerpAPI — ranked results, open in browser
├── quantum_creativity_engine.py  # Quantum-seeded creative idea generator using Qiskit + GPT-4
│
├── diva_gesture_tracker.py       # Hand gesture tracker — pinch (Tab), swipe (scroll) via MediaPipe
├── presentation_gesture.py       # Presentation mode gesture control — right swipe → next slide
│
├── diva_github_uploader.py       # GitHub manager — upload, list, access, delete, commit, merge branches
├── terminal_error_logger.py      # Run Python files, catch errors, explain with Gemini, log to Notion
│
├── working_day/
│   └── app_lanchuar.py           # DynamicLauncher — launch apps/websites, save/load workspaces
│
├── scaffolding/
│   ├── scaffold.py               # ScaffoldingManager — create Flask/Django/FastAPI project templates
│   └── templates.json            # Project template definitions (folders, files, aliases)
│
├── managment/
│   ├── CalenderManagment.py      # CalendarManager — Google Calendar events and tasks via OAuth
│   └── email_managment.py        # EmailManager — Gmail read, search, send via OAuth + fuzzy contacts

```

---

## ✨ Features

### 🎙️ Voice Interaction
- **Wake word activation** — say the assistant's name (e.g. *"Hey Diva"*) to activate
- **VAD (Voice Activity Detection)** — continuous listening via `webrtcvad` and `pyaudio`; only processes when speech is detected
- **Interrupt detection** — if you speak while Diva is talking, it stops and listens
- **Retry logic** — automatically asks you to repeat if speech isn't recognized
- **Confirmation prompts** — all destructive or important actions require a "yes" before proceeding
- **Offline fallback** — uses Vosk for offline speech recognition when internet is unavailable

### 🔊 Text-to-Speech
- Primary: **gTTS** (Google Text-to-Speech) — splits text into natural sentence chunks, saves as MP3, and plays via `mpv` (or `mpg123` as fallback) on Linux, `afplay` on macOS, and `start` on Windows
- Initialized but not active: **pyttsx3** with `espeak` is set up but the active `speak()` path uses gTTS instead
- Non-blocking: speech runs in a daemon thread so listening can continue in parallel

### 📧 Email (Gmail)
- Read inbox headlines (unread emails)
- Search emails by subject keyword
- Compose emails using Gemini AI and send them
- Fuzzy contact matching — say a name, Diva finds the email address

### 📅 Calendar & Tasks (Google Calendar)
- Create events from natural speech (e.g. *"Team meeting tomorrow at 3pm"*)
- Create tasks with 15-minute popup reminders
- Natural language time parsing via `dateparser`
- View upcoming and completed events

### 🐙 GitHub
- Upload a local project folder as a new repository
- List all your repositories
- Browse repository contents by name (fuzzy matched)
- Delete repositories
- Batch commit local changes to a branch (creates branch if it doesn't exist)
- Merge branches with conflict detection

### 🔍 Google Search
- Voice-triggered search via SerpAPI
- Returns top 3 results ranked (GitHub > Stack Overflow > other)
- Open a result by saying "first result", "second result", etc.

### 🚀 App Launcher
- Open desktop apps by name (VS Code, Chrome, Terminal, Notion, Telegram, etc.)
- Open websites by name (YouTube, GitHub, Figma, Canva, Trello, and 40+ more)
- Cross-platform: Linux (`.desktop` files + PATH), macOS (`mdfind`), Windows (Program Files search)

### 💼 Workspace Manager
- **Save workspace**: detects currently open windows (Linux via `wmctrl`) and saves the app list
- **Load workspace**: re-launches all saved apps in one command — *"start my working day"*

### 🛠️ Project Scaffolding
Create full project structures from a voice command:

| Template | Aliases |
|---|---|
| `flask-project` | flask, flask-app |
| `django-project` | django, python fullstack |
| `fastapi-project` | fast api, fastapi |

Each scaffold generates folders, base files, `requirements.txt`, a `README.md`, and installs dependencies. Optional database config and auth module can be added.

### 🤚 Gesture Control
Two gesture modes available:

**General mode** (`zeno_gesture_tracker.py`):
- Pinch (thumb + index finger) → `Tab`
- Horizontal swipe → scroll down
- Vertical swipe → scroll up

**Presentation mode** (`presentation_gesture.py`):
- Right swipe → next slide (`→` arrow key)

### ⚛️ Quantum Creativity Engine
Generates AI-powered creative tech project ideas using:
1. A **6-qubit quantum circuit** (via Qiskit + Qiskit Aer) to produce a probabilistic "creativity seed"
2. The seed **mutates the prompt** along three axes: theme, aesthetic, and audience
3. **GPT-4** generates the final idea at a temperature tuned by the seed's entropy

Select a mood (from 29 options) and a tech domain (from 33 options), add an optional thought, and get a unique buildable idea every time.

### 🐛 Terminal Error Logger
Run any Python script through Diva and it will:
1. Catch any runtime errors
2. Extract the error type, affected file, and stack trace
3. Ask Gemini AI to explain the bug and suggest a fix
4. Log everything to a **Notion database** (auto-created on first run)
5. Deduplicate repeated errors using MD5 hashing

### 🖥️ PyQt5 Desktop GUI (`app.py`)
- Animated chat bubble interface (user + assistant messages with slide/fade animations)
- Real-time voice waveform visualizer with volume-level animation
- Ripple-effect mic button with pulse animation
- Typing indicator with bouncing dots
- Gradient header with live status label
- Fade-in splash screen on launch

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- A microphone
- Linux recommended (workspace detection uses `wmctrl`; all other features are cross-platform)

### Installation

```bash
git clone https://github.com/your-username/diva.git
cd diva
pip install -r requirements.txt
```

Key dependencies include: `speechrecognition`, `pyaudio`, `webrtcvad`, `pyttsx3`, `google-generativeai`, `openai`, `qiskit`, `qiskit-aer`, `mediapipe`, `pyautogui`, `PyGithub`, `fuzzywuzzy`, `rapidfuzz`, `google-api-python-client`, `google-auth-oauthlib`, `dateparser`, `PyQt5`, `requests`, `python-dotenv`, `vosk`, `notion-client`

### Environment Variables

Create a `.env` file in the project root:

```env
# Required
API_KEY=your_gemini_api_key
GITHUB_TOKEN=your_github_personal_access_token
SERPAPI_KEY=your_serpapi_key
OPENAI_KEY=your_openai_api_key

# For error logging to Notion
NOTION_TOKEN=your_notion_integration_token
NOTION_PAGE_ID=your_notion_parent_page_id
```

### Google API Setup

Diva uses Gmail and Google Calendar via OAuth 2.0.

1. Go to [Google Cloud Console](https://console.cloud.google.com/) and create a project
2. Enable the **Gmail API**, **Google Calendar API**, and **People API**
3. Create OAuth 2.0 credentials (Desktop app type)
4. Download and save as `credentials.json` (for Gmail) and `googlecal.json` (for Calendar)
5. On first run, a browser window opens for authorization — `token.json` is saved automatically thereafter

### Optional: Offline Speech Recognition (Vosk)

```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

Place the extracted folder in the project root. Diva detects and uses it automatically when offline.

---

## 🖥️ Running Diva

### Voice Assistant (CLI)

```bash
python main.py
```

Diva starts listening immediately. Say *"Hey Diva"* or just *"Diva"* to activate command mode.

### Desktop GUI

```bash
python app.py
```

Click the mic button to start/stop listening. Messages appear as animated chat bubbles.

### Terminal Error Logger

```bash
python terminal_error_logger.py "python your_script.py"
```

Errors are caught, explained by Gemini, and logged to your Notion database automatically.

---

## 🗣️ Voice Commands Reference

| Say... | Action |
|---|---|
| *"Hey Diva"* | Wake word — activates command mode |
| *"Open VS Code"* / *"Launch Chrome"* | Opens an app or website |
| *"Start my working day"* | Launches your saved workspace |
| *"Save my workspace"* | Saves currently open apps as workspace |
| *"Create a project"* | Guided project scaffolding |
| *"Schedule a meeting tomorrow at 2pm"* | Creates a Google Calendar event |
| *"Add a task: finish report by Friday"* | Creates a task with reminder |
| *"Send an email"* | Guided email composition via Gemini |
| *"Check inbox"* | Reads your latest unread emails |
| *"Search email for invoice"* | Searches Gmail by subject |
| *"Google how to center a div"* | Web search, open result by voice |
| *"GitHub"* | GitHub management (upload/list/access/delete) |
| *"Wild idea"* | Launches the Quantum Creativity Engine |
| *"Activate gesture"* | Starts hand gesture tracking |
| *"Stop gesture"* | Stops hand gesture tracking |
| *"Generate readme"* | Auto-documents the project from docstrings |
| *"Help"* | Lists all available commands |
| *"Goodbye"* | Shuts down Diva |

Any unrecognized command is answered by **Gemini 2.0 Flash** as a general question.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push and open a Pull Request

---

## 📄 License

This project is open source. See `LICENSE` for details.
