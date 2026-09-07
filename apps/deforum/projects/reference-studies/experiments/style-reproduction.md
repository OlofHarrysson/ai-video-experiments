# First style-reproduction study

Status: accepted by Olof and implemented in the separate [Brain Entity style study](../../brain-entity-study/experiments/style.md). This document retains the evaluation brief; results and every generation belong to that project.

## Target

Use [Brain Entity](../references/brain-entity.md), especially 36–42s, as the first benchmark. Make a new six-second orange/teal graphic illustration in which a central circular opening changes between mechanical and organic forms. The viewer should notice intentional transformation and sustained visual detail. The blue/black ink style of [Tomorrow](../references/tomorrow.md) is a separate second benchmark.

Olof explicitly said the current style is not good enough and wants to reproduce qualities of existing good-looking art first. Both references are identified as Deforum; no requirement to use identical models/settings. Treat this as the current quality criterion. Earlier fixed-seed and scene-preservation wins remain technical findings, not proof of artistic success.

## Smallest next test

1. Produce a small set of original still candidates beside a reference frame. Match large shapes, line character, palette, contrast and density of detail before paying for a sequence. Start by testing the creator-credited SDXL art LoRA if available/compatible; model choice serves the image target.
2. Animate one selected candidate for six seconds with one planned ring transformation. A simple animated silhouette/control guide is a hypothesis for maintaining composition during stronger repainting. Verify actual ControlNet compatibility before inference; do not copy our depth-only marsh workflow unchanged.
3. Compare start/middle/end and short intervals around the transformation against the reference. Render a second version only to address a visible mismatch. Preserve all attempts and expose the video in chat.

## Review criteria

| Criterion | Desired evidence |
| --- | --- |
| Graphic identity | Strong black ground, orange accents, teal/cyan/cream forms, confident dark contours. |
| Composition | One dominant opening; deliberate space around it; supporting details do not hide the focal point. |
| Detail over time | Crisp illustrated texture persists beyond the first second without progressive blur. |
| Transformation | The dominant shape clearly develops across the clip; movement is more than a small static-image pan. |
| Consistency of style | Surfaces and subject may morph while palette, line character and rendering style stay recognizable. |
| Playback | Review motion, discontinuities and tempo directly; a sharp contact sheet is insufficient. |

Camera calibration, control strength, prompt travel, seed/cadence and optional interpolation are variables to investigate. Exact values are not recoverable from the reference and should be chosen through bounded tests. Audio may follow once the visual study works; exact song/beat reproduction is outside this first test.
