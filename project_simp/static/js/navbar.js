document.addEventListener('DOMContentLoaded', () => {
  const dropdowns = document.querySelectorAll('.dropdown');
  const isTouchDevice = 'ontouchstart' in window || matchMedia('(pointer: coarse)').matches;
  const isMobileContext = () => isTouchDevice || window.innerWidth <= 768;

  const hideAllDropdowns = (except) => {
    dropdowns.forEach(d => {
      if (d === except) return;
      const content = d.querySelector('.dropdown-content');
      if (!content) return;
      content.style.opacity = '0';
      setTimeout(() => {
        content.style.visibility = 'hidden';
        content.style.display = 'none';
      }, 400);
      const t = d.querySelector('.dropdown-toggle');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  };

  dropdowns.forEach(dropdown => {
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const content = dropdown.querySelector('.dropdown-content');
    if (!toggle || !content) return;

    let fadeOutTimeout;
    let isOpen = false;

    Object.assign(content.style, {
      opacity: '0',
      visibility: 'hidden',
      display: 'none',
      transition: 'opacity 0.4s ease'
    });

    const showDropdown = () => {
      clearTimeout(fadeOutTimeout);
      hideAllDropdowns(dropdown);
      content.style.display = 'block';
      content.style.visibility = 'visible';
      requestAnimationFrame(() => {
        content.style.opacity = '1';
      });
      isOpen = true;
      toggle.setAttribute('aria-expanded', 'true');
    };

    const hideDropdown = () => {
      content.style.opacity = '0';
      fadeOutTimeout = setTimeout(() => {
        content.style.visibility = 'hidden';
        content.style.display = 'none';
      }, 400);
      isOpen = false;
      toggle.setAttribute('aria-expanded', 'false');
    };

    // Click: drives mobile/touch (tap to open/close). On desktop it just
    // stops "#" toggle links from jumping the page to the top.
    toggle.addEventListener('click', (e) => {
      if (isMobileContext()) {
        e.preventDefault();
        isOpen ? hideDropdown() : showDropdown();
      } else if (toggle.getAttribute('href') === '#') {
        e.preventDefault();
      }
    });

    // Hover: drives desktop only. Checked live so resizing the window
    // switches behavior without needing a page reload.
    toggle.addEventListener('mouseenter', () => {
      if (isMobileContext()) return;
      showDropdown();
    });
    toggle.addEventListener('mouseleave', () => {
      if (isMobileContext()) return;
      if (!content.matches(':hover')) hideDropdown();
    });

    content.addEventListener('mouseenter', () => {
      if (isMobileContext()) return;
      showDropdown();
    });
    content.addEventListener('mouseleave', () => {
      if (isMobileContext()) return;
      hideDropdown();
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      hideAllDropdowns(null);
    }
  });

  document.addEventListener('click', (e) => {
    dropdowns.forEach(dropdown => {
      if (!dropdown.contains(e.target)) {
        const content = dropdown.querySelector('.dropdown-content');
        if (content && content.style.display !== 'none') {
          content.style.opacity = '0';
          setTimeout(() => {
            content.style.visibility = 'hidden';
            content.style.display = 'none';
          }, 400);
          const toggle = dropdown.querySelector('.dropdown-toggle');
          if (toggle) toggle.setAttribute('aria-expanded', 'false');
        }
      }
    });
  });

  // ---- Mobile hamburger menu ----
  const navToggle = document.getElementById('navToggle');
  const navCollapse = document.getElementById('navCollapse');

  if (navToggle && navCollapse) {
    const closeMenu = () => {
      navCollapse.classList.remove('active');
      navToggle.setAttribute('aria-expanded', 'false');
      navToggle.innerHTML = '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
      hideAllDropdowns(null);
    };

    const openMenu = () => {
      navCollapse.classList.add('active');
      navToggle.setAttribute('aria-expanded', 'true');
      navToggle.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
    };

    navToggle.addEventListener('click', () => {
      navCollapse.classList.contains('active') ? closeMenu() : openMenu();
    });

    // Close the mobile panel when an actual navigation link is clicked —
    // but NOT the "Categories" dropdown-toggle itself, since that should
    // expand inline, not close the whole menu.
    navCollapse.querySelectorAll('.nav-links a:not(.dropdown-toggle), .user-actions a').forEach(link => {
      link.addEventListener('click', closeMenu);
    });

    document.addEventListener('click', (event) => {
      const isInside = navCollapse.contains(event.target) || navToggle.contains(event.target);
      if (!isInside && navCollapse.classList.contains('active')) {
        closeMenu();
      }
    });

    window.addEventListener('resize', () => {
      if (window.innerWidth > 768 && navCollapse.classList.contains('active')) {
        closeMenu();
      }
    });
  }
});