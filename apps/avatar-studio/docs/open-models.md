# Open models and editable 3D avatars

Research checked 2026-09-30 against official repositories, model cards, documentation, and provider pricing. Prices are USD and may change. No paid generation was performed as part of this research.

The current priority is direct control over a character's appearance and performance. A real 3D scene fits that requirement. The video models below produce rendered video, not an editable mesh, facial rig, clothing system, or reusable camera. Their outputs can look three-dimensional without being editable 3D assets.

## Shortlist

| Model | Useful role | License and local requirements | Verified hosted option |
| --- | --- | --- | --- |
| **Qwen3-TTS 1.7B — Alibaba** | Scripted speech for the 3D character; clone a voice from a short recording, or use a designed/preset voice. | [Code](https://github.com/QwenLM/Qwen3-TTS) and [Base weights](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base): Apache 2.0. Official quickstart uses CUDA; no reliable minimum VRAM stated. The documented language list does not include Swedish. | fal [cloning](https://fal.ai/models/fal-ai/qwen-3-tts/clone-voice/1.7b): **$0.0008 per minute** of reference audio, as listed. fal [speech](https://fal.ai/models/fal-ai/qwen-3-tts/text-to-speech/1.7b): **$0.09 per 1,000 characters**. |
| **Wan 2.2 S2V — Alibaba** | Image + audio + motion prompt → talking video. A low-cost comparison for an eventual rendered-video workflow. | [Code/models](https://github.com/Wan-Video/Wan2.2): Apache 2.0. Official S2V single-GPU example requires **80GB VRAM**. The separate Wan 5B model's lower requirement does not apply to S2V. | [fal](https://fal.ai/models/fal-ai/wan/v2.2-14b/speech-to-video): **$0.10/video second at 480p**, **$0.15 at 580p**, **$0.20 at 720p**. Billing seconds are calculated at **16fps**. |
| **LongCat-Video-Avatar 1.5 — Meituan** | May 2026 upgrade for audio-driven characters, stylized subjects, and long video; eight-step distilled inference. | [Code](https://github.com/meituan-longcat/LongCat-Video) and [1.5 weights](https://huggingface.co/meituan-longcat/LongCat-Video-Avatar-1.5): MIT. CUDA stack; INT8 option. No dependable minimum VRAM found in the official material inspected. | [fal LongCat Single Avatar](https://fal.ai/models/fal-ai/longcat-single-avatar/image-audio-to-video): **$0.15/video second at 480p**, **$0.30 at 720p**. The hosted page does **not** establish that it runs v1.5. |
| **EchoMimic V3 — Ant Group** | Image + audio + prompt → talking character, including directed movement. Smaller model family worth comparing. | [Code](https://github.com/antgroup/echomimic_v3) and [weights](https://huggingface.co/BadToBest/EchoMimicV3): Apache 2.0. Official [UI configuration](https://github.com/antgroup/echomimic_v3/blob/main/app_mm.py) suggests shorter chunks for 12/16GB than 24GB GPUs; this is not a universal minimum-memory guarantee. | [fal](https://fal.ai/models/fal-ai/echomimic-v3): **$0.20/generated video second**, based on input-audio length. |
| **InfiniteTalk — MeiGen** | Animate a reference image or redub footage with matching lips, head, and body motion. | [Code/models](https://github.com/MeiGen-AI/InfiniteTalk): Apache 2.0. Wan 14B backbone; CUDA, offloading, and FP8 paths. Official docs warn of increasing color drift beyond one minute from a single image. No dependable numeric VRAM minimum verified. | No provider price verified. The official repository now points toward LongCat Avatar. |
| **MuseTalk 1.5 — Tencent Music** | Lip-sync existing footage while retaining the recorded performance. | [Code](https://github.com/TMElyralab/MuseTalk): MIT; trained models explicitly allowed for commercial use, with separate dependency licenses. Official speed claim: 30fps+ on V100. Processes a 256×256 face region; documented limitations include identity-detail loss and jitter. | Official Hugging Face demo linked from the repository. No paid hosting price verified. |

All video options still need speech supplied separately. No benchmark here establishes which best preserves Olof's face or preferred performance; a short comparison with the same portrait and recording would be needed.

### Voice control caveat

The fal [Qwen speech schema](https://fal.ai/models/fal-ai/qwen-3-tts/text-to-speech/1.7b/api) says the style prompt is ignored when a cloned speaker embedding is supplied. That path supports script control and cloned identity, but does not establish independent natural-language emotion control over the clone. A recorded performance gives direct control over pacing and emotion. Qwen's voice-design, preset-voice, and cloning capabilities are distinct modes.

## Exclusions

- **HunyuanVideo-Avatar:** the [Tencent community license](https://github.com/Tencent-Hunyuan/HunyuanVideo-Avatar/blob/main/LICENSE) excludes the EU, UK, and South Korea, with restrictions extending to outputs. It is unsuitable as the default Sweden-based experiment under that license.
- **Fish Speech / S2 Pro:** the [current repository](https://github.com/fishaudio/fish-speech) places both code and weights under the Fish Audio Research License. Do not describe it as a permissively licensed alternative to Qwen.

## Actual editable 3D

**Procedural browser character:** the smallest experiment for camera, appearance, expressions, audio playback, and export. It needs no model download or paid image/video inference. Its visual quality is limited by the authored geometry and materials; audio-energy mouth motion is not phoneme-accurate lip-sync. This is the current demo route.

**MetaHuman:** a stronger realism upgrade with actual meshes, rigs, appearance authoring, and facial animation. [Current licensing](https://www.metahuman.com/license) allows use with any engine or creative software and is free below $1 million in revenue under Unreal's standard terms. The [hardware guidance](https://dev.epicgames.com/documentation/metahuman/metahuman-hardware-requirements-in-unreal-engine?lang=en-US) recommends 16 physical cores, 32GB RAM, and RTX 3070/RX 6800 XT or Apple M2 Ultra with 8GB VRAM. Current documentation includes macOS support; older Windows-only advice is stale. This is a substantially heavier authoring workflow than the browser prototype.

**VRoid → VRM:** a practical stylized asset upgrade. [Own models can be commercially used](https://vroid.pixiv.help/hc/en-us/articles/4405813333657-Can-I-use-the-models-created-with-VRoid-Studio-Stable-Ver-for-commercial-purposes), subject to third-party asset terms. [VRM export](https://vroid.pixiv.help/hc/en-us/articles/15760756822297-I-want-to-learn-more-about-the-VRM-export-feature) retains configured expressions; preserve the `.vroid` source for continued character editing. [Each VRM carries permissions](https://vrm.dev/en/licenses/1.0/) for avatar use, modification, and redistribution. The format itself is not a blanket asset license. VRoid also restricts applications that generate/output modified combinations of its meshes and textures; assess that separately before building a character-creator product around its assets.

## Budget and access

- Prove the character controls with the local 3D demo first.
- Hosted Qwen speech costs cents for a short script. Cloning needs a clean recording and its reference text; it does not require cloning the face.
- If a video comparison becomes useful, reserve at most **$10** for a few 10-second runs: Wan 480p about **$1**, LongCat 480p about **$1.50**, EchoMimic about **$2** per run, before voice generation.
- Direct fal API access needs `FAL_KEY`; an existing connected fal integration can avoid adding another key. Voice cloning requires permission to upload the recording. Imported audio in the current local demo does not itself require an external API.
- Keep the total project limit at **$50** unless Olof explicitly raises it. This document records options, not authorization for additional provider purchases or runs.
