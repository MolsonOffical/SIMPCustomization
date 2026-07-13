// cart.js — handles quantity changes and item removal on the Your Cart page

document.addEventListener('DOMContentLoaded', function () {

  function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;
    // Fallback: read from cookie if no form token is present on this page
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  function formatNPR(amount) {
    return 'NPR ' + Math.round(amount).toLocaleString('en-IN');
  }

  function updateSummary(subtotal, cartItemCount) {
    document.getElementById('summary-item-count').textContent = cartItemCount;
    document.getElementById('summary-items-total').textContent = formatNPR(subtotal);
    document.getElementById('summary-subtotal').textContent = formatNPR(subtotal);
    document.getElementById('summary-total').textContent = formatNPR(subtotal);
    document.getElementById('cart-item-count-label').textContent =
      cartItemCount + (cartItemCount === 1 ? ' item' : ' items');

    var badge = document.getElementById('nav-cart-count');
    if (badge) {
      badge.textContent = cartItemCount;
      badge.hidden = cartItemCount <= 0;
    }
  }

  function updateCardTotal(card, lineTotal) {
    var totalEl = card.querySelector('.line-total-value');
    if (totalEl) totalEl.textContent = Math.round(lineTotal).toLocaleString('en-IN');
  }

  function sendQuantityUpdate(itemId, quantity, card) {
    fetch(window.CART_URLS.updateQuantity, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ item_id: itemId, quantity: quantity })
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (errData) {
            throw new Error(errData.error || 'Request failed with status ' + res.status);
          });
        }
        return res.json();
      })
      .then(function (data) {
        updateCardTotal(card, parseFloat(data.line_total));
        updateSummary(parseFloat(data.subtotal), data.cart_item_count);
      })
      .catch(function (err) {
        console.error('Quantity update failed:', err);
        alert(err.message || 'Could not update quantity. Please try again.');
      });
  }

  function sendRemoveItem(itemId, card) {
    fetch(window.CART_URLS.removeItem, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: JSON.stringify({ item_id: itemId })
    })
      .then(function (res) {
        if (!res.ok) {
          return res.json().then(function (errData) {
            throw new Error(errData.error || 'Request failed with status ' + res.status);
          });
        }
        return res.json();
      })
      .then(function (data) {
        card.remove();
        updateSummary(parseFloat(data.subtotal), data.cart_item_count);

        if (data.cart_item_count <= 0) {
          location.reload(); // show the empty-cart state
        }
      })
      .catch(function (err) {
        console.error('Remove item failed:', err);
        alert(err.message || 'Could not remove item. Please try again.');
      });
  }

  document.querySelectorAll('.cart-card').forEach(function (card) {
    var itemId = card.dataset.itemId;
    var unitPrice = parseFloat(card.dataset.unitPrice) || 0;
    var qtyInput = card.querySelector('.qty-input');
    var decBtn = card.querySelector('[data-qty-dec]');
    var incBtn = card.querySelector('[data-qty-inc]');
    var removeBtn = card.querySelector('[data-remove-id]');

    decBtn.addEventListener('click', function () {
      var qty = parseInt(qtyInput.value, 10) || 1;
      if (qty > 1) {
        qty -= 1;
        qtyInput.value = qty;
        updateCardTotal(card, unitPrice * qty);
        sendQuantityUpdate(itemId, qty, card);
      }
    });

    incBtn.addEventListener('click', function () {
      var qty = parseInt(qtyInput.value, 10) || 1;
      if (qty < 10) {
        qty += 1;
        qtyInput.value = qty;
        updateCardTotal(card, unitPrice * qty);
        sendQuantityUpdate(itemId, qty, card);
      }
    });

    removeBtn.addEventListener('click', function () {
      if (confirm('Remove this item from your cart?')) {
        sendRemoveItem(itemId, card);
      }
    });
  });

  var checkoutBtn = document.getElementById('btn-checkout');
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', function () {
      // TODO: wire this up once a checkout/order flow exists
      alert('Checkout is coming soon.');
    });
  }

  var khaltiBtn = document.getElementById('btn-khalti');
  if (khaltiBtn) {
    khaltiBtn.addEventListener('click', function () {
      // TODO: wire this up once Khalti payment integration is set up
      alert('Khalti checkout is coming soon.');
    });
  }

});