"""Extract a ZIP archive into a destination directory.

Usage:
    python unzip.py input/data.zip input/
    python unzip.py input/data.zip input/subfolder/
"""
import argparse
import zipfile
from pathlib import Path


def unzip_archive(input_path: Path, output_path: Path) -> list[Path]:
    """Extract an archive and return the extracted file paths."""
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path.mkdir(parents=True, exist_ok=True)

    extracted_paths: list[Path] = []
    with zipfile.ZipFile(input_path) as archive:
        for member in archive.infolist():
            member_path = (output_path / member.filename).resolve()
            if output_path.resolve() not in member_path.parents:
                raise ValueError(f"Unsafe archive path: {member.filename}")
            archive.extract(member, output_path)
            if not member.is_dir():
                extracted_paths.append(member_path)

    return extracted_paths


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract a ZIP archive into a destination directory."
    )
    parser.add_argument("input_file", type=Path, help="ZIP archive to extract")
    parser.add_argument(
        "destination_path",
        type=Path,
        help="Destination directory",
    )
    args = parser.parse_args()
    output_path = args.destination_path

    try:
        extracted_paths = unzip_archive(args.input_file, output_path)
    except (FileNotFoundError, OSError, ValueError, zipfile.BadZipFile) as error:
        parser.error(str(error))

    print(f"Done: {args.input_file} -> {output_path}")
    print(f"Files extracted: {len(extracted_paths)}")
    for extracted_path in extracted_paths:
        print(extracted_path)


if __name__ == "__main__":
    main()