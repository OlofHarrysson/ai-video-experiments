(function (scope) {
  function frameAt(times, seconds) {
    if (!times.length || !Number.isFinite(seconds)) throw new Error('Invalid video timeline');
    let lo = 0, hi = times.length;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (times[mid] <= seconds + 1e-7) lo = mid + 1;
      else hi = mid;
    }
    return Math.max(0, lo - 1);
  }
  function seekTime(clip, frame) {
    const start = clip.times[frame];
    const end = clip.times[frame + 1] ?? clip.duration;
    return start + (end - start) / 2;
  }
  function paintingAt(anchors, frame, direction) {
    return direction > 0
      ? (anchors.find(value => value > frame) ?? frame)
      : ([...anchors].reverse().find(value => value < frame) ?? frame);
  }
  const core = {frameAt, seekTime, paintingAt};
  if (typeof module !== 'undefined' && module.exports) module.exports = core;
  else scope.MediaReviewTimeline = core;
})(globalThis);
