"""Split a CSV file into a requested number of parts.

Usage:
    python split-big-csv.py number_of_parts input_file.csv
    python split-big-csv.py 10 folder/data.csv

Output files are created beside the input file using names such as
input/data_01.csv through input/data_10.csv. The header is written to every
part, and data rows are distributed as evenly as possible.
"""
import argparse
import csv
from pathlib import Path


def split_csv(input_path: Path, part_count: int) -> list[Path]:
    """Split a CSV into parts and return the generated output paths."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if part_count < 1:
        raise ValueError("The number of parts must be at least 1.")

    with input_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.reader(input_file)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("Input CSV is empty.") from error
        rows = list(reader)

    row_count = len(rows)
    base_size, remainder = divmod(row_count, part_count)
    width = max(2, len(str(part_count)))
    output_paths: list[Path] = []
    row_start = 0

    for part_number in range(1, part_count + 1):
        part_size = base_size + (1 if part_number <= remainder else 0)
        output_path = input_path.with_name(
            f"{input_path.stem}_{part_number:0{width}d}{input_path.suffix}"
        )
        with output_path.open("w", newline="", encoding="utf-8") as output_file:
            writer = csv.writer(output_file)
            writer.writerow(header)
            writer.writerows(rows[row_start : row_start + part_size])
        output_paths.append(output_path)
        row_start += part_size

    return output_paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Split a CSV file into a requested number of parts."
    )
    parser.add_argument("part_count", type=int, help="Number of output files")
    parser.add_argument("input_file", type=Path, help="CSV file to split")
    args = parser.parse_args()

    try:
        output_paths = split_csv(args.input_file, args.part_count)
    except (FileNotFoundError, OSError, ValueError) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {len(output_paths)} files")
    for output_path in output_paths:
        print(output_path)


if __name__ == "__main__":
    main()