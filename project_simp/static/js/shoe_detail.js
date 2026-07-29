(function () {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const variantsDataEl = document.getElementById('variants-data');
    const variantsData = variantsDataEl ? JSON.parse(variantsDataEl.textContent) : [];

    const mainImageEl = document.getElementById('main-image');
    const priceEl = document.getElementById('shoe-price');
    const stockEl = document.getElementById('shoe-stock');
    const hiddenVariantInput = document.getElementById('selected-variant-id');
    const quantityInput = document.getElementById('quantity');

    let currentVariantId = hiddenVariantInput ? parseInt(hiddenVariantInput.value, 10) : null;

    function findVariant(id) {
        return variantsData.find(v => v.id === id);
    }

    function findVariantByColorAndSize(colorId, sizeId) {
        return variantsData.find(v => v.color_id === colorId && v.size_id === sizeId);
    }

    function updateSizeOptionsForColor(colorId) {
        document.querySelectorAll('.size-btn').forEach(btn => {
            const btnColorId = parseInt(btn.dataset.colorId, 10);
            if (btnColorId === colorId) {
                btn.classList.remove('hidden');
                const variant = findVariant(parseInt(btn.dataset.variantId, 10));
                btn.classList.toggle('disabled', !!variant && variant.stock === 0);
            } else {
                btn.classList.add('hidden');
            }
        });
    }

    window.selectVariant = function (variantId) {
        const variant = findVariant(variantId);
        if (!variant) return;

        currentVariantId = variant.id;

        if (mainImageEl) {
            const imageUrl = variant.photo || mainImageEl.dataset.default;
            mainImageEl.style.backgroundImage = `url('${imageUrl}')`;
        }

        if (priceEl) {
            const roundedPrice = Math.round(parseFloat(variant.price));
            priceEl.textContent = `NPR.${roundedPrice}`;
        }

        if (stockEl) {
            if (variant.stock > 0) {
                stockEl.classList.remove('out');
                stockEl.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${variant.stock} in stock`;
            } else {
                stockEl.classList.add('out');
                stockEl.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Out of stock';
            }
        }

        if (hiddenVariantInput) {
            hiddenVariantInput.value = variant.id;
        }

        if (quantityInput) {
            quantityInput.max = variant.stock;
            quantityInput.disabled = variant.stock === 0;
            if (parseInt(quantityInput.value, 10) > variant.stock) {
                quantityInput.value = variant.stock > 0 ? 1 : 0;
            }
            if (variant.stock > 0 && parseInt(quantityInput.value, 10) < 1) {
                quantityInput.value = 1;
            }
        }

        document.querySelectorAll('.thumb').forEach(el => {
            el.classList.toggle('active', parseInt(el.dataset.colorId, 10) === variant.color_id);
        });

        document.querySelectorAll('.size-btn').forEach(el => {
            el.classList.toggle('selected', parseInt(el.dataset.variantId, 10) === variant.id);
        });

        document.querySelectorAll('.color-swatch').forEach(el => {
            el.classList.toggle('selected', parseInt(el.dataset.colorId, 10) === variant.color_id);
        });

        updateSizeOptionsForColor(variant.color_id);

        const url = new URL(window.location);
        url.searchParams.set('variant', variant.id);
        window.history.replaceState({}, '', url);
    };

    window.selectColor = function (colorId) {
        const current = findVariant(currentVariantId);
        const sizeId = current ? current.size_id : null;

        let match = findVariantByColorAndSize(colorId, sizeId);

        if (!match) {
            const colorVariants = variantsData.filter(v => v.color_id === colorId);
            match = colorVariants.find(v => v.stock > 0) || colorVariants[0];
        }

        if (match) {
            window.selectVariant(match.id);
        }
    };

    window.changeQty = function (delta) {
        if (!quantityInput || quantityInput.disabled) return;
        const max = parseInt(quantityInput.max, 10) || 1;
        let value = parseInt(quantityInput.value, 10) || 1;
        value += delta;
        if (value < 1) value = 1;
        if (value > max) value = max;
        quantityInput.value = value;
    };

    if (currentVariantId) {
        const initial = findVariant(currentVariantId);
        if (initial) {
            updateSizeOptionsForColor(initial.color_id);
        }
    }
})();
const commentField = document.getElementById('id_comment');
const charHint = document.getElementById('char-hint');
if (commentField && charHint) {
  const updateHint = () => {
    const len = commentField.value.trim().length;
    charHint.textContent = `${len} / 30 characters`;
    charHint.classList.toggle('char-hint--ok', len >= 30);
  };
  commentField.addEventListener('input', updateHint);
  updateHint(); // handles the case where a failed submit re-renders with existing text
}
const fileInput = document.getElementById('id_files');
const uploadContainer = document.getElementById('media-upload');
const addTile = uploadContainer ? uploadContainer.querySelector('.media-tile--add') : null;

if (fileInput && uploadContainer && addTile) {
  let selectedFiles = [];

  fileInput.addEventListener('change', () => {
    selectedFiles = selectedFiles.concat(Array.from(fileInput.files));
    renderTiles();
  });

  function renderTiles() {
    uploadContainer.querySelectorAll('.media-tile--preview').forEach(t => t.remove());

    selectedFiles.forEach((file, index) => {
      const tile = document.createElement('div');
      tile.className = 'media-tile media-tile--preview';

      if (file.type.startsWith('image')) {
        const img = document.createElement('img');
        img.src = URL.createObjectURL(file);
        tile.appendChild(img);
      } else {
        const icon = document.createElement('i');
        icon.className = 'fa-solid fa-video';
        tile.appendChild(icon);
      }

      const removeBtn = document.createElement('button');
      removeBtn.type = 'button';
      removeBtn.className = 'media-tile__remove';
      removeBtn.innerHTML = '&times;';
      removeBtn.addEventListener('click', () => {
        selectedFiles.splice(index, 1);
        syncFileInput();
        renderTiles();
      });
      tile.appendChild(removeBtn);

      uploadContainer.insertBefore(tile, addTile);
    });

    syncFileInput();
  }

  function syncFileInput() {
    const dt = new DataTransfer();
    selectedFiles.forEach(file => dt.items.add(file));
    fileInput.files = dt.files;
  }
}
const ratingLabels = { 1: 'Poor', 2: 'Fair', 3: 'Good', 4: 'Very Good', 5: 'Delightful' };
const ratingLabelEl = document.getElementById('rating-label');
document.querySelectorAll('.star-picker input[type="radio"]').forEach(input => {
  input.addEventListener('change', () => {
    if (ratingLabelEl) ratingLabelEl.textContent = ratingLabels[input.value];
  });
});
function openLightbox(url) {
  document.getElementById('lightbox-img').src = url;
  document.getElementById('lightbox-overlay').classList.add('active');
}
function closeLightbox() {
  document.getElementById('lightbox-overlay').classList.remove('active');
}
function toggleReviewMenu(btn) {
  const dropdown = btn.nextElementSibling;
  const isOpen = dropdown.classList.contains('active');
  document.querySelectorAll('.review-menu__dropdown.active').forEach(d => d.classList.remove('active'));
  if (!isOpen) dropdown.classList.add('active');
}
document.addEventListener('click', (e) => {
  if (!e.target.closest('.review-menu')) {
    document.querySelectorAll('.review-menu__dropdown.active').forEach(d => d.classList.remove('active'));
  }
});