document.addEventListener('DOMContentLoaded', () => {
  const navToggle = document.getElementById('navToggle');
  const navCollapse = document.getElementById('navCollapse');
  const dropdowns = document.querySelectorAll('.dropdown');
  const mobileQuery = window.matchMedia('(max-width: 900px)');

  const isMobile = () => mobileQuery.matches;

  /* ---------------- Hamburger menu ---------------- */
  const openMenu = () => {
    navCollapse.classList.add('is-open');
    navToggle.setAttribute('aria-expanded', 'true');
  };

  const closeMenu = () => {
    navCollapse.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    closeAllDropdowns();
  };

  const toggleMenu = () => {
    if (navCollapse.classList.contains('is-open')) {
      closeMenu();
    } else {
      openMenu();
    }
  };

  if (navToggle && navCollapse) {
    navToggle.addEventListener('click', (e) => {
      e.preventDefault();
      toggleMenu();
    });
  }

  /* ---------------- Dropdown helpers ---------------- */
  const fadeShow = (content) => {
    clearTimeout(content._fadeTimeout);
    content.style.display = 'block';
    content.style.visibility = 'visible';
    requestAnimationFrame(() => {
      content.style.opacity = '1';
    });
  };

  const fadeHide = (content) => {
    content.style.opacity = '0';
    content._fadeTimeout = setTimeout(() => {
      content.style.visibility = 'hidden';
      content.style.display = 'none';
    }, 250);
  };

  const closeAllDropdowns = () => {
    dropdowns.forEach((dropdown) => {
      const toggle = dropdown.querySelector('.dropdown-toggle');
      const content = dropdown.querySelector('.dropdown-content');
      dropdown.classList.remove('is-open');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
      if (content && dropdown.classList.contains('dropdown--profile')) {
        fadeHide(content);
      }
    });
  };

  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector('.dropdown-toggle');
    const content = dropdown.querySelector('.dropdown-content');
    if (!toggle || !content) return;

    const isProfile = dropdown.classList.contains('dropdown--profile');
    const isCategories = dropdown.classList.contains('dropdown--categories');

    // Popover dropdowns (profile, and categories on desktop) start hidden
    // via inline fade styles. On mobile, categories switches to a CSS-driven
    // inline accordion instead (see navbar.css) so we leave it alone there.
    const initPopoverHidden = () => {
      Object.assign(content.style, {
        opacity: '0',
        visibility: 'hidden',
        display: 'none',
        transition: 'opacity 0.25s ease'
      });
    };

    if (isProfile) initPopoverHidden();
    if (isCategories && !isMobile()) initPopoverHidden();

    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      const willOpen = !dropdown.classList.contains('is-open');

      // Close sibling dropdowns first
      dropdowns.forEach((d) => {
        if (d !== dropdown) {
          d.classList.remove('is-open');
          const dToggle = d.querySelector('.dropdown-toggle');
          const dContent = d.querySelector('.dropdown-content');
          if (dToggle) dToggle.setAttribute('aria-expanded', 'false');
          if (dContent && d.classList.contains('dropdown--profile')) fadeHide(dContent);
        }
      });

      dropdown.classList.toggle('is-open', willOpen);
      toggle.setAttribute('aria-expanded', String(willOpen));

      // Profile is always a floating popover -> fade it.
      // Categories is a floating popover only on desktop; on mobile it's
      // a plain inline accordion handled purely by the .is-open CSS class.
      if (isProfile || (isCategories && !isMobile())) {
        if (willOpen) fadeShow(content); else fadeHide(content);
      }
    });

    // Desktop hover convenience (skipped on touch devices)
    const supportsHover = matchMedia('(hover: hover)').matches;
    if (supportsHover) {
      const showOnHover = () => {
        if (isMobile()) return;
        dropdowns.forEach((d) => {
          if (d !== dropdown) {
            const dContent = d.querySelector('.dropdown-content');
            if (dContent && d.classList.contains('dropdown--profile')) fadeHide(dContent);
            d.classList.remove('is-open');
          }
        });
        dropdown.classList.add('is-open');
        toggle.setAttribute('aria-expanded', 'true');
        fadeShow(content);
      };
      const hideOnLeave = () => {
        if (isMobile()) return;
        setTimeout(() => {
          if (!dropdown.matches(':hover')) {
            dropdown.classList.remove('is-open');
            toggle.setAttribute('aria-expanded', 'false');
            fadeHide(content);
          }
        }, 60);
      };
      dropdown.addEventListener('mouseenter', showOnHover);
      dropdown.addEventListener('mouseleave', hideOnLeave);
    }
  });

  /* ---------------- Close menu when a real nav link is clicked ---------------- */
  navCollapse?.querySelectorAll('a:not(.dropdown-toggle)').forEach((link) => {
    link.addEventListener('click', () => {
      if (isMobile()) closeMenu();
    });
  });

  /* ---------------- Escape key ---------------- */
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllDropdowns();
      if (isMobile()) closeMenu();
    }
  });

  /* ---------------- Click outside ---------------- */
  document.addEventListener('click', (e) => {
    dropdowns.forEach((dropdown) => {
      if (!dropdown.contains(e.target)) {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const content = dropdown.querySelector('.dropdown-content');
        dropdown.classList.remove('is-open');
        if (toggle) toggle.setAttribute('aria-expanded', 'false');
        if (content && dropdown.classList.contains('dropdown--profile')) fadeHide(content);
      }
    });

    if (
      navCollapse &&
      navCollapse.classList.contains('is-open') &&
      !navCollapse.contains(e.target) &&
      !navToggle.contains(e.target)
    ) {
      closeMenu();
    }
  });

  /* ---------------- Reset state on breakpoint change ---------------- */
  mobileQuery.addEventListener('change', () => {
    closeAllDropdowns();
    navCollapse.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    // Re-hide the categories popover styles appropriately for the new mode
    document.querySelectorAll('.dropdown--categories .dropdown-content').forEach((content) => {
      content.removeAttribute('style');
    });
  });
});