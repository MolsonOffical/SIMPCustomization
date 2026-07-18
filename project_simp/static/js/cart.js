/* ============================================================
   cart.js — client for the server-side (login-required) cart
   Drop this in /static/js/cart.js and include it on EVERY page
   that needs cart awareness (navbar badge) — shoe pages, the
   customizer, the cart page, checkout, etc.

   The cart lives in the database as accounts.models.CartItem —
   this file just talks to the JSON endpoints in shoes/views.py.

   URL paths are read from window.CART_ENDPOINTS (set via
   {% url %} tags in cart.html / your base template) so this file
   never has to hardcode where the "shoes" app is mounted. Sensible
   defaults are used if that global isn't set.
   ============================================================ */

const CART_ENDPOINT_DEFAULTS = {
  list: "/shoes/cart/api/items/",
  add: "/shoes/cart/api/add/",
  update: "/shoes/cart/api/update/",
  remove: "/shoes/cart/api/remove/",
  clear: "/shoes/cart/api/clear/",
};

function cartEndpoint(name) {
  const overrides = window.CART_ENDPOINTS || {};
  return overrides[name] || CART_ENDPOINT_DEFAULTS[name];
}

function getCookie(name) {
  const match = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
  return match ? decodeURIComponent(match[2]) : null;
}

async function apiRequest(url, { method = "GET", body } = {}) {
  const opts = {
    method,
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
  };
  if (method !== "GET") {
    opts.headers["X-CSRFToken"] = getCookie("csrftoken");
  }
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);

  if (res.status === 401 || res.status === 403) {
    window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
    throw new Error("Not authenticated");
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed (${res.status})`);
  }
  return data;
}

const Cart = {
  // cache of the last cart payload from the server:
  // { items, count, subtotal, shipping_label, shipping_fee, total }
  _cache: { items: [], count: 0, subtotal: "0", shipping_label: "—", total: "0" },

  /* ---------- reads ---------- */

  async refresh() {
    try {
      this._cache = await apiRequest(cartEndpoint("list"));
    } catch (e) {
      console.error("Cart: failed to load cart", e);
    }
    this.renderBadge();
    return this._cache;
  },

  getCached() {
    return this._cache;
  },

  /* ---------- mutations ----------
     Each resolves with the fresh cart payload and fires
     "cart:updated" with that payload as `detail`. */

  // Cart.addItem({ pattern: "nike-converse-low-top", size: "9",
  //                colors: { "Outside Body": "#B50024", "Laces": "#40E0D0" },
  //                quantity: 1 })
  async addItem(payload) {
    const data = await apiRequest(cartEndpoint("add"), { method: "POST", body: payload });
    this._afterMutation(data);
    return data;
  },

  async updateQuantity(itemId, quantity) {
    const data = await apiRequest(cartEndpoint("update"), {
      method: "POST",
      body: { item_id: itemId, quantity },
    });
    this._afterMutation(data);
    return data;
  },

  async removeItem(itemId) {
    const data = await apiRequest(cartEndpoint("remove"), {
      method: "POST",
      body: { item_id: itemId },
    });
    this._afterMutation(data);
    return data;
  },

  async clear() {
    const data = await apiRequest(cartEndpoint("clear"), { method: "POST" });
    this._afterMutation(data);
    return data;
  },

  _afterMutation(data) {
    this._cache = data;
    this.renderBadge();
    window.dispatchEvent(new CustomEvent("cart:updated", { detail: data }));
  },

  /* ---------- UI helpers ---------- */

  formatCurrency(n) {
    const rounded = Math.round(parseFloat(n) || 0);
    return "NPR " + rounded.toLocaleString("en-US");
  },

  renderBadge() {
    const badge = document.querySelector("#cart-badge");
    if (!badge) return;
    const count = this._cache.count || 0;
    badge.textContent = count;
    badge.style.display = count > 0 ? "inline-flex" : "none";
  },

  toast(message) {
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

 function initAddToCartForm() {
  const form = document.querySelector("#cart-form");
  if (!form) return;

  form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const quantity = parseInt(document.querySelector("#quantity")?.value, 10) || 1;
    const variantInput = document.querySelector("#selected-variant-id");

    // Regular (admin-added) shoe: form carries a real ShoesVariant id.
    if (variantInput && variantInput.value) {
      const variantId = parseInt(variantInput.value, 10);
      if (!variantId) {
        Cart.toast("Please select a color and size first.");
        return;
      }
      try {
        await Cart.addItem({ variant_id: variantId, quantity });
        Cart.toast("Added to cart");
      } catch (err) {
        Cart.toast(err.message || "Couldn't add that to your cart.");
      }
      return;
    }

    // Customizer-designed shoe: pattern + per-zone colors.
    const pattern = form.dataset.pattern;
    const size = document.querySelector("#size-select")?.value;
    const colors = window.selectedColors || {};

    if (!pattern || !size) {
      Cart.toast("Please choose a size before adding to cart.");
      return;
    }

    try {
      await Cart.addItem({ pattern, size, colors, quantity });
      Cart.toast("Added to cart");
    } catch (err) {
      Cart.toast(err.message || "Couldn't add that to your cart.");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  Cart.refresh();
  initAddToCartForm();
});