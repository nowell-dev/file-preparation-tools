"""Combine multiple CSV files into one CSV file.

Usage:
    python combine-csv.py input_file.csv output_file.csv
    python combine-csv.py folder/data*.csv folder/data-combined.csv
    python combine-csv.py folder/data01.csv folder/data02.csv folder/data-combined.csv

Input paths may include wildcards. The output file is excluded from the input
matches when it is already present.
"""
import argparse
import csv
import glob
from pathlib import Path


def resolve_input_files(input_patterns: list[str], output_path: Path) -> list[Path]:
    """Expand input paths and return unique CSV files in sorted order."""
    output_resolved = output_path.resolve()
    input_files: set[Path] = set()
    for pattern in input_patterns:
        matches = glob.glob(pattern)
        if not matches and not any(character in pattern for character in "*?["):
            matches = [pattern]
        for match in matches:
            input_path = Path(match)
            if input_path.is_file() and input_path.resolve() != output_resolved:
                input_files.add(input_path)

    if not input_files:
        raise FileNotFoundError("No input CSV files matched the supplied path(s).")
    return sorted(input_files, key=lambda path: str(path).lower())


def combine_csv(input_patterns: list[str], output_path: Path) -> tuple[int, int]:
    """Combine matching CSV files and return file and row counts."""
    input_files = resolve_input_files(input_patterns, output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    header: list[str] | None = None
    combined_rows: list[list[str]] = []

    for input_path in input_files:
        with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
            reader = csv.reader(input_file)
            try:
                current_header = next(reader)
            except StopIteration as error:
                raise ValueError(f"Input CSV is empty: {input_path}") from error

            if header is None:
                header = current_header
            elif current_header != header:
                raise ValueError(f"CSV header does not match: {input_path}")
            combined_rows.extend(reader)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(header)
        writer.writerows(combined_rows)

    return len(input_files), len(combined_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Combine multiple CSV files, including wildcard matches."
    )
    parser.add_argument(
        "input_patterns",
        nargs="+",
        help="CSV paths or wildcard patterns to combine",
    )
    parser.add_argument("output_file", type=Path, help="Destination CSV file")
    args = parser.parse_args()

    try:
        file_count, row_count = combine_csv(args.input_patterns, args.output_file)
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {file_count} files -> {args.output_file}")
    print(f"Data rows written: {row_count}")


if __name__ == "__main__":
    main()