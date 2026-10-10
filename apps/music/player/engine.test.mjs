import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Mixer} from './engine.js';
function setup(resume=async()=>{}) {
  const sources=[];
  const context={currentTime:10,destination:{},resume,createGain(){return {gain:{value:0,cancelScheduledValues(){},setTargetAtTime(value){this.value=value;}},connect(){},disconnect(){}};},createBufferSource(){const node={connect(){},disconnect(){},start(...args){this.startArgs=args;},stop(){this.stopped=true;}};sources.push(node);return node;}};
  const mixer=new Mixer(context,30);mixer.buffers={bass:{},chord:{}};
  return {context,mixer,sources};
}
test('parts start at one shared clock/offset; mute and solo never restart them',async()=>{
  const {mixer,context,sources}=setup();mixer.offset=7.5;await mixer.play();
  assert.deepEqual(sources.map(s=>s.startArgs),[[10.04,7.5],[10.04,7.5]]);
  context.currentTime=13.04;const position=mixer.position();
  mixer.mute('chord');assert.equal(mixer.nodes[1].gain.gain.value,0);
  mixer.isolate('chord');assert.equal(mixer.nodes[0].gain.gain.value,0);assert.equal(mixer.nodes[1].gain.gain.value,1);
  assert.equal(mixer.position(),position);assert.equal(sources.length,2);
  mixer.reset();assert.ok(mixer.nodes.every(n=>n.gain.gain.value===1));
});
test('seek stops old voices and retains position across pause',async()=>{
  const {mixer,context,sources}=setup();await mixer.play();context.currentTime=12.04;
  await mixer.seek(21);assert.ok(sources.slice(0,2).every(s=>s.stopped));
  assert.ok(sources.slice(2).every(s=>s.startArgs[1]===21));
  context.currentTime=13.08;mixer.pause();assert.ok(Math.abs(mixer.offset-22)<1e-8);
});
test('a pause cancels a pending play',async()=>{
  let resolve;const {mixer,sources}=setup(()=>new Promise(r=>resolve=r));
  const pending=mixer.play();mixer.pause();resolve();await pending;assert.equal(sources.length,0);
});
test('loop position wraps and switching loop mode keeps the playhead',async()=>{
  const {mixer,context}=setup();await mixer.play();context.currentTime=42.04;
  assert.ok(Math.abs(mixer.position()-2)<1e-8);mixer.setLoop(false);assert.ok(Math.abs(mixer.position()-2)<1e-8);
  context.currentTime=80;assert.equal(mixer.position(),30);
});

test('seeking to the end stops playback instead of jumping back to the beginning',async()=>{
 const {mixer,sources}=setup();await mixer.play();mixer.setLoop(false);await mixer.seek(30);
 assert.equal(mixer.playing,false);assert.equal(mixer.position(),30);assert.equal(sources.length,2);
});
