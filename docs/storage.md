# Local media storage

Keep every unique generation, reference and cut. Save space by sharing identical bytes and retiring verified duplicate scratch copies. No artwork quality reduction is required for this cleanup.

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
4. Retain every video's current playable export and every diffusion painting, settings/graphs, lineage, noise/latent diagnostics and reference. Do not delete unique RIFE or motion frames as part of duplicate cleanup.
5. Keep the current project available locally. The next larger storage step would be a verified external archive for older frame sequences, with a small local index and the videos still reviewable. No external archive or backup is configured yet. Deleting rebuildable intermediate frames or changing their archive format remains a separate retention decision.

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

Validation: the repository's **63 local tests** pass, including archive corruption/mismatch rejection, archive hardlinks, extraction dry runs, independent writes to cloned copies, immutable targets, and the recurrent runner checks. Both latest full films decode successfully and the existing reviewer returns HTTP 200. No render recipe or reviewer UI changed.
