import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class GateResult:
    gate_name: str
    status: str  # pass | fail | skip
    exit_code: int
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    evidence_paths: list[str]
    notes: Optional[str]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_gate(
    gate_name: str,
    cmd: list[str] | None,
    evidence_log_path: Path,
    cwd: Optional[Path] = None,
    env: Optional[dict[str, str]] = None,
    skip_reason: Optional[str] = None,
) -> GateResult:
    started = datetime.now(timezone.utc)
    t0 = time.time()

    if cmd is None:
        _write_text(evidence_log_path, f"SKIP: {skip_reason or 'no command'}\nexit_code=0\n")
        finished = datetime.now(timezone.utc)
        dur = int((time.time() - t0) * 1000)
        return GateResult(
            gate_name=gate_name,
            status="skip",
            exit_code=0,
            started_at=started,
            finished_at=finished,
            duration_ms=dur,
            evidence_paths=[str(evidence_log_path)],
            notes=skip_reason,
        )

    evidence_log_path.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env={**os.environ, **(env or {})},
        capture_output=True,
        text=True,
    )

    content = []
    content.append(f"cmd: {' '.join(cmd)}\n")
    content.append(proc.stdout or "")
    if proc.stderr:
        content.append("\n--- stderr ---\n")
        content.append(proc.stderr)
    content.append(f"\nexit_code={proc.returncode}\n")
    _write_text(evidence_log_path, "".join(content))

    finished = datetime.now(timezone.utc)
    dur = int((time.time() - t0) * 1000)
    status = "pass" if proc.returncode == 0 else "fail"

    return GateResult(
        gate_name=gate_name,
        status=status,
        exit_code=proc.returncode,
        started_at=started,
        finished_at=finished,
        duration_ms=dur,
        evidence_paths=[str(evidence_log_path)],
        notes=None,
    )
