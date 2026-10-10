# Strudel operating guide

Use [Strudel](https://strudel.cc/) to compose and edit music through code in the Codex internal browser. Start with this guide; search the local documentation when a less familiar function is needed.

Reviewed 2026-10-10: all 46 English documentation pages in the main navigation, plus the linked Vim guide. The [source index](sources/README.md) links each official page and its local text snapshot, including embedded MiniREPL examples. This covers the workshop, sound generation, effects, pattern functions, musical concepts, integrations, and development manual. Blog posts, showcase videos, translations, external documentation, and every entry in the REPL's separate function reference are outside this reading scope.

## Open and operate

1. Open `https://strudel.cc/` with `cua.createBrowserTab("iab", url, {visible:true})`, or reuse its existing tab.
2. Inspect the current editor before replacing anything. Preserve existing user code first.
3. Focus the code editor, select all with `super+a`, and paste the replacement. Read back the editor before playing. **AX `setValue` did not update CodeMirror in the tested session; focus/select/paste worked.**
4. Click **play**. After changing a running pattern, click **update**. Click **stop** to halt playback. Buttons were verified; documented keyboard shortcuts include Ctrl+Enter to evaluate.
5. Open **menu → console** to check evaluation errors and sample loading. **sounds** lists the available samples and synths; **reference** searches functions.
6. Save the evaluated source to a `.strudel` text file. The address-bar fragment contains the evaluated code; keep that full URL as a reopening shortcut. A short **share** URL depends on Strudel's database, so the local source is the durable copy.
7. Keep the user-facing browser tab with `markDeliverable()`. Leave playback stopped at handoff unless continuous playback is wanted.

Use fresh accessibility state after interactions; numeric element IDs are session-specific. Do not manipulate private editor or audio-engine internals to operate the app.

## The essential model

- A **pattern** describes events over time and repeats indefinitely. Strudel calls events **haps**.
- A **cycle** has a fixed duration. Adding more space-separated events makes them fit into the same cycle, so they happen faster.
- For one four-beat bar per cycle, use `setcpm(BPM/4)`. At 96 BPM, `setcpm(96/4)` gives 2.5 seconds per cycle. Four cycles take 10 seconds.
- Use `$:` before each independent layer, or combine layers with `stack(a,b,c)`. Prefix a label with `_` to mute it, e.g. `_$:`.
- Double quotes and backticks support mini-notation in the REPL. Single quotes are ordinary strings. Backticks allow multiline patterns.
- Chained parameter functions usually preserve the rhythm on the left: `note("c3 e3 g3").s("triangle")` has three notes; putting a single sound event first can change the result. Use `struct` to supply an explicit rhythm.

Sources: [cycles](https://strudel.cc/understand/cycles/), [syntax](https://strudel.cc/learn/code/), [alignment](https://strudel.cc/technical-manual/alignment/).

## Mini-notation cheatsheet

| Syntax | Meaning | Example |
|---|---|---|
| spaces | Divide the available time equally | `s("bd hh sd hh")` |
| `~` or `-` | Rest | `s("bd ~ sd ~")` |
| `[a b]` | Subdivide one slot | `s("bd [hh hh] sd hh")` |
| `<a b>` | Alternate across cycles | `s("bd <sd cp>")` |
| `*n` | Speed up/repeat inside the slot | `s("hh*8")` |
| `/n` | Slow across more cycles | `note("[c3 e3 g3]/2")` |
| comma | Simultaneous events | `note("[c3,eb3,g3]")` |
| `@n` | Give an event relative duration weight | `note("c3@3 g3")` |
| `!n` | Replicate an element in its sequence | `note("<c3!3 g3>")` |
| `:n` | Sample index; also separates multi-value parameters | `s("hh:1")` |
| `(pulses,steps,rotation)` | Euclidean rhythm; rotation optional | `s("bd(3,8)")` |
| `?p` | Probability of removing the event | `s("hh*8?0.2")` |
| `a \| b` | Random choice per cycle | `s("bd \| rim")` |

Reference: [mini-notation](https://strudel.cc/learn/mini-notation/).

## Sounds, notes and mixing

- `s` and `sound` are aliases. Drum names include `bd` kick, `sd` snare, `cp` clap, `hh` closed hat, `oh` open hat, and `rim` rimshot. `.bank("RolandTR909")` selects a drum machine.
- `note("c2 eb2 g2")` sets pitches; MIDI numbers work too. `n` is an index, **not** an alias of `note`: it can choose a sample or, with `.scale("C4:minor")`, a scale degree.
- Built-in synths include `sine`, `triangle`, `sawtooth`, and `square`. Synths avoid external instrument-sample dependencies.
- `.gain(.3)` changes level; `.pan(.2)` places sound toward the left; `.lpf(800)` softens high frequencies. Start with modest gains and preserve headroom when stacking voices.
- `.attack(.01).decay(.2).sustain(.1).release(.1)` shapes amplitude. Attack, decay, release are seconds; sustain is a level. `.clip(.5)` shortens an event relative to its duration.
- `.room(.3)` sends to reverb. `.delay(.25)` sets delay level, **not delay time**; `.delaytime(.3125)` is seconds. At 96 BPM, .3125 seconds is an eighth note. Keep feedback below 1.
- Global reverb/delay settings are shared by **orbit**. Give layers distinct `.orbit(2)` / `.orbit(3)` values if they need independent settings.
- Standard audio effects follow the engine's signal-chain order. Repeating `.lpf(...)` overrides its earlier value; it does not create a second filter.

Sources: [samples](https://strudel.cc/learn/samples/), [synths](https://strudel.cc/learn/synths/), [effects](https://strudel.cc/learn/effects/).

## Variation and arrangement

| Goal | Tools |
|---|---|
| Change timing | `.fast(2)`, `.slow(2)`, `.early(1/8)`, `.late(1/8)` |
| Add a little swing | `.swingBy(.12,4)` on eighth-note hats |
| Transform a phrase | `.rev()`, `.palindrome()`, `.ply(2)` |
| Add a periodic fill | `.lastOf(4, x => x.ply(2))` |
| Remove occasional hits | `.degradeBy(.15)` |
| Gate a layer | `.mask("<0 1 1 1>")` |
| Set an onset pattern | `.struct("x ~ ~ x ~ x ~ ~")` |
| Sequence sections | `arrange([4, intro], [8, main], [4, outro])` — also repeats |
| Layer modified copies | `.superimpose(...)`, `.layer(...)`, `.off(1/8, ...)` |
| Automate per event | `.lpf(sine.range(400,2000).slow(8))` |
| Modulate during held notes | `.lfo({control:'lpf', rate:2, depth:.5})` — verify current support |
| Automatic chord voicings | `chord("<Cm7 AbM7 EbM7 Bb7>").voicing()` |
| See events or audio | `.punchcard()`, `._punchcard()`, `._scope()` |

Signals supplied to normal pattern parameters are generally sampled at event time. They do not necessarily modulate a held note continuously; the dedicated LFO and envelopes serve that purpose. `n(...).scale(...)` is usually the simplest way to keep a melody in key.

For sample manipulation, look up `cut`, `begin/end`, `loopAt`, `fit`, `chop`, `slice`, and `splice`. For precise composition, distinguish `pick`, `pickRestart`, and `pickSqueeze`; they preserve, restart, or squeeze selected patterns differently.

## Export audio

Verified procedure:

1. Evaluate the finished code and allow its samples to load.
2. Open **menu → export**. Set a filename, start cycle, end cycle, and sample rate.
3. Turn **Multi Channel Orbits** off for a normal stereo mix. The tested UI initially had it on.
4. Set cycles **0 to 8** and **48000 Hz** for a 20-second render at 96 BPM / four beats per cycle.
5. Start a browser download wait, then click **Export to WAV**. Save the returned file in the workspace. Export stopped live playback in the tested session.
6. Verify duration, channel count, and non-silent signal. The chosen cycle range is a hard endpoint; allow for effect tails when making a finished track.

The [FAQ](https://strudel.cc/learn/faq/) documents WAV export. The exact controls above were inspected in the live app.

## Samples, integrations and less common features

- Custom samples: `samples({...}, baseURL)` or a hosted `strudel.json`. Local **sounds → import-sounds → import sounds folder** keeps imported sounds in the browser. Do not upload private samples just to use them.
- Offline: the app can be cached, but samples are loaded on demand. Test the specific sounds offline before depending on them.
- MIDI can sequence external software/hardware; OSC/SuperDirt needs additional setup. MQTT sends patterned messages. These are optional and were not configured here.
- Hydra supplies visuals; CSound supplies an alternative synthesis engine with documented integration limits. Gamepads and motion sensors can control parameters.
- Mondo is an alternative syntax. Stepwise functions and xenharmonic tuning are marked experimental in the docs; consult their snapshots before use.
- For embedding, the manual distinguishes iframe/embed, `@strudel/repl`, and UI-free `@strudel/web`. Read the project's license before building an integration; this guide is about operating the existing app.

## Troubleshooting and documentation drift

- No sound: check **play/stop**, the console, gains/mutes, and whether samples finished downloading. A running UI alone does not prove speaker output.
- Missing sound: check **sounds** and the selected bank; not all drum machines contain every drum type.
- Wrong rhythm: check `[]` versus `<>`, the number of beats assigned to a cycle, and which pattern supplies the event structure.
- Missing function: search **reference**. Artist-specific functions may come from external scripts; do not assume they are built in.
- Some older pages still describe a default of one cycle/second or no local sample import. The current workshop says 0.5 cycles/second, and the current samples page documents folder import. Set tempo explicitly rather than inheriting it.
- For unfamiliar or experimental behavior, verify against the current app and official source. Some dynamically supplied reference descriptions may be absent from the text snapshots; the app's **reference** tab remains the lookup path.

## First beat and verification

**Window Seat** is a four-bar groove at 96 BPM: TR-909 drums, lightly swung hats, a filtered bass, soft triangle chords, and a delayed sine melody.

- [Editable code](beats/window-seat.strudel)
- [20-second stereo WAV](beats/window-seat-96bpm.wav)
- [Full reopening URL](beats/window-seat.url.txt)
- [Browser screenshot](beats/window-seat.jpg)

The evaluated code was recovered from Strudel's own URL fragment and saved locally. Playback showed active event highlighting; the console confirmed sample loads without errors. Strudel's renderer completed cycles 0–8. File checks: PCM 16-bit stereo, 48 kHz, exactly 20 seconds, mean volume −18.2 dBFS, peak −0.2 dBFS. These checks confirm a successful, non-silent render; they do not constitute a listening review or confirmation of the user's speaker output.

Search the documentation from the repository root:

```sh
rg -n 'swingBy|delaytime|voicing|arrange' references/strudel/sources
```

## Artist study: DJ_Dave

Studied 2026-10-10 after Olof supplied [her 808 on Twitch hybrid set](https://www.youtube.com/watch?v=E1K6Sv-oIb0). This is a study of her stated methods across several sources, not an auditory analysis of that full set. The research included interviews, her coauthored paper, official release metadata, and captions from her own production demonstration. No claim of having listened through her catalogue.

### What to learn

- **The music must work on its own.** She describes prioritizing the musical result and rehearsing code she knows well enough to perform precise transitions. Her example of a rising high-pass filter ends with a coordinated mute. Translate this into intentional section changes, not a loop left running while the operator types. [Magnetic interview, 2022](https://magneticmag.com/2022/04/dj-dave-castles-live-coding-and-the-algorave/).
- **Samples become instruments.** Vocal slicing and reordered fragments are a central technique; her workflow combines Strudel sound creation with Logic arrangement. A compelling vocal texture needs appropriate source audio; a vowel-filtered synthesizer is only a synthetic approximation of that role. [Lucid Monday interview](https://lucidmonday.com/blog/digital-cover-dj-dave).
- **Prepare controls that change several layers together.** Her own *Hard Refresh* walkthrough shows switchable kick and sidechain patterns, a clap and break loop, bass with a filter control, and two vocal chops. She explains that this organization enables simultaneous changes for builds and drops. Use a small control block and prepared sections when performing. [Official demonstration](https://www.youtube.com/watch?v=W24pteoigXk); captions retrieved successfully through yt-dlp, 85-second video.
- **Hooks can grow out of experiments.** In her account of *Next to U*, a missing comma changed simultaneous pitches into an alternating sequence; she kept the result and added a repitched unused topline. She also explicitly resists restricting herself to a single genre. Treat unexpected but promising patterns as composition material, then select deliberately. [Notion interview, July 2026](https://notion.online/dj_dave-is-the-algoraver-live-coding-the-function/).
- **A hybrid set has more sound sources than the code editor.** She describes two DJ channels alongside one live-coded computer channel. Do not assume everything audible in the supplied hybrid set was synthesized in Strudel. Her discussion of *World’s Hardest Game* also emphasizes a strong synth lead as an inspiration. [PAPER interview, March 2024](https://www.papermag.com/dj-dave-interview).
- **Let the listener understand the performance.** In her coauthored paper she explains starting with a simple sample, demonstrating rate and pattern changes, then revealing prepared song code. The explicit warning about matching pop's pace of structural change is in coauthor Lil Data's section, not DJ_Dave's individual section. Both inform our performance approach, but attribution matters. [Davis, Armitage and Lobban, 2024](https://iil.is/pdf/2024_iclc_davis_et_al_pop.pdf).

Her official [Hardcore Software release](https://djdave.bandcamp.com/album/hardcore-software), dated October 2, 2026, places her work across dance, electronic, hyperpop, algorave and technopop. These are release tags, not a listening verdict.

### Applying this in our sets

Our interpretation: introduce an identifiable motif early; change one meaningful musical feature every 8–16 bars; prepare breakdown and return together; use silence as contrast; keep one familiar element across a transition. These bar counts are our working arrangement choices, not a rule attributed to DJ_Dave. Avoid equating faster tempo or extra layers with greater interest. Use vocal material when available and appropriate, rather than claiming plain synth loops reproduce her full production.

The live sketches are saved under [beats/window-seat-live](beats/window-seat-live/). They are original exercises using broad compositional lessons, not transcriptions or copies of her songs.
