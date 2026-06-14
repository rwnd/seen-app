(function () {
  const uuid = window.SEEN_UUID;
  let result = window.SEEN_RESULT || {};
  let pollTimer = null;
  let audioBound = false;
  let revealed = false;

  const stage = document.getElementById('result-stage');
  const curtain = document.getElementById('result-curtain');
  const curtainSub = document.getElementById('curtain-sub');
  const reflectionText = document.getElementById('reflection-text');
  const theLineText = document.getElementById('the-line-text');
  const audio = document.getElementById('reflection-audio');
  const playPause = document.getElementById('play-pause');
  const progress = document.getElementById('audio-progress');
  const audioStatus = document.getElementById('audio-status');
  const resultImage = document.getElementById('result-image');
  const imageFallback = document.getElementById('image-fallback');
  const shareBtn = document.getElementById('share-btn');

  const curtainSteps = {
    image: document.getElementById('curtain-step-image'),
    voice: document.getElementById('curtain-step-voice'),
  };

  function stepReady(step) {
    const status = result.steps?.[step]?.status;
    if (status === 'skipped') {
      return step === 'text' ? !!result.reflection : false;
    }
    return status === 'ready';
  }

  function stepPending(step) {
    const status = result.steps?.[step]?.status;
    return status === 'pending' || status === 'generating';
  }

  function stepTerminal(step) {
    const status = result.steps?.[step]?.status;
    return status === 'ready' || status === 'error' || status === 'skipped';
  }

  function stepError(step) {
    return result.steps?.[step]?.status === 'error';
  }

  function payoffReady() {
    if (!result.reflection && !stepReady('text')) return false;
    return stepTerminal('image') && stepTerminal('voice');
  }

  function formatTime(sec) {
    if (!sec || Number.isNaN(sec)) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${String(s).padStart(2, '0')}`;
  }

  function updateCurtainSteps() {
    ['image', 'voice'].forEach((step) => {
      const el = curtainSteps[step];
      if (!el) return;
      el.classList.remove('is-active', 'is-done', 'is-error');
      if (stepReady(step)) el.classList.add('is-done');
      else if (stepError(step)) el.classList.add('is-error');
      else if (stepPending(step)) el.classList.add('is-active');
    });

    if (!curtainSub) return;
    const imagePending = stepPending('image');
    const voicePending = stepPending('voice');
    if (imagePending && voicePending) {
      curtainSub.textContent = 'Composing your page and voice';
    } else if (imagePending) {
      curtainSub.textContent = 'Illustrating your page…';
    } else if (voicePending) {
      curtainSub.textContent = 'Recording your narrator…';
    } else {
      curtainSub.textContent = 'Opening your reflection…';
    }
  }

  function revealReflection() {
    if (!result.reflection) return;
    reflectionText.textContent = result.reflection;
    reflectionText.classList.remove('hidden');
    reflectionText.classList.add('content-visible');
    if (theLineText && result.the_line) theLineText.textContent = result.the_line;
  }

  function bindAudio() {
    if (audioBound || !result.audio_file) return;
    audioBound = true;
    audio.src = `/data/${result.audio_file}?t=${Date.now()}`;
    playPause.disabled = false;
    audioStatus.textContent = 'Ready to play';

    playPause.addEventListener('click', () => {
      if (audio.paused) audio.play().catch(() => {});
      else audio.pause();
    });

    audio.addEventListener('play', () => {
      playPause.textContent = '❚❚';
    });
    audio.addEventListener('pause', () => {
      if (!audio.ended) playPause.textContent = '▶';
    });
    audio.addEventListener('ended', () => {
      playPause.textContent = '▶';
      audioStatus.textContent = 'Finished';
    });
    audio.addEventListener('timeupdate', () => {
      if (audio.duration) {
        progress.style.width = `${(audio.currentTime / audio.duration) * 100}%`;
        audioStatus.textContent = `${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
      }
    });
    audio.addEventListener('loadedmetadata', () => {
      audioStatus.textContent = `0:00 / ${formatTime(audio.duration)}`;
    });
  }

  function updateAudio() {
    const voiceStep = result.steps?.voice?.status;
    if (voiceStep === 'skipped') {
      audioStatus.textContent = 'Voice not enabled';
      playPause.disabled = true;
      return;
    }
    if (stepPending('voice')) {
      audioStatus.textContent = 'Loading voice…';
      playPause.disabled = true;
      return;
    }
    if (stepError('voice')) {
      audioStatus.textContent = 'Voice unavailable';
      playPause.disabled = true;
      return;
    }
    if (stepReady('voice') && result.audio_file) {
      bindAudio();
    }
  }

  function revealImage() {
    if (stepError('image')) {
      resultImage?.classList.add('hidden');
      imageFallback?.classList.remove('hidden');
      return;
    }
    if (!result.comic_file) return;

    imageFallback?.classList.add('hidden');
    resultImage.classList.remove('hidden');
    resultImage.src = `/data/${result.comic_file}?t=${Date.now()}`;
    resultImage.onload = () => resultImage.classList.add('is-loaded');
    if (resultImage.complete) resultImage.classList.add('is-loaded');
  }

  function tryAutoPlay() {
    if (!audioBound || !result.audio_file || stepError('voice')) return;
    audio.play().catch(() => {
      audioStatus.textContent = 'Tap play to hear your reflection';
    });
  }

  function dismissCurtain() {
    if (!curtain || !stage) return;
    curtain.setAttribute('aria-hidden', 'true');
    stage.classList.add('is-revealed');
    window.setTimeout(() => {
      curtain.hidden = true;
      stage.classList.add('is-curtain-gone');
    }, 700);
  }

  function revealPayoff() {
    if (revealed) return;
    revealed = true;

    updateCurtainSteps();
    revealReflection();
    revealImage();
    updateAudio();

    if (stage) {
      stage.classList.remove('is-held');
    }

    if (curtain && !curtain.hidden) {
      dismissCurtain();
    } else if (stage) {
      stage.classList.add('is-revealed', 'is-curtain-gone');
    }

    window.setTimeout(tryAutoPlay, 750);
  }

  function render() {
    if (payoffReady()) {
      revealPayoff();
      return;
    }
    updateCurtainSteps();
  }

  async function poll() {
    try {
      const res = await fetch(`/api/result/${uuid}`);
      if (!res.ok) return;
      result = await res.json();
      render();
      if (result.status === 'ready' || result.status === 'error' || payoffReady()) {
        clearInterval(pollTimer);
      }
    } catch (e) {
      console.warn('Result poll failed', e);
    }
  }

  if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
      const url = window.location.href;
      try {
        await navigator.clipboard.writeText(url);
        shareBtn.textContent = 'Copied!';
        setTimeout(() => { shareBtn.textContent = 'Copy link'; }, 2000);
      } catch {
        prompt('Copy this link:', url);
      }
    });
  }

  if (payoffReady()) {
    if (curtain) curtain.hidden = true;
    if (stage) {
      stage.classList.remove('is-held');
      stage.classList.add('is-revealed', 'is-curtain-gone');
    }
    revealPayoff();
  } else {
    render();
    pollTimer = setInterval(poll, 1500);
    poll();
  }
})();
