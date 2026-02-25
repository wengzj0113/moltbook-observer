# Moltbook Observer

<div align="center">
  <img src="static/logo_placeholder.png" alt="Moltbook Observer Logo" width="120" height="120" />
  <h3>The Front Page of the Agent Internet</h3>
  <p>Real-time Intelligence Monitor for AI Agents & Submolts</p>
</div>

---

## 📖 Introduction

**Moltbook Observer** is a powerful, real-time intelligence monitoring dashboard designed to track, analyze, and visualize activities from the Moltbook ecosystem (the "Reddit for AI Agents").

It serves as a command center for human operators to observe AI agent behaviors, track viral conversations, and discover emerging submolts (communities) in the agent internet.

![Dashboard Screenshot](static/screenshot_dashboard.png)

## ✨ Key Features

*   **🕵️ Real-time Intel Feed**: Live stream of posts from all agents, with auto-refresh and "New/Top/Discussed" filters.
*   **🌍 Multi-language Support**: Seamless auto-translation for 8 languages (EN, ZH, FR, JA, KO, RU, ES, IT).
*   **📊 Live Analytics**: Visualized activity charts, system load monitoring, and agent activity heatmaps.
*   **🏆 Leaderboards**: Real-time rankings for "Karma Kings" (Top Agents) and "Most Vocal" (High Frequency) entities.
*   **🔍 Deep Search**: Full-text search capability across all intercepted signals and agent profiles.
*   **📱 Responsive Design**: Modern "Glassmorphism" UI that works perfectly on Desktop, Tablet, and Mobile.

## 🚀 Quick Start

### Prerequisites

*   Python 3.10+
*   pip

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/moltbook-observer.git
    cd moltbook-observer
    ```

2.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Observer**
    ```bash
    python -m uvicorn main:app --reload
    ```

4.  **Access the Dashboard**
    Open your browser and visit: `http://localhost:8000`

## 🛠️ Technology Stack

*   **Backend**: FastAPI (Python), SQLAlchemy, APScheduler
*   **Frontend**: HTML5, Tailwind CSS, Vanilla JS (No build step required)
*   **Database**: SQLite (Default) / PostgreSQL (Supported)
*   **Data Collection**: Custom async collectors with robust fallback mechanisms

## 📦 Deployment

### Deploy to Render (Recommended)

This project is configured for one-click deployment on Render.

1.  Fork this repo.
2.  Create a new **Web Service** on Render.
3.  Connect your repo.
4.  Render will auto-detect the `render.yaml` config.
5.  **Important**: Add a Disk mount at `/data` to persist your SQLite database.

### Deploy with Docker

```bash
docker build -t moltbook-observer .
docker run -d -p 8000:8000 -v $(pwd)/data:/data moltbook-observer
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## ⚠️ Disclaimer

This is an unofficial observer tool and is not affiliated with Moltbook directly. Data is collected from public APIs.

---

<div align="center">
  Made with ❤️ by the OpenClaw Community
</div>
