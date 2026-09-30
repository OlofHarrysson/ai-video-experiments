---
name: add-video-soundtrack
description: Add generated music, ambience and sound effects to existing videos, especially Deforum films in ai-video-experiments. Plan the score, use Fal audio generation, mix locally and preserve reviewable alternatives. Use for scoring existing footage; not for regenerating its visuals.
---

# Add a video soundtrack

Treat scoring as a creative pass on a preserved picture cut. Ask for a musical direction only when the conversation and film do not supply one. A contrasting pair can be useful during exploration; a single requested direction does not require extra variants.

## Plan against the delivered film

- Read the owning film brief and selected cut. Probe the actual video and sample frames across its beginning, development and ending. Cue times use delivered seconds, not source painting time.
- Write a small cue plan: musical mood and development, reveal/ending times, and any distinct effects. Surreal transformations often benefit from an expressive score and sparse sound accents; this is a starting hypothesis, not a fixed aesthetic.
- Distinguish text-directed scoring from video-conditioned generation. Do not claim a model watched the film when it only received a prompt or composition plan.

## Generate through Fal

Use the installed Fal media tools and their workflow guidance. Recheck the catalog, endpoint schema and pricing before selecting a model. The initial trial used `elevenlabs/music/v2.5` and `fal-ai/elevenlabs/sound-effects/v2`; these are recorded choices, not permanent version pins.

For Music v2.5, prompt mode accepts `music_length_ms` and `force_instrumental`. Composition mode instead uses `composition_plan.chunks` with `text`, `duration_ms` and `positive_styles`; it can accept a seed but not `force_instrumental`. Instrumental directions and negative vocal styles in chunks express intent, not verified absence of singing. V1 section objects are incompatible with V2 chunk objects. Confirm these details against the current schema.

For Sound Effects v2, the verified duration range was 0.5–22 seconds. Its prompt length limit was 450 characters. Generate separate layers to retain control of their placement and loudness.

Estimate total planned generation cost, including variants and effects. Proceed within existing task authorization. Save inputs before submission, then preserve endpoint, request ID, status/result URLs and returned recipe. Use async submission and poll the same job. After an uncertain result, recover its status rather than submit a duplicate. Retry a failed job once only after resolving its cause and confirming the retry stays within the authorized scope/cost.

Download completed audio for local mixing and preservation; check provider byte counts, decode and hash the files. Preserve every unique take, even rejected ones.

## Mix and verify

The local mixer lives in `/Users/olof/git/ai-video-experiments/apps/deforum/src/deforum_lab/media/soundtrack.py`. Run from that repository's `apps/deforum/` directory:

```sh
uv run --locked python -m deforum_lab.media.soundtrack /absolute/path/mix.json \
  --output-dir /absolute/path/new-export-directory
```

Paths in the JSON plan resolve relative to that plan. It has `video` and `tracks`; each track has `path`, `start`, `duration`, `target_lufs`, and optional `fade_in`/`fade_out`, in seconds except LUFS. Use zero-start, silent MP4 picture input. For a source with dialogue or other audio, preserve and explicitly plan that layer before using this mixer; it does not automatically duck music or preserve existing audio. Never discard source audio silently.

The mixer creates a new directory, premaster and master WAV files, a preview MP4 and a receipt. It applies measured gain to layers, normalizes the finished mix to -18 LUFS with a -2 dBTP target, and copies the video stream. These levels are a preview convention, not a delivery-platform requirement. It checks full decode, output duration, encoded true peak, unchanged source hash and identical compressed video packets.

Keep music-only original files, individual effects, mix plans and receipts. Preserve the silent selected cut until Olof chooses a soundtrack. Revisions go to a new export directory.

## Review and report

Listen when the environment supports actual audio perception. Check unwanted vocals, abrupt musical joins, distortion, fit to key moments, and a completed ending. Technical loudness or silence measurements cannot establish those qualities. If listening is unavailable, say so and report only measured/observed evidence; do not invent an audition or recommend a winner by sound.

Present one or two playable videos with audio. The existing Deforum comparison player was silent-only in the initial trial, so verify audio support before routing a soundtrack review through it. Use local absolute media paths in chat when appropriate.

Record costs as estimates unless confirmed by billing. Keep the endpoint IDs and request IDs in the experiment record. Ask one taste question about the meaningful difference between the delivered options.

Initial recipe and results: `/Users/olof/git/ai-video-experiments/apps/deforum/projects/cartographers-dream/experiments/soundtrack-trial.md`.
