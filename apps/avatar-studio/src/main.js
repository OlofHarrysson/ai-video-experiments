import './style.css';
import { createAvatar } from './avatar.js';

const SAMPLE = "Hello Olof. I'm a real three dimensional character. You can change my look, move the camera, and direct my performance. This is a sample voice. Your own voice can come next.";
const DEFAULTS = { skin: '#d89c79', hair: '#372820', shirt: '#456c64', eyes: '#568b8b', hairStyle: 'swept', glasses: false, headWidth: 1 };
const app = document.querySelector('#app');
app.innerHTML = `
  <header><a class="brand" href="/" aria-label="Character studio home"><span class="brand-mark">◉</span> Character studio</a><span class="header-note">A little room to become someone else.</span><span class="local"><i></i> Local studio</span></header>
  <main>
    <aside class="panel">
      <div class="panel-heading"><h1>Your character</h1><button id="reset" class="text-button">Reset</button></div>
      <p class="intro">Shape the look. Direct the performance.</p>
      <div class="preset-row" aria-label="Character presets"><button data-preset="studio" class="preset active">Studio</button><button data-preset="creative" class="preset">Creative</button><button data-preset="night" class="preset">Midnight</button></div>
      <section><h2>Appearance</h2>
        <div class="color-grid"><label>Skin<input type="color" id="skin" value="#d89c79"></label><label>Hair<input type="color" id="hair" value="#372820"></label><label>Clothes<input type="color" id="shirt" value="#456c64"></label><label>Eyes<input type="color" id="eyes" value="#568b8b"></label></div>
        <label class="field">Hair style<select id="hairStyle"><option value="swept">Swept</option><option value="crop">Short crop</option><option value="bald">No hair</option></select></label>
        <label class="range-label" for="headWidth">Face width</label><input type="range" id="headWidth" min="0.85" max="1.15" step="0.01" value="1">
        <label class="check"><input id="glasses" type="checkbox"><span>Round glasses</span></label>
      </section>
      <section><h2>Performance</h2><label class="range-label" for="expression">Expression <span>Neutral → Warm</span></label><input id="expression" type="range" min="0" max="1" step="0.01" value="0.45"><label class="range-label" for="gesture">Movement <span>Still → Animated</span></label><input id="gesture" type="range" min="0" max="1" step="0.01" value="0.45"></section>
      <details><summary>About this demo</summary><p>Real, editable 3D geometry. The character is a sample, not a likeness of Olof. Mouth movement follows audio energy; phoneme-accurate lip-sync and a cloned voice are next steps.</p><p>Appearance changes stay in your browser. Imported audio stays on this computer.</p></details>
      <button id="save-look" class="text-button save-look">Save look ↓</button>
    </aside>
    <div class="workspace">
      <section class="stage" aria-label="3D character preview">
        <canvas id="character" aria-label="Interactive 3D character. Drag to orbit and scroll to zoom."></canvas>
        <div class="stage-top"><span class="stage-label"><i></i> Live 3D</span><button id="camera" class="small-button">Reset camera ↺</button></div>
        <div class="stage-caption"><span id="character-name">The studio look</span><small>Drag to orbit · Scroll to zoom</small></div>
      </section>
      <section class="script-panel">
        <div class="script-heading"><h2>Give them something to say</h2><button id="sample" class="text-button">Load AI voice sample</button></div>
        <label for="script" class="sr-only">Script</label><textarea id="script" maxlength="1800" spellcheck="false">${SAMPLE}</textarea>
        <div class="voice-row"><label for="voice">Preview voice</label><select id="voice" aria-label="Preview voice"><option>Loading local voices…</option></select><label for="rate">Pace</label><input id="rate" type="range" min="110" max="230" value="170" step="5"><output id="rate-label">170 wpm</output><button id="generate" class="secondary">Voice this script</button></div>
        <div class="transport"><button id="play" class="primary" disabled>▶ Play</button><input id="timeline" aria-label="Playback position" type="range" min="0" max="100" step="0.1" value="0"><span id="time">0:00 / 0:00</span><button id="export" class="secondary" disabled>Export video ↓</button><label class="import-button" for="audio-file">Import audio<input type="file" id="audio-file" accept="audio/*"></label></div>
        <div class="status-row"><p id="status" role="status">Loading the Qwen AI voice sample…</p><span id="source">Sample voice · not Olof</span></div>
        <a id="download" hidden>Download video</a>
      </section>
    </div>
  </main><footer><span>Change the character. Keep the performance.</span><span>Prototype 01 · Made with Olof</span></footer>`;

const $ = id => document.getElementById(id);
const avatar = createAvatar($('character'));
let appearance = { ...DEFAULTS };
let context, analyser, streamDestination, buffer, player;
let playing = false, startedAt = 0, offset = 0, recording = false, recorder, captureStream;
let exportFailure = null;
let generating = false;
let audioLoading = false;
let localSpeechAvailable = false;
const spectrum = new Uint8Array(256);
let cachedEnergy = 0;
const status = (text, error = false) => { $('status').textContent = text; $('status').classList.toggle('error', error); };
const time = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
const presets = {
  studio: { ...DEFAULTS },
  creative: { ...DEFAULTS, skin: '#b77d59', hair: '#523032', shirt: '#aa6045', eyes: '#6e563b', hairStyle: 'crop', glasses: true },
  night: { ...DEFAULTS, skin: '#744e3b', hair: '#211e26', shirt: '#444b69', eyes: '#5a6a7d', hairStyle: 'bald', glasses: true },
};
function applyAppearance() {
  for (const [key, value] of Object.entries(appearance)) { if ($(key).type === 'checkbox') $(key).checked = value; else $(key).value = value; }
  avatar.updateAppearance(appearance);
}
for (const key of Object.keys(DEFAULTS)) $(key).addEventListener('input', () => {
  appearance[key] = $(key).type === 'checkbox' ? $(key).checked : $(key).type === 'range' ? Number($(key).value) : $(key).value;
  avatar.updateAppearance(appearance);
  document.querySelectorAll('.preset').forEach(b => b.classList.remove('active'));
  $('character-name').textContent = 'Your custom look';
});
document.querySelectorAll('[data-preset]').forEach(button => button.addEventListener('click', () => {
  appearance = { ...presets[button.dataset.preset] }; applyAppearance();
  document.querySelectorAll('.preset').forEach(b => b.classList.toggle('active', b === button));
  $('character-name').textContent = `The ${button.textContent.toLowerCase()} look`;
}));
$('reset').onclick = () => { document.querySelector('[data-preset="studio"]').click(); $('expression').value = .45; $('gesture').value = .45; avatar.setExpression(.45); avatar.setGesture(.45); avatar.resetCamera(); };
$('camera').onclick = () => avatar.resetCamera();
$('expression').oninput = () => avatar.setExpression(Number($('expression').value));
$('gesture').oninput = () => avatar.setGesture(Number($('gesture').value));
$('rate').oninput = () => { $('rate-label').textContent = `${$('rate').value} wpm`; };
function saveBlob(blob, name) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 30000);
}
$('save-look').onclick = () => saveBlob(new Blob([JSON.stringify({ appearance, expression: Number($('expression').value), movement: Number($('gesture').value) }, null, 2)], { type: 'application/json' }), 'character-look.json');

function ensureAudio() {
  if (!context) {
    context = new AudioContext();
    analyser = context.createAnalyser(); analyser.fftSize = 512; analyser.smoothingTimeConstant = .5;
    streamDestination = context.createMediaStreamDestination();
    analyser.connect(context.destination); analyser.connect(streamDestination);
  }
  return context;
}
function progress() { return playing ? Math.min(buffer.duration, context.currentTime - startedAt) : offset; }
function stopAudio(reset = false) {
  if (playing) offset = progress();
  playing = false;
  if (player) { player.onended = null; player.stop(); player.disconnect(); player = null; }
  if (reset) offset = 0;
  avatar.setSpeaking(false); avatar.setEnergy(0);
  $('play').textContent = '▶ Play';
}
function endRecording() { if (recorder?.state === 'recording') recorder.stop(); }
async function playAudio(from = offset) {
  if (!buffer) return;
  const ctx = ensureAudio(); await ctx.resume();
  stopAudio();
  offset = from >= buffer.duration - .02 ? 0 : from;
  player = ctx.createBufferSource(); player.buffer = buffer; player.connect(analyser);
  startedAt = ctx.currentTime - offset; playing = true; avatar.setSpeaking(true);
  player.onended = () => { playing = false; offset = 0; player?.disconnect(); player = null; avatar.setSpeaking(false); avatar.setEnergy(0); $('play').textContent = '▶ Play'; endRecording(); };
  player.start(0, offset); $('play').textContent = recording ? '■ Stop export' : 'Ⅱ Pause';
}
async function loadAudio(arrayBuffer, source, message) {
  stopAudio(true);
  buffer = await ensureAudio().decodeAudioData(arrayBuffer);
  $('download').hidden = true;
  $('play').disabled = false; $('export').disabled = false;
  $('timeline').value = 0; $('source').textContent = message;
  status(`Ready · ${buffer.duration.toFixed(1)} seconds`);
}
function beginAudioLoad() {
  if (recording || generating || audioLoading) return false;
  audioLoading = true; stopAudio(true); recordingControls(true); $('play').disabled = true;
  return true;
}
function finishAudioLoad() {
  audioLoading = false; recordingControls(false); $('play').disabled = !buffer; $('export').disabled = !buffer;
}
async function loadSample() {
  if (!beginAudioLoad()) return;
  try {
    const response = await fetch('/audio/sample.mp3');
    if (!response.ok) throw new Error('Sample audio is not installed yet. Generate a local voice or import audio.');
    await loadAudio(await response.arrayBuffer(), 'sample', 'Qwen · Aiden sample voice');
    $('script').value = SAMPLE;
  } catch (error) { status(error.message, true); }
  finally { finishAudioLoad(); }
}
$('sample').onclick = loadSample;
$('play').onclick = async () => {
  try { if (recording) { stopAudio(true); endRecording(); } else if (playing) stopAudio(); else await playAudio(); }
  catch (error) { status(error.message, true); }
};
$('timeline').oninput = async () => { if (!buffer || recording) return; const target = Number($('timeline').value) / 100 * buffer.duration; if (playing) await playAudio(target); else offset = target; };
$('script').oninput = () => { status('Script changed. Choose “Voice this script” to update the audio.'); };
$('generate').onclick = async () => {
  if (!beginAudioLoad()) return;
  stopAudio(true); generating = true; $('generate').disabled = true;
  status('Voicing your script on this Mac…');
  try {
    const response = await fetch('/api/speech', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: $('script').value, voice: $('voice').value, rate: Number($('rate').value) }) });
    if (!response.ok) throw new Error((await response.json()).error);
    await loadAudio(await response.arrayBuffer(), 'local', `Local voice · ${$('voice').value}`);
  } catch (error) { status(error.message, true); }
  finally { generating = false; finishAudioLoad(); }
};
$('audio-file').onchange = async event => {
  const file = event.target.files[0];
  if (!file || !beginAudioLoad()) return;
  try { await loadAudio(await file.arrayBuffer(), 'import', `Imported · ${file.name}`); status('Imported audio is ready. The script box does not change this recording.'); }
  catch { status('This audio could not be decoded. Try WAV, MP3 or M4A.', true); }
  finally { finishAudioLoad(); }
};
function recordingControls(locked) {
  for (const id of ['export','generate','sample','audio-file','timeline','voice','rate','script']) $(id).disabled = locked;
  if (!localSpeechAvailable) $('generate').disabled = true;
}
$('export').onclick = async () => {
  if (!buffer || recording || generating || audioLoading) return;
  try {
    ensureAudio(); await context.resume(); stopAudio(true);
    const mimeType = ['video/webm;codecs=vp9,opus', 'video/webm;codecs=vp8,opus', 'video/webm'].find(x => MediaRecorder.isTypeSupported(x));
    if (!mimeType) throw new Error('WebM recording is unavailable in this browser. Open the studio in Chrome.');
    captureStream = $('character').captureStream(30);
    const combined = new MediaStream([...captureStream.getVideoTracks(), ...streamDestination.stream.getAudioTracks()]);
    const chunks = [];
    recorder = new MediaRecorder(combined, { mimeType, videoBitsPerSecond: 6000000 });
    recorder.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
    recorder.onstop = async () => {
      captureStream.getTracks().forEach(track => track.stop());
      $('play').textContent = '▶ Play';
      if (exportFailure) { recording = false; recordingControls(false); status(exportFailure, true); return; }
      const blob = new Blob(chunks, { type: mimeType });
      try {
        status('Saving the finished video on this computer…');
        const response = await fetch('/api/export', { method: 'POST', headers: { 'Content-Type': mimeType }, body: blob });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error);
        $('download').href = result.url; $('download').download = 'character-performance.webm'; $('download').hidden = false;
        $('download').textContent = 'Download your video ↓'; $('download').title = result.path;
        status('Video saved on this computer. Ready to download.');
      } catch (error) { status(`Could not save video: ${error.message}`, true); }
      finally { recording = false; recordingControls(false); }
    };
    recorder.onerror = event => { exportFailure = `Recording failed: ${event.error?.message || 'unknown error'}`; status(exportFailure, true); stopAudio(); endRecording(); };
    exportFailure = null; $('download').hidden = true;
    recording = true; recordingControls(true); recorder.start(250);
    await playAudio(0); status('Recording your performance… keep this tab visible.');
  } catch (error) { exportFailure = error.message; recording = false; recordingControls(false); endRecording(); status(error.message, true); }
};

const resize = () => { const box = $('character').getBoundingClientRect(); avatar.resize(box.width, box.height); };
new ResizeObserver(resize).observe($('character'));
document.addEventListener('visibilitychange', () => {
  if (document.hidden && recording && recorder?.state === 'recording') { exportFailure = 'Export stopped because the tab was hidden. Keep it visible for a full take.'; stopAudio(true); endRecording(); status(exportFailure, true); }
});
function frame(ms) {
  let energy = 0;
  if (playing && analyser) {
    analyser.getByteTimeDomainData(spectrum);
    let sum = 0; for (const value of spectrum) sum += ((value - 128) / 128) ** 2;
    energy = Math.min(1, Math.max(0, (Math.sqrt(sum / spectrum.length) - .008) * 7));
  }
  cachedEnergy += (energy - cachedEnergy) * .45;
  avatar.setEnergy(cachedEnergy); avatar.render(ms / 1000);
  if (buffer) { const t = progress(); $('time').textContent = `${time(t)} / ${time(buffer.duration)}`; $('timeline').value = t / buffer.duration * 100; }
  requestAnimationFrame(frame);
}
applyAppearance(); avatar.setExpression(.45); avatar.setGesture(.45); requestAnimationFrame(frame);
fetch('/api/voices').then(async response => { if (!response.ok) throw new Error((await response.json()).error); return response.json(); }).then(voices => {
  $('voice').innerHTML = ''; voices.forEach(v => { const option = new Option(`${v.name} · ${v.language.replace('_','-')}`, v.name); $('voice').add(option); });
  if (voices.some(v => v.name === 'Daniel')) $('voice').value = 'Daniel';
  if (!voices.length) throw new Error('No supported local voices found. Use the sample or import audio.');
  localSpeechAvailable = true; $('generate').disabled = audioLoading || recording || generating;
}).catch(error => { $('generate').disabled = true; $('voice').innerHTML = '<option>Local speech unavailable</option>'; status(error.message, true); });
loadSample();
