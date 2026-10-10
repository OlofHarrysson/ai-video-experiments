# Same score, three palettes

Olof says Undercurrent's structure is closer to what he wants, but remains unsure about the instruments. His request is to preserve the groove and arrangement while trying two alternative sound palettes.

- **[Current](exports/palette-comparison-v001/current.wav):** Undercurrent v002, the reference he heard.
- **[Smoke](exports/palette-comparison-v001/smoke.wav):** low-harmonic rounded chord bodies, noise-based dusty hats, a softer layered clap and brushed details.
- **[Wire](exports/palette-comparison-v001/wire.wav):** saturated narrow-pulse chord stabs with a shorter decay, a short noise clap, brighter metallic hats and tighter noise details.

These descriptions express the synthesis choices, not a validated listening verdict. All three are 30 seconds. Copies are matched to **−17.61 LUFS** using only constant attenuation; originals remain preserved. Listen for the character of the chord stabs, clap and upper percussion. The bass synthesis and kick sample are retained in both alternatives.

## Controlled comparison

All three assembled Strudel sources have the same SHA-256: `27fdc3c2be5a6c29023800967ef57923ea5af3e37b8ff03159ec3826f67243d0`. Notes, onsets, swing, gain patterns, filter automation, panning, effects and section masks remain fixed. Only the sample library changes. The replacement chord samples contain the same MIDI pitches; their harmonic content and envelopes differ. Changed envelopes can affect perceived groove even with identical event timing.

The `RolandTR909_cp/hh/oh` bank names are compatibility slots for the unchanged score: those sounds are newly synthesized in Smoke/Wire. Only the `bd` sample remains the copied 909 recording. [Generator](make_comparison_palettes.py) and [asset provenance](references/comparison-palettes.json) make this explicit. The original sample library is untouched.

[Comparison evidence](palette-comparison-evidence.json) records source identity, preserved kick hashes, bass-stem sample differences, rendered levels and verification of the matched files. No audio-model ranking was used. Olof's palette preference remains open. The existing 36 Python tests and Ruff pass; no renderer or reusable tooling changes were needed.

## Reproduce

From `apps/music`, use either `assembly-smoke.json` or `assembly-wire.json` through the existing assembler and project renderer:

```sh
uv run --locked python music.py assemble projects/undercurrent/assembly-smoke.json --out NEW_ASSEMBLY
uv run --locked python music.py render-project NEW_ASSEMBLY/project.json --revision smoke --out NEW_RENDER
```

The deterministic generator creates both sample folders and manifests on a fresh restore and refuses to overwrite the preserved palettes. Each alternative has its own master and four stems under `renders/`. Comparison copies, generated samples and rendered audio are local and ignored by Git; source, generator and evidence are tracked. Wet rerenders need not be byte-identical.

Smoke's final isolated detail export timed out after 180 seconds before sample loading. Its master and three other stems had completed. The original failed receipts remain intact; one standalone retry succeeded at `renders/smoke-details-retry/`, and the audit uses that explicit recovery path. The full comparison mix was not regenerated or altered. The runtime incident is recorded as AF-20261010-182707 in the central agent-friction log; its root cause is unresolved.
