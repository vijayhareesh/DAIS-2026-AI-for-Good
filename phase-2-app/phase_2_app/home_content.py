from __future__ import annotations

from pathlib import Path


def _section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {heading}":
            start = index + 1
            break
    if start is None:
        return ""

    section_lines: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        section_lines.append(line)
    return "\n".join(section_lines).strip()


def _title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").split(" - ", 1)[0].strip()
    return "HealthVerify India"


def project_summary(path: Path) -> dict[str, str]:
    markdown = path.read_text(encoding="utf-8")
    return {
        "title": _title(markdown),
        "inspiration": _section(markdown, "Inspiration"),
        "what_it_does": _section(markdown, "What it does"),
        "how_we_built_it": _section(markdown, "How we built it"),
        "next_steps": _section(markdown, "What's next for HealthVerify India"),
    }
