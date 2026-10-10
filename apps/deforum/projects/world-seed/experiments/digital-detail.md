# Crisp digital rendering during motion

Authorized 2026-10-10 after Olof tentatively preferred the original opening over the full-prompt and six-step alternatives. He wants highly detailed, crisp digital art while retaining freedom to change styles between worlds. This study tests rendering language, without adding objects or changing the camera.

Compare the original two-second opening with `d03-crisp-digital`: seventeen new repaints from the same preserved opening, native 1536×1024, eighteen paintings total, three Euler intervals, identical seed/noise schedules and 4.5× delivery timing. The starting still remains the original oil-painting generation. This asks whether new conditioning changes its repeated surface treatment; it does not test a fresh digital-art opening.

Use the original travelling prompt schedule. Replace only its two rendering phrases with: “Meticulously detailed surreal digital illustration, crisp contours, finely resolved surface textures, delicate engraved linework, clearly separated overlapping forms, controlled highlights and deep clean shadows.” Retain objects, palette, layout, lighting colors and all generation/finishing settings. The new first travelling prompt is 103 words. [Exact configuration](configs/d03-crisp-digital.json).

[Krea's official Turbo examples](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md) range from a ten-word scene description to multi-sentence paragraphs. Several put medium near the beginning, describe visible features and composition, and finish with lighting or rendering treatment; their order varies. They include both crisp graphic treatments and deliberately broad painted brushwork. These are examples, not an established optimum prompt length or a claim that digital painting always means sharp detail. Our rendering phrase is an authored hypothesis based on these patterns, not a quotation or a proven Krea preset.

Inspect every new painting, the first repaint transition and matched late windows after identical RIFE finishing. Look for distinct roots, moss and petal veins that survive movement, with no new jump, blotchy edges or unstable decorative marks. Retain the full thirty-second film and prior tests. Human playback preference determines whether this is useful.

## Result and screening

[Compare with the original](http://localhost:3028/world-seed-detail) · [Digital-art test](../exports/v002/d03-crisp-digital/faster/rife-moving-tail/preview.mp4).

Assistant judgment: the new wording gives finer, more even petal veins and cleaner outlined forms, especially in the final painting at 1.875s. The bridge develops a continuous engraved surface; the original retains a more open, interwoven structure and stronger painted highlights. The digital variant also flattens into a more graphic botanical illustration and continues to simplify foliage and surface texture. This is a discernible rendering change, not a demonstrated overall fidelity improvement or proof that oil-painting wording caused the previous softness. Keep the original as the working choice until human playback review.

All seventeen new paintings were inspected in consecutive sheets; the first repaint and final painting were compared at native resolution with the original. Every frame of the opening pair (0–0.125s), matched windows at 0.875–1.125s and 1.75–1.958333s, including a separately extracted last frame, were inspected. The bridge and doorway remain connected in these windows. Small plants, petal contours and fine ornament still change between repaints; the new phrase does not establish persistent micro-detail. The full-delivery opening pair matches the separately inspected early pair.

Generation receipts, executed graphs, prefix retention and all seventeen seed/sigma pairs pass verification. First warped inputs have identical decoded pixels. Only the two specified rendering phrases differ from the original travelling schedule; duration is bounded to the common comparison range. Both deliveries retain eighteen paintings and 48 frames at 24 fps, native 1536×1024, with identical finishing settings. Full decode, source hashes, timing and moving-tail validation pass. [Controlled comparison](digital-detail-check.json) · [Execution and delivery](digital-detail-execution.json).

All 242 remote output/receipt files are hash-verified locally. After confirming an empty queue, 34 verified ComfyUI input/output duplicates were removed, and the owned Pod was deleted. A follow-up lists no Pods; the shared model volume remains. Estimated compute was at most $0.11, excluding storage. No separate external backup was made.

The existing reviewer defaults to Original / Crisp digital illustration; both earlier comparisons remain selectable. It serves the verified MP4 bytes and range requests. Browser playback reaches frame 47 in both clips, and painting stepping reaches painting 1 / frame 3 in both. The reviewer remains running for Olof. No viewer code or layout changed. Human preference is pending.

## Reproduction

From `apps/deforum`, run `uv run --locked python projects/world-seed/experiments/film.py plan d03-crisp-digital`, then `render` with an explicit owned deployment receipt, and `check`. Finish with `projects/world-seed/experiments/finish.py d03-crisp-digital pair --version v002`, inspect, then `full` and `tail`. The saved configuration owns the exact prompt schedule. Rebuild `media_review/sessions/world-seed-detail.json` with `media_review.build(..., local=True)` and refresh the existing reviewer through Terminal Manager.
