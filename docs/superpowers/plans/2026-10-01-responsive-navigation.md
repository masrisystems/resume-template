# Responsive Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a responsive, accessible, mobile-first navigation bar on `career.masrisystems.com` with a hamburger toggle and slide-down drawer under 900px, eliminating horizontal overflow while preserving all test invariants.

**Architecture:** Replace the desktop-only/scroll-strip approach on `#top-nav` with a dual-mode layout: an inline desktop nav for viewports > 900px and a fixed header with brand, theme toggle, and hamburger button for viewports <= 900px. A glassmorphic `#nav-drawer` contains full-width touch targets, language toggle, and starter kit download CTA.

**Tech Stack:** Semantic HTML5, Vanilla CSS3 (glassmorphism, media queries), Vanilla JavaScript (`hub.js`), Python `unittest` (`tests/test_career_hub.py`).

---

### Task 1: Add Responsive Navigation Tests to Test Suite

**Files:**
- Modify: `tests/test_career_hub.py`

- [ ] **Step 1: Write failing test in `tests/test_career_hub.py`**

Add `test_14_responsive_navigation_and_drawer` asserting:
1. `#nav-toggle-btn` exists within `#top-nav`, has `aria-controls="nav-drawer"`, `aria-expanded="false"`, and SVG icon.
2. `#nav-drawer` exists within `#top-nav`, has class `nav-drawer`, and contains all 7 section links.
3. Every link in `#nav-drawer` points to a valid section anchor.
4. `hub.js` contains `function toggleMobileNav` and `function closeMobileNav`.
5. Zero emojis in all new elements.

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_career_hub.py`
Expected: FAIL on `test_14_responsive_navigation_and_drawer` (Missing `#nav-toggle-btn`)

- [ ] **Step 3: Commit test changes**

Run:
```bash
git add tests/test_career_hub.py
git commit -m "test: add responsive navigation and mobile drawer test cases"
```

---

### Task 2: Implement Responsive Navigation Markup in `index.html`

**Files:**
- Modify: `index.html:93-120`

- [ ] **Step 1: Update `#top-nav` structure in `index.html`**

Update `#top-nav` to:
1. Wrap desktop links in `.nav-links.desktop-nav-links`.
2. Group desktop actions (`#lang-toggle-nav-btn`, Portfolio link, Download Kit CTA) in `.nav-desktop-actions`.
3. Add `#nav-toggle-btn` to `.nav-controls` with `#nav-icon-menu` and `#nav-icon-close` SVG vector icons.
4. Add `#nav-drawer` containing `.nav-links.mobile-nav-links` and `.nav-drawer-actions` (language switch, portfolio, download CTA).
5. Ensure zero emojis and all classes conform to testing invariants.

- [ ] **Step 2: Verify markup syntax**

Run: `python -c "from bs4 import BeautifulSoup; soup = BeautifulSoup(open('index.html', encoding='utf-8'), 'html.parser'); assert soup.find(id='nav-toggle-btn'); assert soup.find(id='nav-drawer'); print('HTML valid')"`
Expected: `HTML valid`

---

### Task 3: Implement Responsive Navigation Styles in `style.css`

**Files:**
- Modify: `style.css:380-645`

- [ ] **Step 1: Update styles in `style.css`**

1. Remove the old `overflow-x: auto` from `.top-nav-inner` under `@media (max-width: 900px)`.
2. Add `.nav-toggle-btn` styles (38x38px flex button, border hairline, hover state, dark mode support).
3. Hide `.nav-toggle-btn` and `#nav-drawer` on desktop (`@media (min-width: 901px)`).
4. Hide `.desktop-nav-links` and `.nav-desktop-actions` on mobile/tablet (`@media (max-width: 900px)`).
5. Style `#nav-drawer`: fixed positioning below top nav (64px top offset), full width, max-height `calc(100vh - 64px)`, glassmorphic blur (`rgba(255,255,255,0.98)` / `rgba(15,23,42,0.98)` in dark), shadow, and smooth slide-down animation.
6. Style `.drawer-link` with 44px min-height touch targets, padding, rounded hover pill styles.
7. Style `.nav-drawer-actions` with clean layout for language button, portfolio link, and full-width download CTA.
8. Add `@media (max-width: 480px)` refinements for `.nav-tag` and `.nav-brand-title` so the header fits effortlessly on 320px screens.

- [ ] **Step 2: Sync stylesheets using engine**

Run: `python -c "from engine.config import sync_stylesheets; sync_stylesheets(); print('Stylesheets synced')"`
Expected: `Stylesheets synced`

---

### Task 4: Implement Mobile Navigation Controller in `hub.js`

**Files:**
- Modify: `hub.js`

- [ ] **Step 1: Add mobile nav interaction logic in `hub.js`**

Implement:
1. `toggleMobileNav()`: Toggles `.is-open` on `#nav-drawer`, updates `aria-expanded` and icon visibility (`#nav-icon-menu` / `#nav-icon-close`).
2. `closeMobileNav()`: Removes `.is-open`, sets `aria-expanded="false"`, shows menu icon, hides close icon.
3. Event listeners:
   - Window click outside `#top-nav` closes the drawer.
   - Window resize (> 900px) closes the drawer.
   - Keyboard listener for `Escape` key closes the drawer and restores focus.

- [ ] **Step 2: Run test suite**

Run: `python -m unittest tests/test_career_hub.py`
Expected: 14 tests pass (100% OK).

- [ ] **Step 3: Commit implementation**

Run:
```bash
git add index.html style.css hub.js jobs/roles/html/style.css jobs/resumes/style.css
git commit -m "feat: implement responsive top navigation drawer with accessible hamburger toggle"
```

---

### Task 5: End-to-End Verification & Validation

**Files:**
- Inspect: `index.html`, `style.css`, `hub.js`

- [ ] **Step 1: Validate resume files with engine**

Run: `python jobs/engine.py validate-resume --file resume.html`
Expected: `[OK] Resume Validation PASSED: resume.html`

- [ ] **Step 2: Verify DOM structure programmatically**

Run: DOM verification checking desktop & mobile attributes, ARIA tags, zero emojis, and anchor validity.

- [ ] **Step 3: Run full unittest suite**

Run: `python -m unittest tests/test_career_hub.py`
Expected: All tests pass.
