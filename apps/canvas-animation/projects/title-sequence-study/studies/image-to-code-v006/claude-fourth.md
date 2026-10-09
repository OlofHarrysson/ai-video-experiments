# Fourth visual consultation

Read-only Claude Code consultation, 2026-10-09. Author model: claude-opus-5-5. Reviewed output-sculpt-02 against the generated reference.

I'd now put it at about **7.5/10**, up from 7. The material changes worked, but the S has a bigger problem than its curl: the whole upper half and spine are mis-traced. I've included a replacement path below that fixes the curl as part of that. I didn't modify any files; the scratch images are in `/tmp/wh8/`, outside the repo.

## Did the changes improve it?

| Change | Verdict |
|---|---|
| Darker sidewalls | **Clear win.** The bright lavender slab is gone and the letters finally sit in depth like the reference. |
| Gold plinth and star | **Win.** It now reads as a pedestal, and the WILD/HOURS hierarchy is cleaner. |
| Gold O star, faceted spurs | Small win. It's correct jewellery, but too small to matter at normal size. |
| H crossbar | Fine, neutral. |
| Custom face patches | **Roughly neutral.** At normal size they're mostly invisible on W and D. On I and L they read as faint washes, not as obviously flat panels. They don't hurt, but they don't deliver the reference's broad lit-to-shadow sheen either. Don't spend more time on them. |
| Redrawn S | **Not fixed.** Your instinct is right, and the cause is bigger than the curl. |

## ⚠️ RISK OR DEVIATION: the S is mis-traced, and the curl problem comes from that

I measured the reference's ivory face edges and compared them with your S path:

| Row | Reference left edge | Ours |
|---|---|---|
| y=660 | 1165 | 1140 |
| y=720 | 1190 | 1153 |
| y=760 | 1243 | 1194 |

- **Spine is offset.** Our spine and upper bowl sit 20–49px left of and below the reference. The spine's lower edge passes (1234,781), where the reference passes about (1234,756).
- **That squeezes the lower counter.** It leaves no room around the curl, so the curl's top ends up about 10px from the spine.
- **The renderer then fills the gaps.** It adds about 12px of red and gold *outward* from every face edge. Any face-to-face gap under about 24px therefore fills completely.
  - That fill causes the cusp and pinch where the curl meets the spine.
  - It also causes the tiny red dot of an eye: the path's eye is about 28px across, so only about 4px is left after the bands.
- **The reference keeps its gaps open.** The curl ball has 40–70px of dark around it, and the eye notch is about 32×48px.

## Proposed S path (drop-in replacement for `geometry.js` `id:'S'`)

```
M 1331 602 C 1316 630 1312 662 1322 692
C 1310 662 1294 632 1272 615 C 1250 602 1219 603 1209 626
C 1200 648 1220 678 1254 700 C 1300 728 1352 758 1368 800
C 1384 842 1372 898 1336 928 C 1300 954 1232 954 1194 936
C 1176 926 1170 908 1172 890 C 1168 846 1184 792 1222 788
C 1250 786 1264 810 1262 832 C 1260 860 1242 878 1218 877
C 1208 876 1202 870 1205 862 C 1208 856 1216 856 1221 852
C 1234 842 1234 818 1212 813 C 1192 809 1184 828 1186 850
C 1188 874 1200 893 1224 905 C 1260 920 1306 914 1322 880
C 1334 846 1318 812 1290 795 C 1258 775 1210 744 1186 714
C 1168 694 1160 666 1166 640 C 1172 612 1200 596 1240 593
C 1275 591 1306 600 1331 602 Z
```

What it changes:
- **Upper bowl, spine and outer bowl** now follow the reference's ivory face edges.
- **The curl** is a round ball whose spiral terminal tucks in at the lower left, matching the reference's eye placement:
  - about 37px of face clearance to the spine, so a dark gap survives the bands;
  - an eye about 40px across, leaving a visible dark core of roughly 15px inside the gold;
  - a 12–17px gap between the terminal and the stem, so the bands bridge it as a gold spiral seam, as in the reference.
- **The beak and the R-leg merge** are essentially unchanged.

How I checked it: I wrote a simulator of the 12px red/gold band offset. It reproduces the current pinch and tiny eye exactly. With the new path the counter is open, the curl is free-standing and the eye is clearly readable at 1×. Compare `/tmp/wh8/cand3_1x.png` (reference | current | v2 | proposed) and `/tmp/wh8/cand3.png` at 2×.

Remaining caveats:
- The simulation has no shading. Confirm with a real render and re-check the sidewall around the curl.
- The reference curl is still a slightly fatter ball. If it reads as a "6" hook in the real render, push the top-right control points about 4px outward.

## The two strongest remaining changes at normal size

1. **The S above.** It's the end of HOURS and the most visible geometric flaw left. It's a path swap, about 15 minutes plus a re-render.
2. **A warm light pass on the glints and gold.** This is a judgment call between this and pink modelling, but it's what I notice first at full-image size.
   - **Glints:** the reference has about 8 glints. They're warm gold, with long cross rays and a 60–80px bloom, each sitting on a rim hotspot. Ours are a few tiny white sparks. This, more than geometry, is what still reads as "clean vector" rather than "polished".
   - **Gold:** on the pink letters our gold also reads pale lemon. Give the rim profile a deeper orange-brown low end so it reads as metal against the pink.
   - **Cost:** about 45 minutes, all in `renderer.js`, with no geometry changes.

Pink face modelling is a close third. If the motion preview shows the pink looking flat in movement, it may overtake the glints.
