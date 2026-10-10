import assert from 'node:assert/strict';
import {mkdir} from 'node:fs/promises';
import {chromium} from 'playwright-core';
import {measurePage} from '../../tools/design-harness/modules/geometry/observe.mjs';
import {writeEvidence} from '../../tools/design-harness/modules/core/evidence.mjs';

const phase = process.argv[2] || 'after';
assert.ok(['before','after'].includes(phase));
const url = process.env.PLAYER_URL || 'http://localhost:3046/';
const output = `player/design/evidence/${phase}`;
await mkdir(output,{recursive:true});
const browser = await chromium.launch({channel:'chrome',headless:true});
try {
  for (const [name,viewport] of Object.entries({desktop:{width:1100,height:850},mobile:{width:390,height:844}})) {
    const page = await browser.newPage({viewport});
    const issues=[];
    page.on('pageerror',e=>issues.push(e.message));
    page.on('console',m=>{if(m.type()==='error' && !(phase==='before' && m.location().url.endsWith('/favicon.ico')))issues.push(m.text());});
    await page.goto(url);
    await page.getByRole('button',{name:'Play',exact:true}).waitFor();
    await page.waitForFunction(()=>!document.querySelector('#play').disabled);
    const legacy=await page.locator('#palette').count()>0;
    assert.equal(await page.locator('.track').count(),legacy?8:9);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    if(phase==='after') {
      assert.equal(await page.locator('textarea, #save, .feedback, #palette').count(),0);
      await page.getByRole('button',{name:'Only Bass',exact:true}).click();
      await page.getByRole('button',{name:'Only Chords · steady rhythm',exact:true}).click();
      assert.equal(await page.locator('.solo[aria-pressed=true]').count(),1);
      assert.equal(await page.locator('.track:not(.silent)').count(),1);
      assert.equal(await page.locator('[data-track=chords-flow].silent').count(),0);
      await page.getByRole('button',{name:'Only Chords · steady rhythm',exact:true}).click();
      assert.equal(await page.locator('.track:not(.silent)').count(),8);
      await page.getByRole('switch',{name:'Sound on/off Bass',exact:true}).click();
      assert.equal(await page.locator('[data-track=bass].silent').count(),1);
      await page.getByRole('button',{name:'Only Bass',exact:true}).click();
      assert.equal(await page.locator('[data-track=bass].silent').count(),0);
      await page.getByRole('button',{name:'Only Bass',exact:true}).click();
      assert.equal(await page.locator('[data-track=bass].silent').count(),1);
      await page.getByRole('button',{name:'Reset mix',exact:true}).click();
      await page.getByRole('button',{name:'Play',exact:true}).click();
      await page.waitForFunction(()=>Number(document.querySelector('#seek').value)>.15);
      await page.getByRole('button',{name:'Pause',exact:true}).click();
      // Human switches select alternative rows without restarting any audio.
      const position=Number(await page.locator('#seek').inputValue());
      await page.getByRole('switch',{name:'Sound on/off Chords · original rhythm',exact:true}).click();
      assert.equal(await page.locator('[data-track=chords-flow].silent').count(),1);
      assert.equal(await page.locator('[data-track=chords-original].silent').count(),0);
      assert.ok(Math.abs(Number(await page.locator('#seek').inputValue())-position)<.1);
      // Send a real agent command and wait for the browser's acknowledgement.
      async function control(command) {
        for(let n=0;n<40;n++){const s=await page.request.get(url+'/api/state').then(r=>r.json());if(s.connected)break;await new Promise(r=>setTimeout(r,100));}
        const r=await page.request.post(url+'/api/control',{data:command});
        assert.equal(r.status(),202);
        const {queued}=await r.json();
        let actual;
        for(let n=0;n<40;n++){actual=await page.request.get(url+'/api/state').then(r=>r.json());if(actual.last_applied_command>=queued)break;await new Promise(r=>setTimeout(r,100));}
        assert.ok(actual.last_applied_command>=queued,'Browser acknowledged command');
        assert.equal(actual.state.error,null);
        return actual.state;
      }
      let state=await control({action:'only',track:'chords-original'});
      assert.equal(state.only,'chords-original');
      assert.deepEqual(state.tracks.filter(t=>t.audible).map(t=>t.id),['chords-original']);
      state=await control({action:'only',track:'bass'});
      assert.deepEqual(state.tracks.filter(t=>t.audible).map(t=>t.id),['bass']);
      state=await control({action:'seek',value:7.5});assert.equal(state.time,7.5);
      state=await control({action:'volume',value:.4});assert.equal(state.volume,.4);
      state=await control({action:'loop',value:false});assert.equal(state.loop,false);
      state=await control({action:'play'});assert.equal(state.playing,true);
      state=await control({action:'pause'});assert.equal(state.playing,false);
      state=await control({action:'enabled',track:'chords-flow',value:true});
      assert.equal(state.only,null);assert.equal(state.tracks.find(t=>t.id==='chords-original').enabled,false);
      await control({action:'reset'});await control({action:'volume',value:.8});await control({action:'loop',value:true});
      await page.getByRole('button',{name:'Restart',exact:true}).click();
    }
    const observation=await measurePage(page,{id:'player',root:'main',regions:[
      {id:'heading',selector:'header',role:'heading'},
      {id:'transport',selector:'.transport',role:'controls'},
      {id:'tracks',selector:'#tracks',role:'content'},
      {id:'chords',selector:legacy?'[data-track=chords]':'[data-track=chords-flow]',role:'track'},
    ],relationships:[]});
    assert.deepEqual(issues,[]);
    for(const [view,crop] of [['context',undefined],['detail',legacy?'[data-track=chords]':'[data-track=chords-flow]']]) {
      const report=await writeEvidence(page,{basePath:`${output}/${name}-${view}`,identity:{target:'player',state:'paused',viewport:name},observation,issues,crop});
      assert.equal(report.status,'complete');
    }
    console.log(`${phase} ${name}: controls, viewport and evidence passed`);
    await page.close();
  }
} finally {await browser.close();}
