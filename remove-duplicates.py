##################################
"""
Remove exact duplicate rows from a CSV file.
This script reads a CSV file, removes any exact duplicate rows (keeping only the first occurrence),
    and writes the cleaned data to a new CSV file. The output file can be specified, or if omitted, the input file will be updated in place.

This has only one input parameter, the input CSV file.
The output file is optional; if not provided, the input file will be updated in place.

Usage:
    python remove-duplicates.py input_file.csv output_file.csv
    python remove-duplicates.py input_file.csv
    python remove-duplicates.py folder/data.csv folder/data-cleaned.csv
    python remove-duplicates.py folder/data.csv
"""
##################################
import argparse
import csv
import tempfile
from pathlib import Path


def remove_duplicates(input_path: Path, output_path: Path) -> tuple[int, int]:
    """Copy a CSV while keeping only the first occurrence of each row."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.reader(input_file)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("Input CSV is empty.") from error

        unique_rows: list[list[str]] = []
        seen_rows: set[tuple[str, ...]] = set()
        total_rows = 0

        for row in reader:
            total_rows += 1
            # The complete row is the key, so only exact duplicates are removed.
            row_key = tuple(row)
            if row_key not in seen_rows:
                seen_rows.add(row_key)
                unique_rows.append(row)

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
                writer.writerow(header)
                writer.writerows(unique_rows)
            temporary_path.replace(input_path)
        else:
            with output_path.open("w", newline="", encoding="utf-8") as output_file:
                writer = csv.writer(output_file)
                writer.writerow(header)
                writer.writerows(unique_rows)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return len(unique_rows), total_rows - len(unique_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove exact duplicate rows from a CSV file."
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
        unique_count, duplicate_count = remove_duplicates(
            args.input_file, output_file
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {output_file}")
    print(f"Unique data rows written: {unique_count}")
    print(f"Duplicate rows removed: {duplicate_count}")


if __name__ == "__main__":
    main()