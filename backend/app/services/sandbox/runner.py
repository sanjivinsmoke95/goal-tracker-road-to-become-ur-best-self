"""Isolated code runner (Milestone 9).

User code NEVER runs inside the API process. Each run happens in a separate
subprocess, in a throwaway temp directory, with a wall-clock timeout, capped
output, and (on POSIX) CPU/address-space rlimits.

This is the initial sandbox. For untrusted/multi-user production, front it with
a container/nsjail per run — the interface here (run_code) stays the same.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass

TIMEOUT_SECONDS = 5
MAX_OUTPUT = 64 * 1024  # 64 KB
CPU_SECONDS = 5
ADDRESS_SPACE = 512 * 1024 * 1024  # 512 MB


@dataclass
class RunResult:
    stdout: str
    stderr: str
    exit_code: int | None
    time_ms: int
    timed_out: bool
    error: str | None = None


def _which(*names: str) -> str | None:
    for n in names:
        if shutil.which(n):
            return n
    return None


# language -> (source filename, compile cmd or None, run cmd)
def _plan(language: str, workdir: str) -> tuple[str, list[str] | None, list[str]] | None:
    lang = language.lower()
    if lang == "python":
        py = _which("python3", "python")
        return ("main.py", None, [py or sys.executable, "main.py"])
    if lang in ("javascript", "js", "node"):
        node = _which("node")
        return ("main.js", None, [node, "main.js"]) if node else None
    if lang in ("typescript", "ts"):
        tsx = _which("tsx") or _which("ts-node")
        node = _which("node")
        if tsx:
            return ("main.ts", None, [tsx, "main.ts"])
        return ("main.ts", None, [node, "--experimental-strip-types", "main.ts"]) if node else None
    if lang in ("cpp", "c++"):
        gpp = _which("g++", "clang++")
        if not gpp:
            return None
        return ("main.cpp", [gpp, "-O2", "-std=c++17", "main.cpp", "-o", "prog"], [os.path.join(workdir, "prog")])
    return None


SUPPORTED = ["python", "javascript", "typescript", "cpp"]


def _limits():  # pragma: no cover - POSIX only, exercised at runtime
    try:
        import resource

        resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
        try:
            resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE, ADDRESS_SPACE))
        except (ValueError, OSError):
            pass  # RLIMIT_AS unsupported on some platforms (e.g. macOS)
    except Exception:
        pass


def _trunc(s: str) -> str:
    return s if len(s) <= MAX_OUTPUT else s[:MAX_OUTPUT] + "\n…[output truncated]"


def run_code(language: str, code: str, stdin: str = "") -> RunResult:
    workdir = tempfile.mkdtemp(prefix="sandbox-")
    try:
        plan = _plan(language, workdir)
        if plan is None:
            return RunResult("", "", None, 0, False, error=f"Language '{language}' is not available on this host.")
        filename, compile_cmd, run_cmd = plan
        with open(os.path.join(workdir, filename), "w") as f:
            f.write(code)

        preexec = _limits if os.name == "posix" else None

        if compile_cmd:
            comp = subprocess.run(compile_cmd, cwd=workdir, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
            if comp.returncode != 0:
                return RunResult("", _trunc(comp.stderr), comp.returncode, 0, False, error="Compilation failed")

        start = time.monotonic()
        try:
            proc = subprocess.run(
                run_cmd, cwd=workdir, input=stdin, capture_output=True, text=True,
                timeout=TIMEOUT_SECONDS, preexec_fn=preexec,
            )
        except subprocess.TimeoutExpired:
            return RunResult("", "", None, TIMEOUT_SECONDS * 1000, True, error="Time limit exceeded")
        elapsed = int((time.monotonic() - start) * 1000)
        return RunResult(_trunc(proc.stdout), _trunc(proc.stderr), proc.returncode, elapsed, False)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
