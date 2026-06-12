(function () {
  const select = document.getElementById('archetype-select');
  const slugInput = document.getElementById('archetype_slug');
  const categoryInput = document.getElementById('question_category');
  const narratorInput = document.getElementById('narrator_slug');
  const card = document.getElementById('archetype-card');
  const img = document.getElementById('archetype-img');
  const nameEl = document.getElementById('archetype-name');
  const taglineEl = document.getElementById('archetype-tagline');
  const sectionQuestions = document.getElementById('section-questions');
  const sectionResponse = document.getElementById('section-response');
  const sectionNarrator = document.getElementById('section-narrator');
  const questionText = document.getElementById('question-text');
  const responseLabel = document.getElementById('response-label');
  const textarea = document.getElementById('user_response');
  const charCount = document.getElementById('char-count');
  const goBtn = document.getElementById('go-btn');

  let selectedCategory = null;
  let selectedNarrator = null;

  function updateGo() {
    const ok =
      slugInput.value &&
      selectedCategory &&
      textarea.value.trim().length >= 20 &&
      selectedNarrator;
    goBtn.disabled = !ok;
  }

  select.addEventListener('change', () => {
    const slug = select.value;
    slugInput.value = slug;
    selectedCategory = null;
    categoryInput.value = '';
    selectedNarrator = null;
    narratorInput.value = '';
    document.querySelectorAll('.question-tile, .narrator-tile').forEach((t) => t.classList.remove('selected'));

    if (!slug) {
      card.classList.add('hidden');
      sectionQuestions.classList.add('hidden');
      sectionResponse.classList.add('hidden');
      sectionNarrator.classList.add('hidden');
      updateGo();
      return;
    }

    const a = ARCHETYPES[slug];
    img.src = `/static/images/archetypes/${slug}.png`;
    img.alt = a.name;
    img.onerror = () => { img.style.visibility = 'hidden'; };
    nameEl.textContent = a.name;
    taglineEl.textContent = a.tagline;
    card.classList.remove('hidden');
    sectionQuestions.classList.remove('hidden');
    sectionResponse.classList.add('hidden');
    sectionNarrator.classList.add('hidden');
    questionText.classList.add('hidden');
    updateGo();
  });

  document.querySelectorAll('.question-tile').forEach((tile) => {
    tile.addEventListener('click', () => {
      const slug = slugInput.value;
      if (!slug) return;
      selectedCategory = tile.dataset.category;
      categoryInput.value = selectedCategory;
      document.querySelectorAll('.question-tile').forEach((t) => t.classList.remove('selected'));
      tile.classList.add('selected');
      const q = ARCHETYPES[slug].questions[selectedCategory];
      questionText.textContent = q;
      questionText.classList.remove('hidden');
      responseLabel.textContent = q;
      sectionResponse.classList.remove('hidden');
      updateGo();
    });
  });

  textarea.addEventListener('input', () => {
    charCount.textContent = textarea.value.length;
    if (textarea.value.trim().length >= 20) {
      sectionNarrator.classList.remove('hidden');
    }
    updateGo();
  });

  document.querySelectorAll('.narrator-tile').forEach((tile) => {
    tile.addEventListener('click', () => {
      selectedNarrator = tile.dataset.slug;
      narratorInput.value = selectedNarrator;
      document.querySelectorAll('.narrator-tile').forEach((t) => t.classList.remove('selected'));
      tile.classList.add('selected');
      updateGo();
    });
  });
})();
