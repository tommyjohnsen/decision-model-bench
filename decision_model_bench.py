#!/usr/bin/env python3
"""Benchmark decision models through an OpenAI-compatible HTTP endpoint."""

from __future__ import annotations

import argparse
import json
import math
import resource
import statistics
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class Case:
    case_id: str
    prompt: str
    expected: str


def load_cases(path: Path) -> list[Case]:
    cases: list[Case] = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                case = Case(str(item["id"]), str(item["prompt"]), str(item["expected"]))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"invalid case at line {line_number}: {exc}") from exc
            if not case.prompt.strip() or not case.expected.strip():
                raise ValueError(f"invalid case at line {line_number}: empty prompt or expected")
            cases.append(case)
    if not cases:
        raise ValueError("dataset contains no cases")
    return cases


def normalize(value: str) -> str:
    """Normalize a short verdict while avoiding substring-based false matches."""
    text = value.strip().casefold()
    if text.startswith("```") and text.endswith("```"):
        text = text[3:-3].strip()
    first_line = text.splitlines()[0].strip()
    return first_line.rstrip(".!,:;").strip()


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def peak_rss_mib() -> float:
    value = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # Linux reports KiB; macOS reports bytes.
    if sys.platform == "darwin":
        value /= 1024
    return value / 1024


def completion(endpoint: str, model: str, prompt: str, timeout: float) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 32,
        }
    ).encode()
    request = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.load(response)
        return str(body["choices"][0]["message"]["content"])
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"completion request failed: {exc}") from exc


def run(cases: Iterable[Case], endpoint: str, model: str, timeout: float) -> dict[str, Any]:
    results = []
    latencies = []
    for case in cases:
        started = time.perf_counter()
        output = completion(endpoint, model, case.prompt, timeout)
        latency_ms = (time.perf_counter() - started) * 1000
        correct = normalize(output) == normalize(case.expected)
        latencies.append(latency_ms)
        results.append(
            {
                "id": case.case_id,
                "expected": case.expected,
                "output": output,
                "correct": correct,
                "latency_ms": round(latency_ms, 3),
            }
        )
    return {
        "model": model,
        "endpoint": endpoint,
        "cases": len(results),
        "correct": sum(item["correct"] for item in results),
        "accuracy": sum(item["correct"] for item in results) / len(results),
        "latency_ms": {
            "mean": round(statistics.fmean(latencies), 3),
            "p50": round(statistics.median(latencies), 3),
            "p95": round(percentile(latencies, 0.95), 3),
        },
        "runner_peak_rss_mib": round(peak_rss_mib(), 3),
        "results": results,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("cases", type=Path, help="JSONL dataset")
    result.add_argument("--model", required=True, help="model identifier sent to the server")
    result.add_argument("--endpoint", required=True, help="OpenAI-compatible API base URL")
    result.add_argument("--timeout", type=float, default=60, help="per-request timeout in seconds")
    result.add_argument("--output", type=Path, help="write full JSON report to this file")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.timeout <= 0:
        raise SystemExit("--timeout must be positive")
    try:
        report = run(load_cases(args.cases), args.endpoint, args.model, args.timeout)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    summary = {key: report[key] for key in ("model", "cases", "correct", "accuracy", "latency_ms", "runner_peak_rss_mib")}
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
