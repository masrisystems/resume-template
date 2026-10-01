# Design Specification: Responsive Top Navigation (`career.masrisystems.com`)

**Date**: 2026-10-01  
**Target Component**: Pinned Top Header & Navigation (`#top-nav`, `style.css`, `hub.js`, `index.html`)  
**Status**: Proposed & Ready for Implementation  

---

## 1. Context & Motivation

The WebResume & Career Hub currently features a glassmorphic pinned top navigation bar (`#top-nav`) containing the brand logo/title/tag, 7 section links (`.nav-links`), and 4 control actions (`.nav-controls`).

On desktop viewports (>= 901px), the bar displays cleanly in a single horizontal row. However, on mobile and tablet viewports (<= 900px), the bar previously relied on `overflow-x: auto` on `.top-nav-inner`, resulting in a horizontally scrolling strip without a hamburger menu. On smartphone screens (360px - 430px), most navigation links and the primary download CTA were pushed off-screen horizontally without clear visual affordances or touch-friendly menus.

## 2. Requirements & Success Criteria

1. **Clean Viewport Differentiation**:
   - **Desktop (>= 901px)**: Horizontal layout preserved with brand, 7 inline nav links, and control action buttons.
   - **Mobile / Tablet (<= 900px)**:
     - Header bar remains pinned (64px height) with brand on the left, quick theme toggle, and an accessible hamburger button on the right.
     - A collapsible slide-down drawer (`#nav-drawer`) reveals all 7 section links and secondary action buttons (`EN / DE`, `Portfolio`, `Download Kit`).
2. **Touch-Friendly & WCAG Accessible**:
   - Minimum 44px touch targets on mobile links.
   - ARIA support: `aria-expanded`, `aria-controls="nav-drawer"`, `aria-label="Toggle navigation menu"`.
   - Keyboard interaction: Pressing `Escape` closes the drawer and returns focus to the toggle button.
   - Auto-closing: Clicking any navigation link smoothly scrolls to the section and closes the drawer.
3. **Aesthetic & Brand Invariants**:
   - Seamless light/dark mode support with glassmorphic blur and subtle hairline borders matching the Airtable Editorial Dialect.
   - **Zero Emojis**: Strictly Lucide-style SVG vector icons for the hamburger (3 horizontal bars) and close icon (`X`).
   - Zero horizontal page overflow across all smartphone widths (down to 320px).
4. **Test Suite Integrity**:
   - 100% pass rate on `python -m unittest tests/test_career_hub.py`.
   - Preservation of `#top-nav`, `.nav-links a`, `#theme-toggle-nav-btn`, and `no-print` class.

---

## 3. Architecture & Component Structure

### 3.1 HTML Structure (`index.html`)

```html
<nav id="top-nav" class="no-print" aria-label="Main Navigation">
  <div class="hub-container top-nav-inner">
    <!-- Brand Identity -->
    <a href="#hero" class="nav-brand" aria-label="Career Engine Homepage">
      <img src="./assets/masrisystems-logo-light.webp" alt="Masri Systems" class="nav-logo nav-logo-light" />
      <img src="./assets/masrisystems-logo-dark.webp" alt="Masri Systems" class="nav-logo nav-logo-dark" />
      <span class="nav-brand-title">Career Engine</span>
      <span class="nav-tag">Open Source</span>
    </a>

    <!-- Desktop Nav Links (hidden on mobile <= 900px) -->
    <ul class="nav-links desktop-nav-links">
      <li><a href="#daily-workflow" class="nav-link">Daily Routine</a></li>
      <li><a href="#brief-showcase" class="nav-link">Results</a></li>
      <li><a href="#prompts" class="nav-link">AI Prompts</a></li>
      <li><a href="#cover-letters" class="nav-link">Cover Letters</a></li>
      <li><a href="#engine" class="nav-link">CLI Engine</a></li>
      <li><a href="#workflows" class="nav-link">Skills</a></li>
      <li><a href="#resume" class="nav-link">Web Resume</a></li>
    </ul>

    <!-- Controls Cluster -->
    <div class="nav-controls">
      <!-- Theme toggle is kept in top bar for instant access -->
      <button id="theme-toggle-nav-btn" class="btn-pill-sm" onclick="toggleTheme()" aria-label="Toggle Theme">
        <span class="theme-label-light hidden dark:inline">Light</span>
        <span class="theme-label-dark inline dark:hidden">Dark</span>
      </button>

      <!-- Desktop-only controls (hidden on mobile <= 900px, present inside mobile drawer) -->
      <div class="nav-desktop-actions">
        <button id="lang-toggle-nav-btn" class="btn-pill-sm" onclick="switchLanguage()">EN / DE</button>
        <a href="https://links.masrisystems.com" target="_blank" rel="noopener noreferrer" class="btn-pill-sm">Portfolio</a>
        <a href="./download/resume-template-starter.zip" download="resume-template-starter.zip" class="btn-primary btn-nav-cta">Download Kit</a>
      </div>

      <!-- Mobile Hamburger Toggle Button (visible <= 900px) -->
      <button id="nav-toggle-btn" class="nav-toggle-btn" aria-label="Toggle navigation menu" aria-expanded="false" aria-controls="nav-drawer" onclick="toggleMobileNav()">
        <svg id="nav-icon-menu" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
        <svg id="nav-icon-close" class="h-5 w-5 hidden" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
  </div>

  <!-- Mobile Navigation Drawer -->
  <div id="nav-drawer" class="nav-drawer no-print" aria-hidden="true">
    <div class="nav-drawer-inner">
      <ul class="nav-links mobile-nav-links">
        <li><a href="#daily-workflow" class="drawer-link" onclick="closeMobileNav()">Daily Routine</a></li>
        <li><a href="#brief-showcase" class="drawer-link" onclick="closeMobileNav()">Results</a></li>
        <li><a href="#prompts" class="drawer-link" onclick="closeMobileNav()">AI Prompts</a></li>
        <li><a href="#cover-letters" class="drawer-link" onclick="closeMobileNav()">Cover Letters</a></li>
        <li><a href="#engine" class="drawer-link" onclick="closeMobileNav()">CLI Engine</a></li>
        <li><a href="#workflows" class="drawer-link" onclick="closeMobileNav()">Skills</a></li>
        <li><a href="#resume" class="drawer-link" onclick="closeMobileNav()">Web Resume</a></li>
      </ul>
      <div class="nav-drawer-actions">
        <div class="nav-drawer-row">
          <button class="btn-pill-sm drawer-pill-btn" onclick="switchLanguage()">Language: EN / DE</button>
          <a href="https://links.masrisystems.com" target="_blank" rel="noopener noreferrer" class="btn-pill-sm drawer-pill-btn">Portfolio</a>
        </div>
        <a href="./download/resume-template-starter.zip" download="resume-template-starter.zip" class="btn-primary drawer-cta-btn">Download Kit</a>
      </div>
    </div>
  </div>
</nav>
```

### 3.2 CSS System (`style.css`)

1. **Hamburger Button**:
   - `nav-toggle-btn`: 38px x 38px, flex centered, rounded-md, border hairline, surface background, subtle hover and active state. Hidden when `min-width: 901px`.
2. **Drawer Styling**:
   - `position: fixed; top: 64px; left: 0; right: 0; width: 100%;`
   - Background: `rgba(255, 255, 255, 0.98)` with `backdrop-filter: blur(16px)`, dark mode: `rgba(15, 23, 42, 0.98)` with dark hairline border.
   - Max height: `calc(100vh - 64px)`, `overflow-y: auto`.
   - Box shadow: `0 12px 32px rgba(0,0,0,0.08)`.
   - Transitions: Smooth fade and slide animation.
3. **Breakpoints**:
   - `<= 900px`: Desktop links & desktop-actions hidden; hamburger visible; drawer activated.
   - `<= 480px`: `.nav-tag` hidden or made compact; brand logo & title fit effortlessly on 320px screens.

### 3.3 JS Logic (`hub.js`)

1. `toggleMobileNav()`: Toggles `.is-open` class on `#nav-drawer`, updates `aria-expanded` and icon state (`#nav-icon-menu` vs `#nav-icon-close`).
2. `closeMobileNav()`: Closes the drawer and restores icon state.
3. Keyboard & Outside-Click Listeners:
   - Close on `Escape` key.
   - Close on clicking outside `#top-nav`.
   - Close on resizing window to > 900px.

---

## 4. Verification Plan

1. **Unit Tests**:
   - Run `python -m unittest tests/test_career_hub.py` to confirm all 13 tests pass.
2. **Role Compilation**:
   - Run `python jobs/engine.py validate-resume --file resume.html` to confirm engine validity.
3. **DOM & Responsive Testing**:
   - Inspect `#top-nav`, `#nav-toggle-btn`, `#nav-drawer`, links, theme toggle, and styles across 375px (mobile), 768px (tablet), and 1200px (desktop).
