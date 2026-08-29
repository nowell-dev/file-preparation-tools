"""Expand semicolon-separated values in a CSV column into separate rows.

Usage:
    python parse-column.py column input_file.csv output_file.csv
    python parse-column.py address folder/data.csv folder/data-addresses.csv
    python parse-column.py phone folder/data.csv folder/data-phones.csv

The selected column is split on semicolons. Rows with multiple values are
expanded into one row per value, while all other columns are preserved.
"""
import argparse
import csv
import tempfile
from pathlib import Path


def parse_column(
    column_name: str, input_path: Path, output_path: Path
) -> tuple[int, int]:
    """Write one row for each value and return input and output row counts."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("Input CSV is empty or has no header.")
        if column_name not in reader.fieldnames:
            raise ValueError(f"Input CSV must contain a '{column_name}' column.")

        expanded_rows: list[dict[str, str]] = []
        input_count = 0
        for row in reader:
            input_count += 1
            values = [
                value.strip()
                for value in row[column_name].split(";")
                if value.strip()
            ]
            for value in values or [""]:
                expanded_row = dict(row)
                expanded_row[column_name] = value
                expanded_rows.append(expanded_row)

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
                writer = csv.DictWriter(temporary_file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(expanded_rows)
            temporary_path.replace(input_path)
        else:
            with output_path.open("w", newline="", encoding="utf-8") as output_file:
                writer = csv.DictWriter(output_file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(expanded_rows)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()

    return input_count, len(expanded_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Expand semicolon-separated values in a CSV column."
    )
    parser.add_argument("column", help="Column to parse")
    parser.add_argument("input_file", type=Path, help="CSV file to parse")
    parser.add_argument(
        "output_file",
        type=Path,
        nargs="?",
        help="Destination CSV; omit to update the input file",
    )
    args = parser.parse_args()
    output_file = args.output_file or args.input_file

    try:
        input_count, output_count = parse_column(
            args.column, args.input_file, output_file
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {output_file}")
    print(f"Input rows: {input_count}")
    print(f"Output rows: {output_count}")


if __name__ == "__main__":
    main()