# Proposal: About Page

**File name:** `AboutPage.md`  
**Status:** Archived  
**Created:** June 27, 2026  
**Archived:** June 27, 2026  
**Outcome:** Implemented — static About page with hero, mission, steps, stats, values, and CTA sections  
**Type:** Frontend — static marketing page

---

## 1. Summary

Create a dedicated **About page** (`/about/`) that describes the SIMP platform — a Nepal-based custom shoe design and ordering service. The page replaces the current dead `#` link in the navbar and follows the home page's visual language (green/black theme, Barlow Condensed headings, Inter body, responsive grid layouts).

The page is fully static (no database models needed), mirroring the approach used for the home page.

---

## 2. Relevance to Current Project State

| Reference | Relevance |
|-----------|-----------|
| `PROJECT_DOCUMENTATION.md` §4.2 — Home page static sections | About page follows same pattern: static content, no backend data binding |
| `PROJECT_DOCUMENTATION.md` §4.1 — Layout navbar | Current About link points to `#`; needs wiring to real route |
| `PROJECT_DOCUMENTATION.md` §5.1 UI Gap #2 — Navbar inconsistency | Guest navbar currently shows "About" as dead link — this resolves it |
| Home page existing "About" section | The home page already has a stats-based about section — the dedicated About page expands on that story rather than replacing it |
| NavbarConsistency (archived) | Auth navbar removed About link; guest navbar kept it. Proposal should decide whether authenticated users also get About |

---

## 3. Content Outline

### Hero Banner
- Full-width dark/green gradient banner
- Heading: "Our Story" (Barlow Condensed, large)
- Subtitle: "How SIMP is reshaping custom footwear for Nepal"
- CTA button: "Start Designing" (links to `/customize/` placeholder)

### Mission Section
- Two-column grid: text left, image right
- Text: SIMP's mission — bridging custom shoe design with Nepali craftsmanship, local payments (eSewa, Khalti), and nationwide delivery
- Image: Shoe customization / design process visual

### How It Works (3 steps)
- Reuse the 3-step card pattern from the home page but tailored to the company story:
  1. **Choose Your Style** — Pick from categories, colors, patterns
  2. **Customize & Order** — Upload artwork, select size, pay locally
  3. **Delivered to Your Door** — Handcrafted and shipped across Nepal

### Why SIMP
- Stats grid (like home page about section):
  - "500+ Custom Designs"
  - "Nationwide Delivery"
  - "Local Payments (eSewa, Khalti)"
  - "100% Satisfaction"

### Team / Values
- Simple row of value cards: Quality, Craftsmanship, Local First, Sustainability

### Final CTA
- "Ready to design your perfect pair?"
- Large button: "Get Started" → `/register/`

---

## 4. Dependencies & Constraints

### Image
- A shoe customization-related image is needed in `static/images/` (e.g., `about-hero.jpg` or `shoe-design.jpg`). Not present in the current static directory.
- **Suggestion:** Add a royalty-free shoe or design-process image. The image should be locally stored in `static/images/`.

### Route wiring
- The guest navbar's About link in `layout.html` must be updated from `href="#"` to `{% url 'account:about' %}`.

### No database changes
- Page is fully static — no models, migrations, or forms required.

---

## 5. Design Direction

### Theme palette (matching home page)
| Token | Value |
|-------|-------|
| `--ink` | `#111111` |
| `--green` | `#1a7a4a` |
| `--green-mid` | `#2ea865` |
| `--green-light` | `#e8f5ee` |
| `--gray-light` | `#f7f7f7` |

### Typography
- Headings: `'Barlow Condensed', sans-serif` (uppercase, bold)
- Body: `'Inter', sans-serif`

### Layout
- Full-width hero with overlay
- Content sections in centered containers (max-width ~1200px)
- Alternating text/image grids using CSS Grid
- Responsive breakpoints matching existing (768px, 576px)

### Existing patterns to follow
- Template extends `layout.html`, loads `{% load static %}`
- Page-specific CSS via `{% block extra_header %}` linking to `static/css/about.css`
- Font Awesome 6 for icons
- Consistent spacing and hover states

---

## 6. Open Questions

1. **Image sourcing** — Should the image be downloaded from a free stock site, or should I create an SVG/CSS illustration placeholder? The image needs to relate to shoes or customization.

2. **Auth navbar** — Currently, the guest navbar shows "About" but the auth navbar (from NavbarConsistency) does not. Should authenticated users also see "About" in their nav, or is it guest-only (marketing) content?

3. **Home page About section overlap** — The home page already has a stats-based "About" section. Should the dedicated About page complement or replace what's on the home page?

4. **About link label** — Keep as "About" or use "Our Story" for the nav link?

---

## 7. Files Expected to Change

| File | Action |
|------|--------|
| `account/views.py` | Add `AboutPage` view |
| `account/urls.py` | Add `about/` route |
| `account/templates/Home/about.html` | **New** — page template |
| `static/css/about.css` | **New** — page styles |
| `templates/layout.html` | Update About link to real URL |
| `static/images/<about-image>.jpg` | **New** — shoe customization image |

**No migrations, models, or forms required.**

---

## 8. Acceptance Criteria (high level)

- [ ] `/about/` loads and renders with correct content
- [ ] Navbar About link navigates to `/about/`
- [ ] Page matches home page theme (green/black, Barlow Condensed headings)
- [ ] At least one shoe customization-related image displayed
- [ ] Responsive layout at desktop, tablet, and mobile
- [ ] No console errors
- [ ] No database changes required
