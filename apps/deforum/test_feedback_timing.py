"""Frame-rate migration must preserve physical repaint instants."""
import unittest
from fractions import Fraction
from feedback_timing import FeedbackTiming


class TimingTests(unittest.TestCase):
    def test_new_defaults_are_24fps_and_interpolated(self):
        t=FeedbackTiming()
        self.assertEqual((t.fps,t.cadence,t.start,t.count,t.interpolate),(24,6,72,72,True))

    def test_all_previous_cadences_keep_the_same_repaint_times(self):
        for cadence in (3,7,10,15):
            a=FeedbackTiming(fps=12,repaint_seconds=Fraction(cadence,12))
            b=FeedbackTiming(repaint_seconds=Fraction(cadence,12))
            self.assertEqual(b.cadence,2*cadence)
            self.assertEqual([a.seconds(i) for i in range(a.start,a.start+a.count,a.cadence)],
                             [b.seconds(i) for i in range(b.start,b.start+b.count,b.cadence)])

    def test_unrepresentable_intervals_do_not_silently_change_pacing(self):
        for value in (Fraction(1,10),0,-1):
            with self.assertRaises(ValueError):FeedbackTiming(repaint_seconds=value)


if __name__=='__main__':unittest.main()
