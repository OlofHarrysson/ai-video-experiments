import { createAvatar } from './avatar.js';
import { motionPose } from './motion-sequence.js';

const DURATION = 8;
const canvas = document.querySelector('#motion');
const button = document.querySelector('#record');
const status = document.querySelector('#status');
const download = document.querySelector('#download');
const avatar = createAvatar(canvas);
avatar.renderer.setPixelRatio(1);
avatar.resize(1280, 960);
avatar.camera.position.set(0, 2.4, 7.3);
avatar.updateAppearance({skin:'#b77d59',hair:'#523032',shirt:'#aa6045',eyes:'#6e563b',hairStyle:'crop',glasses:true,headWidth:1});
avatar.setExpression(.45);
avatar.setGesture(0);
avatar.setSpeaking(false);
avatar.render(0, motionPose(0));
let recording = false;
let recorder;
let failure;
button.onclick = async () => {
  if (recording) return;
  recording = true; failure = null; button.disabled = true; download.hidden = true;
  const chunks = [];
  const stream = canvas.captureStream(30);
  try {
    const mimeType = ['video/webm;codecs=vp9','video/webm;codecs=vp8'].find(type => MediaRecorder.isTypeSupported(type));
    if (!mimeType) throw new Error('WebM recording unavailable.');
    recorder = new MediaRecorder(stream, {mimeType,videoBitsPerSecond:6000000});
    recorder.ondataavailable = event => { if(event.data.size) chunks.push(event.data); };
    recorder.onerror = event => { failure = event.error?.message || 'Recording failed.'; };
    recorder.onstop = async () => {
      stream.getTracks().forEach(track => track.stop());
      try {
        if (failure) throw new Error(failure);
        status.textContent = 'Saving source…';
        const response = await fetch('/api/export',{method:'POST',headers:{'Content-Type':mimeType},body:new Blob(chunks,{type:mimeType})});
        const saved = await response.json();
        if (!response.ok) throw new Error(saved.error);
        download.href = saved.url; download.title = saved.path; download.hidden = false;
        status.textContent = `Source saved: ${saved.path}`;
      } catch(error) { status.textContent = `Failed: ${error.message}`; }
      finally { recording = false; button.disabled = false; }
    };
    avatar.render(0, motionPose(0));
    recorder.start(250);
    const start = performance.now();
    function frame(now) {
      const t = Math.min((now-start)/1000,DURATION);
      avatar.render(t,motionPose(t));
      status.textContent = `Rendering ${t.toFixed(1)} / ${DURATION} seconds`;
      if (t < DURATION && !failure) requestAnimationFrame(frame);
      else recorder.stop();
    }
    requestAnimationFrame(frame);
  } catch(error) {
    stream.getTracks().forEach(track => track.stop());
    recording = false; button.disabled = false; status.textContent = `Failed: ${error.message}`;
  }
};
document.addEventListener('visibilitychange',()=>{if(document.hidden&&recording)failure='Recording interrupted because the tab was hidden.';});
