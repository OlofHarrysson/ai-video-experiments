const {test} = require('node:test');
const assert = require('node:assert/strict');
const {frameAt,seekTime,paintingAt} = require('./timeline.js');
test('fractional and variable frame times: exact edges, bounds, and seek midpoints', () => {
  const clip = {times:[0,.041708,.09,.16], duration:.20};
  for (let n=0;n<clip.times.length;n++) {
    assert.equal(frameAt(clip.times,clip.times[n]),n);
    assert.equal(frameAt(clip.times,seekTime(clip,n)),n);
  }
  assert.equal(frameAt(clip.times,.089),1);
  assert.equal(frameAt(clip.times,-1),0);
  assert.equal(frameAt(clip.times,12),3);
  assert.throws(()=>frameAt([],0));
  assert.throws(()=>frameAt([0],NaN));
});
test('painting navigation uses recorded anchors and handles endpoints',()=>{
  const anchors=[0,12,36,50];
  assert.equal(paintingAt(anchors,12,1),36);
  assert.equal(paintingAt(anchors,35,-1),12);
  assert.equal(paintingAt(anchors,0,-1),0);
  assert.equal(paintingAt(anchors,55,1),55);
  assert.equal(paintingAt([],4,1),4);
});
