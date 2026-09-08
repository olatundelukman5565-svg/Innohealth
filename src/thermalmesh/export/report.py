"""Quality report generation (JSON + human-readable text)."""

from __future__ import annotations

from pathlib import Path

from thermalmesh.export.json import export_json


def export_quality_report(metrics: dict, output_dir: str | Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = export_json(metrics, output_dir / "quality_report.json")
    text_path = output_dir / "quality_report.txt"
    text_path.write_text(_render_text(metrics))
    return json_path, text_path


def _render_text(metrics: dict) -> str:
    lines = ["INNOHEALTH THERMALMESH PIPELINE - QUALITY REPORT", "=" * 50, ""]

    def render_section(title: str, data: dict) -> None:
        lines.append(title)
        lines.append("-" * len(title))
        for key, value in data.items():
            lines.append(f"  {key}: {value}")
        lines.append("")

    for section, data in metrics.items():
        if isinstance(data, dict):
            render_section(section.upper(), data)
        else:
            lines.append(f"{section}: {data}")
    return "\n".join(lines)
