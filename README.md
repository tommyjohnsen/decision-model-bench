<!--
PROVENANCE (mirror of .provenance/ledger.jsonl; ledger wins)
written-by: unknown (pre-provenance) | 2026-10-15 | b698260
modified-by: codex/gpt-5.6-sol | 2026-10-26 | f104964 | provenance block added
reviewed-by: claude-code/claude-opus-5-5 | 2026-10-26 | APPROVE
END PROVENANCE
-->
# decision-model-bench

A small, dependency-free benchmark for decision and verdict models served by an OpenAI-compatible HTTP API. It sends labeled JSONL cases, scores exact normalized verdicts, and reports accuracy, request latency, and the benchmark runner's peak resident memory (RSS).

## Install

Python 3.10 or newer is sufficient; there are no third-party packages.

```sh
git clone <repository-url>
cd decision-model-bench
python3 -m unittest -v
```

Start a local model server that exposes `/v1/chat/completions`, such as llama.cpp's server mode.

## Usage

Each JSONL record needs string fields `id`, `prompt`, and `expected`:

```json
{"id":"case-1","prompt":"Reply allow or deny: ...","expected":"allow"}
```

Run the benchmark:

```sh
python3 decision_model_bench.py examples/cases.jsonl \
  --model local-model \
  --endpoint YOUR_API_BASE_URL \
  --output report.json
```

The summary is printed to standard output. `--output` saves the summary plus every raw model response. Use `--timeout` to change the per-request timeout.

## Limits

- Scoring compares the normalized first response line with the expected label. It is intentionally strict and does not judge semantic equivalence.
- Requests run sequentially, so latency represents end-to-end single-request behavior rather than throughput.
- RSS measures the benchmark runner, not a separately running model server. Use server-side metrics to measure model memory.
- The endpoint is expected to require no authentication. Put authentication and transport controls in a trusted local proxy if needed.
- Case prompts and raw outputs are written to the report when `--output` is used; do not use sensitive data without an appropriate handling policy.

## License

Apache-2.0. See LICENSE and NOTICE.
