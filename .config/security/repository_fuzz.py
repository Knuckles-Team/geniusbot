#!/usr/bin/env python3
# ruff: noqa: I001 -- synchronized across repositories with different import policies
"""Bounded, dependency-free fuzz smoke test for repository config parsers."""

from __future__ import annotations

import itertools
import json
import sys
import tomllib
from pathlib import Path


MAX_FILES = 16
MAX_SOURCE_BYTES = 1024 * 1024


def _corpus(root: Path) -> list[tuple[str, bytes]]:
    values: list[tuple[str, bytes]] = []
    try:
        candidates = sorted(
            path
            for path in root.iterdir()
            if path.suffix.casefold() in {".json", ".toml"}
        )[:MAX_FILES]
    except OSError:
        candidates = []
    for path in candidates:
        suffix = path.suffix.casefold()
        try:
            size = path.stat().st_size
            if path.is_symlink() or not 0 < size <= MAX_SOURCE_BYTES:
                continue
            values.append((suffix, path.read_bytes()))
        except OSError:
            continue
    return values


def _mutations(payload: bytes) -> tuple[bytes, ...]:
    midpoint = max(1, len(payload) // 2)
    return (
        payload[:midpoint],
        payload + b"\x00",
        b"{" * 128 + payload[:64],
        b"[" * 128 + payload[:64],
        payload[:32] + b"\xff\xfe" + payload[32:64],
        b"null trailing",
        b"key = [1, 2,",
        b"\n" * 4096 + payload[:128],
    )


def _exercise(suffix: str, payload: bytes) -> None:
    text = payload.decode("utf-8")
    if suffix == ".json":
        json.loads(text)
    else:
        tomllib.loads(text)


def _fuzz_pairs(corpus: list[tuple[str, bytes]]):
    for suffix, payload in corpus:
        for mutation in _mutations(payload):
            yield suffix, mutation


def _case_crashed(suffix: str, payload: bytes) -> bool:
    """Run one fuzz case. True only if the parser raised something other
    than an expected decode error -- an unexpected crash."""
    try:
        _exercise(suffix, payload)
    except (UnicodeDecodeError, json.JSONDecodeError, tomllib.TOMLDecodeError):
        return False
    except Exception:
        return True
    return False


def _run_cases(corpus: list[tuple[str, bytes]], limit: int) -> tuple[int, int]:
    """Exercise up to `limit` (suffix, mutation) fuzz cases, cycling the
    corpus if it's smaller than `limit`. Returns (cases, crashes)."""
    pairs = list(_fuzz_pairs(corpus))
    crashes = 0
    cases = 0
    for suffix, mutation in itertools.islice(itertools.cycle(pairs), limit):
        cases += 1
        if _case_crashed(suffix, mutation):
            crashes += 1
    return cases, crashes


def _write_report(output: Path, cases: int, crashes: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "version": 1,
                "kind": "fuzz",
                "passed": crashes == 0,
                "cases": cases,
                "failures": 0,
                "crashes": crashes,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def main() -> int:
    if len(sys.argv) != 2:
        return 2
    corpus = _corpus(Path.cwd()) or [(".json", b'{"seed": true}')]
    cases, crashes = _run_cases(corpus, 64)
    _write_report(Path(sys.argv[1]), cases, crashes)
    return 0 if crashes == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
