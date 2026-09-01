##################################
"""
Parameters:
    parameter 1: path/to/input_file.csv
    parameter 2 (optional): path/to/output_file.csv
        if supplied, the cleaned data will be saved to this file
        if not supplied, the cleaned data will overwrite the input file

Usage:
    python remove-duplicates.py folder/data.csv folder/data-cleaned.csv
    python remove-duplicates.py folder/data.csv
"""
##################################
import sys
import pandas as pd


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: python remove-duplicates.py input_file.csv [output_file.csv]"
        )

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else input_path

    df = pd.read_csv(input_path)
    df = df.drop_duplicates()
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
