(function () {
  const phrases = [
    'Reading between your words…',
    'Finding the shape of your thinking…',
    'Composing your reflection…',
    'Almost ready…',
  ];
  let idx = 0;
  let phraseTimer = null;
  let pollTimer = null;

  const titleEl = document.getElementById('processing-title');
  const phraseEl = document.getElementById('processing-phrase');
  const progressEl = document.getElementById('processing-progress');
  const errorBox = document.getElementById('processing-error');
  const errorMessageEl = document.getElementById('processing-error-message');
  const errorActionsEl = document.getElementById('processing-error-actions');
  const retryForm = document.getElementById('retry-form');
  const stepsEl = document.getElementById('processing-steps');

  const stepEls = {
    text: document.getElementById('step-text'),
    image: document.getElementById('step-image'),
    voice: document.getElementById('step-voice'),
  };

  function applyStepState(stepKey, status) {
    const el = stepEls[stepKey];
    if (!el) return;
    el.classList.remove('is-active', 'is-done', 'is-error', 'is-pending', 'is-skipped');
    if (status === 'generating') el.classList.add('is-active');
    else if (status === 'ready') el.classList.add('is-done');
    else if (status === 'error') el.classList.add('is-error');
    else if (status === 'skipped') el.classList.add('is-skipped');
  }

  function updateSteps(steps) {
    if (!steps) return;
    ['text', 'image', 'voice'].forEach((key) => {
      const step = steps[key];
      if (step) applyStepState(key, step.status);
    });
  }

  phraseTimer = setInterval(() => {
    idx = (idx + 1) % phrases.length;
    phraseEl.textContent = phrases[idx];
  }, 3000);

  function showError(message, canRetry) {
    if (phraseTimer) clearInterval(phraseTimer);
    if (pollTimer) clearTimeout(pollTimer);

    titleEl.textContent = 'Something went wrong';
    phraseEl.classList.add('hidden');
    if (progressEl) progressEl.classList.add('hidden');
    if (stepsEl) stepsEl.classList.add('hidden');
    errorBox.classList.remove('hidden');
    errorMessageEl.textContent = message || 'Something went wrong.';

    if (canRetry && retryForm) {
      retryForm.action = `/reflect/retry/${window.SEEN_UUID}`;
      errorActionsEl.classList.remove('hidden');
    }
  }

  async function poll() {
    try {
      const res = await fetch(`/api/status/${window.SEEN_UUID}`);
      const data = await res.json();
      updateSteps(data.steps);
      if (data.text_ready) {
        window.location.href = `/result/${window.SEEN_UUID}`;
        return;
      }
      if (data.status === 'error') {
        showError(data.message, data.can_retry);
        return;
      }
    } catch (e) {
      console.warn('Poll failed', e);
    }
    pollTimer = setTimeout(poll, 1200);
  }

  poll();
})();
