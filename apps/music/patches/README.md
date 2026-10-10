# Strudel export scheduling patch

`@strudel+web+1.3.0.patch` changes only the ES-module bundle used by our renderer. It schedules events one cycle at a time while the OfflineAudioContext is suspended/resumed, matching the exporter served by strudel.cc on 2026-10-10. The original npm build schedules the entire piece before rendering. That changed sampled sections in our practical beat despite an identical event multiset.

`npm ci` runs `renderer/apply-patch.mjs`. It checks the original/patched bundle SHA-256, applies this patch with the system `patch` utility, and verifies the result. The runtime independently checks the patched checksum. No silent use of an unpatched or changed package is allowed. Updating Strudel requires rechecking the upstream exporter, removing/adapting this patch and running the reference parity tests.

Evidence: [renderer validation](../docs/renderer-validation.md). Source inspected: [published exporter](https://unpkg.com/@strudel/webaudio@1.3.0/webaudio.mjs) and [website module](https://strudel.cc/_astro/spectrum.DmSH5sgu.js), retained locally with its hash in the evidence record. The latter URL is a build asset and may disappear on a website update.

The patched Strudel code and this derived patch are licensed under **AGPL-3.0-or-later**, copyright Strudel contributors and the patch contributors. The upstream license is retained in [LICENSE-AGPL-3.0.txt](LICENSE-AGPL-3.0.txt). Installed packages retain their own notices and licenses.
