#!/usr/bin/env python3
"""Count standard working days (Mon-Fri) between two dates, inclusive.

Usage:
    working_days.py FROM TO [--holidays LIST | --holidays-file FILE] [--exclude-start] [--show-days]

FROM/TO are dates in YYYY-MM-DD. If TO < FROM the result is 0.
The weekday of every date is derived from the real calendar (no
day-of-month patterns), so the same day-of-month may be a weekend in one
month and a workday in another.
--exclude-start drops the first day from the count (use when the analysis
date is a working day and must not count as a full remaining day).
Holidays come only from a real calendar: either a comma-separated list of
YYYY-MM-DD dates or a text file with one date per line.
--show-days prints one line per date with its weekday and why it was
counted or skipped, ending with "total: N" (verification mode).
"""

import argparse
import sys
from datetime import date, timedelta


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}")


def load_holidays(args) -> set[date]:
    raw = []
    if args.holidays:
        raw.extend(args.holidays.split(","))
    if args.holidays_file:
        with open(args.holidays_file, encoding="utf-8") as fh:
            raw.extend(line.strip() for line in fh if line.strip())
    holidays = set()
    for item in raw:
        item = item.strip()
        if not item:
            continue
        try:
            holidays.add(date.fromisoformat(item))
        except ValueError:
            sys.exit(f"invalid holiday date: {item!r}")
    return holidays


def main() -> None:
    parser = argparse.ArgumentParser(description="Count working days between two dates, inclusive.")
    parser.add_argument("from_date", type=parse_date)
    parser.add_argument("to_date", type=parse_date)
    parser.add_argument("--holidays", help="comma-separated YYYY-MM-DD holidays")
    parser.add_argument("--holidays-file", help="text file with one YYYY-MM-DD holiday per line")
    parser.add_argument(
        "--exclude-start",
        action="store_true",
        help="do not count the first (analysis) day as a full remaining day",
    )
    parser.add_argument(
        "--show-days",
        action="store_true",
        help="print per-date lines with weekday and skip reason, then 'total: N'",
    )
    args = parser.parse_args()

    if args.to_date < args.from_date:
        print("total: 0" if args.show_days else 0)
        return

    holidays = load_holidays(args)
    current = args.from_date
    end = args.to_date
    count = 0
    first_day_skipped = False
    while current <= end:
        included = True
        reason = "workday"
        if args.exclude_start and not first_day_skipped:
            first_day_skipped = True
            included = False
            reason = "excluded-start"
        elif current.weekday() >= 5:
            included = False
            reason = "weekend"
        elif current in holidays:
            included = False
            reason = "holiday"
        if included:
            count += 1
        if args.show_days:
            print(f"{current.isoformat()} {current.strftime('%a')} {reason}")
        current += timedelta(days=1)

    if args.show_days:
        print(f"total: {count}")
    else:
        print(count)


if __name__ == "__main__":
    main()
