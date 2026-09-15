import io
import os
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

from deforum_lab.media.clones import copy_media, share_duplicate
from deforum_lab.media.storage import audit, digest, retire_extraction


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.archive = self.root / "complete.tar.gz"
        with tarfile.open(self.archive, "w:gz") as stream:
            item = tarfile.TarInfo("art/frame.png")
            item.size = 5
            stream.addfile(item, io.BytesIO(b"image"))
            linked = tarfile.TarInfo("art/copy.png")
            linked.type = tarfile.LNKTYPE
            linked.linkname = "art/frame.png"
            stream.addfile(linked)
        self.extraction = self.root / "downloaded-complete"
        (self.extraction / "art").mkdir(parents=True)
        for name in ("frame.png", "copy.png"):
            (self.extraction / "art" / name).write_bytes(b"image")

    def retire(self, apply=False, expected=None):
        return retire_extraction(
            self.archive,
            self.extraction,
            expected or digest(self.archive),
            self.root / "receipt.json",
            apply,
        )

    def test_verified_hardlink_archive_and_dry_run(self):
        self.assertFalse(self.retire()["applied"])
        self.assertTrue(self.extraction.exists())
        archive_hash = digest(self.archive)
        self.assertTrue(self.retire(apply=True)["applied"])
        self.assertFalse(self.extraction.exists())
        self.assertEqual(digest(self.archive), archive_hash)

    def test_unarchived_or_modified_file_prevents_any_deletion(self):
        for name in ("new.png", "frame.png"):
            path = self.extraction / "art" / name
            path.write_bytes(b"different")
            with self.assertRaisesRegex(ValueError, "not preserved"):
                self.retire(apply=True)
            self.assertTrue((self.extraction / "art/copy.png").exists())
            path.unlink()

    def test_bad_archive_hash_prevents_deletion(self):
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.retire(apply=True, expected="0" * 64)
        self.assertTrue(self.extraction.exists())

    def test_receipt_cannot_overwrite_retained_archive_or_unrelated_file(self):
        expected = digest(self.archive)
        for receipt in (self.archive, self.root / "unrelated.json"):
            if receipt != self.archive:
                receipt.write_text('{"important": true}')
            with self.assertRaises(ValueError):
                retire_extraction(
                    self.archive, self.extraction, expected, receipt, True
                )
            self.assertEqual(digest(self.archive), expected)
            self.assertTrue(self.extraction.exists())

    def test_symlink_prevents_deletion(self):
        (self.extraction / "external").symlink_to(self.archive)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.retire(apply=True)
        self.assertTrue(self.extraction.exists())

    def test_audit_counts_hardlinked_bytes_once(self):
        before = audit(self.root)
        os.link(self.archive, self.root / "alias.tar.gz")
        after = audit(self.root)
        self.assertEqual(before["allocated_file_bytes"], after["allocated_file_bytes"])
        self.assertEqual(before["file_paths"] + 1, after["file_paths"])

    def test_new_media_copy_preserves_source_and_refuses_overwrite(self):
        source = self.extraction / "art/frame.png"
        target = self.root / "new.png"
        copy_media(source, target)
        self.assertEqual(target.read_bytes(), source.read_bytes())
        target.write_bytes(b"changed")
        self.assertEqual(source.read_bytes(), b"image")
        with self.assertRaises(FileExistsError):
            copy_media(source, target)

    @unittest.skipUnless(sys.platform == "darwin", "APFS-specific optimization")
    def test_clone_preserves_bytes_and_independent_future_writes(self):
        source = self.extraction / "art/frame.png"
        target = self.extraction / "art/copy.png"
        before = target.stat().st_mtime_ns
        self.assertTrue(share_duplicate(source, target, digest(source)))
        self.assertNotEqual(source.stat().st_ino, target.stat().st_ino)
        self.assertEqual(target.stat().st_mtime_ns, before)
        self.assertEqual(source.read_bytes(), target.read_bytes())
        target.write_bytes(b"changed")
        self.assertEqual(source.read_bytes(), b"image")

    @unittest.skipUnless(sys.platform == "darwin", "APFS-specific optimization")
    def test_clone_refuses_different_bytes_and_skips_existing_hardlinks(self):
        source = self.extraction / "art/frame.png"
        target = self.extraction / "art/copy.png"
        target.write_bytes(b"other")
        with self.assertRaisesRegex(ValueError, "contents differ"):
            share_duplicate(source, target, digest(source))
        self.assertEqual(target.read_bytes(), b"other")
        os.link(target, target.with_suffix(".alias"))
        self.assertFalse(share_duplicate(source, target, digest(source)))


if __name__ == "__main__":
    unittest.main()
