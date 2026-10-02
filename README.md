# Project SEKAI Event Competition Analysis

Japanese-server event rankings (ranking cut-offs) of *Project SEKAI COLORFUL STAGE!*, analysed to understand how competition changes across event formats and over time.

> **2026 update — the 2025 conclusions are superseded.** A re-analysis (`v2_2026/`) found two problems in the original version and extended the data to Sept 2026. The original 2025 files are kept unchanged in the repo root for reference, but their headline claims ("the gap between top and casual players widened after the CN server launch", "the CN launch brought players back") do not hold.

## v2 (2026) — current

**Data.** Final ranking cut-offs from the public [sekai.best](https://sekai.best/) API for events 120–218 (events starting 2024-01-31 to 2026-09-14): 96 events (75 marathon, 15 World Link, 6 Cheerful Carnival) plus 70 World Link character chapters. Event metadata from [Sekai-World/sekai-master-db-diff](https://github.com/Sekai-World/sekai-master-db-diff).
Quality checks: the 61 events overlapping the 2025 hand-collected table match within 0.09%; two incomplete sekai.best snapshots (event 126, event 124 chapter 3) and events 120–123 (not tracked) use the 2025 table; event 199 has no data and is dropped; anniversary finales 180 and 218 are excluded; every newly added event's final snapshot is within 15 minutes of the event end.

**What was wrong in v1.**
1. World Link events have one row for the whole event plus one row per chapter; v1 treated all of them as separate events (double counting).
2. Different event formats were pooled. World Link rows are far more competitive than marathons, and their share of the sample rose after the CN launch, which created an apparent rise in competition.
3. Only before/after means were compared, without checking the pre-existing trend.

How the headline shrinks as the comparison gets cleaner (CN launch before → after, means; top = rank 1,000, gap = rank 1,000 ÷ rank 100,000):

| Counting rule | Top | Gap |
|---|---|---|
| Event rows + chapter rows pooled (v1 style) | +62% | +22% |
| One row per event, all types pooled | +30% | +8% |
| One row per event, marathons only | +6% | +2% |

**Findings.**
1. *Casual-player participation rose, then fell.* The marathon rank-100,000 cut-off (points per day) grew about +2.7% per month in the 14 months before the CN launch and fell about −2.6% per month in the 18 months after (both p < 1e-6; n = 34 / 41). The turning point coincides with the CN launch, but these data cannot separate causes (players moving to the CN server, the JP server's own content cycle, or something else).
2. *Within the same format, the top/casual gap did not widen* (marathon median 11.9× → 12.0×, p = 0.72).
3. *Single-character World Link chapters concentrate competition at the top*: median gap ≈ 47–54× versus 12× for marathons. 2-day and 3-day chapters do not differ significantly (p = 0.5), so duration alone does not explain the concentration. These are observational associations.

**Design implications (interpretation, not proven by the data).**
- To track broad participation, watch mid-tier cut-offs; top cut-offs barely moved while casual participation was rising.
- Event theme scope is worth testing as a lever on competitive pressure; shortening an event is unlikely to help on its own.
- Compare event "heat" across periods only after stratifying by event type, otherwise a change in the schedule mix changes the conclusion.

**Reproduce.**
```bash
cd v2_2026
python3 fetch_sekai_best.py   # optional: re-scrape (~1 request/s); writes sekai_best_borders.csv
python3 reanalysis2.py        # stratified comparisons, interrupted time series, format comparison
python3 charts2.py            # fig1_mass_trend.png, fig2_format_gap.png
```
Requires pandas, numpy, scipy, statsmodels, matplotlib. Chinese write-up: `v2_2026/FINDINGS_zh.md`.

## v1 (2025) — original project, kept for reference

`pjsk_project.ipynb` / `pjsk_project.py`, `pjsk_events.csv`, `pjsk_chara.csv`, `pjsk_predict.csv`, and the slide deck. See the note above for why its conclusions are superseded.
