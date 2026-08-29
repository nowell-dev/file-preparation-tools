##################################
"""
Find and isolate CSV rows containing a string.
This script reads a CSV file and writes the header plus every row containing
the requested string in any column to a new *_isolated.csv file.

The input path and search string are required. The output file is created beside
the input file automatically.

Usage:
    python find-and-isolate.py folder/data.csv "example.com"
    python find-and-isolate.py folder/data.csv " / " " "
"""
##################################
import argparse
import csv
from pathlib import Path


def find_and_isolate(input_path: Path, search_string: str) -> tuple[Path, int, int]:
    """Write the header and rows containing search_string anywhere in the row."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = input_path.with_name(f"{input_path.stem}_isolated{input_path.suffix}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.reader(input_file)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("Input CSV is empty.") from error

        total_rows = 0
        matched_rows = 0

        with output_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header)

            for row in reader:
                total_rows += 1
                if any(search_string in value for value in row):
                    writer.writerow(row)
                    matched_rows += 1

    return output_path, total_rows, matched_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find and isolate CSV rows containing a string."
    )
    parser.add_argument(
        "input_file", type=Path, help="CSV file to search"
    )
    parser.add_argument("search_string", help="Literal string to find in each row")
    args = parser.parse_args()

    try:
        output_file, total_count, matched_count = find_and_isolate(
            args.input_file, args.search_string
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {output_file}")
    print(f"Data rows searched: {total_count}")
    print(f"Rows isolated: {matched_count}")


if __name__ == "__main__":
    main()