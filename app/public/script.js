(() => {
  const $ = (sel) => document.querySelector(sel);
  const btnStart = $('#btn-start');
  const btnTalk = $('#btn-talk');
  const controls = $('#controls');
  const statusPill = $('#status-pill');
  const wordBox = $('#prompt-word');
  const userText = $('#user-text');
  const assistantText = $('#assistant-text');
  const assistantAudio = $('#assistant-audio');

  // State machine
  const State = Object.freeze({
    Idle: 'Idle',
    Ready: 'Ready',
    Recording: 'Recording',
    Processing: 'Processing',
    Speaking: 'Speaking'
  });
  let state = State.Idle;

  // Media
  let mediaStream = null;
  let mediaRecorder = null;
  let chunks = [];
  let spaceDown = false;

  function setStatus(next) {
    state = next;
    statusPill.textContent = next;
    statusPill.className = 'status-pill';
    if (next === State.Ready) statusPill.classList.add('status--ready');
    if (next === State.Recording) statusPill.classList.add('status--record');
    if (next === State.Processing) statusPill.classList.add('status--process');
    if (next === State.Speaking) statusPill.classList.add('status--speak');
  }

  async function ensureMic() {
    if (mediaStream) return mediaStream;
    mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    return mediaStream;
  }

  function setupRecorder() {
    if (!mediaStream) return null;
    const mr = new MediaRecorder(mediaStream, { mimeType: 'audio/webm' });
    chunks = [];

    mr.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunks.push(e.data);
    };

    mr.onstop = async () => {
      // Combine the chunks into a single blob
      const blob = new Blob(chunks, { type: 'audio/webm' });
      chunks = [];
      await handleUtterance(blob);
    };

    return mr;
  }

  function activateTalkButton(active) {
    btnTalk.disabled = !active;
    btnTalk.classList.toggle('active', active);
  }

  function setRecordingUI(on) {
    btnTalk.classList.toggle('recording', on);
  }

  // === Main flow ===
  btnStart.addEventListener('click', async () => {
    try {
      await ensureMic();
      mediaRecorder = setupRecorder();
      controls.hidden = false;
      activateTalkButton(true);
      setStatus(State.Ready);
      btnStart.textContent = 'Ready';
      // Focus body to capture SPACE easily
      window.focus();
    } catch (e) {
      setStatus('Mic blocked');
      console.error(e);
      alert('Microphone permission is required.');
    }
  });

  // Prevent page scroll when using SPACE
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space') e.preventDefault();
  }, { passive: false });

  // SPACE to start/stop recording
  window.addEventListener('keydown', async (e) => {
    if (e.code !== 'Space' || spaceDown || state !== State.Ready) return;
    spaceDown = true;
    try {
      if (!mediaRecorder) mediaRecorder = setupRecorder();
      mediaRecorder.start(100); // timeslice in ms (small chunks if you want streaming later)
      setRecordingUI(true);
      setStatus(State.Recording);
    } catch (err) {
      console.error(err);
    }
  });

  window.addEventListener('keyup', async (e) => {
    if (e.code !== 'Space' || !spaceDown) return;
    spaceDown = false;
    if (state === State.Recording && mediaRecorder && mediaRecorder.state !== 'inactive') {
      setRecordingUI(false);
      setStatus(State.Processing);
      mediaRecorder.stop();
    }
  });

  // Click on talk button (for users who prefer mouse)
  btnTalk.addEventListener('mousedown', async () => {
    if (state !== State.Ready) return;
    try {
      if (!mediaRecorder) mediaRecorder = setupRecorder();
      mediaRecorder.start(100);
      setRecordingUI(true);
      setStatus(State.Recording);
    } catch (e) { console.error(e); }
  });
  btnTalk.addEventListener('mouseup', async () => {
    if (state === State.Recording && mediaRecorder && mediaRecorder.state !== 'inactive') {
      setRecordingUI(false);
      setStatus(State.Processing);
      mediaRecorder.stop();
    }
  });
  btnTalk.addEventListener('mouseleave', async () => {
    // Safety: if mouse leaves while recording, also stop
    if (state === State.Recording && mediaRecorder && mediaRecorder.state !== 'inactive') {
      setRecordingUI(false);
      setStatus(State.Processing);
      mediaRecorder.stop();
    }
  });

  async function handleUtterance(blob) {
    try {
      userText.textContent = '…';
      assistantText.textContent = '…';

      // Build multipart form data: { audio: <blob> }
      const fd = new FormData();
      fd.append('audio', blob, 'utterance.webm');

      // Call your backend (implement this route)
      // Expected JSON: { topic, user_text, reply_text, audio_url }
      const res = await fetch('/api/speak', { method: 'POST', body: fd });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      // Update UI
      if (data.topic) wordBox.textContent = data.topic;
      if (data.user_text) userText.textContent = data.user_text;
      if (data.reply_text) assistantText.textContent = data.reply_text;

      // Optional TTS playback
      if (data.audio_url) {
        setStatus(State.Speaking);
        assistantAudio.src = data.audio_url;
        await assistantAudio.play().catch(() => {});
        // When audio ends, go back to Ready
        assistantAudio.onended = () => setStatus(State.Ready);
      } else {
        setStatus(State.Ready);
      }
    } catch (err) {
      console.error(err);
      assistantText.textContent = 'There was a problem. Please try again.';
      setStatus(State.Ready);
    }
  }
})();
