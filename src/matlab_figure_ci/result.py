"""Result objects shared by CLI commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _line_number(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        line = int(value)
    except (TypeError, ValueError):
        return None
    return line if line > 0 else None


@dataclass
class Finding:
    severity: str
    rule_id: str
    path: str
    line: int | None
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "rule_id": self.rule_id,
            "path": self.path,
            "line": self.line,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        return cls(
            severity=str(data.get("severity", "")),
            rule_id=str(data.get("rule_id", "")),
            path=str(data.get("path", "")),
            line=_line_number(data.get("line")),
            message=str(data.get("message", "")),
        )


@dataclass
class ScanResults:
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    skipped_binary_count: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for finding in self.findings if finding.severity == "warning")

    @property
    def exit_code(self) -> int:
        return 1 if self.error_count else 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_scanned": self.files_scanned,
            "skipped_binary_count": self.skipped_binary_count,
            "findings": [finding.to_dict() for finding in self.findings],
        }


@dataclass
class GalleryItem:
    status: str
    path: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "path": self.path, "message": self.message}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GalleryItem":
        return cls(
            status=str(data.get("status", "")),
            path=str(data.get("path", "")),
            message=str(data.get("message", "")),
        )


@dataclass
class GalleryResults:
    items: list[GalleryItem] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for item in self.items if item.status == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for item in self.items if item.status == "warning")

    @property
    def checked_count(self) -> int:
        return sum(1 for item in self.items if item.status == "ok")

    @property
    def exit_code(self) -> int:
        return 1 if self.error_count else 0

    def to_dict(self) -> dict[str, Any]:
        return {"items": [item.to_dict() for item in self.items]}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GalleryResults":
        return cls(items=[GalleryItem.from_dict(item) for item in data.get("items", [])])


@dataclass
class CheckResults:
    summary: dict[str, Any]
    findings: list[Finding]
    scan: ScanResults
    gallery: GalleryResults
    render: dict[str, Any]
    config_path: str
    tool_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "scan": self.scan.to_dict(),
            "gallery": self.gallery.to_dict(),
            "render": self.render,
            "config_path": self.config_path,
            "tool_version": self.tool_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CheckResults":
        findings = [Finding.from_dict(item) for item in data.get("findings", [])]
        return cls(
            summary=dict(data.get("summary", {})),
            findings=findings,
            scan=ScanResults(
                findings=[Finding.from_dict(item) for item in data.get("scan", {}).get("findings", [])],
                files_scanned=int(data.get("scan", {}).get("files_scanned", 0)),
                skipped_binary_count=int(data.get("scan", {}).get("skipped_binary_count", 0)),
            ),
            gallery=GalleryResults.from_dict(data.get("gallery", {})),
            render=dict(data.get("render", {"status": "skipped", "message": "disabled"})),
            config_path=str(data.get("config_path", "")),
            tool_version=str(data.get("tool_version", "")),
        )
