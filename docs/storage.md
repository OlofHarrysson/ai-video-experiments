# Local media storage

Keep original paintings, references, cuts and final videos. Treat documented, reproducible finishing frames as temporary working media and clean them up when an experiment is finished, following the completion checklist below. Historical media with incomplete records needs a separate audit.

**Current storage status, October 26:** Deforum occupies **135.4 GB** by `du`, down from **316.8 GB**, after an [older-project PNG retirement](#approved-older-png-retirement-october-26) and an [additional World Seed / Glass Tide cleanup](#additional-newer-project-png-retirement-october-26) requested by Olof. Both include original generated paintings; the records below identify affected projects and restoration limits. The two execution windows observed **88.03 GB** of additional physical free space combined; about **123 GB** is now free. The preservation rule above still applies to future work.

## What was taking space

The 2026-09-15 audit measured about **155 GiB** in the checkout, including **148 GiB** in Deforum. Its project folders accounted for about **113 GiB**, working files **35 GiB**, and the Python environment **0.21 GiB**. These rounded `du` figures count existing hardlinks once.

Approximately **119 GiB** was PNG files, **20 GiB** compressed archives, and **4.4 GiB** MP4 files. The 24 fps frame sequences, copied painting sources, raw motion frames, and unpacked cumulative downloads cost much more than the watchable videos. Embedded reviewer HTML accounted for only **0.84 GiB**, so rebuilding the reviewer was not the priority.

The project-only SHA-256 scan found 13,661 groups of identical PNG/MP4 content occupying separate inodes, representing up to **54.7 GiB** of redundant allocation. Many existing hardlinked frames already shared storage and were excluded from that estimate.

## Cleanup and verification

- Retired eleven `downloaded-*` scratch directories from the two-hour-lab and surreal-hour sessions. All 27,150 loose files were checked against the actual retained archive, after checking the archive's recorded SHA-256. All archives and canonical project media remain available.
- Retired seven story-hour intermediate archive containers after reading every member and proving that the retained `complete.tar.gz` contains the same path, size and hash. Their inventories, recorded hashes and cleanup receipts remain. The retired containers totaled 2,479,577,167 bytes (2.31 GiB). Earlier snapshots in other sessions containing unique versions of code or records were retained.
- Applied APFS copy-on-write sharing to byte-identical project images/videos. Each replacement preserves its filename and bytes; hashes are checked before replacement and again afterward. Existing hardlink groups and differing attributes are skipped. Completed: **33,292 files**, representing **58,605,748,540 bytes (54.6 GiB)** of duplicate content, now share data blocks. All replacements passed post-write SHA-256 checks; 28 existing hardlinked duplicate inodes were left alone.

The implementation uses the Mac's native `clonefile` operation. Its files have separate identities and can be edited independently while initially sharing data blocks. This differs from hardlinks, whose edits affect every linked path. Target permissions/ACL and timestamps are preserved during deduplication; files with different extended attributes are skipped. [Apple's APFS documentation](https://developer.apple.com/documentation/foundation/about-apple-file-system) and the installed `man clonefile` describe the filesystem behavior.

Receipts are local in `apps/deforum/work/storage-audit/`: archive retirement records, the duplicate inventory, per-file clone hashes and execution totals. They contain no new GPU work. The working problem is logged centrally as **AF-20260915-212725**.

**Measurement caveat:** Finder, `du`, and summed file sizes can still count shared clone storage multiple times. Their folder-size totals may remain large after physical space is freed. `df` measures free volume space, but unrelated disk activity and APFS snapshots also affect it. Global free space changed independently during this task; do not attribute its whole increase to this cleanup. Clone receipts report verified bytes consolidated, not an exact independent physical-block census.

## Convention for subsequent experiments

1. Use `deforum_lab.records.copy_verified` for reused paintings and prefixes. It now makes independent APFS clones on supported Mac volumes. Linux and unsupported/cross-volume filesystems use ordinary copies. Permission errors and other failures surface. Existing saved copies still require matching hashes.
2. Verify downloaded archives as a stream. Restore missing canonical project files directly; avoid retaining a second complete unpacked tree in `work/` after verification. Keep the final archive, its checksum and member inventory.
3. Retire earlier cumulative archives only when every member is preserved in the retained archive. A later filename alone does not establish a complete superset: earlier source/config snapshots can differ.
4. Retain every video's current playable export and every diffusion painting, settings/graphs, lineage, noise/latent diagnostics and reference. For future completed experiments, retire documented derived finishing frames using the completion checklist below. The full-rebuild checks later in this document describe the historical October 18 audit, not a requirement to rerender each future film.
5. Keep the current project available locally. The next larger storage step would be a verified external archive for older frame sequences, with a small local index and the videos still reviewable. No external archive or backup is configured yet. The October 18 historical cleanup remains limited to its recorded selections; future completed experiments follow the checklist below.

This improves preservation efficiency; it does not create a second-device backup. A shared clone is another usable path to the same underlying storage.

## Completion checklist for future experiments

Cleanup is part of finishing an experiment, after Olof has accepted the result or explicitly closed the attempt and any dependent editing, frame review or continuation work has ended. A successful render alone does not mark a project finished. Keep unfinished work available. The agent carrying out the experiment owns this closeout step; this is not a scheduled or automatic render-time deletion mechanism.

1. **Keep the creative assets.** Preserve original paintings and references, unique generated takes including rejected alternatives, final videos and audio, versioned cuts, settings/graphs, seeds, lineage, and any intermediate used as a generation input or needed for continued editing.
2. **Save the reconstruction recipe during production.** Record each output's role and hash, its exact input paths/hashes, ordered timing and finishing settings, pinned code/model weights and environment dependencies, and an explicit restoration command. Keep those inputs and dependencies locally. Missing or ambiguous provenance means retain the frames.
3. **Verify the saved result once.** Use the normal final delivery checks: video decode, duration/frame count, dimensions, source/recipe integrity and human review. Reuse recorded successful checks when their inputs and output hashes are unchanged. Do not rerender the whole film solely to authorize deleting its intermediates. A changed finishing method may warrant one bounded reconstruction test, with its cost stated first; do not repeat that test for every unchanged recipe.
4. **Delete only listed, disposable outputs.** Use a manifest-based allowlist for reproducible interpolation and finishing outputs. Verify their identity and check all known downstream input/continuation references before unlinking. Preserve unique warp/generation inputs and unclear frame roles. Check copied or hardlinked finishing frames too, so deleting one path does not leave another unnecessary copy. Never purge a mixed `frames/` directory by name or age.
5. **Leave a receipt and usable review path.** Record deleted paths/hashes, retained inputs, the restore command and measured free-space change. Keep final-video playback available; frame-level review of retired PNGs requires restoration. Restore the needed sequence before future editing that requires those PNGs.

This retains a documented route to regeneration; it does not promise byte-identical output after runtime or hardware changes. The existing `frame_retention retire` command below is restricted to the older audited project and still performs a full rebuild. Do not apply it as the default future closeout command. Future closeout must use a scoped cleanup implementation that follows this checklist, or retain the frames if that implementation cannot establish the required boundaries.

## Tools

Run from `apps/deforum/`:

```sh
uv run --locked python -m deforum_lab.media.storage audit . \
  --report work/storage-audit/current.json
```

This is read-only apart from its JSON report. It counts allocated file bytes once per inode; it cannot detect APFS shared extents.

For a completed session's redundant extraction, use the exact retained archive and its previously recorded checksum:

```sh
uv run --locked python -m deforum_lab.media.storage retire-extraction \
  work/SESSION/complete.tar.gz work/SESSION/downloaded-complete \
  --sha256 RECORDED_ARCHIVE_SHA256 \
  --receipt work/SESSION/extraction-retirement.json
```

The default verifies and writes a dry-run receipt. Add `--apply` to retire the checked extraction. The command refuses mismatched/unarchived files, symlinks, unsupported archive entries, and non-sibling destinations; it never recursively deletes unchecked additions. Run while no producer is writing the session. Files remain recoverable from the retained tar archive.

`deforum_lab.media.clones.share_duplicate` is the guarded helper used for the existing duplicate cleanup. Use it only for hash-matched inactive media; the original scan and applied paths are retained in the local audit receipts. Repeated cloning of already shared files does not establish further savings.

September 15 validation: the repository's **63 local tests** passed, including archive corruption/mismatch rejection, archive hardlinks, extraction dry runs, independent writes to cloned copies, immutable targets, and the recurrent runner checks. At that time, both latest full films decoded successfully and the existing reviewer returned HTTP 200. No render recipe or reviewer UI changed.

## Selective frame retention

See the [format benchmark and cleanup boundaries](research/frame-storage-formats.md): twelve-frame tests find practical lossless WebP about 23% smaller, while stronger PNG compression saves about 5%. Current PNGs already use compression. Recorded cadence alone is insufficient for safe cleanup across old experiments.

Olof has no external drive yet and is open to removing old frames if they can be regenerated conveniently. Recommended boundary: preserve final videos, original diffusion paintings, references and reconstruction records; treat verified RIFE and warp-only intermediate sequences as reclaimable working files. On October 18, Olof authorized deleting verified redundant archives and older interpolation frames that pass reconstruction checks. This does not authorize a blanket purge of `frames/` directories, which also contain original paintings in some runs.

On 2026-09-15, a local reconstruction check reran the first RIFE interval of `fluent-hour-v001/f3-sweeping-worlds/faster` from its saved paintings and recorded settings. All nine PNG files, including seven interpolated frames, reproduced their original SHA-256 hashes. The check took 10.39 seconds including setup; temporary verification output was removed afterward. The existing complete sixteen-second clip recorded 111.54 seconds of local finishing. This proves one interval with the retained runtime/weights, not exact reproduction of every historical experiment or future software version. Evidence: `apps/deforum/work/storage-audit/rebuild-proof.json`.

The videos use H.264, CRF 18, and YUV 4:2:0. Extracting an image from a video is convenient for playback review, but does not recover the original lossless PNG pixels. Keeping the original diffusion paintings protects high-quality continuation and avoids rerunning diffusion, which can be costly and need not reproduce identically.

### Guarded cleanup and restore

`deforum_lab.media.frame_retention` supports completed pre-September-18 full sequences in `modern-model-study` using the unchanged pinned `interpolate.py`. It verifies the original manifest, every source painting, model code/weights, and existing video. A fresh first-pair validation and full reconstruction must reproduce every recorded PNG SHA-256, frame role, setting and provenance field before selected interpolation frames are removed. Anchors, final holds, original paintings, final videos, first-pair validation sets and metadata remain. Historical runner versions are not rebuilt by this command; individually hash-matched copies can be handled separately below. Failed checks are retained.

The October 18 private plan and receipts live in `apps/deforum/work/storage-audit/cleanup-20261018/`. `frame-plan.json` records candidates and dependency exclusions; `frame-progress.json` records completed and skipped sets. Each `frames-*.json` receipt preserves the original recipe, complete reconstruction evidence, selected file hashes and removed paths. Archive member inventories and retained archive hashes are saved separately in that directory. These ignored files must remain with the media.

Restore a retired sequence from its receipt, from `apps/deforum/`:

```sh
uv run --locked python -m deforum_lab.media.frame_retention restore work/storage-audit/cleanup-20261018/frames-RECEIPT-ID.json
```

Restore verifies retained dependencies, regenerates a fresh pair and the full sequence, compares all recorded hashes, and creates only the missing selected PNGs. Existing differing files are rejected. It requires the retained RIFE Python environment, `work/rife-session/Practical-RIFE`, `rife425.zip`, the exact `interpolate.py`, and the source paintings listed in the receipt. Keep these dependencies; a changed runtime must not be assumed to reproduce identical pixels. This is verified regeneration on this Mac, not an external backup.

The dependency scan reads saved JSON paths across projects and working records and excludes referenced frames. The execution allowlist removes only explicit `kind: interpolation` records after a full rebuild. Recent films and unrelated projects are outside this cleanup.

Hardlinked finishing copies need a separate check: removing one name does not release the data while another link remains. `frame_copies` maps explicitly tagged interpolation copies to completed full-rebuild receipts by SHA-256, verifies the entire delivery, and retains its unique warp/tail frames, anchors, video and metadata. A pending manifest containing the same output rows is an output record, not an input dependency. Unknown paths or unmatched copies remain. Copy receipts use the same restore command; it rebuilds the proven source sequence and copies only the missing selected frames into the delivery.


### October 18 cleanup scope

The exhaustive reconstruction batch was stopped at Olof's request after **73 of 89** planned sequences passed. The remaining **16 sequences were rechecked intact and retained**. Final copy cleanup uses only the completed proofs, excludes those sixteen sequences, and performs no further rendering. One base sequence was genuinely restored, hash-verified and retired again earlier in the batch; copy restoration has focused automated coverage but was not rerendered during the final shortened pass.

The full rebuild strategy consumed about 100 minutes before the scope was reduced. Future cleanup should estimate aggregate verification time before execution and agree a bounded approach if full reconstruction would dominate the work. This incident is recorded as AF-20261018-184756.

Validation for the cleanup helpers: **15 focused tests passed**, Ruff passed, and the final private verification receipt records actual deletions and retained-file hashes. The application and render recipes were not changed.

The completed removal receipts cover **31 redundant archives (8,017,083,958 bytes)** and **26,187 interpolation PNG paths**: 15,180 in the 73 rebuilt sequences and 11,007 matching copies across 44 older deliveries. Copy processing retained 72 other deliveries and reported no failures. PNG path sizes total 45,149,077,102 bytes, but hardlinks and APFS clones mean this is not physical space recovered. `final-verification.json` records the observed volume-free-space change separately.

Final readback passed: **26,882 retained files** matched their recorded hashes, all selected deletions were absent, and the retained archives remained present at their recorded sizes. Volume free space rose from **44.77 GB to 70.87 GB**, an observed **26.10 GB** increase during cleanup; unrelated writes and APFS behavior mean this is not an exclusive block accounting. Original paintings, final videos, model/runtime files and reconstruction records were preserved.


### Conservative four-film cleanup, October 18

Following a separate read-only audit and explicit approval, the conservative selection removed **19,933 interpolation PNG paths (37.28 GB logical)** across World Seed, Cartographer’s Dream, Glass Tide and Night Orchard. No reconstruction or re-encoding was performed. The latest review-pending cuts, original paintings, final videos/audio, anchors, unique warped frames, validation pairs and all recorded reconstruction dependencies remain.

Private execution and restoration receipts are in `apps/deforum/work/storage-audit/four-films-20261018/conservative-cleanup/`. `completion.json` records preservation readback and the receipt index; `README.md` gives the restore command. The existing restore CLI accepts the new static-audit copy receipts, reconstructing the pinned base recipe only when restoration is explicitly requested. These receipts do not claim a fresh full reconstruction was demonstrated during cleanup.

Volume free space increased by **21.28 GB**, from **54.25 GB to 75.52 GB**, during this deletion pass. APFS-shared data and unrelated writes explain why the observed change differs from 37.28 GB of deleted file sizes. All non-selected project files passed the final unchanged-file check. The 15 focused tests and Ruff passed; rendering was mocked in restoration tests.


### Remaining interpolation cleanup and broader estimate, October 18

The separately authorized remaining-interpolation pass removed **14,847 PNG paths / 24.66 GB logical** in 31 supported, intact sequences across Modern Model Study and Storm Engine, without rendering. Historical recipes, partial sequences and validation pairs stayed. All 102,324 other files in those projects passed unchanged-file verification. Observed free space increased by **10.12 GB**, to **96.14 GB**, during the pass; hardlinks, APFS sharing and other writes affect these measurements.

Receipts and reconstruction recipes are in `apps/deforum/work/storage-audit/remaining-interpolation-20261018/`; its README contains restoration instructions, subject to the later source retirements below. A separate estimate for deleting most PNGs from projects whose newest media is over seven days old found 173.3 GB of candidate inode allocation, or 122.8 GB excluding Cartographer’s Dream and Night Orchard while their latest cuts await feedback. That estimate included original images and was not approved for execution on October 18. The narrower October 26 selection below received separate approval; no future automatic purge is authorized.

### Approved older-PNG retirement, October 26

Olof approved a concrete selection of **78,645 PNG paths** to reduce Deforum below 200 GB. All selected paths were deleted. They represented **134.21 GB of logical file sizes**, or **120.33 GB of allocated file bytes counting hardlinks once**. The resulting folder measures **196.60 GB**. Observed volume free space increased by **61.22 GB**, from **35.05 GB to 96.27 GB**, during execution; APFS sharing and unrelated disk writes affect the physical-space measurement.

The selection covers generated PNGs in Modern Model Study, Storm Engine, Motion Guide Study, Brain Entity Study, Botanical Cathedral, Guide Redraw, Lantern Marsh, Marsh Story, Model Comparison, Motion Lab, Redraw Lab, SDXL Settings, Seedream Motion, Seedream Repaint and Shape Injection. Original reference folders, Git-tracked files, every non-PNG file and all other projects were excluded. Cartographer’s Dream, Night Orchard, World Seed, Glass Tide, Red Rite and Rainbow Mane were intact at the end of this pass; the later World Seed / Glass Tide retirement is recorded below.

This retirement **includes original generated paintings**. Historical preservation and restoration statements for affected versions no longer establish that their input PNGs remain available. Videos remain playable, but PNG-based frame review, editing and continuation require restoring the relevant inputs first. Retained work archives may contain some images; their recovery coverage was not audited and is not guaranteed. This approval does not authorize future automatic purges.

Private evidence is in `apps/deforum/work/storage-audit/cleanup-20261026/`: the approved path list, execution script, authorization and plan hash, per-file deletion hashes, preservation snapshot, video hashes, and completion receipt. Execution verified every selected file’s identity against the approved plan, recorded its SHA-256 before unlinking, confirmed all selected paths absent, and checked **202,876 retained files** for unchanged identity/size/modification time. All **10,240 retained video paths** passed SHA-256 readback. No rendering, re-encoding or archive removal was performed.

### Additional newer-project PNG retirement, October 26

After seeing that APFS sharing reduced the first pass’s physical recovery, Olof requested additional PNG deletion from newer projects. The stated scope was **World Seed and Glass Tide**, including generated paintings and their editing/continuation tradeoff, while keeping videos, audio, configurations and original reference folders. **30,668 PNG paths** were removed, representing **61.17 GB logical / 61.23 GB inode allocation**. Every non-PNG file, Git-tracked file, reference folder and other project was excluded.

Deforum now measures **135.42 GB**. Observed volume free space increased by another **26.81 GB**, from **96.20 GB to 123.01 GB**, during this pass. The script confirmed all selected paths absent, all **172,219 retained files** unchanged by identity/size/modification time, and all **10,240 retained video paths** unchanged by SHA-256. No rendering, re-encoding or archive deletion occurred. The same restoration limits described above apply to these two projects: videos remain playable, but historical reports do not establish that their PNG inputs remain available.

Private evidence is in `apps/deforum/work/storage-audit/newer-pngs-20261026/`, including the exact allowlist, execution script, per-file deletion hashes, preservation snapshot, video hashes, physical-space observations and completion receipt. Cartographer’s Dream, Night Orchard, Red Rite and Rainbow Mane remain outside both October 26 deletion selections.
