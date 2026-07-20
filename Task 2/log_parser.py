#!/usr/bin/env python3
"""
CLI Log Parser for Tour Enquiries
==================================
Tech stack: Python, argparse, re

Reads a messy, unstructured text file of tour enquiries and extracts:
    - Name
    - Email
    - Destination
for each enquiry, then prints a clean summary table to the terminal.

Usage:
    python log_parser.py sample_enquiries.txt
    python log_parser.py sample_enquiries.txt --unknown-only
    python log_parser.py sample_enquiries.txt --export results.csv
    python log_parser.py sample_enquiries.txt --verbose
"""

import argparse
import csv
import re
import sys


# ---------------------------------------------------------------------------
# Known destinations to match against. Extend this list as needed.
# Multi-word destinations MUST come first in matching so "New York" isn't
# missed in favor of a partial/wrong match.
# ---------------------------------------------------------------------------
KNOWN_DESTINATIONS = [
    "New York", "Bali", "Paris", "Goa", "London", "Dubai", "Bangkok", "Rome",
    "Tokyo", "Maldives", "Switzerland", "Singapore", "Kerala", "Manali",
    "Kashmir", "Sydney",
]

# ---------------------------------------------------------------------------
# REGEX PATTERNS
# ---------------------------------------------------------------------------

# Email: standard pattern, good enough for real-world enquiry text.
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

# Destination: alternation of all known destinations (case-insensitive,
# longest-first so multi-word names win over partial overlaps).
_dest_alternation = "|".join(re.escape(d) for d in
                              sorted(KNOWN_DESTINATIONS, key=len, reverse=True))
DESTINATION_PATTERN = re.compile(rf"\b({_dest_alternation})\b", re.IGNORECASE)

# Name: several common phrasings seen in enquiry text, tried in order.
# Each pattern captures a "Firstname Lastname"-style run of capitalized words.
#
# IMPORTANT:
#   - The capital-letter check ([A-Z]...) must stay CASE-SENSITIVE, or a
#     global re.IGNORECASE would let it match lowercase filler words like
#     "and"/"my" too. Only the trigger phrase (e.g. "hi im") should be
#     matched case-insensitively -- done here with a scoped inline flag
#     (?i:...) rather than a flag on the whole pattern.
#   - The separator between name words uses "[ \t]+" (space/tab only), NOT
#     "\s+", so a name can never accidentally swallow a newline and bleed
#     into the next line (e.g. "Name: Aisha Smith\nEmail: ...").
NAME_WORD = r"[A-Z][a-zA-Z']+"
NAME_CAPTURE = rf"({NAME_WORD}(?:[ \t]+{NAME_WORD}){{0,2}})"

NAME_PATTERNS = [
    re.compile(rf"(?:I'?m|I am|Myself|My name is)[ \t]+{NAME_CAPTURE}"),
    re.compile(rf"(?i:my name is|this is)[ \t]+{NAME_CAPTURE}"),
    re.compile(rf"Name[ \t]*[:\-][ \t]*{NAME_CAPTURE}"),
    re.compile(rf"From[ \t]*[:\-][ \t]*{NAME_CAPTURE}"),
    re.compile(rf"submitted by[ \t]+{NAME_CAPTURE}"),
    re.compile(rf"(?i:hi im)[ \t]+{NAME_CAPTURE}"),
    re.compile(rf"{NAME_CAPTURE}[ \t]+called in"),
    re.compile(rf"Walk-in enquiry:[ \t]*{NAME_CAPTURE}"),
    re.compile(rf"{NAME_CAPTURE}[ \t]*\("),  # "Name (email)" pattern
]

# Words that can look like a name grammatically but never are one --
# guards against false positives from the generic fallback patterns.
NAME_BLACKLIST = {"email", "destination", "message", "name", "from",
                  "source", "note", "enquiry", "contact"}


def extract_email(block: str) -> str | None:
    match = EMAIL_PATTERN.search(block)
    if not match:
        return None
    # Trim trailing sentence punctuation the greedy pattern may have
    # picked up (e.g. "...@gmail.com." at the end of a sentence).
    return match.group().rstrip(".,;:!?")


def extract_destination(block: str) -> str | None:
    match = DESTINATION_PATTERN.search(block)
    if not match:
        return None
    # Normalize casing to the canonical form from KNOWN_DESTINATIONS
    found = match.group(1)
    for dest in KNOWN_DESTINATIONS:
        if dest.lower() == found.lower():
            return dest
    return found


def extract_name(block: str) -> str | None:
    dest_lower = {d.lower() for d in KNOWN_DESTINATIONS}
    for pattern in NAME_PATTERNS:
        match = pattern.search(block)
        if match:
            name = match.group(1).strip()
            first_word = name.split()[0].lower()
            # Guard against accidental matches on destinations or on
            # structural label words (Email, Name, Message, etc.)
            if name.lower() in dest_lower or first_word in NAME_BLACKLIST:
                continue
            return name
    return None


def split_into_blocks(raw_text: str) -> list[str]:
    """
    Split the raw log into candidate enquiry blocks. Blocks are separated
    by one or more blank lines; header/separator/noise lines are filtered
    out before splitting.
    """
    noise_pattern = re.compile(
        r"^(={2,}|-{2,}|#{2,}|\[SYSTEM\]|\[WARN\]|NOTE:).*$", re.IGNORECASE
    )

    filtered_lines = []
    for line in raw_text.splitlines():
        if noise_pattern.match(line.strip()):
            continue
        filtered_lines.append(line)

    cleaned_text = "\n".join(filtered_lines)
    blocks = re.split(r"\n\s*\n+", cleaned_text)
    return [b.strip() for b in blocks if b.strip()]


def parse_enquiries(raw_text: str) -> tuple[list[dict], list[str]]:
    """
    Returns (parsed_entries, unparsable_blocks).
    An entry is considered "parsed" if at least a name OR email was found
    (a block with none of name/email/destination is treated as junk/noise
    and reported separately).
    """
    blocks = split_into_blocks(raw_text)
    parsed = []
    unparsable = []

    for block in blocks:
        name = extract_name(block)
        email = extract_email(block)
        destination = extract_destination(block)

        if not name and not email:
            # Nothing usable in this block -- treat as unparsable noise
            unparsable.append(block)
            continue

        parsed.append({
            "name": name or "N/A",
            "email": email or "N/A",
            "destination": destination or "Unknown",
        })

    return parsed, unparsable


# ---------------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------------
def print_summary(entries: list[dict], unparsable_count: int, total_blocks: int,
                   unknown_only: bool = False) -> None:
    if unknown_only:
        entries = [e for e in entries if e["destination"] == "Unknown"]

    name_width = max([len(e["name"]) for e in entries], default=4)
    name_width = max(name_width, len("Name"))
    email_width = max([len(e["email"]) for e in entries], default=5)
    email_width = max(email_width, len("Email"))
    dest_width = max([len(e["destination"]) for e in entries], default=11)
    dest_width = max(dest_width, len("Destination"))

    header = f"{'Name':<{name_width}}  {'Email':<{email_width}}  {'Destination':<{dest_width}}"
    print(header)
    print("-" * len(header))
    for e in entries:
        print(f"{e['name']:<{name_width}}  {e['email']:<{email_width}}  {e['destination']:<{dest_width}}")

    print()
    print("=" * len(header))
    print("SUMMARY")
    print("=" * len(header))
    print(f"Total blocks scanned:       {total_blocks}")
    print(f"Successfully parsed:        {len(entries) if not unknown_only else '(filtered view - see full run for total)'}" if unknown_only
          else f"Successfully parsed:        {len(entries)}")
    print(f"Unparsable / noise blocks:  {unparsable_count}")

    if not unknown_only:
        dest_counts = {}
        for e in entries:
            dest_counts[e["destination"]] = dest_counts.get(e["destination"], 0) + 1
        print("\nEnquiries by destination:")
        for dest, count in sorted(dest_counts.items(), key=lambda x: -x[1]):
            print(f"  {dest:<{dest_width}}  {count}")


def export_csv(entries: list[dict], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "destination"])
        writer.writeheader()
        writer.writerows(entries)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="log_parser.py",
        description="Extract names, emails, and destinations from a messy "
                     "tour-enquiry log file using regex, and print a clean "
                     "summary to the terminal.",
    )
    parser.add_argument(
        "logfile",
        help="Path to the raw tour-enquiry text log file to parse",
    )
    parser.add_argument(
        "--unknown-only",
        action="store_true",
        help="Only show enquiries where the destination could not be matched "
             "against the known destination list",
    )
    parser.add_argument(
        "--export",
        metavar="FILE.csv",
        help="Also export the parsed results to a CSV file",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print the raw text of blocks that could not be parsed at all",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    try:
        with open(args.logfile, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.logfile}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    blocks = split_into_blocks(raw_text)
    entries, unparsable = parse_enquiries(raw_text)

    print_summary(entries, len(unparsable), len(blocks), unknown_only=args.unknown_only)

    if args.verbose and unparsable:
        print("\n" + "=" * 60)
        print(f"UNPARSABLE BLOCKS ({len(unparsable)}):")
        print("=" * 60)
        for i, block in enumerate(unparsable, 1):
            print(f"\n--- Block {i} ---")
            print(block)

    if args.export:
        export_csv(entries, args.export)
        print(f"\nExported {len(entries)} entries to {args.export}")


if __name__ == "__main__":
    main()
