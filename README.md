# Offline ML-Based Code Review Assistant

> Perform secure, lightning-fast code reviews entirely offline. Powered by local ML models and advanced static analysis, this tool reviews quality, maintainability, and security risks across 13 languages without cloud APIs. Enjoy an IDE-style workspace with detailed SonarQube-like issue explanations and side-by-side refactoring diffs.

---

## 🚀 Key Features

* **100% Secure & Offline**: No cloud APIs (no OpenAI, Claude, or Gemini calls). No network packets leave your computer.
* **Premium IDE Workspace**: Designed with a visual layout containing a collapsible sidebar, command palette modal search (`Ctrl+P`), and bottom system health panel.
* **Circular Health Gauge Dashboard**: Displays overall code health out of 100 with category metrics (Security, Quality, Maintainability, Performance).
* **SonarQube-Inspired Code Guide**: Redesigned right-pane code guides showing:
  * **Why Detected** & **Real-World Threat Consequences**.
  * **Standards Alignment**: Maps issues to **CWE-89**, **OWASP Top 10**, and **CERT** regulations.
  * **Side-by-Side Code Diff**: Visualizes Current Code vs Improved Code side-by-side with refactoring benefits.
* **Auto-Correcting Relative Paths**: Smart backend folder resolver translates dummy path inputs to actual absolute directories on your system automatically.

---

## 🛠️ Supported Languages & Rules

The review engine parses and inspects files in **13 major languages**:
* Python, Java, JavaScript, TypeScript, C, C++, C#, PHP, HTML, CSS, SQL, Bash, and JSON.

---

## 📦 Tech Stack

1. **Frontend Core**: React 18, TypeScript, Tailwind CSS, Zustand, Lucide Icons, Chart.js.
2. **Desktop Container**: Electron (exposed API using secure `preload` scripts).
3. **Inference Server**: Python Flask backend.
4. **Machine Learning**: Scikit-Learn classifiers and regressors (trained local models).

---

## 🚀 Setup & Launching

### Prerequisites
* [Node.js](https://nodejs.org/) (v18+)
* [Python](https://www.python.org/) (v3.10+)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/iamkk2307/Offline-AI-Code-Review-Assistant-System.git
   cd Offline-AI-Code-Review-Assistant-System
   ```

2. **Install all dependencies**:
   ```powershell
   # Install Electron / Client node packages
   npm install
   cd client && npm install
   cd ..
   
   # Install python backend libraries
   pip install -r requirements.txt
   ```

3. **Start the application**:
   ```bash
   # Starts concurrently the Flask server, Vite dev client, and Electron desktop shell
   npm run dev
   ```

---

## 🧪 Running Tests

Validate changes and run the unit/integration suite:
```bash
python -m pytest tests/ -v
```

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
