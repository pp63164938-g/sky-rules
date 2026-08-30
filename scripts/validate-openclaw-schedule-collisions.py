#!/usr/bin/env python3
"""Detect simple OpenClaw Cron and systemd maintenance-window collisions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


MINUTES_PER_DAY = 24 * 60
DAILY_TIMER_PATTERN = re.compile(
    r"OnCalendar\s*=\s*\*-\*-\*\s+(?P<hour>\d{1,2}):(?P<minute>\d{2})(?::\d{2})?"
)


def parse_args() -> argparse.Namespace:
    """Parse exported Cron JSON and the user systemd directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cron-json", required=True, type=Path)
    parser.add_argument("--timer-dir", required=True, type=Path)
    parser.add_argument(
        "--maintenance-pattern",
        action="append",
        default=["refresh", "restart", "gateway"],
        help="Timer filename fragment treated as gateway maintenance",
    )
    return parser.parse_args()


def load_cron_jobs(cron_path: Path) -> list[dict[str, Any]]:
    """Load the public `openclaw cron list --json` structure."""
    value: Any = json.loads(cron_path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("jobs"), list):
        raise ValueError("Cron JSON must contain a jobs array")
    return [job_value for job_value in value["jobs"] if isinstance(job_value, dict)]


def expand_number_field(field_value: str, minimum: int, maximum: int) -> list[int]:
    """Expand the simple numbers, lists, ranges and wildcard used by daily jobs."""
    if field_value == "*":
        return list(range(minimum, maximum + 1))

    values: set[int] = set()
    for part_value in field_value.split(","):
        if re.fullmatch(r"\d+", part_value):
            values.add(int(part_value))
            continue
        range_match = re.fullmatch(r"(\d+)-(\d+)", part_value)
        if range_match:
            start_value, end_value = (int(value) for value in range_match.groups())
            values.update(range(start_value, end_value + 1))
            continue
        raise ValueError(f"unsupported Cron field: {field_value!r}")

    if any(value < minimum or value > maximum for value in values):
        raise ValueError(f"Cron field out of range: {field_value!r}")
    return sorted(values)


def get_job_windows(job_value: dict[str, Any]) -> list[tuple[int, int]]:
    """Return time-of-day runtime windows for a simple five-field Cron schedule."""
    schedule = job_value.get("schedule")
    payload = job_value.get("payload")
    if not isinstance(schedule, dict) or schedule.get("kind") != "cron":
        return []
    if not isinstance(payload, dict):
        payload = {}

    expression = schedule.get("expr")
    if not isinstance(expression, str):
        raise ValueError("Cron schedule is missing expr")
    fields = expression.split()
    if len(fields) != 5:
        raise ValueError(f"unsupported Cron expression: {expression!r}")

    minute_values = expand_number_field(fields[0], 0, 59)
    hour_values = expand_number_field(fields[1], 0, 23)
    # Maintenance timers run daily, so calendar fields only need syntax validation.
    expand_number_field(fields[2], 1, 31)
    expand_number_field(fields[3], 1, 12)
    expand_number_field(fields[4], 0, 7)
    timeout_seconds = payload.get("timeoutSeconds", 300)
    timeout_minutes = max(1, (int(timeout_seconds) + 59) // 60)
    return [
        (hour_value * 60 + minute_value, hour_value * 60 + minute_value + timeout_minutes)
        for hour_value in hour_values
        for minute_value in minute_values
    ]


def get_maintenance_times(
    timer_dir: Path, maintenance_patterns: list[str]
) -> list[tuple[str, int]]:
    """Read fixed daily maintenance times from matching user Timer files."""
    results: list[tuple[str, int]] = []
    normalized_patterns = [pattern_value.lower() for pattern_value in maintenance_patterns]
    for timer_path in sorted(timer_dir.glob("*.timer")):
        if not any(
            pattern_value in timer_path.name.lower()
            for pattern_value in normalized_patterns
        ):
            continue
        timer_text = timer_path.read_text(encoding="utf-8")
        matches = list(DAILY_TIMER_PATTERN.finditer(timer_text))
        if not matches:
            raise ValueError(f"unsupported maintenance OnCalendar: {timer_path.name}")
        for timer_match in matches:
            hour_value = int(timer_match.group("hour"))
            minute_value = int(timer_match.group("minute"))
            if hour_value > 23 or minute_value > 59:
                raise ValueError(f"invalid maintenance time: {timer_path.name}")
            results.append((timer_path.name, hour_value * 60 + minute_value))
    return results


def minute_is_in_window(target_minute: int, start_minute: int, end_minute: int) -> bool:
    """Check a daily minute against a possibly cross-midnight runtime window."""
    for offset_value in (-MINUTES_PER_DAY, 0, MINUTES_PER_DAY):
        shifted_target = target_minute + offset_value
        if start_minute <= shifted_target < end_minute:
            return True
    return False


def main() -> int:
    """Report collisions or unsupported schedule shapes as blocking failures."""
    args = parse_args()
    try:
        cron_jobs = load_cron_jobs(args.cron_json)
        maintenance_times = get_maintenance_times(
            args.timer_dir, args.maintenance_pattern
        )
        collisions: list[str] = []
        for job_value in cron_jobs:
            if job_value.get("enabled") is not True:
                continue
            job_name = str(job_value.get("name") or job_value.get("id") or "unnamed-job")
            for start_minute, end_minute in get_job_windows(job_value):
                for timer_name, timer_minute in maintenance_times:
                    if minute_is_in_window(timer_minute, start_minute, end_minute):
                        collisions.append(
                            f"{job_name} runtime window overlaps {timer_name}"
                        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: unable to validate schedules: {error}", file=sys.stderr)
        return 2

    if collisions:
        print("INVALID")
        for collision_value in sorted(set(collisions)):
            print(f"- {collision_value}")
        return 1

    print("VALID")
    print("- no OpenClaw Cron runtime window overlaps fixed gateway maintenance timers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
