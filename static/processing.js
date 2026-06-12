(function () {
  const phrases = [
    'Reading between your words…',
    'Finding the shape of your thinking…',
    'Composing your reflection…',
    'Almost ready…',
  ];
  let idx = 0;
  const phraseEl = document.getElementById('processing-phrase');
  const errorEl = document.getElementById('processing-error');

  setInterval(() => {
    idx = (idx + 1) % phrases.length;
    phraseEl.textContent = phrases[idx];
  }, 3000);

  async function poll() {
    try {
      const res = await fetch(`/api/status/${window.SEEN_UUID}`);
      const data = await res.json();
      if (data.status === 'ready') {
        window.location.href = `/result/${window.SEEN_UUID}`;
        return;
      }
      if (data.status === 'error') {
        errorEl.classList.remove('hidden');
        errorEl.innerHTML = `${data.message || 'Something went wrong.'} <a href="/">Try again</a>`;
        return;
      }
    } catch (e) {
      console.warn('Poll failed', e);
    }
    setTimeout(poll, 1500);
  }

  poll();
})();
