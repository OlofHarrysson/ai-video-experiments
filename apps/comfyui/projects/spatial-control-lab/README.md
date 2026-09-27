# Spatial control lab

**Completed:** [53-output comparison, recommendation and cost record](report.md). The strongest tested continuation is a Remotion circle guide plus a fixed watermelon reference through GPT Image 2.5 Sunburst. The owned GPU is deleted; all outputs are local.

Approved 2026-09-27, 18:02:37 UTC: explore broadly for at most two hours and $10 in new spend. Deadline 20:02:37 UTC. Test several recent model families and control mechanisms before refining a winner. Preserve and inspect all outputs, measure position/size, and remove owned compute. Earlier Krea experiments are historical comparisons, outside this session's spending.

## Question

Can an authored SVG shape determine where a realistic watermelon appears and how large it is? Start with still images; only investigate continuity after a convincing result. This is independent generation/editing, not a change to the existing Deforum recurrent painting loop.

## Staged comparison

1. Breadth: identical off-centre circle through four current premium image editors (GPT Image 2.5 Sunburst, Seedream 5 Pro, Nano Banana Pro, Qwen Image 3); Qwen Image 2.1 ControlNet Union with outline and depth; explicit masked generation.
2. Generalization: move right and shrink/move upward, retaining prompts and recipe. Compare multiple successful families rather than assuming one successful image is enough.
3. If supported by results, test identity/texture continuity and a short motion proof. Keep deterministic compositing distinct from independently generated or reference-conditioned frames.

The 1024×1024 left/right circles have centres (256,512)/(768,512) and radius 180. The small circle has centre (720,320), radius 100. Original SVGs and their raster counterparts, analytic inverse depth, edges and edit masks are retained under ignored `references/assets/`.

## Evidence and accounting

Exact requests, provider IDs, original outputs, normalized PNGs and hashes are retained under ignored `runs/`. Provider schemas, upload receipts and resource details are private under `apps/comfyui/work/spatial-control-lab/`. Comparisons and approximate segmentation metrics are under ignored `exports/`. Green-foreground geometry measurements require visual validation and are not ground-truth masks.

The public Qwen demo completed outline and depth samples before its anonymous quota was exhausted. Continued structural tests use our own temporary A100 ($1.59/hour), after unauthenticated weight access was verified. Hosted demo and local runtime are recorded separately.

Prices checked live: Seedream 5 Pro 1K $0.0675/image; Nano Banana Pro 1K $0.15/image; Qwen Image 3 1K $0.04/image. GPT Image 2.5 Sunburst uses token billing; published 1024-square high-quality estimate with one input is $0.05268, plus variable prompt/processing usage. Reserve extra headroom rather than treating that estimate as a hard cap. No billing rate expressed in generic “units” is treated as a per-image price without verification.
