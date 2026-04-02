# 🚀 Responsive Portfolio Website (Mini Project)

A complete, multi-section, single-page responsive portfolio website built with pure **HTML5** and **CSS3**. This project demonstrates mastery in semantic structure, advanced layouts (Grid & Flexbox), theming with CSS variables, and modern web accessibility — all without relying on JavaScript libraries.

## 🌟 Key Features

- **8 Core Sections:** Navigation, Hero, About Me, Projects, Experience, Testimonials, Contact, and Footer.
- **Dual Theming:** Seamless Light and Dark mode toggle with `prefers-color-scheme` auto-detection.
- **CSS-Only Interactivity:** Mobile hamburger menu implemented using the "Checkbox Hack" (zero JS).
- **Responsive Mastery:** Mobile-first design architecture with breakpoints at 768px (Tablet), 1024px (Desktop), and 1440px (Wide).
- **Performance Focused:** Utilizes GPU-accelerated `transform` and `opacity` animations for a smooth 60fps experience.
- **Accessibility (A11y):** Skip-to-content links, semantic HTML5, ARIA labels, and WCAG-compliant color contrast.

## 🛠️ Technology Stack

1.  **HTML5:** Semantic tagging (`<main>`, `<section>`, `<article>`, `<nav>`, `<header>`, `<footer>`).
2.  **CSS3:**
    *   **Layout:** CSS Grid (`grid-template-areas`), Flexbox (`justify-content`, `align-items`).
    *   **Theming:** CSS Custom Properties (Variables) for colors, spacing, and typography.
    *   **Animations:** `@keyframes` for entry reveals and interactive hover states.
3.  **JavaScript:** Exactly one line of code to manage the theme toggle state.

## 📁 File Structure

```text
portfolio/
├── index.html           # Main entry point - Semantic structure
├── README.md            # Project documentation (this file)
└── css/
    ├── reset.css        # CSS normalization/reset
    ├── variables.css    # Design tokens (Colors, Spacing, Themes)
    ├── layout.css       # Grid & Flexbox structural blueprints
    ├── components.css   # Visual styling (Cards, Buttons, Forms)
    ├── animations.css   # Motion, transitions, and keyframes
    └── responsive.css   # Mobile-first media queries
```

## 🚀 How to Run

1.  Clone or download the project folder.
2.  Open `index.html` in any modern web browser (Chrome, Firefox, Safari, Edge).
3.  **No server required!** The project runs purely as static files.

## 📝 Implementation Workflow

This project was built following a **modular CSS methodology**:
1.  **Foundation:** Initialized with a custom Reset and root Variables.
2.  **Base:** Mobile layout created first to ensure core readability.
3.  **Enhancement:** Progressive media queries added for larger screens to enable multi-column Grid layouts.
4.  **Polish:** Integrated staggered animations and decorative pseudo-elements (`::before`/`::after`) for a premium "wowed" aesthetic.

## 📧 Contact

Built with passion as part of a front-end development mini-project. Feel free to reach out for collaborations!

---
*Targeting Accessibility Score: 95+ | Desktop Performance: Grade A*
