# Proposal: Navbar Consistency

**File name:** `NavbarConsistency.md`  
**Status:** Archived  
**Created:** June 26, 2026  
**Archived:** June 27, 2026  
**Outcome:** Implemented — guest/auth dual navbar with profile dropdown, icon actions, and responsive layout  
**Type:** UI / Frontend — authenticated navbar experience

---

## 1. Summary

Improve navbar consistency by introducing **two distinct navigation states** in `templates/layout.html`:

| State | Audience | Behavior |
|-------|----------|----------|
| **Guest (unauthenticated)** | Visitors not logged in | **Keep as-is** — Home, Blogs, Categories dropdown, About, search bar, Login, Register |
| **Authenticated** | Logged-in customers | Replace marketing nav with app-focused links and icon actions; move account controls into a **profile dropdown** |

This proposal addresses **UI Improvement #2 (Navbar consistency)** from `PROJECT_DOCUMENTATION.md` in a targeted way: the guest experience stays unchanged; the logged-in experience reflects SIMP’s core product actions (customize, explore, orders, notifications) instead of marketing/blog links.

---

## 2. Proposed Changes (Detailed)

### 2.1 Guest navbar — no change

When `request.user.is_authenticated` is **False**, retain the current structure:

- Brand (logo + SIMP)
- Center links: Home, Blogs, Categories (dropdown), About
- Right area: search form, Login, Register

**Rationale:** User confirmed the pre-login navbar is fine.

---

### 2.2 Authenticated navbar — new center links

When `request.user.is_authenticated` is **True**, **remove** from center nav:

- Blogs
- Categories (dropdown)
- About

**Replace with:**

| Label | Type | Placement | Notes |
|-------|------|-----------|-------|
| **Customize Your Shoes** | Text link | Center nav | Primary CTA; aligns with home hero “Design Now” |
| **Explore** | Text link | Center nav | Browse/discover products (future catalog) |

**Keep:**

- **Home** — still useful as landing/dashboard entry

---

### 2.3 Authenticated navbar — right-side icon actions

On the **right**, near the edge, add icon-only (or icon-primary) actions:

| Element | Icon (Font Awesome) | Purpose |
|---------|---------------------|---------|
| **Your Orders** | e.g. `fa-box` or `fa-bag-shopping` | Link to order history (not built yet) |
| **Notifications** | `fa-bell` | Notification center (not built yet) |

These sit in the right `user-actions` cluster, visually grouped and aligned toward the outer edge.

**Remove from authenticated right area:**

- Inline username text link
- Standalone Logout link
- *(Open decision — see §5)* Search form visibility when logged in

---

### 2.4 Profile icon dropdown (authenticated)

Replace the current username + Logout links with a **profile icon** that opens a dropdown menu.

**Trigger:**

- Circular profile button using:
  - User’s `profile` image if uploaded (`request.user.profile.url`), **or**
  - Default user avatar icon (`fa-solid fa-user-circle` or similar)

**Dropdown contents:**

| Item | Action |
|------|--------|
| **Username** | Display only — `{{ request.user.username }}` (non-clickable header row) |
| **Logout** | Link to `{% url 'account:logout' %}` with logout icon |

**Interaction:**

- Reuse existing dropdown pattern from `navbar.js` (mouseenter/mouseleave fade) **or** extend JS to support click-to-toggle on mobile
- Dropdown panel should be compact (not the wide Categories grid) — single-column menu

---

## 3. Alignment with Project Documentation

### 3.1 Directly related gaps (from `PROJECT_DOCUMENTATION.md`)

| Doc reference | Relevance |
|---------------|-----------|
| §4.1 Shared Layout | Primary file to modify — `templates/layout.html` |
| §4.1 Known gap: empty Categories dropdown | Authenticated users no longer see Categories — reduces confusion until catalog exists |
| UI Improvement #2 — Navbar consistency | Partially addressed: logged-in nav matches product-focused app vs marketing site |
| UI Improvement #4 — Mobile navigation | This work should not regress mobile; may need hamburger follow-up later |
| §2 Out of scope: orders, catalog, notifications | New links/icons are **UI placeholders** until backend routes exist |

### 3.2 Existing implementation to leverage

| Asset | Path | Role |
|-------|------|------|
| Layout template | `project_simp/templates/layout.html` | Conditional `{% if user.is_authenticated %}` blocks |
| Navbar styles | `static/css/navbar.css` | Extend for auth nav links, icon buttons, profile dropdown |
| Navbar JS | `static/js/navbar.js` | Extend dropdown handler for profile menu |
| Font Awesome 6 | CDN in layout | Icons for orders, bell, profile, logout |
| CustomUser.profile | `account/models.py` | Optional profile image in dropdown trigger |
| Logout route | `account:logout` | Already implemented |

### 3.3 Skills required (from `skillSet/skills.md`)

- **§2.1 Django Templates** — `{% if %}`, `{% url %}`, `{% static %}`, template inheritance via `layout.html`
- **§2.2 CSS** — Flexbox navbar layout, sticky positioning, responsive breakpoints
- **§2.3 JavaScript** — Dropdown show/hide; optional keyboard `Escape` to close
- **§2.4 UI/UX** — Clear visual hierarchy: text nav center, utility icons + profile right
- **§1.2 Auth** — Use `request.user.is_authenticated`; no new backend auth logic required

---

## 4. Scope Boundaries

### In scope for this proposal

- Template conditional rendering for guest vs authenticated navbar
- CSS for new links, icon buttons, profile dropdown
- JS updates for profile dropdown behavior
- Placeholder `href="#"` or named routes for future pages (documented in open plan)

### Out of scope (unless added later)

- New Django views/URLs for Customize, Explore, Orders, Notifications
- Notification count badge or real notification data
- Navbar color rebrand to match home page green/black theme (guest navbar stays as-is per user; authenticated styling should remain visually consistent with current white navbar unless open plan specifies otherwise)
- Mobile hamburger menu (separate future proposal)
- Removing or relocating search bar for authenticated users (pending decision)

---

## 5. Open Questions

1. **Search bar when logged in** — Hide it, keep it, or replace with something else? Proposal assumes icons + profile replace the current username/logout area; search behavior is unchanged unless decided in `open:` step.

2. **Link targets (placeholders)** — Suggested defaults until routes exist:
   - Customize Your Shoes → `#` or `/customize` (matches home page CTA, route not implemented)
   - Explore → `#` or `/shop`
   - Your Orders → `#` or `/orders`
   - Notifications → `#` or `/notifications`

3. **Profile image fallback** — Use Font Awesome icon only, or a static default avatar image from `static/images/`?

4. **Home link when authenticated** — Keep “Home” in center nav, or remove in favor of logo-only home navigation?

5. **Notification bell** — Static icon only, or include an empty badge dot for future unread count?

---

## 6. Files Expected to Change (execute phase)

| File | Change type |
|------|-------------|
| `project_simp/templates/layout.html` | Primary — dual navbar markup |
| `project_simp/static/css/navbar.css` | Styles for auth nav, icons, profile dropdown |
| `project_simp/static/js/navbar.js` | Profile dropdown + possibly separate class from Categories dropdown |

**No migration or model changes required** unless profile default image handling is added.

---

## 7. Acceptance Criteria (high level)

- [ ] Guest users see the **exact same** navbar as today (Home, Blogs, Categories, About, search, Login, Register).
- [ ] Authenticated users **do not** see Blogs, Categories, or About.
- [ ] Authenticated users see **Customize Your Shoes** and **Explore** in the center nav.
- [ ] Authenticated users see **Your Orders** icon and **Notification bell** on the right, near the edge.
- [ ] Authenticated users see a **profile icon** with dropdown showing **username** and **Logout**.
- [ ] Profile dropdown uses uploaded profile image when available; sensible fallback otherwise.
- [ ] Logout continues to work via `account:logout`.
- [ ] Navbar remains responsive at existing breakpoints without broken layout.

---

## 8. Next Step

Run:

```
open: NavbarConsistency.md
```

This will produce `NavbarConsistency.open.md` with skills, design spec, patterns, implementation steps, and detailed acceptance criteria.
