# Glass Tide: the world inside the shell

Olof approved the twelve-second layered-motion passage (“Now we're talking”) and requested a finished film between one minute and ninety seconds, with a strong ending. The completed film is 68 seconds: glass reefs become a forest city, amber and obsidian vaults, and blue-violet chambers that gather into a coiled world above a dark sea.

The approved opening and its 108 paintings remain the starting point. The film uses the established Krea 2 Turbo recurrent RGB loop: warped previous painting, noise 0.72, three Euler updates, CFG 1 and additional reference conditioning off. RIFE stays outside feedback. No masks, fixed opening reference or cuts are introduced.

## Direction and selected passages

Camera travel, banks, regional twists, shear and travelling bends overlap, with different movements leading each passage. The final pullback slows gradually while the world continues moving. Material prompts name concrete small structures—windows, narrow stairs, fern leaves and engraved partitions—to support detailed digital artwork.

| Delivery time | Passage | Observed result and directing decision |
| --- | --- | --- |
| 0–12 s | Accepted J opening | Preserve the layered local motion and approved imagery. |
| 12–17 s | [Emerald Veins K](long-k.json) | Emerald glass and copper branches emerge. Broad gemstone surfaces and soft foreground branches increase, so this originally planned ten-second continuation stops after five seconds. |
| 17–29 s | [Canopy Arches L](long-l.json) | A pullback and lateral approach reveal fine ivory terraces, bridges and ferns. The oversized branches clear by about 19 seconds. |
| 29–41 s | [Amber Vaults M](long-m.json) | Banks, opposing curls and a travelling bend carry the terraces into amber glass, obsidian, gold tracery and ruby inlays. A dark opening gradually fills with cathedral forms. |
| 41–53 s | [Indigo Chambers N](long-n.json) | A counterbank, lateral movement, curl, shear and travelling bend cool the architecture into cobalt and violet cells. Late miniature structures simplify into repeated arches and stones. |
| 53–56 s | [Shell Gather P](long-p.json) | More explicit architectural and botanical detail accompanies a gentle gathering motion. Fine towers, stairs, fern leaves and engraved partitions recover in the saved paintings. |
| 56–68 s | [World in the Shell Q](long-q.json) | A regional turn, travelling bend, pullback and counterbank gather the chambers around a turquoise pearl, with miniature cities and trees inside and a dark sea outside. |

These are continuous prompt and motion passages, not edit cuts or separately generated replacement scenes. Every new painting initializes from its moved predecessor. The late composition is more elaborate than one literal isolated nautilus; the generated coil determines the closing focal point.

The detail recovery follows combined prompt and motion changes. It is not an isolated experiment establishing that a particular adjective or focus phrase caused the improvement.

## Closing motion

The first pullback draft, [O](ending-motion-rejected-o.json), was rejected before any diffusion jobs ran. Its warp-only preview crossed a projective horizon: two earlier Hermite camera controls had nonzero terminal velocities and continued extrapolating across later passages. The strong closing pullback compounded that mapping.

P uses the existing continuation controls to preserve the inherited mapping and its initial derivative, then brings those two fields to rest over ten source seconds. A small local curl and gentle global carrier remain. Sampled initial mapping disagreement is below 1e-9 image-height units; sampled derivative error is 4.4e-8. Its complete low-resolution interval sweep and native-resolution first and last spatial steps pass.

Q begins from P's actual last painting. Earlier fields are now static apart from the global carrier. A fresh camera basis matches that carrier's incoming screen velocity, with sampled maximum disagreement of 2.94e-9 image-height units per source second. This avoids extending the accumulated perspective mapping indefinitely. All 108 low-resolution spatial steps and an eight-sample motion overview pass. Model, sampler, initialization and reference policy remain unchanged; shared pipeline code is unmodified.

Q was first rendered for three seconds. Native paintings at source 6204 and 6360 preserve the pearl and reveal towers and trees inside clear coloured chambers. At source 6660, the pearl remains legible, ivory stairways bridge the blue-violet coil, and a dark sea and reflection surround it. At source 7008 the coil is smaller and its outer outline is clearer. The final painting, source 7332, contains the whole glass silhouette above the sea, with a retained turquoise pearl, ivory towers, branching plants and a reflection. The assistant selects this 68-second ending.

## Screening

Review consists of native-resolution paintings, small overview sheets and selected every-frame windows. It does not establish human full-speed rhythm approval.

- **Nineteen-second workprint:** eight-frame overview and every-frame windows at 11.75–12.125, 16.75–17.25 and 18.5–18.875 seconds. Perforations become windows and foreground branches give way to terraces continuously. No conspicuous edit cut or doubled contour appears in those windows. The first 286 lossless delivery frames match the accepted twelve-second passage.
- **Forty-one-second workprint:** eight-frame overview and every-frame windows at 28.875–29.125, 29.875–30.25, 36.625–37 and 40.625–40.875 seconds. Continuous outlines survive the material changes. A small text-like mark near 30 seconds is transient.
- **Dark threshold follow-up:** every-frame windows at 37.5–38.125 and 38.125–38.75 seconds. Cathedral forms gradually appear inside the dark opening while the surrounding rims continue moving. No conspicuous jump or doubled contour appears in these inspected windows.
- **Native checkpoints:** K 1440/1668/1824; L 1920/2040/2376/2628/3120; M 3240/3324/3468/3600/3960/4200/4416; N 4536/4776/5076/5364/5532/5712; P 5880/6036; Q 6204/6360/6660/7008/7332.

Fine glass edges and engraved rims remain clear. Broad nacre and glass faces are smoother, and miniature detail temporarily simplifies late in N before recovering in P/Q. The brief mark near 30 seconds remains in the preserved sequence. These limitations should not be described as uniformly meticulous detail in every frame.

The complete RIFE workprint was screened with ten overview frames and every-frame windows at 40.875–41.125, 52.875–53.125, 55.875–56.125 and 64.5–64.875 seconds: 41 images across four inspected pages. Rims stay connected at the M/N, N/P and P/Q handoffs; local miniature details change while the pearl and outer shell remain recognizable in the late turn. No conspicuous edit jump or doubled rim appears in those windows.

The final delivery retains the first 1,630 lossless frames of that workprint and replaces its two holds with spatial movement. All nine displayed frames at 67.625–67.999 seconds were inspected from the final MP4. The pearl, glass outline, towers, plants and reflection remain coherent; the last two frames continue a subtle drift. The assistant selects this cut. Full-speed human rhythm and ending preference remain open.

## Reproducibility and preservation

Frozen matrices record every prompt, seed, motion field and source painting. Exact generation checks compare submitted graphs, PNG metadata, job IDs, dimensions, output hashes and the RGB warp used as the next input. After each check, a private hash inventory freezes the verified generation files and verifier source. Closeout rechecks those hashes rather than repeating unchanged spatial calculations.

The final delivery retains 612 paintings: 108 accepted paintings plus 504 new jobs (K 45, L 108, M 108, N 108, P 27, Q 108). K's unrendered remainder and the rejected O motion draft are preserved as plans, not counted as generated material. Retiming retains every painting at `round(source_frame / 4.5)`, with RIFE 4.25 between them. Two final spatial frames continue the motion instead of holding the last painting.

The original twelve- and thirty-second MP4s remain separate. Verified byte-identical copies share APFS storage while retaining independent paths. No unique generation is removed.

All 504 new jobs and 8,948 local generation files are preserved. The remote export manifest matches local originals, runtime/model evidence is archived and hash-verified, and the queue is empty. All 1,008 session-owned ComfyUI inputs and outputs were hash-checked before removal. The owned RTX 4090 allocation is deleted and its absence verified; the existing model volume remains. Allocation lifetime at $0.89/hour estimates $2.41 in compute, excluding retained storage and not an invoice.

Local free space fell during finishing. The established guarded APFS sharing helper consolidated byte-identical files in completed Glass Tide deliveries, preserving file contents, timestamps, access rules and independent identities. Every unique image and video remains. The private receipt records the matched paths and hashes; summed shared bytes are not an exact physical-space census.

The first long SSH output stream stopped reporting while remote generation continued. Saved source 1824, the partial check, an empty queue and absence of the remote process established completion; local collection then passed. Only the stale local SSH client was closed. Keepalives and remote render logs were added to the session helper. The root cause remains unverified; incident `AF-20261017-160842` records the evidence.

The [execution receipt](execution-long-finale.json) records generation verification, final frame roles, original preservation, resource deletion and the served player check. [Cut v003](../cuts/v003.md) is the selected 68-second delivery.
