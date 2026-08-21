# iHack UI/UX Styling Guidelines

To maintain aesthetic consistency when adding new features or views, adhere strictly to the following frontend principles. The platform was built primarily utilizing vanilla **Bootstrap 5.3**. Rely on the CSS utility classes rather than creating ad-hoc `.css` files.

## 1. Base Layout Rules
*   **Body Background:** Maintained as `#f8f9fa` (Light grey) via Bootstrap's `bg-light` or `style="body { background-color: #f8f9fa; }"`.
*   **Navigation:** Uses high-contrast dark mode to separate the app boundary. (`navbar-dark bg-dark`).
*   **Containers:** Use constrained standard grids `<div class="container mt-4">` directly beneath the navbar.

## 2. Cards & Structure
All dashboard visual groupings should be housed in soft shadow cards to maintain depth:
```html
<div class="card shadow-sm rounded border-0">
  <div class="card-body">...</div>
</div>
```

## 3. Color Theory & Semantics
Never use colors arbitrarily. Bootstrap contexts mean specific things in the CTF framework:
*   `Primary (Blue)`: Safe, generic actions (e.g., standard Flag Submission inputs, Score Badges).
*   `Danger (Red)`: Specifically reserved for explicit offensive contexts (e.g., the Attack-Defense PoC arena, "Target IP", and "Connect to Console" buttons).
*   `Success (Green)`: Solved challenges or accepted flags. 
*   `Warning (Yellow)`: Reserved for AI Analytics tracking and Administrator data.

## 4. Typography & Badges
*   Use Bootstrap `fw-bold` and `lead` to establish hierarchy.
*   Points and numerical values should always be highlighted inside pill badges for rapid scanning:
  `<span class="badge bg-primary rounded-pill">150 pts</span>`
*   IP Addresses or Mathematical Slopes ($M_c$) should be stylized with `<span class="font-monospace">`.

## 5. Visualizer Integrations (Chart.js)
If adding new graphs, utilize the pre-imported `Chart.js` CDN logic located in `base.html` / `ai_dashboard.html`.
*   *For CTF Data*: Always use `stepped: 'before'` interpolation algorithms to visually mimic standard platforms like CTFd, creating harsh, clear stair-step progressions rather than smooth curves.
