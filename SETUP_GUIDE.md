# Windows Setup Guide: Stock Market Distribution Analyzer

This guide provides step-by-step instructions for setting up, configuring, and running the Stock Market Distribution Analyzer on a Windows operating system. It is written specifically for university students, educators, and beginners.

---

## 1. Prerequisites

Before starting, ensure your Windows PC has Python installed.

1. **Check Python Installation:**
   - Open Command Prompt (`cmd.exe`) or Windows PowerShell.
   - Type:
     ```cmd
     python --version
     ```
   - If Python is installed, you will see output such as `Python 3.11.9`. Python 3.10, 3.11, or 3.12 is recommended.
2. **If Python is NOT Installed:**
   - Visit [python.org/downloads](https://www.python.org/downloads/) and download the Windows installer.
   - Run the installer. **CRITICAL STEP:** On the very first installation screen, check the checkbox labeled:
     > **[X] Add python.exe to PATH**
   - Click "Install Now" and wait for the installer to finish.

---

## 2. Automated Setup (Recommended)

The simplest way to configure the environment is using the included batch scripts:

1. Navigate to the `Stock_Return_AI_Lab` folder in Windows File Explorer.
2. Double-click the file named **`setup_windows.bat`**.
3. A Command Prompt window will appear and perform the following automated actions:
   - Verifies Python is reachable in your system PATH.
   - Creates an isolated virtual environment in a folder named `.venv`.
   - Upgrades `pip` to the latest version.
   - Installs all required statistical, web, and charting packages from `requirements.txt`.
   - Copies `.env.example` to `.env` if `.env` does not already exist.
   - Generates the bundled sample CSV files in `data/sample_data/`.
4. When finished, you will see `SETUP COMPLETED SUCCESSFULLY!`. Press any key to close the window.

---

## 3. Starting the Dashboard

1. In the `Stock_Return_AI_Lab` folder, double-click **`start_dashboard.bat`**.
2. The script will:
   - Activate the virtual environment (`.venv`).
   - Check if port 5000 is available (or open the existing instance if already running).
   - Start the local Flask web server.
   - Wait until the server responds to a health check (`/health`).
   - Automatically open your default web browser to:
     ```
     http://127.0.0.1:5000
     ```
3. **Important:** Keep the Command Prompt window open while you use the application. The window displays real-time server logs and diagnostic information.
4. **Stopping the Server:** To shut down the web application, click inside the Command Prompt window and press `Ctrl + C`, then press `Y` when prompted.

---

## 4. Running the Automated Tests

To verify that return formulas, data loaders, distribution fits, and risk metrics are functioning properly:

1. Double-click **`run_tests.bat`**.
2. A window will open and execute `pytest tests -v`.
3. You will see 30 unit and integration tests execute with green `PASSED` indicators.
4. The tests run completely offline using mathematical synthetic data and require neither an internet connection nor an API key.

---

## 5. Configuring Optional AI Features

The application operates completely offline with full statistical functionality without an AI key. To enable optional LLM-driven commentary:

1. Open the `.env` file located in `Stock_Return_AI_Lab/` using Notepad or your favorite text editor.
2. Locate the line:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Replace `your_openai_api_key_here` with your actual OpenAI API key (starts with `sk-...`).
4. Save the file and restart `start_dashboard.bat`.
5. The dashboard will now provide enhanced natural-language commentary alongside the deterministic baseline scoring.

---

## 6. Manual Setup (For Advanced Users / Command Line)

If you prefer to set up manually via PowerShell or Command Prompt:

```cmd
cd path\to\Stock_Return_AI_Lab

:: Create virtual environment
python -m venv .venv

:: Activate virtual environment
.venv\Scripts\activate

:: Upgrade pip and install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Generate sample data files
python -c "import sys; sys.path.append('.'); from data.csv_provider import generate_sample_csv_files; generate_sample_csv_files()"

:: Run tests
pytest tests -v

:: Start server
python app.py
```
Open `http://127.0.0.1:5000` in your web browser.
