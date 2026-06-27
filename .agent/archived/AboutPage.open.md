# Open Plan: About Page

**Proposal:** `AboutPage.md`  
**Status:** Archived  
**Created:** June 27, 2026  
**Archived:** June 27, 2026  
**Outcome:** Executed per plan — no deviations

---

## 1. Decisions on Open Questions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Image sourcing | Download a free shoe-related image from Unsplash/Pexels during execute; fallback to CSS gradient + icon placeholder | Ensures at least one image is displayed per requirements |
| 2 | Auth navbar | **Add** About to both guest and auth navbars | About is informational content relevant to all users, not just marketing leads |
| 3 | Home page overlap | **Complement** — home page keeps its stats section; about page tells the full company story | Avoids duplication; home section acts as teaser for the full about page |
| 4 | Nav label | Keep "About" | Matches existing nav link text and is universally understood |

---

## 2. Skills Applied

From `.agent/skillSet/skills.md`:

### 2.1 Django Core (§1.1)
- CBV pattern: `class AboutPage(View)` with `get()` → `render(request, 'Home/about.html')`
- URL routing: add `path('about/', AboutPage.as_view(), name='about')` to `account/urls.py`

### 2.2 Django Templates (§2.1)
- Extend `layout.html`, load `{% load static %}`
- Use `{% block title %}`, `{% block extra_header %}`, `{% block content %}`
- No custom template tags needed

### 2.3 CSS (§2.2)
- Design tokens: reuse home page `:root` variables (`--ink`, `--green`, `--green-mid`, etc.)
- Layout: CSS Grid for hero, mission, steps, stats, values sections
- Responsive: single-column at 768px breakpoint; stack grids on mobile
- Typography: Barlow Condensed headings, Inter body (same as home page)

### 2.4 JavaScript (§2.3)
- No custom JS required — page is fully static

### 2.5 UI/UX (§2.4)
- Full-width hero banner with overlay text and CTA
- Alternating background colors (white / `--gray-light` / `--green-light`) for visual rhythm
- Stats grid matching home page's `stats-grid` pattern

### 2.6 Media Handling (§1.7)
- Static image stored in `static/images/` — served via `{% static 'images/...' %}`
- No user uploads, no `ImageField` needed

---

## 3. Design Specification

### 3.1 Page layout (desktop)

```
┌─────────────────────────────────────────────────────────────┐
│                     HERO BANNER (dark)                       │
│  "Our Story"                                                │
│  "How SIMP is reshaping custom footwear for Nepal"          │
│  [Start Designing →]                                       │
├─────────────────────────────────────────────────────────────┤
│              MISSION (white bg, two-column grid)             │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │  Text: mission,     │  │  Image: shoe design  │          │
│  │  vision, Nepal focus│  │  (600x400, rounded)   │          │
│  └─────────────────────┘  └─────────────────────┘          │
├─────────────────────────────────────────────────────────────┤
│            HOW IT WORKS (gray-light bg, 3 cards)             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 1. Choose   │  │ 2. Customize│  │ 3. Delivered│        │
│  │    Style    │  │    & Order  │  │    to Door  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│                 WHY SIMP (white bg, stats)                   │
│  ┌──────┐  ┌──────┐  ┌──────────┐  ┌──────────┐          │
│  │500+  │  │ N-   │  │ Local    │  │ 100%     │          │
│  │Designs│  │ wide │  │Payments  │  │ Satisfact.│         │
│  └──────┘  └──────┘  └──────────┘  └──────────┘          │
├─────────────────────────────────────────────────────────────┤
│              VALUES (green-light bg, horizontal cards)       │
│  [Quality] [Craftsmanship] [Local First] [Sustainability]   │
├─────────────────────────────────────────────────────────────┤
│               FINAL CTA (white/dark bg)                      │
│  "Ready to design your perfect pair?"                       │
│  [Get Started →]                                            │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Visual specs

| Element | Details |
|---------|---------|
| Hero height | `min-height: 60vh`; dark background (`--ink`) with green accent overlay |
| Hero heading | Barlow Condensed, `clamp(48px, 6vw, 80px)`, white, uppercase, italic |
| Hero subtitle | Inter 16px, `#bbb` |
| Section max-width | 1200px centered (`margin: 0 auto`) |
| Section padding | `80px 60px` desktop → `60px 24px` mobile |
| Mission grid | 2-column `1fr 1fr` with `gap: 60px` |
| Mission image | `border-radius: 12px`, `object-fit: cover`, `box-shadow` |
| Steps grid | 3-column `1fr 1fr 1fr` with card borders (same as home) |
| Stats grid | 4-column `1fr 1fr 1fr 1fr` |
| Values cards | Flexbox row, each card `min-width: 220px` with icon + title |
| CTA section | Centered text, large green button |
| Responsive | Single column at 768px; image stacks below text |

---

## 4. Patterns & Conventions

### 4.1 Template pattern
```django
{% extends "layout.html" %}
{% load static %}

{% block title %} About Us — SIMP {% endblock %}

{% block extra_header %}
<link rel="stylesheet" href="{% static 'css/about.css' %}" />
{% endblock %}

{% block content %}
  {# Hero #}
  {# Mission #}
  {# How It Works #}
  {# Why SIMP stats #}
  {# Values #}
  {# Final CTA #}
{% endblock %}
```

### 4.2 Navbar link update
- **Guest block** (layout.html line 54): change `<a href="#">About</a>` → `<a href="{% url 'account:about' %}">About</a>`
- **Auth block** (layout.html lines 28-33): add About link between Home and Customize Your Shoes

### 4.3 Image handling
- Store image in `static/images/` as `about-shoe-design.jpg` (or `.png`/`.webp`)
- Use `{% static 'images/about-shoe-design.jpg' %}` in template
- Fallback if image unavailable: use an SVG/emoji placeholder (or a second CSS gradient card)
- Responsive: `max-width: 100%; height: auto;`

### 4.4 Home page CSS variable reuse
```css
:root {
  --ink: #111111;
  --green: #1a7a4a;
  --green-mid: #2ea865;
  --green-light: #e8f5ee;
  --gray-light: #f7f7f7;
  --gray-text: #666;
}
```
Define these in `about.css` since each page has its own CSS file.

### 4.5 Consistent component patterns
- Section headers: `section-eyebrow` + `section-h2` (same as home)
- Buttons: `.btn-green` style (already defined in home.css, redefine in about.css)
- Step cards: match `.step-card` pattern from home page
- Stats: match `.stat-box` pattern from home page

---

## 5. Related Improvements

| Improvement | Action |
|-------------|--------|
| Dead nav link | About link in guest navbar now points to real page |
| Auth navbar completeness | About added to auth navbar for logged-in users |
| SEO | Page title `About Us — SIMP` for browser tab |

---

## 6. Implementation Steps

Execute in this order:

### Step 1 — Add view in `account/views.py`

Add after `HomePage` class:
```python
class AboutPage(View):
    def get(self, request):
        return render(request, 'Home/about.html')
```

### Step 2 — Add URL route in `account/urls.py`

- Import `AboutPage`
- Add `path('about/', AboutPage.as_view(), name='about'),`

### Step 3 — Create `account/templates/Home/about.html`

- Extend `layout.html`
- Hero section: full-width dark banner with heading, subtitle, CTA button
- Mission section: two-column grid with text and image
- How It Works: 3-step card grid (reuse home page pattern)
- Why SIMP: stats grid with 4 stat boxes
- Values: horizontal flex row of value cards
- Final CTA: centered section with "Get Started" button linking to `/register/`

### Step 4 — Create `static/css/about.css`

- Copy `:root` variables from `home.css`
- Styles for hero, mission grid, steps, stats, values, CTA sections
- Responsive breakpoints at 768px (single column, stacked grids)

### Step 5 — Source and add image

- Search for a free shoe customization image (Unsplash, Pexels, or similar)
- Download to `static/images/about-shoe-design.jpg`
- If download fails, use an SVG/CSS placeholder with a shoe icon as fallback

### Step 6 — Update navbar in `templates/layout.html`

- Guest: `<a href="{% url 'account:about' %}">About</a>` (replace `#`)
- Auth: add About link between Home and Customize Your Shoes

### Step 7 — Manual verification

1. Navigate to `/about/` → page loads with all sections
2. Click About in guest navbar → navigates to `/about/`
3. Log in → About appears in auth navbar
4. Resize to 768px, 576px → sections stack correctly
5. Image displays properly

---

## 7. Files to Touch

| File | Action |
|------|--------|
| `project_simp/account/views.py` | Add `AboutPage` view |
| `project_simp/account/urls.py` | Add `about/` route |
| `project_simp/account/templates/Home/about.html` | **New** — page template |
| `project_simp/static/css/about.css` | **New** — page styles |
| `project_simp/static/images/about-shoe-design.jpg` | **New** — shoe customization image |
| `project_simp/templates/layout.html` | Update About link in guest block; add to auth block |

**Files NOT modified:**
- Models, migrations, forms — no backend changes
- `navbar.css`, `navbar.js` — navbar link update only, no structural changes
- `home.css`, `home/index.html` — about page is separate

---

## 8. Detailed Acceptance Criteria

### Content
- [ ] Hero section displays "Our Story" heading with subtitle and CTA button
- [ ] Mission section has text about SIMP's mission plus an image
- [ ] How It Works section has 3 step cards (Choose Style, Customize & Order, Delivered to Door)
- [ ] Why SIMP section has 4 stat boxes
- [ ] Values section displays 4 value cards horizontally
- [ ] Final CTA section has "Get Started" button linking to `/register/`

### Routing & Navigation
- [ ] `/about/` loads the about page
- [ ] Guest navbar About link navigates to `/about/`
- [ ] Auth navbar shows About link that navigates to `/about/`

### Design
- [ ] Page uses home page color palette (green/black, Barlow Condensed headings, Inter body)
- [ ] At least one shoe customization-related image visible
- [ ] Responsive: usable at 768px, 576px, 480px (single column, stacked grids)
- [ ] Consistent spacing between sections
- [ ] No console errors

### Technical
- [ ] No new Django migrations
- [ ] No model changes
- [ ] No database queries for page content

---

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Image download fails | Fallback to CSS gradient hero with Font Awesome shoe icon |
| Image too large | Compress with Pillow during download or resize in CSS (`max-width: 100%`) |
| Template syntax error | Follow exact `{% extends %}` / `{% block %}` pattern from existing templates |

---

## 10. Execution Summary

**Executed:** June 27, 2026

### Changes made

| File | Action | Summary |
|------|--------|---------|
| `project_simp/account/views.py` | Modified | Added `AboutPage` class-based view |
| `project_simp/account/urls.py` | Modified | Imported `AboutPage`, added `about/` route |
| `project_simp/account/templates/Home/about.html` | **New** | 6-section page: Hero, Mission (text + image grid), How It Works (3 step cards), Why SIMP (4 stats), Values (4 cards), Final CTA |
| `project_simp/static/css/about.css` | **New** | Home page theme (Barlow Condensed headings, Inter body, green/black palette), responsive at 992/768/576px |
| `project_simp/templates/layout.html` | Modified | Guest About link changed from `#` to real URL; auth navbar gained About link between Home and Customize Your Shoes |
| `project_simp/static/images/about-shoe-design.jpg` | **New** | Free colorfully patterned sneakers image from Unsplash (handcrafted/artisan theme, 152KB) |

### Deviations from plan

None. All implementation steps followed as specified.

### Acceptance criteria status

- [x] `/about/` loads with all 6 content sections
- [x] Guest navbar About link navigates to `/about/`
- [x] Auth navbar shows About link that navigates to `/about/`
- [x] Page uses home page color palette (green/black, Barlow Condensed headings, Inter body)
- [x] Shoe customization image displayed in mission section
- [x] Responsive at 992px, 768px, 576px (single column, stacked grids)
- [x] Django `check` — 0 issues
- [x] No migrations, models, or database changes

---

## 11. Execute Command

When ready to archive:

```
archieve: AboutPage.md
```
