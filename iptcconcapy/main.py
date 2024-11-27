import argparse
import csv
from pathlib import Path

INPUT_DELIMITER = ":"
OUTPUT_DELIMITER = ","

# Column names
COL_FILENAME = "Filename"
COL_SIZE = "Size"
COL_WIDTH = "Width"
COL_OBJECT_NAME = "IPTC:ObjectName"
COL_SUP_CATEGORY = "IPTC:Sup."
COL_SOURCE = "IPTC:Source"

# Values
CATEGORY = "MQB - Iconotheque"
SOURCE = "evian"
MIN_SIZE = 2
MAX_SIZE = 4
WIDTH_DPI = "3200 DPI"


def concatenate_csv_files(input_directory: Path, output_file: Path):
    # List all CSV files in the directory
    """
    Concatenate multiple CSV files from the given input directory into a single CSV file.
    The function considered that all files have an header, only the first header will be used.

    Args:
        input_directory: The directory containing the CSV files to concatenate.
        output_file: The file path of the output CSV file.
    """
    csv_files = [f for f in input_directory.iterdir() if f.suffix == ".csv"]

    # Open the output CSV file for writing
    with output_file.open(mode="w", newline="") as output_csv:
        csv_writer = None

        # Loop through each CSV file and append its content
        for csv_file in csv_files:
            with csv_file.open(mode="r") as input_csv:
                csv_reader = csv.reader(input_csv, delimiter=INPUT_DELIMITER)
                headers = next(csv_reader)  # Read the header

                # Write headers only once, in the first iteration
                if csv_writer is None:
                    csv_writer = csv.writer(output_csv, delimiter=OUTPUT_DELIMITER)
                    csv_writer.writerow(headers)  # Write the header to the output file

                # Write the rest of the rows
                for row in csv_reader:
                    csv_writer.writerow(row)


def check_csv(file_path):
    """
    Reads a CSV file and performs validation checks on each row.

    It will checks :
        - If any data is missing or empty.
        - If the 'COL_SIZE' column value is between `MIN_SIZE` and `MAX_SIZE` (in Mio).
        - If the 'COL_WIDTH' column value is equal to `WIDTH_DPI`.
        - If the `COL_OBJECT_NAME` column value matches the prefix of `COL_FILENAME`.
        - If the `COL_SUP_CATEGORY` column value is equal to `CATEGORY`.
        - If the `COL_SOURCE` column value is equal to `SOURCE`.

    Prints a list of errors for each row that does not meet the criteria,
    including the line number and the row content.

    Args:
        file_path (Path): The path to the CSV file to be checked.
    """
    with file_path.open(mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=",")
        for row_num, row in enumerate(csv_reader, start=1):
            errors = []

            # Check if any data is missing or empty
            if any(not value for value in row.values()):
                errors.append("Missing data")

            try:
                size_str = row.get(COL_SIZE, "").replace(" Mio", "").strip()
                size = float(size_str)
                if not MIN_SIZE <= size <= MAX_SIZE:
                    errors.append(f"Size ({size} Mio) is out of range ({MIN_SIZE}-{MAX_SIZE} Mio)")
            except ValueError:
                errors.append("Invalid Size value")

            width_value = row.get(COL_WIDTH, "").strip()
            if width_value != WIDTH_DPI:
                errors.append(f"{COL_WIDTH} should be '{WIDTH_DPI}' but we find '{width_value}'")

            filename_value = row.get(COL_FILENAME, "").strip()
            object_value_prefix = row.get(COL_OBJECT_NAME, "").strip().split("_")[0]
            if filename_value != object_value_prefix:
                errors.append(
                    f"{COL_FILENAME} ('{filename_value}') does not match "
                    f"{COL_OBJECT_NAME} prefix ('{object_value_prefix}')"
                )

            category_value = row.get(COL_SUP_CATEGORY, "").strip()
            if category_value != CATEGORY:
                errors.append(
                    f"{COL_SUP_CATEGORY} should be '{CATEGORY}' but we find '{category_value}'"
                )

            source_value = row.get(COL_SOURCE, "").strip()
            if source_value != SOURCE:
                errors.append(f"{COL_SOURCE} should be '{SOURCE}' but we find '{source_value}'")

            # Print errors if any
            if errors:
                print(f"Line {row_num} has the following issues:")
                for error in errors:
                    print(f"  - {error}")
                print(f"{row}")
                print()


def main():
    """
    Entry point of the application.

    This function parses the command line arguments, checks for the existence
    of the input directory, and calls the concatenate_csv_files function
    to perform the actual concatenation.
    """
    parser = argparse.ArgumentParser(description="Concatenate all CSV files in a directory.")
    parser.add_argument(
        "input_directory", type=str, help="Path to the directory containing CSV files"
    )
    args = parser.parse_args()

    input_directory = Path(args.input_directory)
    global_file = Path("concatenated_output.csv")

    if not input_directory.exists():
        print(f"Input directory {input_directory.resolve()} does not exist.")
        return

    concatenate_csv_files(input_directory, global_file)

    check_csv(global_file)


if __name__ == "__main__":
    main()
