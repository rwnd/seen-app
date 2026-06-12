(function () {
  const audio = document.getElementById('reflection-audio');
  const overlay = document.getElementById('autoplay-overlay');
  const startBtn = document.getElementById('start-audio');
  const playPause = document.getElementById('play-pause');
  const progress = document.getElementById('audio-progress');
  const status = document.getElementById('audio-status');
  const shareBtn = document.getElementById('share-btn');
  const comicImg = document.querySelector('.comic-img');

  function playAudio() {
    overlay.classList.add('hidden');
    audio.play().catch(() => {});
  }

  startBtn.addEventListener('click', playAudio);
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) playAudio();
  });

  playPause.addEventListener('click', () => {
    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  });

  audio.addEventListener('play', () => {
    playPause.textContent = '❚❚';
    status.textContent = 'Playing reflection…';
  });

  audio.addEventListener('pause', () => {
    playPause.textContent = '▶';
    if (!audio.ended) status.textContent = 'Paused';
  });

  audio.addEventListener('ended', () => {
    playPause.textContent = '▶';
    status.textContent = 'Finished';
  });

  audio.addEventListener('timeupdate', () => {
    if (audio.duration) {
      progress.style.width = `${(audio.currentTime / audio.duration) * 100}%`;
    }
  });

  document.querySelectorAll('.tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
      tab.classList.add('active');
      document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
    });
  });

  if (comicImg) {
    comicImg.addEventListener('click', () => {
      window.open(comicImg.src, '_blank');
    });
  }

  shareBtn.addEventListener('click', async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      shareBtn.textContent = 'Copied!';
      setTimeout(() => { shareBtn.textContent = 'Share link'; }, 2000);
    } catch {
      prompt('Copy this link:', url);
    }
  });
})();
