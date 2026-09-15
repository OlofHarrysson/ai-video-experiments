# Frame formats and conservative cleanup

Evidence checked 2026-09-15. No production format changed and no existing frames were removed in this study.

## PNG compression is already active

The recurrent warp writer and RIFE interpolation writer use Pillow's default PNG save behavior. The documented default is ZLIB level 6; `optimize=True` uses level 9. These settings change compression effort, not image quality. [Pillow PNG documentation](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#png).

The pinned ComfyUI revision `12d5279438bfefc058a269eae805ceab6047777f` sets `SaveImage.compress_level = 4`. Its preview node uses level 1. These are compressed PNGs. [Pinned source](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L1500).

Our twelve sampled images occupied 20,404,357 bytes, versus 46,817,280 bytes of unpacked RGB pixels. They were already about 56% smaller than raw RGB. Every PNG compresses a complete image independently; our delivery videos can also exploit similarity across time. Intricate artwork and noise leave less redundancy for lossless image compression.

## Measured alternatives

Twelve full-resolution RGB frames sampled current Krea paintings, RIFE intermediate frames, a warped input, a correlated-noise painting, earlier SDXL work and earlier animation. Pillow 12.3.0, libwebp 1.6.0; no resizing or color quantization. Every decode was compared against every original RGB byte. Existing textual PNG metadata was retained in the PNG tests and counted as a JSON sidecar for WebP.

| Encoding | Total size | Reduction from originals | Encoding time, all 12 | Identical pixels |
| --- | ---: | ---: | ---: | --- |
| Existing files | 20.40 MB | — | — | — |
| PNG, level 6 | 20.48 MB | −0.4% | 0.96 s | Yes |
| PNG, optimized | 19.41 MB | 4.9% | 7.54 s | Yes |
| WebP lossless, effort 80 / method 4 | 15.64 MB | 23.4% | 6.62 s | Yes |
| WebP lossless, effort 100 / method 6 | 14.99 MB | 26.6% | 142.59 s | Yes |

Sizes use decimal MB. This is a small mixed sample and one encoding pass, not a whole-library savings estimate or a sustained performance guarantee. Decoding all twelve files took 0.23–0.27 seconds for these methods. More expensive WebP settings saved only another 0.65 MB and took about 22 times as long as the practical WebP setting.

WebP was explicitly encoded with `lossless=True` and `exact=True`. Its lossless `quality` value controls effort; it is not a license to lose detail. [Pillow WebP options](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#webp). Other codecs, including AVIF and JPEG XL, were not benchmarked here.

Detailed sources, hashes, parameters and per-image results are in [the benchmark data](frame-storage-benchmark.json). Local fixtures and decoder checks are in `apps/deforum/work/storage-audit/formats/`.

## Compatibility and migration scope

One sampled lossless WebP decoded to the original RGB bytes through local Pillow, OpenCV, FFmpeg, and the separate RIFE environment's Pillow. This verifies local decoding, not a complete new WebP pipeline. The pinned ComfyUI loader uses its video/image loading implementation and Pillow; a hosted WebP upload/load has not been exercised during this study. [Pinned LoadImage implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L1571).

Our own recurrent runner, client, RIFE inventory and encoder commands hardcode PNG names, PNG upload content types or PNG signatures. The format is therefore not a drop-in filename substitution. A small next experiment could store intermediate frames as lossless WebP and materialize PNG only where the existing interface requires it. Original diffusion paintings can remain PNG, retaining embedded ComfyUI metadata and current continuation records.

Lossless pixels do not imply identical file bytes. Recompressing PNG or converting to WebP changes the SHA-256 recorded by existing manifests, even when the image is identical. A migration must preserve metadata and distinguish original-file identity, decoded-pixel identity and stored representation. It must also retain the APFS sharing gained in the previous cleanup: independently re-encoding every copy would allocate duplicate data again. No bulk conversion is proposed without those changes.

## Cleanup cannot infer frame roles from cadence

The modern-model exports contain 267 manifests with output-frame records, seven model/role combinations, and ten combinations of timing fields. These include ordinary RIFE, variable painting timestamps, raw holds, fixed-state diagnostics, SPEED diagnostics, retimed excerpts, final warp frames and assembled films. These counts classify records; they do not certify any files for deletion.

Both original diffusion outputs and disposable intermediates can live in a directory named `frames/`. A filename or an every-Nth-frame rule is insufficient. Assembled films can also depend on frames from earlier projects, while a continuation's resume check depends on its original initialization image.

The earlier nine-frame reconstruction proves only one RIFE interval with the retained runtime. A cleanup implementation should:

1. Start with a narrow supported finishing family and explicit completed outputs. Leave active work and unknown/missing/inconsistent manifests ineligible.
2. Read each frame's recorded role, actual timestamps, source indices, source hashes, model/runtime settings and reconstruction recipe. Protect original paintings, references, initialization images, cut dependencies and provenance records.
3. Rebuild the entire candidate sequence into temporary storage while the original still exists. Verify its output hashes. A successful sample alone is not enough to authorize removing the rest.
4. Preserve a restore receipt and all required source/model/recipe files outside the deletion set. Ensure the restore path does not depend on intermediate files it plans to remove, including the current first-pair validation artifacts.
5. Present an exact file list in a dry run. Recheck it before applying; purge only listed eligible derived files. Keep the video, metadata and originals. Age can select candidates but cannot establish safety.

A changed cadence is manageable when its actual frame plan is recorded. The unresolved risk is an incomplete reconstruction/dependency record. Such experiments should be retained until they have a verified adapter. A generic age-based purge is not implemented or validated for this archive.

Recommendation: try practical lossless WebP on a new intermediate-frame output first; build a narrowly scoped, fully verified purge/restore workflow separately. The existing PNG pipeline remains the production path.
