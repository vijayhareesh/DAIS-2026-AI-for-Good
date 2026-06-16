from __future__ import annotations


def result_heading(total_count: int, visible_count: int) -> str:
    if total_count <= visible_count:
        return f"Top Matches ({total_count})"
    return f"Top {visible_count} of {total_count} Matches"
