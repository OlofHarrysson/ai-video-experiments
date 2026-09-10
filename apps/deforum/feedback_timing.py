"""Time-based defaults for new feedback experiments; historical recipes stay explicit."""
from dataclasses import dataclass
from fractions import Fraction


def whole_frames(seconds, fps):
    frames=Fraction(str(seconds))*fps
    if frames.denominator!=1:
        raise ValueError(f'{seconds} seconds is not an exact frame interval at {fps} fps')
    return int(frames)


@dataclass(frozen=True)
class FeedbackTiming:
    fps: int=24
    repaint_seconds: Fraction=Fraction(1,4)
    duration_seconds: Fraction=Fraction(3)
    start_seconds: Fraction=Fraction(3)
    interpolate: bool=True

    def __post_init__(self):
        if self.fps<1 or self.repaint_seconds<=0 or self.duration_seconds<=0 or self.start_seconds<0:
            raise ValueError('FPS, repaint interval and duration must be positive; start must be nonnegative')
        for value in (self.repaint_seconds,self.duration_seconds,self.start_seconds):whole_frames(value,self.fps)

    @property
    def cadence(self):return whole_frames(self.repaint_seconds,self.fps)
    @property
    def count(self):return whole_frames(self.duration_seconds,self.fps)
    @property
    def start(self):return whole_frames(self.start_seconds,self.fps)
    def seconds(self,global_frame):return float(Fraction(global_frame,self.fps))
