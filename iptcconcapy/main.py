import argparse
import csv
from pathlib import Path

INPUT_DELIMITER = ":"
OUTPUT_DELIMITER = ","


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
    output_file = Path("concatenated_output.csv")

    if not input_directory.exists():
        print(f"Input directory {input_directory.resolve()} does not exist.")
        return

    concatenate_csv_files(input_directory, output_file)


if __name__ == "__main__":
    main()
