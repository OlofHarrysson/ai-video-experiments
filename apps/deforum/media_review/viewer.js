(function () {
  const root = document.getElementById('deforum-media-review');
  const data = JSON.parse(document.getElementById('deforum-review-data').textContent);
  const {frameAt, seekTime, paintingAt} = globalThis.MediaReviewTimeline;
  const find = selector => root.querySelector(selector);
  const stack = find('[data-stack]'), slider = find('[data-timeline]');
  const playButton = find('[data-action="play"]');
  const clips = new Map(data.clips.map(clip => [clip.id, clip]));
  let selected = [...data.selected], slots = [], cursor = 0, wanted = 0;
  let playing = false, seeking = false, generation = 0, raf = 0;
  let speed = 1, ready = false, lastCorrection = 0;
  let lifecycle = new AbortController();
  find('[data-quality]').textContent = data.quality;

  function fail(error) {
    pause(); ready = false; playButton.disabled = true;
    find('[data-error]').hidden = false;
    find('[data-error]').textContent = `Unable to review this media: ${error.message}`;
    find('[data-status]').textContent = 'Media error';
  }
  function pause() {
    playing = false; cancelAnimationFrame(raf);
    slots.forEach(slot => slot.video.pause());
    root.dataset.playing = 'false';
    playButton.textContent = 'Play all';
  }
  function master() { return slots[0].clip; }
  function textFor(clip, frame) {
    const item = clip.roles[frame];
    if (!item) return 'Video frame · painting metadata unavailable';
    if (item.kind === 'anchor') return `Painting ${item.source_index}`;
    if (item.kind === 'hold') return `Hold · painting ${item.source_index}`;
    if (item.kind === 'final_hold') return `Final hold · painting ${item.source_index}`;
    if (item.kind === 'warp') return `Spatial warp · painting ${item.source_index}`;
    return `In-between · paintings ${item.source_pair[0]} → ${item.source_pair[1]}`;
  }
  function updateReadouts(time, exact) {
    cursor = frameAt(master().times, time);
    slider.value = String(cursor);
    find('[data-position]').textContent = `frame ${cursor} / ${master().times.length - 1} · ${master().times[cursor].toFixed(3)} s`;
    slider.setAttribute('aria-valuetext', `Frame ${cursor}, ${master().times[cursor].toFixed(3)} seconds`);
    for (const slot of slots) {
      const frame = exact ? frameAt(slot.clip.times, time) : frameAt(slot.clip.times, slot.video.currentTime);
      slot.label.textContent = `Frame ${frame} · ${slot.clip.times[frame].toFixed(3)} s`;
      slot.kind.textContent = textFor(slot.clip, frame) + (time >= slot.clip.duration ? ' · clip ended' : '');
      slot.panel.dataset.frame = String(frame);
      if (slot.branch) slot.branch.href = `/branch?${new URLSearchParams({source:slot.clip.branch_source,frame})}`;
    }
    const anchors = master().anchors;
    find('[data-action="previous-painting"]').disabled = !ready || paintingAt(anchors, cursor, -1) === cursor;
    find('[data-action="next-painting"]').disabled = !ready || paintingAt(anchors, cursor, 1) === cursor;
    find('[data-action="previous"]').disabled = !ready || cursor === 0;
    find('[data-action="next"]').disabled = !ready || cursor === master().times.length - 1;
    root.dataset.frame = String(cursor);
    root.dataset.playing = String(playing);
  }
  function loaded(video, signal) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => done(new Error('Video loading timed out')), 20000);
      function done(error) {
        clearTimeout(timer); signal.removeEventListener('abort', onabort); video.removeEventListener('loadeddata', onload); video.removeEventListener('error', onerror);
        error ? reject(error) : resolve();
      }
      const onabort = () => done(new DOMException('Review changed', 'AbortError'));
      signal.addEventListener('abort', onabort, {once:true});
      const onload = () => done(), onerror = () => done(new Error('Video could not be decoded'));
      video.addEventListener('loadeddata', onload); video.addEventListener('error', onerror);
      if (video.readyState >= 2) done();
    });
  }
  function seek(slot, frame, signal) {
    const video = slot.video, time = seekTime(slot.clip, frame);
    if (!video.seeking && Math.abs(video.currentTime - time) < 1e-6) return Promise.resolve();
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => done(new Error('Frame seeking timed out')), 10000);
      function done(error) {
        clearTimeout(timer); signal.removeEventListener('abort', onabort); video.removeEventListener('seeked', onseek); video.removeEventListener('error', onerror);
        error ? reject(error) : resolve();
      }
      const onabort = () => done(new DOMException('Review changed', 'AbortError'));
      signal.addEventListener('abort', onabort, {once:true});
      const onseek = () => done(), onerror = () => done(new Error('Frame could not be decoded'));
      video.addEventListener('seeked', onseek); video.addEventListener('error', onerror);
      video.currentTime = time;
    });
  }
  async function drainSeeks() {
    if (seeking || !ready) return;
    seeking = true; playButton.disabled = true; root.dataset.state = 'seeking';
    const epoch = generation;
    try {
      while (epoch === generation) {
        const frame = wanted, time = master().times[frame];
        await Promise.all(slots.map(slot => seek(slot, frameAt(slot.clip.times, time), lifecycle.signal)));
        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
        if (epoch !== generation) return;
        updateReadouts(time, true);
        if (wanted === frame) break;
      }
    } catch (error) { if (epoch === generation) fail(error); }
    finally {
      seeking = false;
      if (epoch === generation && ready) {
        playButton.disabled = false; root.dataset.state = 'ready';
        find('[data-status]').textContent = 'Paused · controls apply to every video';
      } else if (ready) drainSeeks();
    }
  }
  function go(frame) {
    if (!ready) return;
    pause(); wanted = Math.max(0, Math.min(master().times.length - 1, frame));
    drainSeeks();
  }
  async function togglePlay() {
    if (!ready || seeking) return;
    const epoch = generation;
    if (playing) { go(frameAt(master().times, slots[0].video.currentTime)); return; }
    if (cursor === master().times.length - 1) { wanted = 0; await drainSeeks(); if (!ready) return; }
    try {
      playing = true; playButton.textContent = 'Pause all';
      slots.forEach(slot => { slot.video.playbackRate = speed; });
      await Promise.all(slots.filter(slot => master().times[cursor] < slot.clip.duration).map(slot => slot.video.play()));
      if (epoch !== generation || !playing) return;
      find('[data-status]').textContent = 'Playing · linked to the first video';
      raf = requestAnimationFrame(tick);
    } catch (error) { if (epoch === generation) fail(error); }
  }
  function tick(now) {
    if (!playing) return;
    const time = slots[0].video.currentTime;
    if (slots[0].video.ended || time >= master().duration - .005) { go(master().times.length - 1); return; }
    if (now - lastCorrection > 80) {
      for (const slot of slots.slice(1)) {
        const frame = frameAt(slot.clip.times, time);
        if (time >= slot.clip.duration) {
          slot.video.pause();
          if (frameAt(slot.clip.times, slot.video.currentTime) !== frame) slot.video.currentTime = seekTime(slot.clip, frame);
        } else if (Math.abs(slot.video.currentTime - time) > .025 && !slot.video.seeking) {
          slot.video.currentTime = time;
        }
      }
      lastCorrection = now;
    }
    updateReadouts(time, false); raf = requestAnimationFrame(tick);
  }
  async function rebuild(time = 0) {
    pause(); ready = false; generation += 1; const epoch = generation;
    lifecycle.abort(); lifecycle = new AbortController();
    const signal = lifecycle.signal;
    playButton.disabled = true; root.dataset.state = 'loading';
    find('[data-error]').hidden = true; find('[data-status]').textContent = 'Loading videos…';
    slots.forEach(slot => { slot.video.removeAttribute('src'); slot.video.load(); });
    stack.replaceChildren(); slots = [];
    selected.forEach((id, index) => {
      const clip = clips.get(id), panel = document.createElement('section');
      panel.dataset.clip = id; panel.setAttribute('aria-label', `Video ${index + 1}: ${clip.label}`);
      const heading = document.createElement('div'); heading.className = 'review-heading';
      const choice = document.createElement('label'); choice.className = 'form-label review-choice';
      choice.append(document.createTextNode(`Video ${index + 1}`));
      const select = document.createElement('select'); select.className = 'form-select'; select.setAttribute('aria-label', `Video ${index + 1}`);
      data.clips.forEach(item => select.add(new Option(item.label, item.id)));
      select.value = id; choice.append(select); heading.append(choice);
      const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'btn btn-ghost';
      remove.textContent = 'Remove'; remove.disabled = selected.length === 1; remove.setAttribute('aria-label', `Remove video ${index + 1}`);
      heading.append(remove); panel.append(heading);
      const caption = document.createElement('div'); caption.className = 'review-caption text-small';
      const brief = document.createElement('span'); brief.textContent = clip.note; caption.append(brief);
      if (clip.details) {
        const info = document.createElement('button'); info.type = 'button'; info.className = 'btn review-info';
        info.textContent = 'ⓘ'; info.setAttribute('aria-label', `Generation details for video ${index + 1}`);
        const details = document.createElement('div'); details.className = 'review-details';
        details.id = `review-details-${epoch}-${index}`; details.setAttribute('popover', 'auto');
        details.setAttribute('role', 'tooltip'); details.textContent = clip.details;
        info.setAttribute('aria-describedby', details.id);
        info.setAttribute('aria-expanded', 'false');
        let pinned = false, hideTimer;
        const hide = () => { if (!pinned && details.isConnected) details.hidePopover(); };
        const show = () => {
          clearTimeout(hideTimer);
          details.showPopover();
          const rect = info.getBoundingClientRect(), box = details.getBoundingClientRect();
          details.style.left = `${Math.max(12, Math.min(rect.left, innerWidth - box.width - 12))}px`;
          details.style.top = `${Math.max(12, Math.min(rect.bottom + 8, innerHeight - box.height - 12))}px`;
        };
        info.addEventListener('pointerenter', show);
        info.addEventListener('pointerleave', () => { hideTimer = setTimeout(hide, 150); });
        info.addEventListener('focus', show);
        info.addEventListener('blur', () => { pinned = false; hide(); });
        info.addEventListener('click', () => { pinned = !pinned; if (pinned) show(); else hide(); });
        details.addEventListener('pointerenter', () => clearTimeout(hideTimer));
        details.addEventListener('pointerleave', () => { hideTimer = setTimeout(hide, 150); });
        details.addEventListener('toggle', event => {
          info.setAttribute('aria-expanded', String(event.newState === 'open'));
          if (event.newState === 'closed') pinned = false;
        });
        caption.append(info, details);
      }
      panel.append(caption);
      const video = document.createElement('video'); video.muted = true; video.playsInline = true; video.preload = 'auto';
      video.setAttribute('aria-label', clip.label); video.src = clip.src; panel.append(video);
      const meta = document.createElement('div'); meta.className = 'review-meta text-small tabular-nums';
      const label = document.createElement('span'), kind = document.createElement('span'); meta.append(label, kind); panel.append(meta);
      let branch = null;
      if (clip.branch_source && ['localhost','127.0.0.1'].includes(location.hostname)) {
        branch = document.createElement('a'); branch.className = 'btn'; branch.textContent = 'Branch from here';
        branch.setAttribute('aria-label', `Plan a continuation from video ${index+1}`);
        branch.addEventListener('click', pause); meta.append(branch);
      }
      stack.append(panel); slots.push({clip, video, panel, label, kind, branch});
      if (video.requestVideoFrameCallback) {
        const presented = (_, metadata) => {
          if (epoch !== generation) return;
          panel.dataset.presentedFrame = String(frameAt(clip.times, metadata.mediaTime));
          video.requestVideoFrameCallback(presented);
        };
        video.requestVideoFrameCallback(presented);
      }
      select.addEventListener('change', () => { selected[index] = select.value; rebuild(master().times[cursor]).catch(fail); });
      remove.addEventListener('click', () => { const at = master().times[cursor]; selected.splice(index, 1); rebuild(at).catch(fail); });
    });
    find('[data-action="add"]').disabled = selected.length >= Math.min(3, data.clips.length);
    try { await Promise.all(slots.map(slot => loaded(slot.video, signal))); }
    catch (error) { if (epoch === generation) throw error; return; }
    if (epoch !== generation) return;
    ready = true; slider.max = String(master().times.length - 1);
    wanted = frameAt(master().times, time); updateReadouts(master().times[wanted], true);
    await drainSeeks();
  }
  slider.addEventListener('input', () => go(Number(slider.value)));
  find('[data-speed]').addEventListener('change', event => {
    speed = Number(event.target.value); slots.forEach(slot => { slot.video.playbackRate = speed; });
  });
  root.addEventListener('click', event => {
    if (!ready) return;
    const action = event.target.closest('[data-action]')?.dataset.action;
    if (action === 'play') togglePlay();
    else if (action === 'next') go((seeking ? wanted : cursor) + 1);
    else if (action === 'previous') go((seeking ? wanted : cursor) - 1);
    else if (action === 'next-painting') go(paintingAt(master().anchors, seeking ? wanted : cursor, 1));
    else if (action === 'previous-painting') go(paintingAt(master().anchors, seeking ? wanted : cursor, -1));
    else if (action === 'add') {
      const next = data.clips.find(clip => !selected.includes(clip.id));
      if (next && selected.length < 3) { const at = master().times[cursor]; selected.push(next.id); rebuild(at).catch(fail); }
    }
  });
  document.addEventListener('keydown', event => {
    if (!ready || event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey ||
        event.target.closest('input, select, textarea, button, a, [contenteditable]:not([contenteditable="false"]), [role="slider"], [role="textbox"]')) return;
    if (event.code === 'Space') { event.preventDefault(); togglePlay(); }
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault(); const direction = event.key === 'ArrowRight' ? 1 : -1;
      const frame = seeking ? wanted : cursor;
      go(event.shiftKey ? paintingAt(master().anchors, frame, direction) : frame + direction);
    }
  });
  document.addEventListener('visibilitychange', () => { if (document.hidden && playing) go(cursor); });
  rebuild().catch(fail);
})();
