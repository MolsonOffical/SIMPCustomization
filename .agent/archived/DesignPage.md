# Proposal: DesignPage

**File name:** `DesignPage.md`  
**Status:** Archived  
**Created:** June 27, 2026  
**Archived:** June 27, 2026  
**Outcome:** Created 3D shoe designer page (Three.js procedural model, 5-part color customization, pattern textures), login redirect flow, and auth navbar link  
**Type:** Frontend — 3D shoe customization page with interactive preview  
**Skill set:** `Frontend-Design`

---

## 1. Summary

Create a **Shoe Customization Designer** page (`/design/`) that lets users interactively customize a 3D shoe model. The page is split: **left panel** has design controls (colors per shoe part, size selector, pattern/swatch picker), **right panel** has a full-viewport 3D shoe preview built with Three.js that updates live as options change and supports mouse-drag rotation.

**Connected flows:**
- About page "Start Designing" → login → redirects to `/design/`
- Auth navbar "Customize Your Shoes" → links to `/design/`
- Login flow checks for `next` parameter to redirect to design page after auth

---

## 2. Relevance to Current Project State

| Reference | Relevance |
|-----------|-----------|
| `AboutPageRefinement.md` (archived) | Changed "Start Designing" to link to login — now needs to complete the redirect flow to `/design/` |
| `PROJECT_DOCUMENTATION.md` §4.1 Navbar | Auth navbar has "Customize Your Shoes" placeholder (`#`) — needs real URL |
| `PROJECT_DOCUMENTATION.md` §4.4 Login page | Login redirect currently hardcoded to `account:home` — needs `next` param support |
| `Frontend-Design` skill | Live interactive 3D preview is the signature element; restrained left-panel controls |

### Current behavior
- Auth navbar "Customize Your Shoes" → `#` (coming soon placeholder)
- Login success → always redirects to home
- No design/customization page exists
- About page links to login but login has no redirect-to-design logic

---

## 3. Detailed Changes

### 3.1 New route: `/design/`

**URL:** `account/urls.py` — `path('design/', DesignPage.as_view(), name='design')`

**View:** `account/views.py` — `DesignPage` (requires login via `LoginRequiredMixin` or manual redirect)

**Template:** `account/templates/Design/designer.html`

**Static files:**
- `static/css/designer.css` — Layout for split panel, control styling
- `static/js/designer.js` — Three.js scene setup, model loading, color sync, OrbitControls
- `static/models/shoe.glb` — 3D shoe model with named parts for per-section recoloring

### 3.2 Page layout (split panel)

```
┌──────────────────┬──────────────────────────────┐
│   DESIGN CONTROLS │        3D SHOE PREVIEW        │
│  (left panel)    │      (right, full height)     │
│                  │                              │
│  ┌────────────┐  │     ┌──────────────────┐     │
│  │ Size       │  │     │                  │     │
│  │ [S M L XL] │  │     │   3D Shoe Model  │     │
│  │            │  │     │   (OrbitControls) │     │
│  │ Color per  │  │     │                  │     │
│  │ part:      │  │     │                  │     │
│  │  • Upper   │  │     └──────────────────┘     │
│  │  • Sole    │  │                              │
│  │  • Lining  │  │                              │
│  │  • Lace    │  │                              │
│  │  • Heel    │  │                              │
│  │            │  │                              │
│  │ Pattern:   │  │                              │
│  │ [swatches] │  │                              │
│  │            │  │                              │
│  │ [Add to    │  │                              │
│  │  Cart]     │  │                              │
│  └────────────┘  │                              │
└──────────────────┴──────────────────────────────┘
```

**Left panel** (30–35% width):
- **Size selector** — Pill buttons for S / M / L / XL (or EU sizes)
- **Color per part** — Each named shoe section gets a labeled color picker (e.g., "Upper", "Sole", "Lining", "Lace", "Heel"). Clicking a picker changes that mesh's material color in real time.
- **Pattern swatches** — Small image tiles for pre-designed patterns (floral, geometric, camo, solid). Selecting a pattern maps it as a texture onto the upper.
- **Add to Cart** button (placeholder — not functional until cart is built)

**Right panel** (65–70% width):
- Full-height Three.js canvas
- 3D shoe model centered with ambient + directional lighting
- Mouse drag to rotate; scroll to zoom
- Model updates color/texture immediately when controls change

### 3.3 3D Model & Three.js approach

**Model:** A GLB shoe file stored at `static/models/shoe.glb`. The model must have named meshes (`upper`, `sole`, `lining`, `lace`, `heel`) for per-part recoloring.

- If a suitable free model with named parts is found online, download and convert to GLB
- If not, build a procedural shoe with Three.js BufferGeometry (box sole, curved upper with LatheGeometry, etc.)

**Three.js setup (`designer.js`):**
```js
// Scene, camera, renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, containerWidth / containerHeight, 0.1, 100);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

// OrbitControls
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

// Lights
const ambient = new THREE.AmbientLight(0xffffff, 0.5);
const directional = new THREE.DirectionalLight(0xffffff, 1);

// Load GLB
const loader = new GLTFLoader();
loader.load('/static/models/shoe.glb', (gltf) => {
  shoeParts = {};
  gltf.scene.traverse((child) => {
    if (child.isMesh) shoeParts[child.name] = child;
  });
  scene.add(gltf.scene);
});

// Color change
function setPartColor(partName, hexColor) {
  if (shoeParts[partName]) {
    shoeParts[partName].material.color.set(hexColor);
  }
}
```

**CDN dependencies (loaded via `<script>` tags in the template):**
- Three.js (`https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`)
- OrbitControls (ES module or bundled)
- GLTFLoader (ES module or bundled)

### 3.4 Login redirect flow

**About page "Start Designing" button:**
Update link from `{% url 'account:login' %}?from=about` to `{% url 'account:login' %}?next={% url 'account:design' %}`

This uses Django's convention: `?next=` is a standard pattern understood by `LoginRequiredMixin` and manual redirect logic.

**Login view change (`LoginUser.post`):**
```python
def post(self, request):
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        ...
        login(request, user)
        if not user.is_email_verified:
            return redirect('account:send_otp')

        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('account:home')
```

**About page button link:** `{% url 'account:login' %}?next={% url 'account:design' %}`.

**Login context banner:** Keep existing "Login to start designing" logic — `?from=about` check stays alongside `?next=`.

### 3.5 Auth navbar

Change `layout.html` line 31:
```html
<a href="{% url 'account:design' %}">Customize Your Shoes</a>
```

### 3.6 Design options data (Phase 1 — hardcoded)

For the initial delivery, design options are **hardcoded in the template/JS** — no database models, no migrations:

**Shoe parts (for color pickers):**
```js
const parts = ['upper', 'sole', 'lining', 'lace', 'heel'];
const defaultColors = {
  upper: '#1a7a4a',    // SIMP green
  sole: '#333333',     // dark grey
  lining: '#ffffff',   // white
  lace: '#1a7a4a',     // SIMP green
  heel: '#222222',     // near-black
};
```

**Pattern swatches:** 4–6 image files in `static/images/patterns/` (e.g., floral, geometric, camo, stripe, solid). Loading a pattern sets it as a texture map on the `upper` mesh.

**Sizes:** `['EU 38', 'EU 39', 'EU 40', 'EU 41', 'EU 42', 'EU 43', 'EU 44']`

---

## 4. Dependencies & Constraints

- **3D model asset** — Requires a free shoe GLB with named parts, or procedural shoe built in code. This is the biggest unknown.
- **Three.js CDN** — No build step needed; loaded via `<script>` tags
- **No migrations, no models** — All design options are frontend-only for Phase 1
- **No cart/checkout** — "Add to Cart" button is a visual placeholder, not functional
- **Login redirect** — Uses Django's standard `?next=` pattern; no session changes needed

---

## 5. Design Direction (per Frontend-Design skill)

### Grounding
The subject is **custom footwear** — the design page itself is a tool, not a marketing page. The aesthetic should be **clean, precise, tool-like**: dark controls panel, minimal chrome, shoe takes center stage.

### Token system
- **Background**: Near-black `#1a1a1a` for left panel (tool feel), clean white/grey for right panel (neutral preview backdrop)
- **Accent**: SIMP green `#1a7a4a` for active selections, borders, hover states
- **Type**: Inter (body) for controls, Barlow Condensed for labels
- **Buttons**: Green-filled for primary (Add to Cart), outline for size/pattern selection

### Signature element
The 3D shoe preview itself — interactive, real-time updating, rotatable. This is the one bold element; the controls panel stays restrained.

### Layout signature
Vertical stack on left (compact, scannable), full-height canvas on right. At mobile, controls stack above the preview (both full-width).

---

## 6. Open Questions

1. **3D shoe model source** — Should we use a free GLB from the web (e.g., Sketchfab, Poly Pizza) or build a procedural shoe with Three.js geometry? Procedural gives full part control but looks less realistic; a downloaded model looks better but needs to have correctly named meshes.

2. **Pattern as texture vs procedural** — Should patterns be image textures (requires artwork assets) or procedural patterns generated in Three.js (canvas-based)?

3. **Cart placeholder** — "Add to Cart" button: should it show a toast "Coming soon" or redirect to a not-yet-built page?

4. **Login redirect priority** — Currently `?from=about` controls the banner. Adding `?next=` for redirect. Should we keep both, or replace `?from=about` entirely with `?next=`?

---

## 7. Files to Change / Create

| File | Action |
|------|--------|
| `account/views.py` | Add `DesignPage` view; modify `LoginUser.post()` for `?next=` redirect |
| `account/urls.py` | Add `path('design/', DesignPage.as_view(), name='design')` |
| `account/templates/Design/designer.html` | **New** — full design page template |
| `templates/layout.html` | Change auth navbar "Customize Your Shoes" href from `#` to `{% url 'account:design' %}` |
| `account/templates/Home/about.html` | Change final CTA link to `{% url 'account:login' %}?next={% url 'account:design' %}` |
| `static/css/designer.css` | **New** — split panel layout, control styling |
| `static/js/designer.js` | **New** — Three.js scene, model load, color sync, OrbitControls |
| `static/models/shoe.glb` | **New** — 3D shoe model asset |
| `static/images/patterns/` | **New** — pattern swatch images (4–6 files) |

**Migrations:** None. **Models:** None.

---

## 8. Acceptance Criteria

- [ ] `/design/` page renders with split-panel layout
- [ ] Left panel has color pickers for each shoe part (upper, sole, lining, lace, heel)
- [ ] Left panel has size selector and pattern swatches
- [ ] Right panel shows interactive 3D shoe (Three.js)
- [ ] 3D shoe rotates with mouse drag (OrbitControls)
- [ ] Changing a color picker updates the corresponding mesh part in real time
- [ ] Selecting a pattern swatch textures the upper mesh
- [ ] Auth navbar "Customize Your Shoes" links to `/design/`
- [ ] About page "Start Designing" → login → redirects to `/design/`
- [ ] Direct `/design/` access without login redirects to login (with `?next=/design/`)
- [ ] Login without `?next=` redirects to home (existing behavior unchanged)
- [ ] Django `check` passes with 0 issues
