from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RunRow:
    run_token: str
    project_id: str
    status: str


@dataclass(frozen=True)
class ArtifactRow:
    run_token: str
    project_id: str
    artifact_type: str
    path: str
    checksum_sha256: str
    size_bytes: int
    content_type: Optional[str] = None
