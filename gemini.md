<system_context>
# AI Context Rules: iHack FYP Project

If you are an AI assistant opening this project workspace for a new session, follow these constraints exactly. This repository represents a Bachelor's Degree Final Year Project (FYP).

## 1. Scope & Architectural Constraints
*   **Do Not Over-Engineer**: Do not implement enterprise cloud stacks, microservices, Kubernetes, or complex CI/CD environments. You must stay within the specified Bachelor-level setup constraint.
*   **Containerization**: Target infrastructure (MySQL databases and Attack-Defense target PoCs) must be locally sandboxed exclusively using the `docker-compose.yml` file. No dynamic cloud orchestration.
*   **Database Persistence**: Never wipe the `mysql_data` Docker volume. Flag submissions and user accounts must survive server reloads.

## 2. The AI Module (Cold Start Fallback)
The core component of the thesis is the `Intelligent Dashboard` in the `analytics` application (`views.py` and `services.py`).
*   **Linear Regression**: It uses Scikit-Learn to map cumulative challenge points against `elapsed_time` (Momentum $M_c$).
*   **Cold Start Constraint**: The mathematical array calculations will trigger a divide-by-zero or shape mismatch error if a student has fewer than 2 total submissions.
*   **Rule**: You MUST preserve the `if n < 2` fallback condition returning `0.0, 'Insufficient Data'` before fitting the `LinearRegression()` model.

## 3. Security Limits
*   **Rate Limiting**: Do not remove the strict 5-second `timedelta` cooldown from the `submit_flag` endpoint in `jeopardy/views.py`. It explicitly mitigates script-kiddie brute force point farming.
*   **Leaderboard Micro-Caching**: The frontend dashboard polls `/api/leaderboard/` every 5 seconds. Do not upgrade this to WebSockets, as the HTTP polling behavior is intentionally designed to be evaluated by Apache JMeter load tests.
## 4. Coding Standards
*   **Style**: Reference `STYLEGUIDE.md` for all frontend UI changes. Utilize Vanilla Bootstrap 5.3 utilities instead of custom CSS whenever possible.
*   **Backend**: Adhere strictly to Python PEP8 guidelines. Document complex logic, especially within the AI/Analytics modules.

## 5. Validation and Testing Commands
*   **Database**: When suggesting modifications to `models.py`, ensure you also remind the user to execute `python manage.py makemigrations` and `python manage.py migrate`.
*   **Performance Evaluation**: Any architectural changes to the API endpoints must not break compatibility with the `ihack_load_test.jmx` Apache JMeter stress testing plan.
</system_context>
