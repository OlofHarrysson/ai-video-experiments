# Listening route evaluation

2026-10-10. These are small controlled observations within a composition sprint, not an audio-understanding benchmark or taste validation. Paid calls used the existing OpenRouter key. Each route was explicitly selected; no automatic fallback or retry occurred.

| Model / route | Observation | Consequence |
|---|---|---|
| Gemini 3.1 Pro / Google | Duplicate control identified; detected two novel injected gaps but misplaced their boundaries; some real differences detected; false reversal narrative and missed exposed low-frequency change | No subtle mix adjudication; local verification and human taste judgment required |
| GPT Audio / OpenAI | Duplicate described as essentially identical; initial dropout query received a promise to analyze; novel two-gap probe falsely called continuous | Not adopted for selection |
| MiMo 2.6 Pro / DeepInfra | Apparent initial control successes, then missing-audio claims on unchanged-source and filter controls; zero audio-token usage reported | Initial apparent passes withdrawn; end-to-end audio processing not established |
| MiMo 2.6 Pro / Xiaomi | Explicit first-party route probe timed out after 600 seconds | Provider outcome/cost unknown; not retried |

The novel probe is a 14-second excerpt from Latch v002 with digital silence at 3.25–4.5 and 10.25–10.75 seconds. The prompt gives only total duration and asks for any silence, not its expected position or count. Encoded files, hashes, prompts, provider responses and receipts remain in ignored `screening/`.

The adapter follows the documented [OpenRouter audio input format](https://openrouter.ai/docs/guides/overview/multimodal/audio): base64 WAV with an `input_audio` content part and format field. [Xiaomi's own audio-understanding guide](https://mimo.mi.com/docs/en-US/quick-start/usage-guide/multimodal-understanding/audio-understanding) advertises the selected full model. Catalog metadata and documentation do not establish successful behavior through a particular route; the cause of the inconsistent MiMo observations is unresolved.

`status: complete` means a nonempty provider reply with a stop finish reason, not a useful or correct answer. Human adjudication remains necessary. The default model remains Gemini 3.1 Pro Preview with high reasoning. Other models only run when explicitly selected by `--model`; `--provider` can pin one route, and all fallbacks remain disabled.

The [short-window follow-up](critic/short-review-calibration.md) includes a sample-identical two-second duplicate that received confident claims of different low weight. The narrowed format demonstrably invented a difference; it is not a protocol improvement. The first three-second crop also diluted the intended contrast by including neighboring kicks, illustrating why the submitted matched file must be checked, not only the original source window.
