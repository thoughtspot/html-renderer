# csv_to_json.py
import csv
import json
import argparse
import sys
import os

# Use utf-8-sig to handle potential BOM (Byte Order Mark) in UTF-8 files
DEFAULT_ENCODING = 'utf-8-sig'

def convert_csv_to_json(csv_file_path, json_output_path, encoding, indent):
    """
    Reads a CSV file and converts its content to a JSON array of objects.

    Args:
        csv_file_path (str): Path to the input CSV file.
        json_output_path (str or None): Path to the output JSON file.
                                       If None, prints JSON to stdout.
        encoding (str): Encoding of the input CSV file.
        indent (int or None): Indentation level for JSON pretty-printing.
                              None for compact output.
    """
    data = []
    abs_csv_path = os.path.abspath(csv_file_path)

    # --- Input File Validation ---
    if not os.path.isfile(abs_csv_path):
        print(f"Error: Input CSV file not found at '{abs_csv_path}'", file=sys.stderr)
        sys.exit(1) # Exit indicating error

    print(f"Reading CSV file: '{abs_csv_path}' with encoding '{encoding}'...")

    # --- CSV Reading ---
    try:
        with open(abs_csv_path, mode='r', encoding=encoding, newline='') as csvfile:
            # Use DictReader which automatically uses the first row as field names (keys)
            reader = csv.DictReader(csvfile)

            # Clean up header names (fieldnames) to be more JSON-friendly
            # (lowercase, strip whitespace, replace spaces with underscores)
            # Store original fieldnames in case cleanup causes issues or isn't desired.
            original_fieldnames = reader.fieldnames
            if original_fieldnames:
                reader.fieldnames = [name.strip().lower().replace(' ', '_') for name in original_fieldnames]
                print(f"Using cleaned headers as JSON keys: {reader.fieldnames}")
            else:
                 print("Warning: CSV file appears to have no header row.", file=sys.stderr)
                 # Or potentially exit if headers are strictly required

            # Iterate over rows in the CSV
            for row_number, row_dict in enumerate(reader, start=2): # Start count from 2 (1=header)
                 # Basic check for consistent number of fields if needed, DictReader handles it somewhat
                 # For simplicity here, we directly append the dictionary provided by DictReader
                 data.append(row_dict)

    except FileNotFoundError:
        # Should be caught by the initial check, but good practice to handle here too
        print(f"Error: Input CSV file not found at '{abs_csv_path}'", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error: Could not decode file '{abs_csv_path}' with encoding '{encoding}'.", file=sys.stderr)
        print(f"Please verify the file encoding and try specifying a different one using --encoding", file=sys.stderr)
        print(f"(Common alternatives: 'utf-8', 'latin-1', 'iso-8859-1')", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file on or near row {row_number}: {e}", file=sys.stderr)
        sys.exit(1)

    if not data and original_fieldnames:
         print(f"Warning: CSV file '{abs_csv_path}' contained headers but no data rows.", file=sys.stderr)
         # Proceeding to output empty JSON array: []

    # --- JSON Output ---
    try:
        if json_output_path:
            abs_json_path = os.path.abspath(json_output_path)
            print(f"Writing JSON output to: '{abs_json_path}'...")
            # Write JSON to the specified output file
            with open(abs_json_path, mode='w', encoding='utf-8') as jsonfile:
                # ensure_ascii=False preserves non-ASCII characters correctly in the JSON output
                json.dump(data, jsonfile, indent=indent, ensure_ascii=False)
            print(f"Successfully converted {len(data)} rows to '{abs_json_path}'.")
        else:
            print("Printing JSON output to stdout...")
            # Write JSON to standard output
            # Use ensure_ascii=False here too
            json_string = json.dumps(data, indent=indent, ensure_ascii=False)
            print(json_string)
            # Add a newline if output is compact for better terminal display
            if indent is None:
                print()
            print(f"Successfully converted {len(data)} rows to JSON (stdout).")

    except IOError as e:
        print(f"Error writing JSON to output path '{json_output_path}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error generating or writing JSON: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(
        description="Convert a CSV file to a JSON array of objects (using first row as keys)."
    )
    parser.add_argument(
        "input_csv_file",
        help="Path to the input CSV file."
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT_JSON_FILE",
        help="Path to the output JSON file. If omitted, prints JSON to standard output."
    )
    parser.add_argument(
        "-e", "--encoding",
        default=DEFAULT_ENCODING,
        help=f"Encoding of the input CSV file (default: '{DEFAULT_ENCODING}')."
    )
    parser.add_argument(
        "-i", "--indent",
        type=int,
        metavar="SPACES",
        help="Number of spaces for JSON indentation (pretty-printing). Omit for compact output."
    )

    args = parser.parse_args()

    # Validate indent argument
    indent_level = args.indent
    if indent_level is not None and indent_level < 0:
        print("Error: Indentation level cannot be negative.", file=sys.stderr)
        sys.exit(1)

    # --- Execute Conversion ---
    convert_csv_to_json(
        csv_file_path=args.input_csv_file,
        json_output_path=args.output,
        encoding=args.encoding,
        indent=indent_level
    )

    sys.exit(0) # Explicitly exit with success code
