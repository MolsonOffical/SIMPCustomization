document.addEventListener('DOMContentLoaded', () => {
  const dropdowns = document.querySelectorAll('.dropdown');
  const isTouchDevice = 'ontouchstart' in window || matchMedia('(pointer: coarse)').matches;

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
      if (dropdown.classList.contains('dropdown--profile')) {
        toggle.setAttribute('aria-expanded', 'true');
      }
    };

    const hideDropdown = () => {
      content.style.opacity = '0';
      fadeOutTimeout = setTimeout(() => {
        content.style.visibility = 'hidden';
        content.style.display = 'none';
      }, 400);
      isOpen = false;
      if (dropdown.classList.contains('dropdown--profile')) {
        toggle.setAttribute('aria-expanded', 'false');
      }
    };

    const isProfile = dropdown.classList.contains('dropdown--profile');
    const useClickToggle = isProfile && (isTouchDevice || window.innerWidth <= 768);

    if (useClickToggle) {
      toggle.addEventListener('click', (e) => {
        e.preventDefault();
        if (isOpen) {
          hideDropdown();
        } else {
          showDropdown();
        }
      });
    }

    if (!useClickToggle) {
      toggle.addEventListener('mouseenter', showDropdown);
      toggle.addEventListener('mouseleave', () => {
        if (!content.matches(':hover')) hideDropdown();
      });

      content.addEventListener('mouseenter', showDropdown);
      content.addEventListener('mouseleave', hideDropdown);
    }
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
          if (toggle && dropdown.classList.contains('dropdown--profile')) {
            toggle.setAttribute('aria-expanded', 'false');
          }
        }
      }
    });
  });
});
