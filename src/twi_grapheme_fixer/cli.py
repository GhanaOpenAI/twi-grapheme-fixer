"""
Command-line interface for twi-grapheme-fixer.

Allows fixing and restoring Twi graphemes in text, standard input streams,
or files, with optional English exemption and extended character support.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .converter import TwiGraphemeFixer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="twi-fixer",
        description="Fix Twi (Akan) graphemes using ATR vowel harmony rules with English word exemption.",
    )
    parser.add_argument(
        "text",
        nargs="?",
        default=None,
        help="Text string to convert. If omitted and no input file is specified, reads from stdin.",
    )
    parser.add_argument(
        "-i", "--input",
        dest="input_file",
        help="Path to an input text file to convert.",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_file",
        help="Path to output file. Defaults to stdout.",
    )
    parser.add_argument(
        "-d", "--direction",
        choices=["forward", "reverse"],
        default="forward",
        help="Conversion direction: 'forward' (default) to apply ATR rules, 'reverse' to restore original orthography.",
    )
    parser.add_argument(
        "--exempt-english",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Exempt English words and loanwords from Twi ATR rules (default: enabled).",
    )
    parser.add_argument(
        "--replace-extended",
        action="store_true",
        default=False,
        help="Replace extended characters (ɔ -> ö, ɛ -> ë) in forward mode, or restore them in reverse mode.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="Print conversion statistics and list of exempted English words to stderr.",
    )
    parser.add_argument(
        "--custom-exceptions",
        dest="exceptions_file",
        help="Path to a JSON file containing custom word exception mappings.",
    )
    parser.add_argument(
        "--custom-exempt-words",
        dest="exempt_words_file",
        help="Path to a text file with additional words to exempt (one per line).",
    )
    parser.add_argument(
        "--custom-twi-words",
        dest="twi_words_file",
        help="Path to a text file with additional words to force-treat as Twi (one per line).",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def load_lines_file(path: str) -> List[str]:
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    return [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    custom_exceptions = None
    if args.exceptions_file:
        p = Path(args.exceptions_file)
        if not p.is_file():
            print(f"Error: Exceptions file not found: {args.exceptions_file}", file=sys.stderr)
            return 1
        with open(p, "r", encoding="utf-8") as f:
            custom_exceptions = json.load(f)

    custom_exempt = None
    if args.exempt_words_file:
        try:
            custom_exempt = set(load_lines_file(args.exempt_words_file))
        except Exception as e:
            print(f"Error reading exempt words: {e}", file=sys.stderr)
            return 1

    custom_twi = None
    if args.twi_words_file:
        try:
            custom_twi = set(load_lines_file(args.twi_words_file))
        except Exception as e:
            print(f"Error reading Twi words: {e}", file=sys.stderr)
            return 1

    fixer = TwiGraphemeFixer(
        exempt_english=args.exempt_english,
        replace_extended=args.replace_extended,
        custom_exceptions=custom_exceptions,
        custom_exempt_words=custom_exempt,
        custom_twi_words=custom_twi,
    )

    # Determine input text
    if args.text is not None:
        raw_text = args.text
    elif args.input_file:
        p = Path(args.input_file)
        if not p.is_file():
            print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
            return 1
        raw_text = p.read_text(encoding="utf-8")
    else:
        # Read from stdin
        if sys.stdin.isatty():
            parser.print_help(sys.stderr)
            return 0
        raw_text = sys.stdin.read()

    if args.report:
        converted, report = fixer.convert_with_report(raw_text, direction=args.direction)
        print(f"\n--- Twi Grapheme Fixer Report ---", file=sys.stderr)
        print(f"Total words:      {report['total_words']}", file=sys.stderr)
        print(f"Words converted:  {report['converted']}", file=sys.stderr)
        print(f"English exempted: {report['exempt_english']}", file=sys.stderr)
        if report["exempt_tokens"]:
            sample = report["exempt_tokens"][:15]
            more = f" ... (+{len(report['exempt_tokens']) - 15} more)" if len(report["exempt_tokens"]) > 15 else ""
            print(f"Exempt samples:   {', '.join(sample)}{more}", file=sys.stderr)
    else:
        converted = fixer.convert(raw_text, direction=args.direction)

    if args.output_file:
        out_p = Path(args.output_file)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(converted, encoding="utf-8")
    else:
        # Write to stdout
        sys.stdout.write(converted)
        if args.text is not None and not converted.endswith("\n"):
            sys.stdout.write("\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
