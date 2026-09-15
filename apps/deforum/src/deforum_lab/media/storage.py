"""Audit storage and retire scratch copies only after verifying retained archives."""

import argparse
import hashlib
import json
import os
import stat
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit(root):
    """Count allocated bytes once per inode, including existing hardlinks."""
    root = Path(root).resolve()
    seen = set()
    allocated = Counter()
    extensions = Counter()
    apparent = 0
    paths = 0
    for folder, dirs, names in os.walk(root):
        dirs.sort()
        for name in sorted(names):
            path = Path(folder) / name
            info = path.lstat()
            if not stat.S_ISREG(info.st_mode):
                continue
            paths += 1
            apparent += info.st_size
            key = (info.st_dev, info.st_ino)
            if key in seen:
                continue
            seen.add(key)
            size = info.st_blocks * 512
            allocated[path.relative_to(root).parts[0]] += size
            extensions[path.suffix] += size
    return {
        "root": str(root),
        "file_paths": paths,
        "unique_inodes": len(seen),
        "apparent_bytes": apparent,
        "allocated_file_bytes": sum(allocated.values()),
        "by_top_directory": dict(allocated.most_common()),
        "by_extension": dict(extensions.most_common()),
        "note": "Hardlinks counted once; APFS shared extents/snapshots are not measurable here.",
    }


def member_name(name):
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe archive member: {name}")
    return str(path)


def verified_archive(archive, expected_sha256):
    """Read every member without extracting another copy to disk."""
    archive = Path(archive)
    if archive.is_symlink() or digest(archive) != expected_sha256:
        raise ValueError(f"Archive hash mismatch or symlink: {archive}")
    result = {}
    with tarfile.open(archive, "r|*") as stream:
        for member in stream:
            if member.isdir():
                continue
            name = member_name(member.name)
            if name in result:
                raise ValueError(f"Repeated archive member: {name}")
            if member.isreg():
                data = stream.extractfile(member)
                result[name] = (
                    member.size,
                    hashlib.file_digest(data, "sha256").hexdigest(),
                )
            elif member.islnk():
                # Tar hardlinks refer to an earlier member; never re-decompress gzip.
                result[name] = result[member_name(member.linkname)]
            else:
                raise ValueError(f"Unsupported archive member: {name}")
    return result


def extraction_plan(extraction, members):
    """Reject the whole operation if any loose file is absent or different."""
    extraction = Path(extraction)
    if extraction.is_symlink() or not extraction.is_dir():
        raise ValueError("Expected an ordinary extraction directory")
    files = []
    for folder, dirs, names in os.walk(extraction):
        for name in dirs + names:
            path = Path(folder) / name
            if path.is_symlink():
                raise ValueError(f"Unexpected symlink: {path}")
            if path.is_dir():
                continue
            info = path.stat()
            if not stat.S_ISREG(info.st_mode):
                raise ValueError(f"Unexpected file type: {path}")
            relative = str(path.relative_to(extraction))
            if members.get(relative) != (info.st_size, digest(path)):
                raise ValueError(f"File is not preserved in the archive: {path}")
            files.append(path)
    return files


def retire_extraction(archive, extraction, expected_sha256, receipt, apply=False):
    archive, extraction, receipt = map(Path, (archive, extraction, receipt))
    # Only disposable session extractions, never project references/runs/exports.
    if (
        extraction.parent.resolve() != archive.parent.resolve()
        or not extraction.name.startswith(("downloaded-", "unpacked"))
        or archive.resolve().is_relative_to(extraction.resolve())
        or receipt.resolve().is_relative_to(extraction.resolve())
        or receipt.is_symlink()
        or (receipt.exists() and receipt.samefile(archive))
    ):
        raise ValueError(
            "Expected a sibling scratch extraction and an external receipt"
        )
    if receipt.exists():
        previous = json.loads(receipt.read_text())
        if (
            previous.get("archive") != str(archive.resolve())
            or previous.get("archive_sha256") != expected_sha256
            or previous.get("extraction") != str(extraction.resolve())
            or previous.get("applied") is not False
            or receipt.stat().st_nlink != 1
        ):
            raise ValueError("Existing receipt is not this operation's dry run")
    members = verified_archive(archive, expected_sha256)
    files = extraction_plan(extraction, members)
    result = {
        "archive": str(archive.resolve()),
        "archive_sha256": expected_sha256,
        "extraction": str(extraction.resolve()),
        "verified_files": len(files),
        "applied": False,
        "preservation": "Every loose file matches its retained archive member",
    }
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    if apply:
        # Recheck immediately before unlinking. Never recursively delete an unchecked addition.
        for path in files:
            key = str(path.relative_to(extraction))
            if path.is_symlink() or (path.stat().st_size, digest(path)) != members[key]:
                raise ValueError(f"Extraction changed during cleanup: {path}")
            path.unlink()
        for folder, _, _ in os.walk(extraction, topdown=False):
            Path(folder).rmdir()
        result["applied"] = True
        receipt.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("audit")
    scan.add_argument("root", type=Path)
    scan.add_argument("--report", required=True, type=Path)
    retire = commands.add_parser("retire-extraction")
    retire.add_argument("archive", type=Path)
    retire.add_argument("extraction", type=Path)
    retire.add_argument("--sha256", required=True)
    retire.add_argument("--receipt", required=True, type=Path)
    retire.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "audit":
        result = audit(args.root)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")
    else:
        result = retire_extraction(
            args.archive, args.extraction, args.sha256, args.receipt, args.apply
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
