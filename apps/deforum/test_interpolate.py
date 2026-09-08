"""Timing and source-inventory checks; actual RIFE/MPS is verified by saved pair runs."""

from fractions import Fraction
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from interpolate import frame_plan, inventory


class TimingTests(unittest.TestCase):
    def test_nine_second_cadence_frames_doubled_without_retiming(self):
        rows = frame_plan(108, multiplier=2)
        self.assertEqual(len(rows), 216)
        self.assertEqual(Fraction(len(rows), 24), 9)
        for index, row in enumerate(rows):
            if row['kind'] == 'anchor':
                self.assertEqual(Fraction(index, 24), Fraction(row['source_index'], 12))
            elif row['kind'] == 'interpolation':
                self.assertEqual(Fraction(index, 24),
                    (row['source_pair'][0] + Fraction(row['timestep'])) / 12)
        self.assertEqual(rows[-1], {'kind':'final_hold','source_index':107})

    def test_six_second_timeline_and_original_sample_instants(self):
        rows = frame_plan(48)
        self.assertEqual(len(rows), 144)
        self.assertEqual(Fraction(len(rows), 24), 6)
        anchors = [(index, row["source_index"]) for index, row in enumerate(rows)
                   if row["kind"] == "anchor"]
        self.assertEqual(len(anchors), 48)
        for delivery, source in anchors:
            self.assertEqual(Fraction(delivery, 24), Fraction(source, 8))
        self.assertEqual([row["kind"] for row in rows[-3:]], ["anchor", "final_hold", "final_hold"])
        self.assertTrue(all(row["source_index"] == 47 for row in rows[-3:]))
        interpolated = [(index, row) for index, row in enumerate(rows) if row["kind"] == "interpolation"]
        self.assertEqual(len(interpolated), 94)
        for index, row in interpolated:
            a, b = row["source_pair"]
            self.assertEqual(b, a + 1)
            self.assertEqual(Fraction(index, 24), (a + Fraction(row["timestep"])) / 8)

    def test_first_pair_is_two_anchors_and_two_inferences_without_holds(self):
        rows = frame_plan(2, final_holds=0)
        self.assertEqual([row["kind"] for row in rows],
                         ["anchor", "interpolation", "interpolation", "anchor"])
        self.assertEqual([row["timestep"] for row in rows[1:3]], ["1/3", "2/3"])


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for index in range(48):
            Image.new("RGB", (16, 8), (index, 0, 0)).save(self.root / f"{index}.png")

    def test_numeric_order_and_read_only_inventory(self):
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.iterdir()}
        files, rows = inventory(self.root)
        self.assertEqual([p.stem for p in files], [str(i) for i in range(48)])
        self.assertEqual(len({row["sha256"] for row in rows}), 48)
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.root.iterdir()})

    def test_missing_frame_is_rejected(self):
        (self.root / "4.png").unlink()
        with self.assertRaisesRegex(ValueError, "exactly 48"):
            inventory(self.root)

    def test_duplicate_numeric_index_is_rejected(self):
        (self.root / "4.png").rename(self.root / "00.png")
        with self.assertRaisesRegex(ValueError, "unique and contiguous"):
            inventory(self.root)

    def test_mismatched_dimensions_are_rejected(self):
        Image.new("RGB", (18, 8)).save(self.root / "4.png")
        with self.assertRaisesRegex(ValueError, "dimensions differ"):
            inventory(self.root)


if __name__ == "__main__":
    unittest.main()
