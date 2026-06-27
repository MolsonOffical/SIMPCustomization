# Open Plan: About Page Refinement

**Proposal:** `AboutPageRefinement.md`  
**Status:** Archived  
**Created:** June 27, 2026  
**Archived:** June 27, 2026  
**Skill set:** `Frontend-Design`

---

## 1. Decisions on Open Questions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | Auth navbar About link | **Remove** from auth navbar | About is a marketing landing page for logged-out visitors; no reason for authenticated users to see it. Guest navbar keeps it. |
| 2 | Banner dismissal | GET parameter (`?from=about`) — clears on refresh | Simplest approach, no session state needed. |

---

## 2. Skills Applied

### 2.1 From `skillSet/Frontend-Design/Skills.md`
- **Restraint and self-critique** (§Restraint) — banner is a single restrained addition, not a disruptive element
- **Typography & palette** — banner uses the login page's existing purple accent with a green design icon to subtly bridge the About page's green theme
- **Copy discipline** (§Writing) — "Login to start designing" is concise, active voice, describes exactly what happens

### 2.2 From `skillSet/skills.md`
- **§1.1 Django Core** — CBV modification (`AboutPage.get()`), URL redirect pattern
- **§1.2 Auth** — `request.user.is_authenticated` check, `LoginRequiredMixin` not needed (redirect logic is simpler)
- **§2.1 Django Templates** — `{% if %}`, `{% url %}`, template inheritance
- **§2.2 CSS** — Minimal addition to existing `login.css`; no layout breakage

---

## 3. Design Specification

### 3.1 Login page banner

```
┌──────────────────────────────────────────┐
│ ┌──────────────────────────────────────┐ │
│ │ [🖌] Login to start designing        │ │  ← .login-context-banner (top-right, small pill)
│ ├──────────────────────────────────────┤ │
│ │ LOGIN                                │ │
│ │ ...                                  │ │
│ └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

| Property | Value |
|----------|-------|
| Position | `align-self: flex-end` inside `.box-left` (top-right) |
| Shape | Rounded pill, `border-radius: 20px` |
| Padding | `6px 14px` |
| Font | `12px`, `font-weight: 500` |
| Background | `rgba(108, 99, 255, 0.08)` (matching login alert style) |
| Border | Left `4px solid var(--accent)` |
| Icon | `fa-solid fa-pen-ruler` (design tool icon) |
| Text | "Login to start designing" |
| Display | Only when `show_login_message` is True |
| Responsive | Hidden on mobile (≤768px) or stacked above title |

### 3.2 About page hero (after change)

```
┌────────────────────────────────────────────────────┐
│                   OUR STORY                         │
│  How SIMP is reshaping custom footwear for Nepal   │
│                                                    │
│  ← No button here anymore                          │
└────────────────────────────────────────────────────┘
```

### 3.3 Final CTA (after change)

```
┌──────────────────────────────────────┐
│  Ready to design your perfect pair?  │
│  [Start Designing →]  ← links to login?from=about
└──────────────────────────────────────┘
```

---

## 4. Patterns & Conventions

### 4.1 Guest gate pattern
```python
class AboutPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('account:home')
        return render(request, 'Home/about.html')
```
This follows the same auth-check pattern used elsewhere (e.g., `SendOTPView` checks `pending_user_id`).

### 4.2 Context flag for login banner
```python
class LoginUser(View):
    def get(self, request):
        form = LoginForm()
        context = {'form': form}
        if request.GET.get('from') == 'about':
            context['show_login_message'] = True
        return render(request, 'login/login.html', context)
```

### 4.3 Template conditional in login
```django
{% if show_login_message %}
<div class="login-context-banner">
  <i class="fa-solid fa-pen-ruler" aria-hidden="true"></i> Login to start designing
</div>
{% endif %}
```

### 4.4 Navbar — remove auth About link
In `layout.html` auth nav-links block, remove `<a href="{% url 'account:about' %}">About</a>`. Guest block keeps it unchanged.

---

## 5. Related Improvements

| Improvement | Action |
|-------------|--------|
| Dead CTA flow | Hero button was linking to `/customize` (404) — removed entirely |
| Registration skip | Final CTA was sending users to register; now sends to login (shorter path to designing) |
| Auth navbar tidiness | Marketing page removed from logged-in nav — nav stays focused on app actions |

---

## 6. Implementation Steps

Execute in this order:

### Step 1 — Guest-gate `AboutPage` in `account/views.py`

Add auth check at the top of `AboutPage.get()`:
```python
class AboutPage(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('account:home')
        return render(request, 'Home/about.html')
```

### Step 2 — Add context flag to `LoginUser.get()` in `account/views.py`

```python
class LoginUser(View):
    def get(self, request):
        form = LoginForm()
        context = {'form': form}
        if request.GET.get('from') == 'about':
            context['show_login_message'] = True
        return render(request, 'login/login.html', context)
```

### Step 3 — Update `Home/about.html`

1. Remove the hero button line (`<a href="/customize" class="btn-about-green">Start Designing →</a>`)
2. In final CTA: change text "Get Started" → "Start Designing", change `href` from `{% url 'account:register' %}` to `{% url 'account:login' %}?from=about`

### Step 4 — Add banner to `login/login.html`

Add before the card title:
```django
{% if show_login_message %}
<div class="login-context-banner">
  <i class="fa-solid fa-pen-ruler" aria-hidden="true"></i> Login to start designing
</div>
{% endif %}
```

### Step 5 — Add `.login-context-banner` styles to `static/css/login.css`

```css
.login-context-banner {
  align-self: flex-end;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #0f172a;
  background: rgba(108, 99, 255, 0.08);
  border-left: 4px solid var(--accent);
  border-radius: 20px;
  padding: 6px 14px;
  margin-bottom: 8px;
  white-space: nowrap;
}
```

### Step 6 — Remove About link from auth navbar in `layout.html`

In the `{% if request.user.is_authenticated %}` nav-links block, remove the About link.

### Step 7 — Manual verification

1. Visit `/about/` logged out → page renders normally (no hero button)
2. Visit `/about/` logged in → redirected to `/`
3. Click "Start Designing" on About page → lands on login with banner
4. Banner shows "Login to start designing" at top-right
5. Refresh login page → banner gone
6. Visit `/login/` directly → no banner
7. Guest navbar still has About linking to `/about/`

---

## 7. Files to Touch

| File | Action |
|------|--------|
| `project_simp/account/views.py` | Modify `AboutPage.get()` — auth gate; modify `LoginUser.get()` — context flag |
| `project_simp/account/templates/Home/about.html` | Remove hero button; rename + relink final CTA |
| `project_simp/account/templates/login/login.html` | Add conditional banner |
| `project_simp/static/css/login.css` | Add `.login-context-banner` |
| `project_simp/templates/layout.html` | Remove About link from auth nav-links block |

**Files NOT modified:** urls.py, models, forms, about.css, navbar.css, navbar.js

---

## 8. Detailed Acceptance Criteria

### Guest gating
- [ ] Authenticated user visits `/about/` → redirected to `/`
- [ ] Guest user visits `/about/` → full About page renders

### About page buttons
- [ ] Hero section has no "Start Designing" button
- [ ] Final CTA button text reads "Start Designing →"
- [ ] Final CTA links to `{% url 'account:login' %}?from=about`

### Login banner
- [ ] Login page at `/?from=about` shows "Login to start designing" banner at top-right
- [ ] Banner uses purple accent + pen-ruler icon
- [ ] Login page accessed directly (no `?from=about`) has no banner
- [ ] Refreshing login page clears the banner (GET param drops)

### Navbar
- [ ] Guest navbar still shows About link → `/about/`
- [ ] Auth navbar does NOT show About link

### Technical
- [ ] Django `check` passes with 0 issues
- [ ] No migrations or model changes

---

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Login layout shifts when banner appears | Banner uses `align-self: flex-end` and existing flex layout — no shift because it sits above the title in the same column |
| Banner click doesn't redirect | Banner is informational text + icon, not a link — no click behavior needed |
| Auth user still sees About via direct URL entry | Redirect is server-side in the view — they'll be sent to home before the page renders |

---

## 10. Execute Command

When ready to implement:

```
execute: AboutPageRefinement
```
