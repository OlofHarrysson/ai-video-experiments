# Quality at similar cost

Status: researched; not rendered. [Model/cost research](../../../../../docs/research/models-and-cost.md).

## Question

Can a revised model or workflow retain detail with less flicker and similar cost to SDXL?

## Comparison

Keep the existing middle run as a reference. Separate parameter changes, flow/interpolation, and model changes. For the first modern model, benchmark FLUX.2 Klein 4B distilled through an official native workflow, then a warped-image redraw and eight-frame loop. Use model-appropriate sampling rather than assuming SDXL denoise values transfer.

## Evidence to collect

Playback flicker, detail loss, structure/camera adherence, initialization cost, warm frame time, peak VRAM, full pipeline cost, and Olof's preference. Keep rejected generations. Extend to 40 frames only if the short loop is useful.

## Cost boundary and result

Aim near the SDXL warm baseline of roughly $0.031 per five-second clip. Reconsider before approaching 3× comparable recurring cost. Seedream may supply occasional references; do not use it for every frame under the present cost constraint. No allocation or paid resource is active. Result and run links: pending.
