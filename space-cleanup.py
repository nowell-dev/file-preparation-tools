##################################
"""
Parameters:
    parameter 1: folder/data.csv
    parameter 2 (optional): folder/data-spaces-cleaned.csv
        The output file is optional; if not provided, the input file will be updated in place.

Usage:
    python space-cleanup.py folder/data.csv folder/data-spaces-cleaned.csv
    python space-cleanup.py folder/data.csv
"""
##################################
import sys
import pandas as pd


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python space-cleanup.py input_file.csv [output_file.csv]"
        )

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else input_path

    df = pd.read_csv(input_path)
    for x  in df.columns:
        df[x] = df[x].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()