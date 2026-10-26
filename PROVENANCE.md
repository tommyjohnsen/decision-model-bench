# Provenance

Generated from `.provenance/ledger.jsonl` by the operator tool; do not edit by hand. The ledger is the record of truth; per-file `PROVENANCE` headers mirror it, and the ledger wins on any disagreement.

Each ledger line is one JSON object with `path`, `blob`, `event` (`written` or `reviewed`), `by` (seat/model, or `unknown (pre-provenance)` for history whose author is not recorded), `date`, and either `commit` (written) or `verdict`, `head` and `record` (reviewed). Verdicts are `APPROVE`, `APPROVE_WITH_NITS` or `REJECT`.

`blob` is the git blob SHA-1 of the file after removing its PROVENANCE header block: the lines from the `PROVENANCE` line through the `END PROVENANCE` line inclusive, plus a directly enclosing `<!--` / `-->` line pair. A review applies only while the file's current `blob` equals the reviewed one; any content change makes it stale. A release needs current reviews from claude-code and grok-build; an author never reviews its own work.

Files tracked: 7 (excluding this summary and `.provenance/`). Inline headers: 4. Ledger-only: 3. Written entries current: 7/7. Current reviews: claude-code 7, grok-build 0. Current REJECTs: 0.

| path | header | written-by (current content) | claude-code | grok-build |
|---|---|---|---|---|
| `.gitignore` | inline | unknown (pre-provenance) | APPROVE | - |
| `LICENSE` | ledger | unknown (pre-provenance) | APPROVE | - |
| `NOTICE` | ledger | unknown (pre-provenance) | APPROVE | - |
| `README.md` | inline | unknown (pre-provenance) | APPROVE | - |
| `decision_model_bench.py` | inline | unknown (pre-provenance) | APPROVE | - |
| `examples/cases.jsonl` | ledger | unknown (pre-provenance) | APPROVE | - |
| `test_decision_model_bench.py` | inline | unknown (pre-provenance) | APPROVE | - |
