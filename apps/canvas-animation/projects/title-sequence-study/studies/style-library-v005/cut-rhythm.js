/* Timing experiment: a 120 BPM visual pulse, medium to medium-high activity. */
window.TypeCut = (() => {
  const FPS = 24, BPM = 120, shots = [];
  const bars = [
    [['tube',2,12],['tube',0,12],['tube',1,6],['tube',2,6],['interlock',0,12]],
    [['signature',0,12],['signature',3,12],['signature',1,12],['signature',2,12]],
    [['marquee',0,12],['marquee',2,6],['marquee',0,6],['palace',0,12],['palace',2,12]],
    [['depth',0,12],['depth',3,12],['overprint',2,12],['overprint',0,12]],
    [['interlock',2,12],['interlock',0,6],['interlock',3,6],['signature',3,12],['signature',0,12]],
    [['pinboard',2,12],['slats',2,12],['wire',1,12],['monument',0,12]],
    [['nightwall',0,12],['nightwall',2,6],['nightwall',3,6],['palace',0,12],['palace',2,6],['palace',0,6]],
    [['overprint',0,12],['overprint',3,6],['overprint',2,6],['monolith',2,12],['modular',1,6],['ribbon',0,6]],
    [['breakout',0,12],['breakout',3,6],['depth',0,6],['orbital',1,12],['wingline',2,6],['relic',2,6]],
    [['marquee',2,12],['marquee',0,6],['marquee',3,6],['tube',2,12],['tube',0,6],['tube',3,6]],
    [['triplicate',0,12],['triplicate',2,6],['nightwall',2,6],['stack',0,12],['monument',0,6],['softmetal',0,6]],
    [['interlock',0,12],['signature',0,6],['signature',3,6],['palace',0,12],['interlock',2,6],['interlock',0,6]],
  ];
  const layouts = new Set(TypeCompositions.cards.map(card => card.id));
  let cursor = 0;
  bars.forEach((bar, index) => {
    if (bar.reduce((sum, shot) => sum + shot[2], 0) !== 48) throw new Error('Bar must last four beats');
    for (const [id, state, frames] of bar) {
      const previous = shots.at(-1);
      const nativeOffset = previous?.id === id ? previous.nativeOffset + previous.frames : 0;
      shots.push({id, state, frames, composition: layouts.has(id), nativeOffset,
        bar: index + 1, phase: index < 6 ? 'medium' : 'medium-high', start: cursor, end: cursor + frames});
      cursor += frames;
    }
  });
  function render(frame, target, {label = false} = {}) {
    const f = Math.max(0, Math.min(cursor - 1, Math.floor(frame)));
    const shot = shots.find(shot => f >= shot.start && f < shot.end);
    const g = target.getContext('2d'), art = TypeLibrary.canvas();
    const local = f - shot.start + shot.nativeOffset;
    g.fillStyle = '#030305'; g.fillRect(0, 0, target.width, target.height);
    if (shot.composition) TypeCompositions.render(shot.id, shot.state, local, art);
    else TypeLibrary.render(shot.id, null, shot.state, local, art);
    g.drawImage(art, 0, 0);
    if (label) {
      g.fillStyle = '#17171b'; g.fillRect(0, 720, 1280, 48);
      g.font = '17px system-ui'; g.fillStyle = '#eee';
      g.fillText(`${(f/FPS).toFixed(2)} s · ${shot.id} · ${shot.frames} frames · bar ${shot.bar}`, 20, 752);
    }
    return shot;
  }
  return {FPS, BPM, shots, frames: cursor, duration: cursor / FPS, render};
})();
