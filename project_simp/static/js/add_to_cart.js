/* ==========================================================
   Added to Cart Modal — SIMP
   Include this after the modal HTML is on the page.

   Usage from your customizer's "Add to Cart" button:

     CartModal.show({
       name: 'Custom Shoe',
       size: 'EU 44',
       price: 5499,        // number, in NPR
       quantity: 1,
       image: '/static/img/shoe-thumb.png',
       cartUrl: '/cart/'   // optional, defaults to /cart/
     });

   Typical flow: your "Add to Cart" click handler should first
   POST the customization to Django (fetch), then call
   CartModal.show(...) using the response data (real price,
   real cart item count, etc.) rather than hardcoded values.
   ========================================================== */

const CartModal = (() => {
  let overlay, closeBtn, continueBtn;

  function formatNPR(amount) {
    const num = Number(amount) || 0;
    return 'NPR ' + num.toLocaleString('en-IN');
  }

  function init() {
    overlay = document.getElementById('cart-modal-overlay');
    closeBtn = document.getElementById('cm-close-btn');
    continueBtn = document.getElementById('cm-continue-btn');

    if (!overlay) return;

    closeBtn.addEventListener('click', hide);
    continueBtn.addEventListener('click', hide);

    // Click outside modal closes it
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) hide();
    });

    // Escape key closes it
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !overlay.hidden) hide();
    });
  }

  function show(item) {
    if (!overlay) init();
    if (!overlay) {
      console.error('CartModal: #cart-modal-overlay not found in the DOM.');
      return;
    }

    const {
      name = 'Custom Shoe',
      size = '',
      price = 0,
      quantity = 1,
      image = '',
      cartUrl = '/cart/'
    } = item || {};

    const lineTotal = price * quantity;

    document.getElementById('cm-item-name').textContent = name;
    document.getElementById('cm-item-size').textContent = size;
    document.getElementById('cm-item-price').textContent = formatNPR(price);

    const imgEl = document.getElementById('cm-item-image');
    if (image) {
      imgEl.src = image;
      imgEl.style.display = '';
    } else {
      imgEl.style.display = 'none';
    }

    document.getElementById('cm-item-count').textContent = quantity;
    document.getElementById('cm-items-total').textContent = formatNPR(lineTotal);
    document.getElementById('cm-subtotal').textContent = formatNPR(lineTotal);
    document.getElementById('cm-total').textContent = formatNPR(lineTotal);
    document.getElementById('cm-view-cart').setAttribute('href', cartUrl);

    overlay.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function hide() {
    if (!overlay) return;
    overlay.hidden = true;
    document.body.style.overflow = '';
  }

  document.addEventListener('DOMContentLoaded', init);

  return { show, hide };
})();