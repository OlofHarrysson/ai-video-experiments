# Canvas animation

Motion graphics written in TypeScript and drawn on an HTML canvas. Every frame is a pure function of time, so the browser preview and the headless render match exactly; soundtracks are synthesized in the same page with the Web Audio API and share the film's beat grid. This workflow is separate from diffusion (Deforum, ComfyUI), Blender and stop-motion.

- [AI Filmhack promo](projects/filmhack-promo/README.md): a 30-second Instagram Reel for the AI Filmhack event, with an original synthesized score.

Rendering uses the local Google Chrome through Playwright, and ffmpeg for encoding; no cloud compute. Downloaded fonts, dependencies and renders stay inside each project and are ignored by Git.
