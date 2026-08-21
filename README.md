# CTF Platform - AI-Enhanced Capture The Flag Platform

This is a highly customized, web-based Jeopardy-style cybersecurity competition platform. It features integrated Attack-Defense static Proof-of-Concepts (PoC) with automated 2-minute flag rotation and an advanced AI-driven Intelligent Dashboard that analyzes student momentum.

## Primary Tech Stack
*   **Backend Framework:** Python 3.x / Django 4.2
*   **Database:** MySQL 8.0 (Dockerized Persistent Volume)
*   **Data Science / AI:** Scikit-Learn, Pandas, NumPy
*   **Frontend UI:** HTML5, Bootstrap 5.3, Chart.js
*   **Security & Evaluation:** Apache JMeter (Load stress testing API)

---

## Environment Initialization & Startup Guide

Follow these sequential steps to boot the entire platform from a fresh clone.

### 1. Launch the Infrastructure
The database and target environments run in containerized isolation.
```bash
# Open terminal in the repository root directory

# On Windows
docker-compose up -d --build

# On Pop!-OS / Linux
docker compose up -d --build
```
*This starts the `mysql` backend and the two VulnBoxes (Team A and Team B).*

### 2. Create & Activate Python Environment
To prevent package conflicts with your operating system, you must create and use an isolated virtual environment.

```bash
# 1. Create the virtual environment (only do this the first time)
# On Windows
python -m venv venv

# On Pop!-OS / Linux
python3 -m venv venv
# (If venv is not installed, run: sudo apt install python3-venv)

# 2. Activate the virtual environment
# On Windows
.\venv\Scripts\activate

# On Pop!-OS / Linux
source venv/bin/activate

# 3. Install System Dependencies (Linux Only)
# Pop!-OS / Ubuntu requires MySQL development headers to build the mysqlclient Python package
sudo apt install pkg-config libmysqlclient-dev python3-dev

# 4. Install project dependencies (Make sure the venv is activated first!)
pip install -r requirements.txt
```

### 3. Database Migrations
Synchronize the Django models to the running Docker MySQL container.
```bash
# Note: Ensure your virtual environment is activated first
python manage.py makemigrations accounts jeopardy attack_defense
python manage.py migrate
```

### 4. Setup Administrator Account
Create the lead "Organizer" profile for managing the CTF and accessing the AI dashboard.
```bash
python manage.py createsuperuser
```

### 5. Start the Application & Daemon
You need to run the web server and the background daemon simultaneously.

```bash
# Open a new terminal, activate your venv, and start the background daemon
python manage.py monitor_containers

# In your original terminal, start the web application
python manage.py runserver
```
*Access the site at `http://127.0.0.1:8000/`. The Admin interface is at `/admin/`.*

---

## ⚡ Load Testing (Apache JMeter)
To satisfy the Final Year Project stress testing requirement against the Thundering Herd caching issue:
1. Open **Apache JMeter GUI**.
2. Load the predefined `ctf_load_test.jmx` file located in the root directory.
3. Keep the Django server running in the background.
4. Execute the thread group (Simulating 50 heavy concurrent users scraping the API). 
5. Verify `0.00%` Error Rate in the Summary Report.
