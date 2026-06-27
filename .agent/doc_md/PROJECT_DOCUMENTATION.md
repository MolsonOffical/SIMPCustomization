# SIMP — Project Documentation

**Project:** `project_simp`  
**Framework:** Django 6.0.6  
**Location:** `ProjectA/project_simp`  
**Last reviewed:** June 26, 2026

---

## 1. About the Project

**SIMP** (Shoe Identity & Modification Platform) is a Django web application for a custom footwear business targeting customers in **Nepal**. The platform lets users design and order personalized shoes — choosing styles, colors, patterns, artwork, and sizes — with local payment options (eSewa, Khalti, card) and delivery across Nepal.

The current codebase is in an **early development phase**. The marketing home page and full user authentication flow (registration, login, email OTP verification) are in place. Product catalog, customization tooling, cart/checkout, and blog features are planned but not yet implemented.

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 6.0.6, Python 3.12 |
| Database | SQLite3 (development) |
| Auth | Custom user model (`CustomUser`) extending `AbstractUser` |
| Email | Gmail SMTP via custom SSL email backend |
| Media | Pillow for image uploads (profile/banner) |
| Frontend | Django templates, vanilla CSS, Font Awesome 6 |
| Static assets | `static/` (CSS, JS, images) |

### Project Structure

```
project_simp/
├── project_simp/          # Project settings, URLs, WSGI, custom email backend
├── account/               # Single Django app — auth, home page, OTP flow
│   ├── models.py          # CustomUser, EmailOTP
│   ├── views.py           # Class-based views for all user-facing pages
│   ├── forms.py           # Registration & login forms
│   ├── services.py        # OTP generation, email sending, verification
│   ├── validators.py      # Username, phone, image validators
│   └── templates/         # Home, register, login, verify_email
├── templates/
│   └── layout.html        # Shared navbar + footer shell
├── static/
│   ├── css/               # Page-specific stylesheets
│   ├── js/                # Navbar dropdown behavior
│   └── images/            # Logo, login/register illustrations
├── media/                 # User-uploaded profile/banner images
└── requirements.txt
```

---

## 2. Scope

### In Scope (Current / Planned Product Vision)

- **User accounts** — Registration with extended profile fields (age, gender, phone), login/logout, email verification via OTP
- **Marketing landing page** — Hero, how-it-works, featured products, about, FAQ, footer (static content for now)
- **Nepal-specific validation** — Mobile numbers in Nepal format; pricing in NPR (Rs.)
- **Admin panel** — Django admin for `CustomUser` and `EmailOTP`
- **Future e-commerce** — Product catalog, shoe customization, cart, orders, payments, reviews (UI placeholders exist on home page)

### Out of Scope (Not Yet Started)

- Product/shoe models and database-driven catalog
- Customization designer (live preview, artwork upload)
- Shopping cart and checkout
- Payment gateway integration (eSewa, Khalti)
- Blog and category management
- Search functionality
- User profile editing page
- Automated test coverage
- Production deployment configuration

### URL Routes (Implemented)

| Path | View | Purpose |
|------|------|---------|
| `/` | `HomePage` | Marketing home page |
| `/register/` | `RegisterUser` | User registration |
| `/login/` | `LoginUser` | User login |
| `/logout/` | `LogoutUser` | Session logout |
| `/verify-email/` | `SendOTPView` | OTP send / resend screen |
| `/verify-email/confirm/` | `VerifyOTPView` | OTP submission & verification |
| `/admin/` | Django admin | Staff/superuser management |

---

## 3. Completed Work & Implementation

### 3.1 Custom User Model

**File:** `account/models.py`

`CustomUser` extends Django's `AbstractUser` with additional fields:

| Field | Type | Notes |
|-------|------|-------|
| `age` | PositiveIntegerField | Default 18; validated 13–120 in form |
| `gender` | CharField | Choices: Male, Female |
| `phone_number` | CharField | Nepal mobile format validated |
| `banner` | ImageField | Optional; uploaded to `media/banner/` |
| `profile` | ImageField | Optional; uploaded to `media/profile/` |
| `is_email_verified` | BooleanField | Default `False`; set `True` after OTP verification |

The model overrides `save()` to delete old profile/banner files from disk when images are removed or replaced.

**Configuration:** `AUTH_USER_MODEL = "account.CustomUser"` in `settings.py`.

---

### 3.2 User Registration

**Files:** `account/views.py` → `RegisterUser`, `account/forms.py` → `RegistrationForms`

**Flow:**
1. GET renders the registration form.
2. POST validates via `RegistrationForms` (extends `UserCreationForm`).
3. On success, user is saved, OTP is generated and emailed, and `pending_user_id` is stored in session.
4. User is redirected to `/verify-email/`.

**Validation rules:**
- Username: alphanumeric only (`validate_alphanumeric_username`)
- Age: 13–120
- Phone: Nepal mobile pattern — prefixes 98, 97, or 91 (`validate_nepal_phone`); country code stripped on save
- Password: Django's built-in password validators

**Note:** `profile` and `banner` exist on the model and have validators in the form, but are **not included** in the registration form's `Meta.fields` yet.

---

### 3.3 Login & Logout

**Files:** `account/views.py` → `LoginUser`, `LogoutUser`

**Login flow:**
1. `LoginForm` (extends `AuthenticationForm`) collects username and password.
2. `authenticate()` validates credentials.
3. **Staff/superuser accounts are blocked** from the public login — they must use `/admin/`.
4. If the user is not email-verified, redirect to OTP flow.
5. Otherwise redirect to home.

**Logout:** Clears session and redirects to login with a success message.

---

### 3.4 Email OTP Verification

**Files:** `account/services.py`, `account/models.py` → `EmailOTP`, `account/views.py` → `SendOTPView`, `VerifyOTPView`

**OTP lifecycle:**

```
Registration / Unverified login
        ↓
create_and_send_otp(user)
  ├── Generate 6-digit numeric OTP
  ├── Delete any existing OTPs for user
  ├── Store EmailOTP (expires in 10 minutes)
  └── Send HTML + plain-text email via SMTP
        ↓
User enters OTP on verify page
        ↓
verify_otp(user, submitted_otp)
  ├── invalid  → error message
  ├── expired  → error message, OTP deleted
  └── valid    → is_email_verified=True, OTP deleted, redirect to login
```

**Session tracking:** `request.session['pending_user_id']` links the browser to the unverified user during the OTP flow.

**Email delivery:** Custom `CustomEmailBackend` in `project_simp/email_backend.py` wraps SMTP with relaxed SSL certificate verification for development Gmail SMTP.

---

### 3.5 Forms & Validators

**Files:** `account/forms.py`, `account/validators.py`

| Validator | Rule |
|-----------|------|
| `validate_alphanumeric_username` | Letters and numbers only |
| `validate_nepal_phone` | `(+977)?(98\|97\|91)XXXXXXXX` |
| `validate_image_size` | Max 2 MB |
| `validate_alpha_name` | Letters A–Z only (defined, not yet wired to a field) |

Forms apply Bootstrap-style `form-control` CSS classes and placeholders via `__init__`.

---

### 3.6 Database Migrations

| Migration | Changes |
|-----------|---------|
| `0001_initial` | Creates `CustomUser` with profile fields |
| `0002_customuser_is_email_verified_and_more` | Adds `is_email_verified`; default profile image path |
| `0003_alter_customuser_profile_emailotp` | Adjusts profile field; adds `EmailOTP` model |

---

### 3.7 Admin

**File:** `account/admin.py`

Both `CustomUser` and `EmailOTP` are registered with the default Django admin interface.

---

### 3.8 Home Page (Static Marketing)

**Files:** `account/views.py` → `HomePage`, `account/templates/Home/index.html`, `static/css/home.css`

The home page is a **fully static HTML template** with no backend data binding. It presents:

- Promotional top bar
- Hero section with CTA buttons (`/customize`, `/business` — not routed yet)
- Partner/ratings strip
- 3-step "How it works" section
- 4 hardcoded "Best Selling Styles" product cards
- About section with stats
- Customer wall (emoji placeholders)
- FAQ accordion-style items (non-interactive)
- Full footer with link columns

All product/shop links point to routes that **do not exist yet**.

---

## 4. UI Description & Brief Implementation

### 4.1 Shared Layout (`templates/layout.html`)

**Purpose:** Global shell for every page.

**Components:**
- **Navbar** — Logo + "SIMP" brand, nav links (Home, Blogs, Categories dropdown, About), search input, auth actions (Login/Register or username + Logout)
- **Content block** — Page-specific content injected via `{% block content %}`
- **Simple footer** — Copyright line

**Implementation:**
- CSS: `static/css/navbar.css` — sticky white navbar, blue hover states, dropdown grid for categories
- JS: `static/js/navbar.js` — mouseenter/mouseleave fade for category dropdown
- Font Awesome 6 loaded from CDN for icons

**Known gaps:**
- `categories` context variable is never passed from views — dropdown shows "No categories available"
- Blogs, About, and search form action (`#`) are placeholders
- Home page has its own rich footer inside `{% block content %}`, so pages show **two footers** (layout + home)

---

### 4.2 Home Page

**Template:** `account/templates/Home/index.html`  
**Styles:** `static/css/home.css`

**Visual design:**
- Color palette: black (`#111`), white, green accent (`#1a7a4a` / `#2ea865`)
- Typography: Inter + Barlow Condensed (large uppercase headings)
- Responsive breakpoints at 900px (single-column hero, stacked grids)

**Sections:**

| Section | UI Elements | Implementation |
|---------|-------------|----------------|
| Top bar | Dark promo strip | Static HTML + CSS |
| Hero | Split grid, shoe emoji, payment/delivery badges | CSS grid, emoji placeholder for product image |
| Partners | Brand names + star rating pills | Flexbox strip |
| How it works | 3 numbered step cards | CSS grid, emoji icons |
| Best sellers | 4 product cards with price + Customize CTA | Static cards; links to `/product/N` |
| About | Stats grid + feature rows | Two-column grid |
| Customer wall | 5 image tiles | Emoji placeholders |
| FAQ | 4 question rows with arrow | Static; no expand/collapse JS |
| Footer | 4-column link grid + social links | Static HTML |

---

### 4.3 Registration Page

**Template:** `account/templates/register/register.html`  
**Styles:** `static/css/register.css`

**Layout:** Centered card, split 55/45 — form on left, illustration (`static/images/reg.jpg`) on right.

**Form fields rendered:** username, age, gender, email, phone_number, password1, password2.

**UX details:**
- Django messages displayed as styled alerts
- Per-field error messages below inputs
- Rounded card (`border-radius: 22px`), purple accent (`#6c63ff`)
- Responsive: illustration hidden on smaller screens (via CSS media queries in register.css)

---

### 4.4 Login Page

**Template:** `account/templates/login/login.html`  
**Styles:** `static/css/login.css`

**Layout:** Mirrors registration — form left, illustration (`static/images/lo.jpg`) right.

**Fields:** username, password with placeholders and `form-control` styling.

**Messages:** Error alerts for invalid credentials or blocked admin login.

---

### 4.5 Email Verification (OTP) Page

**Template:** `account/templates/email/verify_email.html`  
**Styles:** `static/css/email/email_verifi.css`

**Layout:** Centered OTP card with purple gradient header.

**Components:**
- 6 individual digit input boxes with auto-focus advance
- Paste support for full 6-digit code
- Hidden field aggregates digits for POST
- Verify button disabled until 6 digits entered
- Countdown timer (10 minutes) before "Resend code" appears
- Resend posts to `/verify-email/`

**Inline JavaScript:** Handles digit input, paste, countdown, and resend visibility — all in the template's `{% block content %}` (no separate JS file).

**Known issue:** Template references `{{ user.email }}` but the view passes `pending_user` — the email address line may not render correctly until fixed.

---

### 4.6 Static Assets Summary

| Asset | Path | Used By |
|-------|------|---------|
| Logo | `static/images/Logo1.png` | Navbar |
| Register illustration | `static/images/reg.jpg` | Register page |
| Login illustration | `static/images/lo.jpg` | Login page |
| Navbar CSS/JS | `static/css/navbar.css`, `static/js/navbar.js` | Layout |
| Home CSS | `static/css/home.css` | Home page |

---

## 5. UI Improvement Opportunities

Use this section to track planned UI/UX enhancements. Items below are suggested starting points based on the current codebase review.

### 5.1 Global / Layout

| # | Area | Current State | Suggested Improvement | Priority | Status |
|---|------|---------------|----------------------|----------|--------|
| 1 | Dual footer | Home has its own footer plus layout footer | Use one footer in `layout.html` or override block on home | Medium | ☐ |
| 2 | Navbar consistency | Home uses green/dark theme; navbar is white/blue | Align navbar colors with home page brand (green/black) | High | ☐ |
| 3 | Categories dropdown | Empty — no backend data | Wire categories from DB or hide until implemented | Low | ☐ |
| 4 | Mobile navigation | Nav links hidden on small screens (home.css) but no hamburger menu | Add responsive mobile nav drawer | High | ☐ |
| 5 | Search bar | Non-functional (`action="#"`) | Implement search or remove until ready | Low | ☐ |

### 5.2 Home Page

| # | Area | Current State | Suggested Improvement | Priority | Status |
|---|------|---------------|----------------------|----------|--------|
| 6 | Product images | Emoji placeholders | Replace with real product photography | High | ☐ |
| 7 | FAQ section | Static rows, no interaction | Add accordion JS or `<details>` elements | Medium | ☐ |
| 8 | CTA links | Point to unimplemented routes | Disable styling or link to waitlist/contact until built | Medium | ☐ |
| 9 | Customer wall | Emoji tiles | User-submitted photos or Instagram embed | Low | ☐ |
| 10 | Hero shoe display | Single emoji | 3D model viewer or rotating product carousel | Medium | ☐ |

### 5.3 Auth Pages

| # | Area | Current State | Suggested Improvement | Priority | Status |
|---|------|---------------|----------------------|----------|--------|
| 11 | Registration fields | No profile/banner upload in form | Add image upload UI with preview | Medium | ☐ |
| 12 | OTP email display | `user.email` vs `pending_user` bug | Fix template variable | High | ☐ |
| 13 | OTP resend timer | UI shows 60s initially but JS uses 10 min | Align timer display with backend expiry | Medium | ☐ |
| 14 | Password strength | Default Django validators only | Visual password strength indicator | Low | ☐ |
| 15 | Login/register link | No cross-link between pages | Add "Already have an account?" / "Sign up" links | Low | ☐ |

### 5.4 Accessibility & Polish

| # | Area | Current State | Suggested Improvement | Priority | Status |
|---|------|---------------|----------------------|----------|--------|
| 16 | Focus states | Limited keyboard focus styling | Add visible focus rings on inputs and buttons | Medium | ☐ |
| 17 | Form labels | Present but could be clearer | Associate `aria-describedby` with error messages | Low | ☐ |
| 18 | Loading states | No feedback on form submit | Add button loading/disabled state during POST | Low | ☐ |
| 19 | Toast messages | Django messages as inline alerts | Optional toast notification system | Low | ☐ |
| 20 | Dark mode | Not supported | Optional theme toggle | Low | ☐ |

### 5.5 Notes / Custom Items

_Add additional UI improvement ideas here as the project evolves._

```
Date: 
Author: 
Description: 


Date: 
Author: 
Description: 

```

---

## Appendix: Running Locally

```bash
cd ProjectA/project_simp
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Create a superuser for admin access:

```bash
python manage.py createsuperuser
```

---

## Appendix: Key Dependencies

```
Django==6.0.6
pillow==12.2.0
asgiref==3.11.1
sqlparse==0.5.5
tzdata==2026.2
```
