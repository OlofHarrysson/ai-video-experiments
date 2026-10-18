# Local media storage

Keep original paintings, references, cuts and final videos. Save space by sharing identical bytes, retiring verified duplicate archives, and selectively removing intermediate frames whose exact reconstruction has passed. No artwork quality reduction is required for this cleanup.

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
4. Retain every video's current playable export and every diffusion painting, settings/graphs, lineage, noise/latent diagnostics and reference. Derived RIFE frames may be retired only under the separately approved full-rebuild checks below; duplicate cleanup alone does not authorize their deletion.
5. Keep the current project available locally. The next larger storage step would be a verified external archive for older frame sequences, with a small local index and the videos still reviewable. No external archive or backup is configured yet. The October 18 selective RIFE retirement below is separately authorized; other intermediate frames remain preserved.

This improves preservation efficiency; it does not create a second-device backup. A shared clone is another usable path to the same underlying storage.

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
