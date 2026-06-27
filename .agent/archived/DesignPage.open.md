# Open Plan: DesignPage

**Proposal:** `DesignPage.md`  
**Status:** Archived  
**Created:** June 27, 2026  
**Archived:** June 27, 2026  
**Skill set:** `Frontend-Design`

---

## 1. Decisions on Open Questions

| # | Question | Decision | Rationale |
|---|----------|----------|-----------|
| 1 | 3D shoe model source | **Procedural** — built with Three.js BufferGeometry/ExtrudeGeometry | No external asset dependency, full part control, no licensing concerns, works immediately. Stylized/low-poly aesthetic intentionally. |
| 2 | Pattern approach | **Canvas-generated textures** in JS — solid, stripe, dot, checkerboard, chevron | Zero image assets needed; patterns are live-generated as CanvasTexture. |
| 3 | Cart placeholder | **Toast** — "Cart coming soon — your design is saved for now" | Honest, non-blocking, non-dead-ending. |
| 4 | Login redirect | **Merge** — `?next=` is primary. Banner shows when either `?next=` or `?from=about` is present. | Single parameter (`?next=`) is standard Django pattern; banner covers both entry paths. |

---

## 2. Skills Applied

### 2.1 From `skillSet/Frontend-Design/Skills.md`
- **Ground it in the subject** (§Ground it) — The subject is custom footwear; the design page is a tool, not a marketing page. Dark tool-like controls panel, shoe takes center stage.
- **Signature element** (§Design principles) — The 3D interactive preview is the one memorable thing. Controls panel stays restrained, neutral, and quiet.
- **Restraint** (§Restraint) — No decoration in the 3D scene (pure white background, clean lighting). Controls use minimal chrome (flat, no shadows, subtle borders).
- **Writing** (§More on writing) — "Start Designing", "Login to start designing", "Cart coming soon" — active voice, plain verbs, sentence case.

### 2.2 From `skillSet/skills.md`
- **§1.1 Django Core** — CBV (`DesignPage`), URL routing with `name=`, `LoginRequiredMixin`
- **§1.2 Auth** — `?next=` redirect pattern, `LoginRequiredMixin` for protecting `/design/`
- **§2.1 Django Templates** — `{% extends "layout.html" %}`, `{% static %}`, `{% url %}`
- **§2.2 CSS** — Responsive split layout, dark panel, green accent on controls
- **§2.3 JavaScript** — Three.js (ES modules via importmap), event delegation for color pickers

---

## 3. Architecture

### 3.1 Page layout

```
┌──────────────────────────────────────────┐
│  <main class="designer-layout">          │
│  ┌───────────┐  ┌──────────────────────┐ │
│  │ .controls │  │ .preview            │ │
│  │  (35%)    │  │  (65%)              │ │
│  │           │  │  [Three.js Canvas]   │ │
│  │  Size     │  │                     │ │
│  │  Colors   │  │  • OrbitControls    │ │
│  │  Patterns │  │  • Ambient + Dir    │ │
│  │  [Add to  │  │  • Procedural shoe  │ │
│  │   Cart]   │  │                     │ │
│  └───────────┘  └──────────────────────┘ │
└──────────────────────────────────────────┘
```

### 3.2 Procedural shoe parts

Each part is a Three.js `Mesh` with `name` and `MeshStandardMaterial`:

| Part Name | Geometry | Visual |
|-----------|----------|--------|
| `upper` | Custom ExtrudeGeometry (foot profile dome) | Main shoe body, covers top of foot |
| `sole` | Rounded box (BoxGeometry + bevel) | Thick platform sole |
| `lining` | Scaled-down upper clone, inverted normals | Interior visible at opening |
| `lace` | Small cylinders + boxes in criss-cross pattern | Laces over the tongue area |
| `heel` | Curved back piece (custom shape) | Heel counter at back |

Default colors match SIMP brand:
- upper: `#1a7a4a`, sole: `#333333`, lining: `#f5f5f5`, lace: `#1a7a4a`, heel: `#222222`

### 3.3 Canvas-generated patterns

`generatePattern(type, color1, color2)` returns a `CanvasTexture`:

| Type | Description |
|------|-------------|
| `solid` | Single flat color |
| `stripe` | Diagonal alternating stripes |
| `dot` | Polka dots on background |
| `checker` | Checkerboard grid |
| `chevron` | Zigzag/chevron repeat |

### 3.4 Login redirect flow

```
About CTA:  /login/?next=/design/
                     ↓
Login GET:  checks ?from=about OR ?next=  → show banner
Login POST: checks ?next=                  → redirect to /design/
                     ↓
             /design/ (requires login)
```

---

## 4. Design Specification

### 4.1 Token system

| Token | Value | Usage |
|-------|-------|-------|
| `--panel-bg` | `#1a1a1a` | Controls panel background |
| `--panel-text` | `#e0e0e0` | Control labels |
| `--preview-bg` | `#f0f0f0` | 3D preview area background |
| `--accent` | `#1a7a4a` | Active state, buttons, borders |
| `--accent-hover` | `#2ea865` | Button hover |
| `--border` | `#333` | Section dividers |
| `--font-label` | `'Barlow Condensed', sans-serif` | Section headings |
| `--font-body` | `'Inter', sans-serif` | Control text |

### 4.2 Controls panel

- Size: Pill buttons (`<button>` with `.size-pill`), active state green fill
- Color: Native `<input type="color">` with a hex label next to it, labeled with the part name
- Pattern: 5 clickable swatch tiles (canvas-rendered 60×60 previews) in a flex grid
- Add to Cart: Full-width green button at bottom

### 4.3 Preview panel

- Full-height Three.js canvas (resizes with window)
- Neutral grey background (`#f0f0f0`)
- Shoe centered, auto-orbit subtle animation on idle
- Mouse drag → rotate, scroll → zoom

### 4.4 Responsive (≤768px)

Controls panel stacks above the preview panel (both full-width). Preview height reduced to 50vh.

---

## 5. File-Level Changes

### 5.1 New files

| File | Content |
|------|---------|
| `account/templates/Design/designer.html` | Template with split-panel layout, Three.js importmap, control HTML |
| `static/css/designer.css` | `.designer-layout` grid, `.controls-panel` / `.preview-panel` styles, control elements |
| `static/js/designer.js` | ES module: build procedural shoe, scene setup, color sync, pattern generator, OrbitControls |

### 5.2 Modified files

| File | Change |
|------|--------|
| `account/views.py` | Add `DesignPage` (LoginRequiredMixin or redirect); modify `LoginUser.post` for `?next=` |
| `account/urls.py` | Add `path('design/', DesignPage.as_view(), name='design')` |
| `templates/layout.html` | Auth navbar: `#` → `{% url 'account:design' %}` |
| `account/templates/Home/about.html` | CTA link: `?from=about` → `?next={% url 'account:design' %}` |
| `account/templates/login/login.html` | Banner condition: add `or request.GET.next` to `show_login_message` |

---

## 6. Implementation Steps

### Step 1 — Add URL route

`account/urls.py`: add import for `DesignPage`, add `path('design/', DesignPage.as_view(), name='design')`.

### Step 2 — Add DesignPage view

`account/views.py`: 
```python
class DesignPage(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'Design/designer.html')
```

`LoginRequiredMixin` automatically redirects unauthenticated users to `settings.LOGIN_URL` with `?next=/design/`.

### Step 3 — Modify LoginUser.post for `?next=`

Add before the final `return redirect('account:home')`:
```python
next_url = request.GET.get('next') or request.POST.get('next')
if next_url:
    return redirect(next_url)
```

### Step 4 — Update login banner condition

`login/login.html`: change `{% if show_login_message %}` to also check for `next` param:
```python
# In LoginUser.get():
if request.GET.get('from') == 'about' or request.GET.get('next'):
    context['show_login_message'] = True
```

### Step 5 — Update about.html CTA

Change `href` from `{% url 'account:login' %}?from=about` to `{% url 'account:login' %}?next={% url 'account:design' %}`.

### Step 6 — Update layout.html navbar

Change auth nav "Customize Your Shoes" from `href="#"` to `href="{% url 'account:design' %}"`.

### Step 7 — Create static/css/designer.css

Full stylesheet with:
- `.designer-layout`: CSS Grid `35% / 65%`, full viewport height minus navbar
- `.controls-panel`: Dark background, scrollable, padding, flex column
- `.preview-panel`: Light gray, relative, Three.js canvas fills it
- `.control-group`: Section wrapper with label, bottom border
- `.size-pill, .size-pill--active`: Pill button styles
- `.color-row`: Label + input[type=color] per part
- `.pattern-grid`: Flex row of 60×60 swatch tiles
- `.btn-add-cart`: Full-width green button
- `@media (max-width: 768px)`: Single column, preview 50vh

### Step 8 — Create static/js/designer.js

ES module (loaded via `<script type="module">`):

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// --- Procedural shoe builder ---
function buildShoe() { ... }  // returns THREE.Group with named meshes

// --- Pattern generator ---
function generatePattern(type, color1, color2) { ... }  // returns CanvasTexture

// --- Scene setup ---
const container = document.getElementById('preview-container');
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(40, ...);
const renderer = new THREE.WebGLRenderer({ antialias: true });
const controls = new OrbitControls(camera, renderer.domElement);

// --- Shoe ---
const shoe = buildShoe();
scene.add(shoe);

// --- Controls wiring ---
document.querySelectorAll('.color-picker').forEach(input => {
  input.addEventListener('input', () => {
    const part = shoe.getObjectByName(input.dataset.part);
    if (part) part.material.color.set(input.value);
  });
});

// --- Animation loop ---
function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();
```

**Procedural shoe construction detail:**
- Build a sole using `BoxGeometry` with position/scale for a sneaker footprint shape
- Build the upper using a custom `Shape` extruded to form the foot dome
- Use `ShapeGeometry` for the heel counter
- Tiny cylinders for lace eyelets, thin cylinders for crossed laces
- Each mesh gets `.name = 'upper'|'sole'|'lining'|'lace'|'heel'`
- Materials are `MeshStandardMaterial` with `color`, `roughness`, `metalness`

### Step 9 — Create account/templates/Design/designer.html

Template extends `layout.html`, overrides `{% block content %}`:

```html
{% extends "layout.html" %}
{% load static %}

{% block title %}Design Your Shoes — SIMP{% endblock %}

{% block extra_header %}
<link rel="stylesheet" href="{% static 'css/designer.css' %}" />
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
  }
}
</script>
{% endblock %}

{% block content %}
<main class="designer-layout">
  <aside class="controls-panel">
    <!-- Size selector -->
    <section class="control-group">
      <h3 class="control-group__label">Size</h3>
      <div class="size-options">
        {% for s in sizes %}
        <button class="size-pill {% if forloop.first %}size-pill--active{% endif %}">{{ s }}</button>
        {% endfor %}
      </div>
    </section>

    <!-- Colors per part -->
    <section class="control-group">
      <h3 class="control-group__label">Colors</h3>
      {% for part in shoe_parts %}
      <div class="color-row">
        <label class="color-row__label" for="color-{{ part.key }}">{{ part.label }}</label>
        <input type="color" id="color-{{ part.key }}" class="color-picker"
               data-part="{{ part.key }}" value="{{ part.default }}">
        <span class="color-row__hex">{{ part.default }}</span>
      </div>
      {% endfor %}
    </section>

    <!-- Pattern swatches -->
    <section class="control-group">
      <h3 class="control-group__label">Pattern</h3>
      <div class="pattern-grid" id="pattern-grid">
        {% for p in patterns %}
        <button class="pattern-swatch" data-pattern="{{ p.key }}" 
                style="background: {{ p.preview }}"
                title="{{ p.label }}"></button>
        {% endfor %}
      </div>
    </section>

    <!-- Add to Cart -->
    <button class="btn-add-cart" id="btn-add-cart">Add to Cart</button>
  </aside>

  <div class="preview-panel" id="preview-container"></div>
</main>
{% endblock %}

{% block script %}
<script type="module" src="{% static 'js/designer.js' %}"></script>
{% endblock %}
```

### Step 10 — Wire up the template context in the view

```python
class DesignPage(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            'sizes': ['EU 38', 'EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43', 'EU 44'],
            'shoe_parts': [
                {'key': 'upper', 'label': 'Upper', 'default': '#1a7a4a'},
                {'key': 'sole', 'label': 'Sole', 'default': '#333333'},
                {'key': 'lining', 'label': 'Lining', 'default': '#f5f5f5'},
                {'key': 'lace', 'label': 'Laces', 'default': '#1a7a4a'},
                {'key': 'heel', 'label': 'Heel', 'default': '#222222'},
            ],
            'patterns': [
                {'key': 'solid', 'label': 'Solid', 'preview': '#1a7a4a'},
                {'key': 'stripe', 'label': 'Stripes', 'preview': 'repeating-linear-gradient(45deg,#1a7a4a,#1a7a4a 4px,#333 4px,#333 8px)'},
                {'key': 'dot', 'label': 'Dots', 'preview': 'radial-gradient(circle,#1a7a4a 3px,#333 3px)'},
                {'key': 'checker', 'label': 'Checker', 'preview': 'repeating-conic-gradient(#1a7a4a 0% 25%,#333 0% 50%) 0 0 / 12px 12px'},
                {'key': 'chevron', 'label': 'Chevron', 'preview': 'repeating-linear-gradient(135deg,#1a7a4a,#1a7a4a 4px,transparent 4px,transparent 8px)'},
            ],
        }
        return render(request, 'Design/designer.html', context)
```

---

## 7. Related Improvements

| Improvement | Action |
|-------------|--------|
| Auth navbar placeholder | "Customize Your Shoes" finally gets a real URL |
| About → login → design flow | Completes the redirect chain from About→login→design |
| Login redirect flexibility | `?next=` support makes login reusable for any future "protected → login → back" flows |

---

## 8. Detailed Acceptance Criteria

### Route & View
- [ ] `/design/` returns 200 for authenticated users
- [ ] `/design/` redirects to `/login/?next=/design/` for unauthenticated users
- [ ] `DesignPage` registered in `account/urls.py` with `name='design'`

### 3D Preview
- [ ] Right panel shows a Three.js canvas with a 3D shoe
- [ ] Shoe has 5 distinct colored parts: upper, sole, lining, lace, heel
- [ ] Mouse drag rotates the shoe (OrbitControls)
- [ ] Scroll zooms in/out
- [ ] Default colors match SIMP brand (green upper, dark sole, etc.)

### Controls
- [ ] Size selector shows EU 38–44 with pill buttons
- [ ] Clicking a size pill activates it (green fill)
- [ ] 5 color pickers, each labeled with the part name
- [ ] Changing a color picker updates the corresponding mesh in real time
- [ ] Pattern grid shows 5 swatches (solid, stripe, dot, checker, chevron)
- [ ] Clicking a pattern applies it as a texture on the `upper` mesh

### Login redirect
- [ ] About page "Start Designing" links to `/login/?next=/design/`
- [ ] Login with valid credentials and `?next=/design/` redirects to `/design/`
- [ ] Login without `?next=` redirects to home (unchanged)
- [ ] Login page shows banner when `?from=about` OR `?next=` is present

### Navbar
- [ ] Auth navbar "Customize Your Shoes" links to `/design/`

### Cart placeholder
- [ ] "Add to Cart" button shows a toast: "Cart coming soon — your design is saved for now"

### Technical
- [ ] Django `check` passes with 0 issues
- [ ] No migrations, no model changes
- [ ] No external model files (no `static/models/`)
- [ ] Three.js loaded via importmap from CDN (no build step)

---

## 9. Risk & Mitigation

| Risk | Mitigation |
|------|------------|
| Procedural shoe looks poor | Stylized/low-poly is intentional — the aesthetic is geometric/blocky, not photorealistic. This is Phase 1; a GLB model can replace it later. |
| Three.js CDN fails | Fallback: a static 2D shoe image as placeholder with a "3D preview unavailable" message. |
| `?next=` redirect bypasses email verification | `?next=` redirect is checked only after `is_email_verified` check — unverified users still go to OTP flow first. |
| Canvas patterns don't texture correctly | Patterns only apply to `upper` mesh. If texture fails, upper defaults to its color (safe fallback). |
| importmap not supported in older browsers | Three.js r160+ requires modern browsers. Acceptable for a 2026 project. |

---

## 10. Execute Command

```
execute: DesignPage
```
