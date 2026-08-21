# CTF Platform - Comprehensive Features & Activity Flows Audit

This document is a detailed, holistic audit of the AI-Enhanced Capture The Flag Platform. It is designed to provide full context for project presentations, outlining every core feature, architectural component, and user activity flow. 

## 1. System Architecture & Tech Stack Overview
The platform is designed as a standalone, localized environment to host both Jeopardy-style and Attack-Defense CTF events without relying on external third-party platforms.
* **Backend Framework:** Django 4.2 (Python 3.x)
* **Database:** Containerized MySQL 8.0 with persistent volumes (`mysql_data`).
* **Frontend:** HTML5, Vanilla Bootstrap 5.3 (no heavy external CSS frameworks to maintain simplicity), and Chart.js for data visualization.
* **AI Engine:** Scikit-Learn (Linear Regression), Pandas, and NumPy.
* **Target Infrastructure:** Docker Compose managing two distinct Vulnerable Machines (VulnBoxes) for Attack-Defense.
* **Testing:** Apache JMeter for load and stress testing API endpoints.

---

## 2. Core Modules & Features

### 2.1 Accounts & Identity Management (`accounts` module)
* **User Profiles:** Extends the default Django User model with a `Profile` containing roles (`admin` or `participant`).
* **Team Grouping:** Participants are grouped into a `Team` entity, allowing collaborative scoring and assignment in the Attack-Defense arena.
* **Automated Provisioning:** Profiles are automatically created upon User registration using Django Signals (`post_save`).

### 2.2 Jeopardy CTF Engine (`jeopardy` module)
* **Categorized Challenges:** Traditional question-and-answer format grouped by `Category`.
* **Dynamic Visibility:** Challenges can be toggled hidden/visible by administrators.
* **Rate-Limited Submissions:** To prevent automated brute-forcing of flags, submissions enforce a strict 5-second `timedelta` rate limit.
* **Real-time Leaderboard API:** The leaderboard exposes an AJAX endpoint (`/api/leaderboard/`) that polls data every 5 seconds. This architectural choice specifically fulfills a Thundering Herd stress testing requirement (simulating 50 heavy concurrent users scraping the API using JMeter).

### 2.3 Attack-Defense PvP Arena (`attack_defense` module)
* **Dynamic Arena Assignments:** Each `Team` is assigned an `ArenaAssignment` binding them to a specific VulnBox container (IP, Web Port, SSH Port) and designating their target opponent (Team A vs. Team B).
* **Automated Background Daemon:** A Python script (`monitor_containers.py`) runs asynchronously every 10 seconds to orchestrate the PvP match:
  * **Uptime Tracking (SLA Defense):** Ping checks the Docker containers. If a team's VulnBox stays 'UP' for 60 seconds (6 consecutive 10s ticks), they are awarded 1 SLA defense point.
  * **Automated Flag Rotation:** Every 120 seconds, the daemon generates a secure randomized flag and uses the Docker SDK to physically inject it into the target container (`/var/www/html/flag.txt`). It then syncs this new flag to the database session.
  * **Data Pruning:** Automatically deletes Uptime logs older than 24 hours to prevent database bloat.
* **PvP Dashboard:** Participants access a dedicated arena (`/attack_defense/arena/`) showing their own box's status (UP/DOWN) and their assigned target's connection details.
* **AJAX Admin Console:** Administrators have a real-time command center (`/attack_defense/admin-dashboard/` and `/attack_defense/setup/`) to start sessions, monitor uptime charts, and view point aggregation tables asynchronously without refreshing the page.

### 2.4 AI-Driven Analytics Dashboard (`analytics` module)
* **Intelligent Momentum Tracking:** Instead of just showing total points, the platform analyzes *how* a student is scoring.
* **Linear Regression Engine:** Uses Scikit-Learn to map cumulative points against the elapsed time (in minutes) since their first solve.
* **Classification States:** Based on the calculated slope, students are classified into states:
  * *Flow State (High Momentum)*: Slope > 2.0
  * *Steady Progress*: Slope > 0.5
  * *Struggling*: Slope > 0
  * *Stagnation (Low Momentum)*: Slope <= 0
* **Cold Start & Error Fallbacks:** The mathematical model includes strict constraints (`n < 2` fallback returning 0.0) to prevent division-by-zero crashes when a user hasn't solved enough challenges.
* **Data Export:** Provides CSV export functionality of all flag submissions for lecturers/researchers to conduct post-competition analysis.

---

## 3. User Activity Flows

### Flow 1: Participant Jeopardy CTF Workflow
1. **Onboarding:** User registers an account, logs in, and is assigned to a Team.
2. **Dashboard Navigation:** User accesses the main Dashboard to view active Categories and Challenges.
3. **Execution:** User attempts to solve a challenge (e.g., reversing a binary offline).
4. **Submission:** User enters the flag in the submission modal. 
5. **Validation:** System checks rate limit (rejects if <5s since last attempt). System evaluates the flag.
6. **Scoring:** If correct, `Submission` is recorded, points are added.
7. **Feedback:** User navigates to the Leaderboard to view their new ranking in real-time.

### Flow 2: Attack-Defense PvP Workflow
1. **Admin Setup:** Admin starts the background daemon and initializes an Attack-Defense Session (`ADSession`), mapping Team A to VulnBox A and Team B to VulnBox B.
2. **Arena Access:** Team A logs into the PvP Arena. The UI displays their target's IP address (VulnBox B).
3. **Offense:** Team A actively exploits VulnBox B. Because the daemon rotates the flag every 2 minutes, Team A must script an exploit to repeatedly retrieve the flag from `/var/www/html/flag.txt`.
4. **Flag Capture:** Team A submits the stolen flag. The system verifies it against the current active 2-minute window. If correct, attack points are awarded and the session marks the flag as 'captured' until the next rotation.
5. **Defense:** Simultaneously, Team A must patch their own VulnBox A. If they fail and the box goes down, they stop earning the 1-point-per-minute SLA defense bonus generated by the background daemon.

### Flow 3: Lecturer / Administrator Analytics Workflow
1. **Monitoring Progress:** Lecturer accesses the AI Dashboard during the competition.
2. **Intervention Identification:** Lecturer views the Momentum Tracker. If a student is flagged as "Struggling" or "Stagnation", the lecturer can physically walk over to their desk to offer hints or check on their well-being.
3. **Post-Event Analysis:** After the event, the Lecturer uses the CSV Export feature to download all submission data for grading or academic research.
4. **Load Verification:** For grading purposes, the Lecturer can run the `ctf_load_test.jmx` file in Apache JMeter to verify the server handles 50 concurrent users at 0.00% error rate, proving the Thundering Herd caching constraint was fulfilled.

---

## Additional Information Required (For You)
If this context file is sufficient for your other Gemini to build the presentation script, you are good to go! 
If you need any deeper technical explanations (e.g., how the Docker socket is bound to the daemon, specific JMeter configuration parameters, or database schema charts), please let me know and I will provide them.
