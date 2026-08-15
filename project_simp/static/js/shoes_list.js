(function() {
    const form = document.getElementById('filterForm');
    const container = document.getElementById('productContainer');
    const toggleBtn = document.getElementById('filterToggleBtn');
    const sidebar = document.getElementById('filterSidebar');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            sidebar.classList.toggle('open');
            toggleBtn.classList.toggle('active');
        });
    }

    function setInitialSidebar() {
        if (!sidebar) return;
        if (window.innerWidth >= 901) {
            sidebar.classList.remove('open');
            toggleBtn.classList.remove('active');
        } else {
            sidebar.classList.remove('open');
            toggleBtn.classList.remove('active');
        }
    }
    setInitialSidebar();

    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(setInitialSidebar, 250);
    });

    function getFilterParams() {
        const formData = new FormData(form);
        const params = new URLSearchParams();
        const categories = formData.getAll('category');
        if (categories.length) params.append('category', categories.join(','));
        const brands = formData.getAll('brand');
        if (brands.length) params.append('brand', brands.join(','));
        const rating = formData.get('rating');
        if (rating) params.append('rating', rating);
        const min_price = formData.get('min_price');
        if (min_price) params.append('min_price', min_price);
        const max_price = formData.get('max_price');
        if (max_price) params.append('max_price', max_price);
        const searched = formData.get('searched');
        if (searched) params.append('searched', searched);
        params.set('page', '1');
        return params;
    }

    function fetchFiltered() {
        const params = getFilterParams();
        const baseUrl = form.getAttribute('action') || window.location.pathname;
        const url = baseUrl + '?' + params.toString();

        fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.text())
        .then(html => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            const newContainer = tempDiv.querySelector('#productContainer');
            if (newContainer) {
                container.innerHTML = newContainer.innerHTML;
                window.history.pushState({}, '', url);
            } else {
                window.location.href = url;
            }
        })
        .catch(() => {
            window.location.href = url;
        });
    }

    window.addEventListener('popstate', function() {
        window.location.reload();
    });

    form.querySelectorAll('input, select').forEach(input => {
        if (input.type === 'number') {
            input.addEventListener('blur', function() {
                fetchFiltered();
            });
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    fetchFiltered();
                }
            });
        } else {
            input.addEventListener('change', function() {
                fetchFiltered();
            });
        }
    });

    const applyBtn = form.querySelector('.btn-apply-filter');
    if (applyBtn) applyBtn.remove();
})();
