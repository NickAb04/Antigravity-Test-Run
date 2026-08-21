# Contributing Guidelines

Thank you for your interest in contributing to the iHack Platform! This repository represents a Bachelor's Degree Final Year Project (FYP) focused on creating an AI-Enhanced CTF platform.

## 1. Scope and Constraints
When contributing or proposing changes, please keep the following academic constraints in mind:
*   **Do not over-engineer**: Avoid adding complex microservices, Kubernetes, or cloud orchestration. The project relies on local Docker Compose.
*   **No WebSockets**: The dashboard uses intentional HTTP polling for JMeter load-testing evaluation. Do not upgrade to WebSockets.

## 2. Setting Up the Development Environment
1. Clone the repository.
2. Start the Docker infrastructure: `docker compose up -d --build`
3. Create and activate a Python virtual environment.
4. Install requirements: `pip install -r requirements.txt`
5. Apply migrations: `python manage.py migrate`
6. Run the background daemon: `python manage.py monitor_containers`

## 3. Branching Strategy
*   `main` - Stable, presentation-ready code.
*   `dev` or `feature/<name>` - Active development branches for new features or experiments.
*   Always test changes against the `ihack_load_test.jmx` JMeter plan to ensure performance remains stable.

## 4. Code Style & PRs
*   Follow PEP-8 guidelines for Python code.
*   For frontend changes, adhere to the rules outlined in `STYLEGUIDE.md` (use Vanilla Bootstrap 5.3 utilities over ad-hoc CSS).
*   Ensure commit messages are descriptive.
