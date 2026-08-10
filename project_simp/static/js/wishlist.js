/* ============================================================
   wishlist.js — client for the server-side (login-required) wishlist
   Drop this in /static/js/wishlist.js and include it on EVERY page
   that needs wishlist awareness (navbar badge, heart buttons on
   shoe cards) — mirrors cart.js's structure and conventions.

   The wishlist lives in the database as accounts.models.WishlistItem —
   this file just talks to the JSON endpoints in shoes/views.py.

   URL paths are read from window.WISHLIST_ENDPOINTS (set via
   {% url %} tags in wishlist.html) so this file never has to
   hardcode where the "shoes" app is mounted. Sensible defaults
   are used if that global isn't set.
   ============================================================ */

const WISHLIST_ENDPOINT_DEFAULTS = {
  list: "/shoes/wishlist/api/items/",
  add: "/shoes/wishlist/api/add/",
  remove: "/shoes/wishlist/api/remove/",
  toggle: "/shoes/wishlist/api/toggle/",
  moveToCart: "/shoes/wishlist/api/move-to-cart/",
};

function wishlistEndpoint(name) {
  const overrides = window.WISHLIST_ENDPOINTS || {};
  return overrides[name] || WISHLIST_ENDPOINT_DEFAULTS[name];
}

// getCookie() and apiRequest() are already defined globally by cart.js,
// which loads before this file on every page (see layout.html). Reusing
// them here keeps CSRF handling and the 401/403 redirect in one place.

const Wishlist = {
  // cache of the last wishlist payload from the server: { items, count }
  _cache: { items: [], count: 0 },

  /* ---------- reads ---------- */

  async refresh() {
    try {
      this._cache = await apiRequest(wishlistEndpoint("list"));
    } catch (e) {
      console.error("Wishlist: failed to load wishlist", e);
    }
    this.renderBadge();
    return this._cache;
  },

  getCached() {
    return this._cache;
  },

  isWishlisted({ variantId, pattern } = {}) {
    return (this._cache.items || []).some(i =>
      variantId ? i.variant_id === variantId : (i.pattern === pattern && !i.variant_id)
    );
  },

  /* ---------- mutations ----------
     Each resolves with the fresh wishlist payload and fires
     "wishlist:updated" with that payload as `detail`. */

  // Wishlist.addItem({ pattern: "nike-converse-low-top", size: "9",
  //                     colors: { "Outside Body": "#B50024" } })
  // or Wishlist.addItem({ variant_id: 12 })
  async addItem(payload) {
    const data = await apiRequest(wishlistEndpoint("add"), { method: "POST", body: payload });
    this._afterMutation(data);
    return data;
  },

  async removeItem(itemId) {
    const data = await apiRequest(wishlistEndpoint("remove"), {
      method: "POST",
      body: { item_id: itemId },
    });
    this._afterMutation(data);
    return data;
  },

  // Used by the heart button on shoe cards — flips wishlisted state
  // in one call. Pass EITHER { variantId } for admin-added shoes with
  // a specific color/size, OR { pattern } for customizer-designed
  // shoes on cards that haven't been customized yet (e.g. homepage).
  // Resolves with { ...payload, is_wishlisted }.
  async toggle({ variantId, pattern } = {}) {
    const body = variantId ? { variant_id: variantId } : { pattern };
    const data = await apiRequest(wishlistEndpoint("toggle"), { method: "POST", body });
    this._afterMutation(data);
    return data;
  },

  async moveToCart(itemId) {
    const data = await apiRequest(wishlistEndpoint("moveToCart"), {
      method: "POST",
      body: { item_id: itemId },
    });
    this._afterMutation(data);
    // moving to cart also changes the cart badge — let cart.js's
    // listeners know, same shape cart mutations already produce.
    if (window.Cart) {
      window.Cart._cache = await apiRequest(cartEndpoint("list"));
      window.Cart.renderBadge();
      window.dispatchEvent(new CustomEvent("cart:updated", { detail: window.Cart._cache }));
    }
    return data;
  },

  _afterMutation(data) {
    this._cache = data;
    this.renderBadge();
    window.dispatchEvent(new CustomEvent("wishlist:updated", { detail: data }));
  },

  /* ---------- UI helpers ---------- */

  renderBadge() {
    const badge = document.querySelector("#wishlist-badge");
    if (!badge) return;
    const count = this._cache.count || 0;
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline-flex" : "none";
  },

  toast(message) {
    // reuse Cart's toast element/styling if available, else make our own
    if (window.Cart && typeof window.Cart.toast === "function") {
      window.Cart.toast(message);
      return;
    }
    let el = document.querySelector("#cart-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "cart-toast";
      document.body.appendChild(el);
    }
    el.textContent = message;
    el.classList.add("cart-toast--show");
    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => {
      el.classList.remove("cart-toast--show");
    }, 2200);
  },
};

/* ---------- heart buttons on shoe cards ----------
   Wires up any .wishlist-heart-btn[data-variant-id] on the page —
   homepage best-sellers, shop listing, shoe detail. Call this after
   the cards are in the DOM (works for both server-rendered cards
   and any you inject via JS later). */
function initWishlistHeartButtons(root = document) {
  root.querySelectorAll(".wishlist-heart-btn").forEach(btn => {
    const variantId = btn.dataset.variantId ? parseInt(btn.dataset.variantId, 10) : null;
    const pattern = btn.dataset.pattern || null;
    if (!variantId && !pattern) return;

    // reflect current state once wishlist data has loaded
    btn.classList.toggle("wishlist-heart-btn--active", Wishlist.isWishlisted({ variantId, pattern }));

    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      btn.disabled = true;
      try {
        const data = await Wishlist.toggle({ variantId, pattern });
        btn.classList.toggle("wishlist-heart-btn--active", data.is_wishlisted);
      } catch (err) {
        Wishlist.toast(err.message || "Couldn't update your wishlist.");
      } finally {
        btn.disabled = false;
      }
    });
  });
}
document.addEventListener("DOMContentLoaded", async () => {
  await Wishlist.refresh();
  initWishlistHeartButtons();
});