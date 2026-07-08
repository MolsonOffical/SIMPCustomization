/* ============================================================
   cart.js — client-side shopping cart
   Drop this in /static/js/cart.js and include it on EVERY page
   that needs cart awareness (navbar badge) — product pages,
   the cart page, checkout, etc.
   ============================================================ */

const CART_STORAGE_KEY = "simp_cart";

const Cart = {
  /* ---------- storage ---------- */

  getItems() {
    try {
      const raw = localStorage.getItem(CART_STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      console.error("Cart: failed to read cart", e);
      return [];
    }
  },

  saveItems(items) {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
    this.renderBadge();
    // let any listening page (e.g. cart.html) know it should re-render
    window.dispatchEvent(new CustomEvent("cart:updated", { detail: items }));
  },

  /* ---------- mutations ---------- */

  // item = { variant_id, name, color, size, price, photo, stock, quantity }
  addItem(item) {
    const items = this.getItems();
    const existing = items.find(i => i.variant_id === item.variant_id);

    if (existing) {
      existing.quantity = Math.min(
        existing.quantity + item.quantity,
        existing.stock || 99
      );
    } else {
      items.push(item);
    }

    this.saveItems(items);
    return items;
  },

  updateQuantity(variantId, quantity) {
    let items = this.getItems();
    const item = items.find(i => i.variant_id === variantId);
    if (!item) return items;

    quantity = Math.max(1, Math.min(quantity, item.stock || 99));
    item.quantity = quantity;

    this.saveItems(items);
    return items;
  },

  removeItem(variantId) {
    const items = this.getItems().filter(i => i.variant_id !== variantId);
    this.saveItems(items);
    return items;
  },

  clear() {
    this.saveItems([]);
  },

  /* ---------- derived data ---------- */

  getCount() {
    return this.getItems().reduce((sum, i) => sum + i.quantity, 0);
  },

  getSubtotal() {
    return this.getItems().reduce(
      (sum, i) => sum + i.quantity * parseFloat(i.price),
      0
    );
  },

  /* ---------- UI helpers ---------- */

  renderBadge() {
    const badge = document.querySelector("#cart-badge");
    if (!badge) return;
    const count = this.getCount();
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
  }
};

/* ============================================================
   Hook into the product detail page's #cart-form
   Reads the currently-selected variant from the page (color
   swatch / size button / quantity input) and the variants-data
   JSON block, so it always adds the exact variant in stock.
   ============================================================ */

function initAddToCartForm() {
  const form = document.querySelector("#cart-form");
  if (!form) return;

  form.addEventListener("submit", function (e) {
    e.preventDefault(); // stop the real POST — cart is client-side now

    const variantId = parseInt(
      document.querySelector("#selected-variant-id").value,
      10
    );
    const quantity = parseInt(
      document.querySelector("#quantity").value,
      10
    ) || 1;

    const variantsDataEl = document.querySelector("#variants-data");
    const variants = variantsDataEl
      ? JSON.parse(variantsDataEl.textContent)
      : [];
    const variant = variants.find(v => v.id === variantId);

    if (!variant) {
      Cart.toast("Could not find that option — please reselect.");
      return;
    }

    const colorBtn = document.querySelector(
      `.color-swatch[data-color-id="${variant.color_id}"]`
    );
    const shoeName =
      document.querySelector(".shoe-title")?.textContent.trim() || "Item";

    Cart.addItem({
      variant_id: variant.id,
      name: shoeName,
      color: colorBtn ? colorBtn.textContent.trim() : "",
      size: variant.size_value,
      price: variant.price,
      photo: variant.photo,
      stock: variant.stock,
      quantity: quantity
    });

    Cart.toast(`Added ${shoeName} (size ${variant.size_value}) to cart`);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  Cart.renderBadge();
  initAddToCartForm();
});
