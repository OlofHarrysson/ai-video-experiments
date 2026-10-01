# Clay animation tools

Small assistant-operated Blender tools extracted for [Side by Side](../projects/clay-dance/README.md). Creative decisions and dance phrases remain with the project.

- `clay_stage.py`: procedural clay materials, two original puppet types, a lit stage, analytic fixed-length two-link limbs, native object-key baking and explicit interpolation modes.
- `render_clay.py`: reopen a self-contained `.blend` and render a range or selected native poses into a new directory. Retains source-frame numbers in its manifest. Current render device is local Apple Metal.
- `check_clay.py`: inspect the reopened scene against its pose manifest, including planted-shoe drift, floor penetration, shoe separation and projected character bounds. It is specialized to the Pip/Bo naming and clay-puppet dimensions; adapt those conventions explicitly for another cast.

The project authoring script loads the toolkit by a resolved file path, without changing `sys.path`. Outputs contain only ordinary Blender meshes, parents, materials and transform keys. Replaying a saved scene does not import this toolkit. The solver's geometry and beat-space target records make motion reviewable; hard-coded shape and timing choices remain easy to change.

Targets beyond limb reach and attempts to overwrite render folders fail explicitly. Pose sources, renders and final encodes have separate owners and locations. The tools neither start a server nor manage cloud infrastructure.
