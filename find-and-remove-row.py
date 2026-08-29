##################################
"""
Find and remove CSV rows containing a string.
This script reads a CSV file and writes the header plus every row not containing
the requested string in any column.

The search string and input path are required. The output file is optional:
- If provided, results are written there
- If omitted, the input file is updated in place

Usage:
    python find-and-remove-row.py "example.com" folder/data.csv
    python find-and-remove-row.py "example.com" folder/data.csv folder/data-removed.csv
    python find-and-remove-row.py " / " folder/data.csv
"""
##################################
import argparse
import csv
import tempfile
from pathlib import Path


def find_and_remove(input_path: Path, search_string: str, output_path: Path | None = None) -> tuple[Path, int, int]:
    """Write the header and rows without search_string anywhere in the row."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path is None:
        output_path = input_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.reader(input_file)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("Input CSV is empty.") from error

        total_rows = 0
        removed_rows = 0
        filtered_rows: list[list[str]] = []

        for row in reader:
            total_rows += 1
            if any(search_string in value for value in row):
                removed_rows += 1
            else:
                filtered_rows.append(row)

    temporary_path: Path | None = None
    try:
        if input_path.resolve() == output_path.resolve():
            with tempfile.NamedTemporaryFile(
                mode="w",
                newline="",
                encoding="utf-8",
                dir=input_path.parent,
                prefix=f".{input_path.stem}-",
                suffix=input_path.suffix,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                writer = csv.writer(temporary_file)
                writer.writerow(header)
                writer.writerows(filtered_rows)
            temporary_path.replace(input_path)
        else:
            with output_path.open("w", newline="", encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow(header)
                writer.writerows(filtered_rows)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return output_path, total_rows, removed_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find and remove CSV rows containing a string."
    )
    parser.add_argument("search_string", help="Literal string to find in each row")
    parser.add_argument(
        "input_file", type=Path, help="CSV file to search"
    )
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        help="Destination CSV; omit to update the input file in place",
    )
    args = parser.parse_args()

    try:
        output_file, total_count, removed_count = find_and_remove(
            args.input_file, args.search_string, args.output_file
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {output_file}")
    print(f"Data rows searched: {total_count}")
    print(f"Rows removed: {removed_count}")


if __name__ == "__main__":
    main()