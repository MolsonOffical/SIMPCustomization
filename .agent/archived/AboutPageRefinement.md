# Proposal: About Page Refinement

**File name:** `AboutPageRefinement.md`  
**Status:** Archived  
**Created:** June 27, 2026  
**Archived:** June 27, 2026  
**Outcome:** Guest-gated About page, consolidated CTAs, added login banner, removed auth nav About link  
**Type:** Frontend — About page guest gating, button relinking, login banner  
**Skill set:** `Frontend-Design`

---

## 1. Summary

Refine the About page to be guest-only, consolidate call-to-action buttons, and add a contextual banner on the login page. Three changes:

1. **Guest-gate the About page** — Authenticated users who visit `/about/` are redirected to home. The page is a marketing landing page, not relevant to logged-in users.
2. **Button consolidation** — Remove the "Start Designing" button from the hero ("Our Story") section. Rename the final CTA "Get Started" button to "Start Designing" and point it to the login page.
3. **Login page banner** — When users arrive at login from the About page's "Start Designing" CTA, show a subtle "login to start" message at the top-right of the login card.

---

## 2. Relevance to Current Project State

| Reference | Relevance |
|-----------|-----------|
| `AboutPage.md` (archived) | The existing About page was just built — this proposal refines its behavior and CTAs |
| `PROJECT_DOCUMENTATION.md` §4.4 Login page | The login card layout needs a small addition for the contextual banner |
| `PROJECT_DOCUMENTATION.md` §4.1 Navbar | Guest-only page means the About link in auth navbar may need reconsideration |
| `Frontend-Design` skillset | UI refinement, type/color, restrained addition to login page |

### Current behavior
- `/about/` renders for all users regardless of auth status
- Hero has "Start Designing →" (links to `/customize/`)
- Final CTA has "Get Started →" (links to `/register/`)
- Login page has no contextual messaging

---

## 3. Detailed Changes

### 3.1 Guest-gate the About page

`account/views.py` — `AboutPage.get()`:
```python
class AboutPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('account:home')
        return render(request, 'Home/about.html')
```

Authenticated users hitting `/about/` are redirected to home immediately.

### 3.2 Button changes

**Hero section** (`Home/about.html` lines 12–21):
- Remove the entire `<a href="/customize" class="btn-about-green">Start Designing →</a>` line
- The hero becomes a purely informational banner (title + subtitle only)

**Final CTA** (`Home/about.html` lines 140–147):
- Change text from "Get Started" to "Start Designing"
- Change link target from `{% url 'account:register' %}` to `{% url 'account:login' %}?from=about`
- Keep all existing styling (`btn-about-green btn-about-green--large`)

### 3.3 Login page "login to start" banner

**`account/views.py` — `LoginUser.get()`:**
- Check `request.GET.get('from')`
- If `from == 'about'`, pass `show_login_message=True` in template context

**`login/login.html`:**
- Add a small banner element at the top-right of `.box-left` (above the form)

**`login.css`:**
- Add `.login-context-banner` styles — small rounded pill/callout, positioned top-right inside `.box-left`

---

## 4. Dependencies & Constraints

- The login page already has a `.box-left` with flex column layout — the banner needs to be positioned without breaking the existing layout
- No new routes, models, or migrations
- The auth navbar's About link (added in NavbarConsistency) should stay — it will simply redirect to home for authenticated users rather than 404ing

---

## 5. Design Direction (per Frontend-Design skill)

### Palette
- Login page uses purple accent (`#6c63ff`) — the banner should use the same accent for consistency
- Small green accent dot/icon to connect it to the About page's green theme
- Subtle, not disruptive — this is a contextual hint, not a modal

### Layout
- Top-right corner of `.box-left`, above the card title
- Small pill/badge shape: `font-size: 12px`, `padding: 6px 14px`, `border-radius: 20px`
- Light background (`rgba(108, 99, 255, 0.08)`) with left accent border matching login's alert style
- Icon: `fa-solid fa-pen-ruler` or `fa-solid fa-paintbrush` (design-related)

### Copy
- "Login to start designing" — concise, action-oriented
- Matches the "Start Designing" button label across the flow

---

## 6. Open Questions

1. **Auth navbar About link** — Currently both guest and auth navbars have About. With guest-gating, authenticated users who click About will just be redirected to home. Should the auth navbar keep the About link, or remove it?

2. **Login banner dismissal** — Should the banner persist across page refresh (via session) or only appear on the initial redirect from the About page? Using a GET parameter (`?from=about`) means it clears on refresh automatically.

---

## 7. Files to Change

| File | Action |
|------|--------|
| `project_simp/account/views.py` | Modify `AboutPage.get()` — redirect if authenticated; modify `LoginUser.get()` — pass `show_login_message` context |
| `project_simp/account/templates/Home/about.html` | Remove hero button; rename final CTA button and relink to login |
| `project_simp/account/templates/login/login.html` | Add contextual banner when `show_login_message` is True |
| `project_simp/static/css/login.css` | Add `.login-context-banner` styles |

**No migrations, models, new views, or new routes required.**

---

## 8. Acceptance Criteria

- [ ] Authenticated users visiting `/about/` are redirected to `/` (home)
- [ ] Guest users see the full About page (unchanged content, minus hero button)
- [ ] Hero section no longer has a "Start Designing" button
- [ ] Final CTA button reads "Start Designing →" and links to login page
- [ ] Login page shows "Login to start designing" banner at top-right when accessed via About page's CTA
- [ ] Login page renders normally (no banner) when accessed directly
- [ ] Banner clears on page refresh (query-parameter-based)
