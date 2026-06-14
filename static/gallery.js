(function () {
  const filters = document.querySelectorAll('.gallery-filter');
  const cards = document.querySelectorAll('.gallery-card');
  const emptyState = document.getElementById('gallery-empty-filter');
  const clearBtn = document.getElementById('gallery-clear-filter');
  const countEl = document.getElementById('gallery-count');

  if (!filters.length || !cards.length) return;

  function setActiveFilter(button) {
    filters.forEach((btn) => {
      const on = btn === button;
      btn.classList.toggle('is-active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
    });
  }

  function applyFilter(slug) {
    let visible = 0;
    cards.forEach((card) => {
      const show = slug === 'all' || card.dataset.archetypeSlug === slug;
      card.classList.toggle('hidden', !show);
      if (show) visible += 1;
    });

    if (countEl) countEl.textContent = String(visible);
    if (emptyState) emptyState.classList.toggle('hidden', visible > 0);
  }

  filters.forEach((btn) => {
    btn.addEventListener('click', () => {
      setActiveFilter(btn);
      applyFilter(btn.dataset.filter);
    });
  });

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const allBtn = document.querySelector('.gallery-filter[data-filter="all"]');
      if (allBtn) {
        setActiveFilter(allBtn);
        applyFilter('all');
      }
    });
  }
})();
