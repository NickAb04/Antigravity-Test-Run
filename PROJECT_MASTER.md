# CTF Master Project Wiki

This document serves as the single source of truth for the CTF Platform, aggregating all critical project information, architecture rules, and setup instructions.

## 1. Project Overview & Proposal
The CTF Platform is a highly customized, web-based Jeopardy-style cybersecurity competition platform integrated with an Attack-Defense static Proof-of-Concept (PoC) featuring automated 2-minute flag rotation and SLA defense tracking. It features an advanced AI-driven Intelligent Dashboard that utilizes Linear Regression algorithms to analyze participant "momentum." This project is built as a Bachelor's Degree Final Year Project (FYP) to provide an in-house customizable solution and reduce dependency on external third-party CTF platforms.

## 2. System Architecture
*   **Backend Framework:** Django 4.2 (Python 3.x)
*   **Database:** MySQL 8.0 (Containerized with persistent volumes)
*   **Frontend UI:** HTML5, Bootstrap 5.3 (Vanilla), Chart.js
*   **AI/Data Science:** Scikit-Learn, Pandas, NumPy
*   **Attack-Defense PoC:** 2 static VulnBoxes (Team A and Team B) managed via Docker
*   **Load Testing:** Apache JMeter (`ctf_load_test.jmx`)

## 3. UI/UX Styleguide
All frontend features must adhere to the `STYLEGUIDE.md` principles:
*   Utilize Vanilla Bootstrap 5.3 utility classes (`bg-light`, `shadow-sm`, `fw-bold`). Do not create ad-hoc CSS files unless absolutely necessary.
*   **Color Semantics**: Primary (Blue) for safe actions, Danger (Red) for offensive contexts, Success (Green) for solved challenges, Warning (Yellow) for AI/Admin data.
*   **Chart.js**: Always use `stepped: 'before'` interpolation for CTF data to mimic standard stair-step progression.

## 4. Environment & Startup Guide
1. Start the Docker Infrastructure (Database & VulnBoxes): `docker-compose up -d`
2. Create and activate a Python virtual environment.
3. Install dependencies: `pip install -r requirements.txt`
4. Apply migrations: `python manage.py makemigrations` and `python manage.py migrate`
5. Create an admin account: `python manage.py createsuperuser`
6. Start the background monitoring daemon in a new terminal: `python manage.py monitor_containers` (This handles uptime tracking, flag rotation every 2 minutes, and SLA defense points).
7. Start the server in the original terminal: `python manage.py runserver`

## 5. Attack-Defense PvP Format & Network Setup
The platform hosts two VulnBoxes. Team A defends VulnBox A and attacks VulnBox B. Team B defends VulnBox B and attacks VulnBox A.
To test this on a local area network (LAN) with other PCs:
1. Ensure the host PC (running `docker-compose up -d`) allows inbound traffic on ports `8081`, `8082`, `2221`, and `2222`.
2. Find the host PC's IP address:
   *   **Windows 11**: Open Command Prompt and run `ipconfig` (Look for IPv4 Address under Wireless LAN or Ethernet).
   *   **Pop!_OS / Linux**: Open Terminal and run `ip a` or `ifconfig`.
3. Other PCs on the same Wi-Fi/Wired network can access the VulnBoxes via the host IP (e.g., `http://<HOST_IP>:8081` or `ssh player@<HOST_IP> -p 2221`).

## 6. AI Agent Context (Gemini Rules)
*   **No Over-Engineering**: Stick to local Docker Compose. Do not add Kubernetes or microservices.
*   **Cold Start Fallback**: The Linear Regression AI module requires an `if n < 2` fallback condition returning `0.0` or 'Insufficient Data'.
*   **No WebSockets**: Keep the 5-second HTTP polling for JMeter stress test compatibility.
*   **Security Limits**: Maintain the 5-second `timedelta` rate limit on flag submissions.
