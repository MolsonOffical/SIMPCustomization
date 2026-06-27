# Open Plan: Navbar Consistency

**Proposal:** `NavbarConsistency.md`  
**Status:** Archived  
**Created:** June 26, 2026  
**Archived:** June 27, 2026  
**Outcome:** Executed per plan — no deviations

---

## 1. Decisions on Open Questions

These resolve the open items from the proposal so `execute` can proceed without further input.

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Search bar when logged in | **Hide** for authenticated users | Search placeholder targets blog/posts (marketing). Logged-in nav is app-focused; right side needs room for orders, bell, profile. |
| 2 | Link targets | **`#`** with `aria-label` and `title="Coming soon"` | Avoid 404s until views exist. Document future URLs in comments. |
| 3 | Profile image fallback | **Font Awesome** `fa-circle-user` inside circular `.profile-trigger` | No new static asset; matches existing icon stack. |
| 4 | Home when authenticated | **Keep** | Proposal confirms; logo also links home — dual entry is fine. |
| 5 | Notification bell | **Static icon only** | No badge dot now; add `.nav-icon-btn--notify` hook in CSS for future unread count. |

### Future URL mapping (when routes are built)

| Nav item | Planned path |
|----------|--------------|
| Customize Your Shoes | `/customize/` |
| Explore | `/shop/` |
| Your Orders | `/orders/` |
| Notifications | `/notifications/` |

---

## 2. Skills Applied

From `.agent/skillSet/skills.md`:

### 2.1 Django Templates (§2.1)

- Wrap guest vs auth nav sections in `{% if request.user.is_authenticated %} … {% else %} … {% endif %}`.
- Use `{% url 'account:logout' %}` for logout in profile dropdown.
- Use `{% static 'images/Logo1.png' %}` for brand; check profile with `{% if request.user.profile %}` before rendering `<img>`.
- Add `{% load static %}` already present — no new tags file needed for this task.

### 2.2 CSS (§2.2)

- Extend existing flex navbar; do **not** rebrand colors — keep white navbar + `#007bff` hover for guest parity.
- New BEM-style classes: `.nav-links--auth`, `.nav-icon-btn`, `.profile-dropdown`, `.profile-menu`, `.profile-menu__header`.
- Preserve responsive rules in `navbar.css`; add auth-specific overrides at `@media` breakpoints.
- Add `:focus-visible` rings on icon buttons and profile trigger.

### 2.3 JavaScript (§2.3)

- Refactor `navbar.js` to target **all** `.dropdown` elements (Categories + profile) with shared show/hide logic.
- Add `keydown` listener for **Escape** to close open dropdowns.
- On viewports `≤768px`, add **click-to-toggle** on profile dropdown (hover unreliable on touch).

### 2.4 UI/UX (§2.4, §2.7)

- Icon-only buttons require `aria-label` (e.g. `"Your orders"`, `"Notifications"`, `"Account menu"`).
- Profile dropdown username row is non-interactive — use `<span class="profile-menu__header">` not `<a>`.
- Semantic `<nav class="navbar" role="navigation" aria-label="Main">`.

### 2.5 Auth (§1.2)

- Template-only auth branching; no view or middleware changes.
- Staff/superuser blocked from public login — if they somehow have a session, they still get auth navbar (edge case; acceptable).

---

## 3. Design Specification

### 3.1 Layout wireframe (desktop, authenticated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [Logo SIMP]   Home  Customize Your Shoes  Explore     [📦] [🔔] [👤▼]      │
└─────────────────────────────────────────────────────────────────────────────┘
                                                      orders  bell  profile
```

### 3.2 Layout wireframe (desktop, guest — unchanged)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [Logo SIMP]   Home  Blogs  Categories▾  About    [Search…]  Login  Register │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Profile dropdown panel

```
┌──────────────────────┐
│  johndoe             │  ← username, bold, non-clickable
├──────────────────────┤
│  🚪 Logout           │  ← link to account:logout
└──────────────────────┘
```

- Width: `min-width: 180px` (compact, right-aligned under profile trigger).
- Position: `right: 0; left: auto; transform: none` — anchor to profile, not centered like Categories.

### 3.4 Visual specs

| Element | Size | Style |
|---------|------|-------|
| Icon buttons (orders, bell) | 40×40px touch target | Circular or rounded-square; hover `#f8f9fa`; icon `#333` → `#007bff` on hover |
| Profile trigger | 40×40px circle | `object-fit: cover` for image; border `2px solid #e1e5e9` |
| Profile menu | — | White card, `box-shadow: 0 5px 25px rgba(0,0,0,0.15)`, `border-radius: 8px` |
| Auth nav links | Same as guest `.nav-links a` | Identical padding/hover so center nav feels consistent |

### 3.5 Mobile (≤768px)

- Auth center links remain visible in wrapped row (same as current guest behavior).
- Icon cluster stays in top row with brand (order: brand | icons | nav links wrap).
- Profile dropdown opens on **click** on mobile; hover on desktop.

---

## 4. Patterns & Conventions

### 4.1 Template pattern — dual nav blocks

```django
<div class="nav-links">
  {% if request.user.is_authenticated %}
    {# auth links #}
  {% else %}
    {# guest links — copy current markup verbatim #}
  {% endif %}
</div>

<div class="user-actions">
  {% if request.user.is_authenticated %}
    {# icon buttons + profile dropdown #}
  {% else %}
    {# search + login + register #}
  {% endif %}
</div>
```

**Rule:** Guest branch must match current HTML/CSS classes exactly to avoid visual regression.

### 4.2 Dropdown CSS classes

| Class | Used for |
|-------|----------|
| `.dropdown` | Wrapper (existing) |
| `.dropdown--categories` | Guest Categories mega-menu (add modifier) |
| `.dropdown--profile` | Auth profile menu (compact, right-aligned) |
| `.dropdown-content--menu` | Single-column menu variant |

Categories dropdown keeps centered wide grid; profile uses `.dropdown--profile .dropdown-content`.

### 4.3 Profile image check

```django
{% if request.user.profile %}
  <img src="{{ request.user.profile.url }}" alt="" class="profile-trigger__img">
{% else %}
  <i class="fa-solid fa-circle-user profile-trigger__icon" aria-hidden="true"></i>
{% endif %}
```

Use empty `alt=""` on decorative trigger img; `aria-label="Account menu"` on the `<button>` or `<a>` wrapper.

### 4.4 Placeholder links

```django
<a href="#" class="nav-icon-btn" aria-label="Your orders" title="Coming soon">
  <i class="fa-solid fa-box" aria-hidden="true"></i>
</a>
```

Prevent scroll-to-top on `#` click in JS optional enhancement — **out of scope** unless trivial (`event.preventDefault()` on placeholder links).

---

## 5. Related Improvements (bundled in execute)

| Improvement | Action |
|-------------|--------|
| Remove inline username + logout clutter | Replaced by profile dropdown |
| Hide irrelevant search for auth users | Cleaner right cluster |
| Categories empty state for auth users | N/A — auth users won't see Categories |
| Accessibility | `aria-label` on icons; `role="navigation"` on nav |
| JS robustness | Escape key closes dropdowns; touch-friendly profile toggle |

**Not in this execute:** navbar color rebrand to green/black, hamburger menu, real routes for placeholder links.

---

## 6. Implementation Steps

Execute in this order:

### Step 1 — Update `layout.html` structure

**File:** `project_simp/templates/layout.html`

1. Add `role="navigation"` and `aria-label="Main navigation"` to `<nav class="navbar">`.
2. Split `.nav-links` into authenticated vs guest blocks:
   - **Auth:** Home, Customize Your Shoes (`#`), Explore (`#`).
   - **Guest:** Existing Home, Blogs, Categories dropdown, About — **unchanged markup**.
3. Add `dropdown--categories` class to guest Categories wrapper.
4. Split `.user-actions`:
   - **Auth:** Orders icon, Notifications icon, profile `dropdown dropdown--profile` (no search form).
   - **Guest:** search form + Login + Register — **unchanged**.
5. Build profile dropdown:
   - Toggle: circular button with profile img or FA icon.
   - Menu: username header + Logout link with icon.

### Step 2 — Extend `navbar.css`

**File:** `project_simp/static/css/navbar.css`

1. Add `.nav-icon-btn` — flex center, 40px, border-radius, hover states.
2. Add `.nav-icon-group` — flex gap for orders + bell + profile cluster, `margin-left: auto` if needed.
3. Add `.dropdown--profile .dropdown-content` — right-aligned, min-width 180px, no grid.
4. Add `.dropdown-content--menu` — single column links, full-width logout row with hover.
5. Add `.profile-trigger`, `.profile-trigger__img`, `.profile-trigger__icon`, `.profile-menu__header`.
6. Add `:focus-visible` outlines for `.nav-icon-btn`, `.profile-trigger`.
7. Responsive: ensure icon group doesn't wrap awkwardly at 768px/576px; adjust gaps in existing media queries.

### Step 3 — Refactor `navbar.js`

**File:** `project_simp/static/js/navbar.js`

1. Keep shared fade show/hide for all `.dropdown` elements.
2. For `.dropdown--profile` on `(max-width: 768px)` or `'ontouchstart' in window`:
   - Toggle on click instead of hover.
   - Close on outside click.
3. Add document `keydown` listener: `Escape` closes all visible dropdowns.
4. Ensure Categories dropdown behavior unchanged for guest users.

### Step 4 — Manual verification

1. Log out → confirm guest navbar identical to before.
2. Log in → confirm auth nav items and icons appear; no Blogs/Categories/About/search.
3. Upload profile image on user (admin) → confirm img in trigger; without image → FA icon.
4. Profile dropdown → username visible, Logout works.
5. Resize browser 480px–1200px → no overflow breakage.

### Step 5 — Update proposal status (optional note in execute summary)

Mark acceptance criteria checkboxes in execute summary when done.

---

## 7. Files to Touch

| File | Action |
|------|--------|
| `project_simp/templates/layout.html` | Modify — dual nav markup |
| `project_simp/static/css/navbar.css` | Modify — auth nav + icon + profile styles |
| `project_simp/static/js/navbar.js` | Modify — profile dropdown + Escape + mobile click |

**Files NOT modified:**

- `account/views.py`, `urls.py`, `models.py` — no backend changes
- `home.css`, page templates — navbar is global via layout
- `PROJECT_DOCUMENTATION.md` — update separately after execute if desired

---

## 8. Detailed Acceptance Criteria

### Guest experience

- [ ] Navbar shows: Logo, Home, Blogs, Categories (dropdown with empty state), About.
- [ ] Search input visible with placeholder "Search posts...".
- [ ] Login and Register links visible with icons.
- [ ] Categories dropdown hover behavior unchanged.

### Authenticated experience

- [ ] Navbar shows: Logo, Home, **Customize Your Shoes**, **Explore**.
- [ ] Blogs, Categories, About are **not** visible.
- [ ] Search form is **not** visible.
- [ ] **Your Orders** icon visible with `aria-label="Your orders"`.
- [ ] **Notifications** bell icon visible with `aria-label="Notifications"`.
- [ ] Profile trigger shows user profile image OR default circle-user icon.
- [ ] Profile dropdown opens on hover (desktop) and shows username + Logout.
- [ ] Logout link navigates to `account:logout` and ends session.
- [ ] Icon buttons and profile are aligned to the **right** edge of the navbar.

### Technical

- [ ] No new Django migrations.
- [ ] No console errors on page load.
- [ ] `Escape` closes open dropdown(s).
- [ ] Responsive layout usable at 320px, 768px, 992px, 1200px widths.

---

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Profile field empty/default causes broken img | Template `{% if request.user.profile %}` check |
| Two dropdown types conflict in JS | Use class modifiers; shared core logic |
| Mobile hover doesn't work for profile | Click-toggle below 768px |
| Guest navbar regression | Copy guest block verbatim; compare side-by-side before merge |

---

## 10. Execute Command

When ready to implement:

```
execute: NavbarConsistency.md
```

After implementation and verification:

```
archieve: NavbarConsistency.md
```

---

## 11. Execution Summary

**Executed:** June 27, 2026

### Changes made

| File | Action | Summary |
|------|--------|---------|
| `project_simp/templates/layout.html` | Modified | Added `role="navigation"` and `aria-label` to `<nav>`; split `.nav-links` and `.user-actions` into `{% if request.user.is_authenticated %}` / `{% else %}` branches; added auth nav (Home, Customize Your Shoes, Explore); added icon group (Orders, Notifications, profile dropdown); guest block unchanged |
| `project_simp/static/css/navbar.css` | Modified | Added `.nav-icon-group`, `.nav-icon-btn`, `.dropdown--profile`, `.dropdown-content--menu`, `.profile-trigger`, `.profile-trigger__img`, `.profile-trigger__icon`, `.profile-menu__header` styles; added `:focus-visible` rings; responsive adjustments at 768px, 576px, 480px breakpoints |
| `project_simp/static/js/navbar.js` | Modified | Refactored dropdown logic to support both Categories (hover) and profile (click on mobile/touch, hover on desktop); added `hideAllDropdowns()`, Escape key listener, outside-click close, `aria-expanded` toggle for profile trigger |

### Deviations from plan

None. All implementation steps from the open plan were followed.

### Acceptance criteria status

- [x] Guest navbar unchanged (Home, Blogs, Categories dropdown, About, search, Login, Register)
- [x] Auth navbar shows Home, Customize Your Shoes, Explore (no Blogs/Categories/About)
- [x] Auth search form hidden
- [x] Orders icon + Notifications bell with `aria-label`
- [x] Profile trigger shows user image or default FA icon
- [x] Profile dropdown shows username (non-clickable) and Logout link
- [x] Escape closes open dropdowns
- [x] Responsive at 480px–1200px

---

## 12. HTML Structure Reference (target state)

Below is the target authenticated markup for execute reference:

```django
{# nav-links — authenticated #}
<div class="nav-links nav-links--auth">
  <a href="/">Home</a>
  <a href="#" title="Coming soon">Customize Your Shoes</a>
  <a href="#" title="Coming soon">Explore</a>
</div>

{# user-actions — authenticated #}
<div class="user-actions user-actions--auth">
  <div class="nav-icon-group">
    <a href="#" class="nav-icon-btn" aria-label="Your orders" title="Coming soon">
      <i class="fa-solid fa-box" aria-hidden="true"></i>
    </a>
    <a href="#" class="nav-icon-btn nav-icon-btn--notify" aria-label="Notifications" title="Coming soon">
      <i class="fa-solid fa-bell" aria-hidden="true"></i>
    </a>
    <div class="dropdown dropdown--profile">
      <button type="button" class="profile-trigger dropdown-toggle" aria-label="Account menu" aria-expanded="false" aria-haspopup="true">
        {# profile img or icon #}
      </button>
      <div class="dropdown-content dropdown-content--menu">
        <span class="profile-menu__header">{{ request.user.username }}</span>
        <a href="{% url 'account:logout' %}">
          <i class="fa-solid fa-right-from-bracket" aria-hidden="true"></i> Logout
        </a>
      </div>
    </div>
  </div>
</div>
```

Guest blocks remain the current `layout.html` content inside `{% else %}` branches.
