# Proposal: RegisterPageRefinement

## Summary
Redesign the registration page to match the dark, split-panel aesthetic already applied to the login page. The layout mirrors the login page: a hero panel with imagery and member benefits on the left, and a dark form panel on the right with Barlow typography, password visibility toggles, and a password strength indicator.

## Relevance to Current Project State
The login page was just redesigned to the dark split-panel look. The register page still uses the old light/purple card-based design. This creates visual inconsistency across the auth flow. Aligning the register page with the login page's design language ensures a cohesive brand experience.

## Skill Set Used
`Frontend-Design`

## Key Design Decisions (from `registration.temp.html`)
- **Dark palette** — Same `:root` tokens as login
- **Typography** — Barlow Condensed (display) + Barlow (body)
- **Layout** — `.auth-wrap` CSS grid split: `1.05fr 1fr`
- **Password toggle** — Eye icon on `password1` and `password2`
- **Password strength** — 4-bar indicator (CSS + JS)
- **Form errors** — `.field-errors` (plural)

## Dependencies & Constraints
- `navbar.css` `* { font-family }` leak — same fix as login (`.auth-wrap *` reset)
- 7 form fields must fit in 380px form panel

## Files
- `register.html` — template
- `register.css` — styles (same base as login.css + select + pw-strength additions)
