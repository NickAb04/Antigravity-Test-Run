# Architecture Overview

## 1. High-Level System Architecture
The CTF Platform is a web-based Cybersecurity Competition Management System built primarily to host Jeopardy-style Capture The Flag (CTF) events with integrated Attack-Defense static Proof-of-Concepts (PoC). The architecture is designed to fulfill the constraints of a Bachelor's Degree Final Year Project (FYP), avoiding over-engineering while providing a robust, standalone environment.

### Core Technologies:
*   **Web Framework**: Django 4.2 (Python 3)
*   **Database**: MySQL 8.0
*   **Frontend**: HTML5, Vanilla Bootstrap 5.3, Chart.js
*   **AI/Data Science**: Scikit-Learn, Pandas, NumPy
*   **Infrastructure**: Docker Compose

## 2. Infrastructure & Deployment (Docker)
The platform relies on containerization strictly for the database and target environments.
*   **Persistent Database (`ctf_mysql`)**: MySQL 8.0 runs in a container with a persistent volume (`mysql_data`) to ensure flag submissions and user accounts survive server reloads.
*   **Vulnerable Targets (`ctf_team_a_vulnbox`, `ctf_team_b_vulnbox`)**: Dedicated Ubuntu-based VulnBoxes running Nginx and SSH. Teams must secure their own box while attacking the other.
*   **Django Application Server**: Runs locally via `python manage.py runserver` (not containerized by default) during development and local demonstration.
*   **Background Daemon**: A custom Django command (`monitor_containers.py`) that uses the Docker SDK to continually monitor the health of the VulnBoxes, prune old log data, automatically rotate and inject new CTF flags every 2 minutes, and award SLA defense points to teams maintaining container uptime.

## 3. Data Flow & Applications
The Django backend is split into logical applications:

*   `accounts`: Manages user authentication, participant profiles, and organizer/administrator privileges.
*   `jeopardy`: Handles challenge hosting, flag submissions, and automated scoring. Features strict rate limiting (5-second `timedelta`) to mitigate brute force point farming.
*   `attack_defense`: Manages the Team A vs Team B PvP arena, the target IPs, and runs the background Docker monitoring daemon.
*   `analytics`: Houses the core "Intelligent Dashboard" and AI components.

## 4. The AI Analytics Module
The intelligent dashboard utilizes machine learning to visualize participant performance trends ("momentum").

*   **Mechanism**: A Linear Regression algorithm (`Scikit-Learn`) maps cumulative challenge points against `elapsed_time`.
*   **Cold Start Fallback**: The mathematical array calculation requires at least two data points. A strict fallback condition (`if n < 2`) returns `0.0` or 'Insufficient Data' before attempting to fit the `LinearRegression()` model to prevent divide-by-zero or shape mismatch exceptions.

## 5. Performance Monitoring
The architecture's leaderboard polling mechanism (HTTP polling every 5 seconds) is intentionally retained over WebSockets to allow evaluation and load/stress testing using Apache JMeter (`ctf_load_test.jmx`), fulfilling the FYP requirement against the Thundering Herd caching issue.
