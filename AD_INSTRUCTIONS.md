# Attack-Defense (AD) Local Competition Guide

This document outlines everything needed to run and participate in the local Attack-Defense CTF game.

## 1. Prerequisites and Network Setup

Since this is a local proof-of-concept running on a single host machine, all players must be able to communicate with the host.

### For the Host (Admin):
- Ensure your machine is connected to a local network (Wi-Fi or LAN).
- Find your machine's local IP address (e.g., `192.168.x.x`). 
  - On Linux/macOS: Run `ifconfig` or `ip a`.
  - On Windows: Run `ipconfig`.
- Start the Django server bound to all interfaces: `python manage.py runserver 0.0.0.0:8000`
- Ensure Docker containers are running: `docker compose up -d`
- Run the AD background daemon: `python manage.py monitor_containers`

### For the Players:
- Connect your laptop to the **same network** as the Host machine.
- You must have an SSH client installed (Terminal on macOS/Linux, PowerShell or PuTTY on Windows).
- You need a modern web browser.

## 2. Admin Setup Checklist

Before players can start, the admin must configure the arena. **Do not use `127.0.0.1` or `localhost`** if players are using their own laptops.

1. Go to the **AD Setup** page on the admin dashboard.
2. **Assign Team A's VulnBox:**
   - Team: Select Team A
   - VulnBox Name: `Team A Box`
   - Docker Container Name: `ctf_team_a_vulnbox`
   - VulnBox IP: `<Host_LAN_IP>` (e.g., `192.168.1.100`)
   - Web Port: `8081` (Must match docker-compose.yml)
   - SSH Port: `2221` (Must match docker-compose.yml)
3. **Assign Team B's VulnBox:**
   - Team: Select Team B
   - VulnBox Name: `Team B Box`
   - Docker Container Name: `ctf_team_b_vulnbox`
   - VulnBox IP: `<Host_LAN_IP>` (e.g., `192.168.1.100`)
   - Web Port: `8082` (Must match docker-compose.yml)
   - SSH Port: `2222` (Must match docker-compose.yml)
4. **Start the Match:**
   - Create a new AD Session (e.g., Session 1), select Team A and Team B, and generate the initial flags.

## 3. How to Play (Instructions for Teams)

Once the game starts, go to the **Attack & Defense Arena (PvP)** page in your dashboard. You have two main objectives: **Defend** your box and **Attack** the enemy's box.

### Objective 1: Defend Your Box (Patching)
Your box has a flag file located at `/var/www/html/flag.txt`. Every 2 minutes, a background daemon updates this flag. If the enemy reads it and submits it, you lose points.
1. **Connect to your box:** Use the "Copy SSH Command" button on your arena page. It will look like this: `ssh player@<IP> -p <PORT>`.
2. **Login:** The default password is `player`. You have `sudo` privileges.
3. **Secure the box immediately:**
   - Change your SSH password immediately (`passwd`). If you don't, the enemy can SSH into your box and read the flag!
   - Secure the web server: By default, Nginx is serving your `flag.txt` publicly. You need to configure Nginx or change file permissions so that external users cannot read it, **BUT** the background daemon must still be able to write to it. (Hint: The daemon runs as `root` via Docker exec, so you can change permissions of the file to restrict read access for web users).

### Objective 2: Attack the Enemy (Exploitation)
The enemy's box is configured identically to yours. You must steal their `flag.txt` and submit it on the Arena page.
1. **Reconnaissance:** Click the "Attack Web Interface" button. By default, this takes you to their Nginx web server.
2. **Exploit:** Because the box is intentionally misconfigured out-of-the-box, you can easily steal their flag by navigating to `http://<enemy_ip>:<enemy_port>/flag.txt`.
3. **Submit:** Copy the flag (format: `CTF{...}`) and paste it into the "Submit Enemy Flag" form on your Arena page.
4. **Repeat:** Flags rotate every 2 minutes. Once the enemy patches the easy web vulnerability, you will need to find other ways in (e.g., did they forget to change their SSH password?).

## 4. Game Rules and Mechanics
- **Flag Rotation:** Flags are rotated every 120 seconds.
- **SLA Points:** Every 1 minute your container is online, you earn 1 Defense Point.
- **Attack Points:** Every valid enemy flag you submit earns you 10 Points.
- **Cooldowns:** If you submit an incorrect flag, you must wait 10 seconds.
- **Destruction Rule:** Do NOT delete the `/var/www/html` directory on your box. If the daemon cannot write the flag to your box, it will crash the script or fail to rotate, potentially breaking the game. You are expected to *patch*, not *destroy*.
