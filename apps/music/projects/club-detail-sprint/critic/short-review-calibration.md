# Short audio-review calibration

2026-10-10. Question: can short isolated windows and a narrow prompt recover the known added low-frequency component in Pressure v006 versus v005, which a longer review missed?

All three requests used Gemini 3.1 Pro Preview through OpenRouter/Google, high reasoning, the same narrowly worded low-weight question with adjusted timing, anonymous version labels, loudness matching and a one-second separating gap. The adapter reported audio tokens. Each completed with `finish_reason: stop`; none was retried automatically.

| Condition | Objective contrast | Response | Interpretation |
| --- | --- | --- | --- |
| 3 s per take, source 11.25–14.25 s | Neighboring kick transients diluted the matched low-band difference to +1.29 dB in B; body −0.91 dB | Indistinguishable, exact same tonal balance | Failed discrimination, but weaker than intended because the crop included adjacent groove |
| 2 s per take, source 11.5–13.5 s | Fully inside exposure. B low-band +8.63 dB, body −1.66 dB after matching | A fuller/heavier, B thinner | Direction conflicts with measured low-band contrast; not usable for this distinction |
| Exact duplicate of the 2 s v006 passage | Sample-identical int16 excerpts; maximum difference 0 | A heavier, B lowest frequencies reduced | Demonstrated false positive |

The last condition establishes that this focused short format can invent tonal differences even when there is no audio difference. It does not rescue the review protocol. Stop tuning subtle low-frequency weight to these reports. They may still suggest broad questions to inspect, but neither confident prose nor a completed request establishes correct hearing.

The duplicate failure also limits inference from a prior longer duplicate test that passed: performance changed across conditions. No general reliable discrimination rate is established by these few tests.

## Retained evidence

Under `.local/`:

- `pressure-short-low-control/` and `pressure-short-low-review/`: seven-second pair and receipt, $0.014404.
- `pressure-isolated-low-control/` and `pressure-isolated-low-review/`: five-second changed pair and receipt, $0.008400.
- `pressure-isolated-duplicate-control/` and `pressure-isolated-duplicate-review/`: five-second exact duplicate, sample equality check and receipt, $0.010236.

The first crop's limitation was identified from the actual submitted matched files, then a different fully isolated condition was prepared. This distinction matters: an intended strong manipulation can become weaker after excerpt selection and matching. All costs and request outcomes are recorded in `review-evidence.json`.
