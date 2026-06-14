(function () {
  const slugInput = document.getElementById('archetype_slug');
  const categoryInput = document.getElementById('question_category');
  const narratorInput = document.getElementById('narrator_slug');
  const card = document.getElementById('archetype-card');
  const img = document.getElementById('archetype-img');
  const nameEl = document.getElementById('archetype-name');
  const categoryTagEl = document.getElementById('archetype-category-tag');
  const taglineEl = document.getElementById('archetype-tagline');
  const sectionQuestions = document.getElementById('section-questions');
  const sectionNarrator = document.getElementById('section-narrator');
  const dividerQuestions = document.getElementById('divider-questions');
  const dividerNarrator = document.getElementById('divider-narrator');
  const questionText = document.getElementById('question-text');
  const reflectAnswerEmpty = document.getElementById('reflect-answer-empty');
  const reflectAnswerForm = document.getElementById('reflect-answer-form');
  const starterList = document.getElementById('starter-list');
  const textarea = document.getElementById('user_response');
  const charCount = document.getElementById('char-count');
  const goBtn = document.getElementById('go-btn');
  const archetypeInput = document.getElementById('archetype-input');
  const archetypeToggle = document.getElementById('archetype-toggle');
  const archetypeListbox = document.getElementById('archetype-listbox');
  const reflectAnswer = document.getElementById('reflect-answer');
  const inputSteps = document.querySelectorAll('.input-step');

  function setInputStep(index) {
    inputSteps.forEach((el, i) => {
      el.classList.toggle('is-current', i === index);
    });
  }

  function setAnswerPanelActive(active) {
    if (reflectAnswer) reflectAnswer.classList.toggle('is-active', active);
  }

  let selectedCategory = null;
  let selectedNarrator = null;
  let highlightIndex = -1;
  let visibleOptions = [];

  const archetypeEntries = Object.entries(ARCHETYPES).map(([slug, a]) => ({
    slug,
    name: a.name,
    category: a.category,
  }));

  function revealSection(el, divider) {
    el.classList.remove('hidden');
    requestAnimationFrame(() => el.classList.add('section-visible'));
    if (divider) divider.classList.remove('hidden');
  }

  function getQuestion(slug, category) {
    const raw = ARCHETYPES[slug].questions[category];
    if (typeof raw === 'string') return { text: raw, starters: [] };
    return raw;
  }

  function updateGo() {
    goBtn.disabled = !(
      slugInput.value &&
      selectedCategory &&
      textarea.value.trim().length >= 20 &&
      selectedNarrator
    );
  }

  function clearStarterSelection() {
    starterList.querySelectorAll('.starter-btn').forEach((btn) => {
      btn.classList.remove('selected');
      btn.setAttribute('aria-selected', 'false');
    });
  }

  function renderStarters(starters) {
    starterList.innerHTML = '';
    if (!starters.length) {
      starterList.classList.add('hidden');
      return;
    }
    starterList.classList.remove('hidden');
    starters.forEach((text) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'starter-btn';
      btn.textContent = text;
      btn.addEventListener('click', () => {
        clearStarterSelection();
        btn.classList.add('selected');
        textarea.value = text;
        charCount.textContent = String(text.length);
        textarea.focus();
        updateGo();
        if (textarea.value.trim().length >= 20 && sectionNarrator.classList.contains('hidden')) {
          revealSection(sectionNarrator, dividerNarrator);
        }
      });
      starterList.appendChild(btn);
    });
  }

  function resetQuestionSelection() {
    selectedCategory = null;
    categoryInput.value = '';
    textarea.value = '';
    charCount.textContent = '0';
    starterList.innerHTML = '';
    starterList.classList.add('hidden');
    document.querySelectorAll('.question-tile').forEach((t) => {
      t.classList.remove('selected');
      t.setAttribute('aria-selected', 'false');
    });
    reflectAnswerForm.classList.add('hidden');
    reflectAnswerEmpty.classList.remove('hidden');
    setAnswerPanelActive(false);
    questionText.textContent = '';
  }

  function filteredArchetypes(query) {
    const q = query.trim().toLowerCase();
    if (!q) return archetypeEntries;
    return archetypeEntries.filter((item) => item.name.toLowerCase().includes(q));
  }

  function groupedByCategory(items) {
    const groups = [];
    const categories = typeof ARCHETYPE_CATEGORIES !== 'undefined'
      ? ARCHETYPE_CATEGORIES
      : [...new Set(items.map((i) => i.category))].sort();

    categories.forEach((category) => {
      const inCategory = items
        .filter((item) => item.category === category)
        .sort((a, b) => a.name.localeCompare(b.name));
      if (inCategory.length) groups.push({ category, items: inCategory });
    });
    return groups;
  }

  function closeListbox() {
    archetypeListbox.classList.add('hidden');
    archetypeInput.setAttribute('aria-expanded', 'false');
    highlightIndex = -1;
    visibleOptions = [];
  }

  function openListbox() {
    archetypeListbox.classList.remove('hidden');
    archetypeInput.setAttribute('aria-expanded', 'true');
  }

  function renderListbox(query) {
    const filtered = filteredArchetypes(query);
    const groups = groupedByCategory(filtered);
    archetypeListbox.innerHTML = '';
    visibleOptions = [];

    if (!groups.length) {
      const empty = document.createElement('li');
      empty.className = 'archetype-list-empty';
      empty.textContent = 'No archetypes match your search';
      archetypeListbox.appendChild(empty);
      openListbox();
      return;
    }

    groups.forEach(({ category, items }) => {
      const heading = document.createElement('li');
      heading.className = 'archetype-list-category';
      heading.textContent = category;
      heading.setAttribute('role', 'presentation');
      archetypeListbox.appendChild(heading);

      items.forEach((item) => {
        const option = document.createElement('li');
        option.className = 'archetype-list-option';
        option.setAttribute('role', 'option');
        option.dataset.slug = item.slug;
        option.textContent = item.name;
        if (slugInput.value === item.slug) option.classList.add('is-selected');

        option.addEventListener('mousedown', (e) => {
          e.preventDefault();
          pickArchetype(item.slug);
        });

        archetypeListbox.appendChild(option);
        visibleOptions.push(option);
      });
    });

    highlightIndex = -1;
    openListbox();
  }

  function setHighlight(index) {
    visibleOptions.forEach((el, i) => {
      el.classList.toggle('is-highlighted', i === index);
      if (i === index) el.scrollIntoView({ block: 'nearest' });
    });
    highlightIndex = index;
  }

  function pickArchetype(slug) {
    if (!ARCHETYPES[slug]) return;
    if (slugInput.value !== slug) selectArchetype(slug);
    else {
      archetypeInput.value = ARCHETYPES[slug].name;
      closeListbox();
    }
  }

  function clearArchetype() {
    slugInput.value = '';
    if (archetypeInput) archetypeInput.value = '';
    card.classList.add('hidden');
    sectionQuestions.classList.add('hidden');
    sectionQuestions.classList.remove('section-visible');
    if (dividerQuestions) dividerQuestions.classList.add('hidden');
    sectionNarrator.classList.add('hidden');
    sectionNarrator.classList.remove('section-visible');
    if (dividerNarrator) dividerNarrator.classList.add('hidden');
    selectedNarrator = null;
    narratorInput.value = '';
    document.querySelectorAll('.narrator-tile').forEach((t) => t.classList.remove('selected'));
    resetQuestionSelection();
    closeListbox();
    setInputStep(0);
    updateGo();
  }

  function selectArchetype(slug) {
    slugInput.value = slug;

    selectedCategory = null;
    selectedNarrator = null;
    narratorInput.value = '';
    categoryInput.value = '';
    document.querySelectorAll('.narrator-tile').forEach((t) => t.classList.remove('selected'));
    sectionNarrator.classList.add('hidden');
    sectionNarrator.classList.remove('section-visible');
    if (dividerNarrator) dividerNarrator.classList.add('hidden');
    resetQuestionSelection();

    const a = ARCHETYPES[slug];
    if (archetypeInput) archetypeInput.value = a.name;
    img.src = `/static/images/archetypes/${slug}.png`;
    img.alt = a.name;
    nameEl.textContent = a.name;
    categoryTagEl.textContent = a.category;
    taglineEl.textContent = a.tagline;
    card.classList.remove('hidden');
    closeListbox();
    revealSection(sectionQuestions, dividerQuestions);
    setInputStep(1);
    updateGo();
  }

  function syncInputOnBlur() {
    const value = archetypeInput.value.trim();
    if (!value) {
      if (slugInput.value) clearArchetype();
      return;
    }

    const exact = archetypeEntries.find(
      (item) => item.name.toLowerCase() === value.toLowerCase()
    );
    if (exact) {
      pickArchetype(exact.slug);
      return;
    }

    const partial = archetypeEntries.filter((item) =>
      item.name.toLowerCase().includes(value.toLowerCase())
    );
    if (partial.length === 1) {
      pickArchetype(partial[0].slug);
      return;
    }

    if (slugInput.value) {
      archetypeInput.value = ARCHETYPES[slugInput.value].name;
    } else {
      archetypeInput.value = '';
    }
  }

  if (archetypeInput) {
    archetypeInput.addEventListener('focus', () => {
      renderListbox(archetypeInput.value);
    });

    archetypeInput.addEventListener('input', () => {
      if (!archetypeInput.value.trim() && slugInput.value) clearArchetype();
      renderListbox(archetypeInput.value);
    });

    archetypeInput.addEventListener('blur', () => {
      setTimeout(syncInputOnBlur, 150);
    });

    archetypeInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        closeListbox();
        archetypeInput.blur();
        return;
      }

      if (!visibleOptions.length) {
        if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
          e.preventDefault();
          renderListbox(archetypeInput.value);
        }
        return;
      }

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        const next = highlightIndex < visibleOptions.length - 1 ? highlightIndex + 1 : 0;
        setHighlight(next);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prev = highlightIndex > 0 ? highlightIndex - 1 : visibleOptions.length - 1;
        setHighlight(prev);
      } else if (e.key === 'Enter') {
        if (highlightIndex >= 0 && visibleOptions[highlightIndex]) {
          e.preventDefault();
          pickArchetype(visibleOptions[highlightIndex].dataset.slug);
        } else if (visibleOptions.length === 1) {
          e.preventDefault();
          pickArchetype(visibleOptions[0].dataset.slug);
        }
      }
    });
  }

  if (archetypeToggle) {
    archetypeToggle.addEventListener('click', () => {
      archetypeInput.focus();
      renderListbox(archetypeInput.value);
    });
  }

  document.addEventListener('click', (e) => {
    if (archetypeCombobox && !archetypeCombobox.contains(e.target)) {
      closeListbox();
    }
  });

  document.querySelectorAll('.question-tile').forEach((tile) => {
    tile.addEventListener('click', () => {
      const slug = slugInput.value;
      if (!slug) return;
      selectedCategory = tile.dataset.category;
      categoryInput.value = selectedCategory;
      document.querySelectorAll('.question-tile').forEach((t) => {
        const on = t === tile;
        t.classList.toggle('selected', on);
        t.setAttribute('aria-selected', on ? 'true' : 'false');
      });

      const question = getQuestion(slug, selectedCategory);
      questionText.textContent = question.text;
      renderStarters(question.starters || []);
      textarea.value = '';
      charCount.textContent = '0';
      reflectAnswerEmpty.classList.add('hidden');
      reflectAnswerForm.classList.remove('hidden');
      setAnswerPanelActive(true);
      setInputStep(1);
      updateGo();
    });
  });

  textarea.addEventListener('input', () => {
    charCount.textContent = textarea.value.length;
    if (textarea.value.trim().length >= 20) {
      if (sectionNarrator.classList.contains('hidden')) {
        revealSection(sectionNarrator, dividerNarrator);
      }
      setInputStep(2);
    } else {
      sectionNarrator.classList.add('hidden');
      sectionNarrator.classList.remove('section-visible');
      if (dividerNarrator) dividerNarrator.classList.add('hidden');
      selectedNarrator = null;
      narratorInput.value = '';
      document.querySelectorAll('.narrator-tile').forEach((t) => t.classList.remove('selected'));
      if (selectedCategory) setInputStep(1);
      else if (slugInput.value) setInputStep(0);
    }
    updateGo();
  });

  document.querySelectorAll('.narrator-tile').forEach((tile) => {
    tile.addEventListener('click', () => {
      selectedNarrator = tile.dataset.slug;
      narratorInput.value = selectedNarrator;
      document.querySelectorAll('.narrator-tile').forEach((t) => {
        t.classList.toggle('selected', t === tile);
      });
      setInputStep(3);
      updateGo();
    });
  });
})();
