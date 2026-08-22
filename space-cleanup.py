##################################
"""
Clean repeated whitespace in a CSV file.
This script reads a CSV file, trims whitespace around each value, collapses
double or triple spaces into one, and writes the cleaned data to a new CSV file.
The output file can be specified, or if omitted, the input file will be updated in place.

This has only one input parameter, the input CSV file.
The output file is optional; if not provided, the input file will be updated in place.

Usage:
    python space-cleanup.py input_file.csv output_file.csv
    python space-cleanup.py input_file.csv
    python space-cleanup.py input/remove-duplicates.csv output/remove-duplicates-spaces-cleaned.csv
    python space-cleanup.py input/remove-duplicates.csv
"""
##################################
import argparse
import csv
import tempfile
from pathlib import Path


def clean_spaces(input_path: Path, output_path: Path) -> tuple[int, int]:
    """Copy a CSV while normalizing whitespace in every cell."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.reader(input_file)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("Input CSV is empty.") from error

        cleaned_rows: list[list[str]] = []
        changed_rows = 0

        for row in reader:
            cleaned_row = [" ".join(value.split()) for value in row]
            if cleaned_row != row:
                changed_rows += 1
            cleaned_rows.append(cleaned_row)

    temporary_path: Path | None = None
    try:
        if input_path.resolve() == output_path.resolve():
            # Write beside the original first, then replace it only after success.
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
                writer.writerow([" ".join(value.split()) for value in header])
                writer.writerows(cleaned_rows)
            temporary_path.replace(input_path)
        else:
            with output_path.open("w", newline="", encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow([" ".join(value.split()) for value in header])
                writer.writerows(cleaned_rows)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return len(cleaned_rows), changed_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean repeated whitespace in a CSV file."
    )
    parser.add_argument("input_file", type=Path, help="CSV file to clean")
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        help="Destination for the cleaned CSV; omit to update the input file",
    )
    args = parser.parse_args()
    output_file = args.output_file or args.input_file

    try:
        row_count, changed_row_count = clean_spaces(
            args.input_file, output_file
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {output_file}")
    print(f"Data rows written: {row_count}")
    print(f"Rows with whitespace cleaned: {changed_row_count}")


if __name__ == "__main__":
    main()