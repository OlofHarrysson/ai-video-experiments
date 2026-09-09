# Playful puppy: Blender authoring proof

Approved 2026-09-09. One puppy, a plain floor, three seconds: notice, play bow, gather, small forward hop, landing and recovery. Native editable Blender rig and keyframes, plus a rendered MP4. No generative video or frame interpolation.

The first proof uses an original simple sculpted puppy. This is a character-motion study; the earlier hand-painted anime finish and dog-park film are outside this test.

Acceptance: Blender installed through the authorized Homebrew path; script-driven bone poses and keyframes survive saving/reopening; full-body bow and airborne hop are visible; planted paws remain fixed during bow; landing has compression and recovery; inspect overview and dense transition frames. Retain drafts and final scene locally.

Implementation: Blender Python authoring, skinned mesh, two-bone leg IK with world-space paw controls, torso/head controls, and ear/tail follow-through. Render native frames, encode with FFmpeg. Small build/review scripts only.
