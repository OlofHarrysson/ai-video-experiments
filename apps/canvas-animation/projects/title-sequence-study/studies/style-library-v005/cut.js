/* Silent escalation study. Each shot owns its geometry; no full-card camera motion. */
window.TypeCut = (() => {
  const FPS = 24;
  const shots = [];
  const add = (id, state, frames, options = {}) => shots.push({ id, state, frames, ...options });
  const card = (id, state, frames, options = {}) => add(id, state, frames, { composition: true, ...options });

  // Space and one quiet object before a larger, physically different sign arrives.
  card('whisper', 0, 42, { phase: 'space' });
  add(null, 0, 8);
  add('tube', 0, 36, { phase: 'one sign' });
  add('tube', 1, 6);
  add('tube', 2, 24, { nativeOffset: 36 });
  add('tube', 0, 8);
  add('tube', 3, 8);
  card('interlock', 0, 32, { phase: 'hierarchy' });
  card('interlock', 1, 8);
  card('interlock', 2, 8);
  card('interlock', 3, 8);
  card('signature', 0, 24, { phase: 'brush silhouette' });
  card('signature', 2, 8);
  card('signature', 3, 16);
  add(null, 0, 4);

  // Longer native movements alternate with material edits and flat printed shapes.
  add('marquee', 0, 20, { phase: 'construction changes' });
  add('marquee', 2, 12, { nativeOffset: 20 });
  add('overprint', 2, 12);
  add('overprint', 0, 8);
  card('breakout', 0, 20);
  card('breakout', 3, 8, { nativeOffset: 20 });
  add('softmetal', 0, 12);
  add('palace', 0, 16);
  add('palace', 2, 8);
  add('wire', 1, 10);
  card('monument', 0, 10);
  add('slats', 1, 8);
  add('ribbon', 0, 8);
  add('relic', 2, 8);
  add('pinboard', 1, 8);
  card('nightwall', 0, 16, { phase: 'density' });
  card('nightwall', 2, 8, { nativeOffset: 16 });
  card('triplicate', 0, 12);
  card('triplicate', 2, 8);

  // The burst uses different silhouettes and scales, with black as an active beat.
  for (const [id, state] of [
    ['monolith', 2], ['orbital', 1], ['slats', 2], ['marquee', 2],
    ['overprint', 0], ['tube', 2], ['ribbon', 3], ['depth', 3],
    ['stack', 0], ['modular', 1], ['relic', 2], ['wingline', 2]
  ]) add(id, state, 4, { phase: 'burst' });
  add(null, 0, 4);
  card('monument', 2, 4);
  card('breakout', 1, 4);
  card('nightwall', 3, 4);
  card('interlock', 0, 4);
  for (const [id, state] of [
    ['depth', 0], ['slats', 1], ['palace', 2], ['overprint', 3],
    ['pinboard', 3], ['stack', 1], ['modular', 1], ['tube', 0],
    ['marquee', 3], ['ribbon', 2], ['chrome', 3], ['monolith', 0]
  ]) add(id, state, 2, { phase: 'peak' });
  add(null, 0, 12, { phase: 'release' });
  card('whisper', 0, 42);
  add(null, 0, 12);

  let cursor = 0;
  for (const shot of shots) {
    shot.start = cursor;
    cursor += shot.frames;
    shot.end = cursor;
  }

  function render(frame, target, { label = false } = {}) {
    const f = Math.max(0, Math.min(cursor - 1, Math.floor(frame)));
    const shot = shots.find(x => f >= x.start && f < x.end);
    const g = target.getContext('2d');
    g.fillStyle = '#030305';
    g.fillRect(0, 0, target.width, target.height);
    const local = f - shot.start + (shot.nativeOffset || 0);
    if (shot.id) {
      const art = TypeLibrary.canvas();
      if (shot.composition) TypeCompositions.render(shot.id, shot.state, local, art);
      else TypeLibrary.render(shot.id, shot.word || null, shot.state, local, art);
      g.drawImage(art, 0, 0);
    }
    if (label) {
      g.fillStyle = '#17171b';
      g.fillRect(0, 720, 1280, 48);
      g.font = '17px system-ui';
      g.fillStyle = '#eee';
      g.fillText(`${(f / FPS).toFixed(2)} s · ${shot.id || 'black pause'} · ${shot.frames} frames`, 20, 752);
    }
    return shot;
  }
  return { FPS, shots, frames: cursor, duration: cursor / FPS, render };
})();
