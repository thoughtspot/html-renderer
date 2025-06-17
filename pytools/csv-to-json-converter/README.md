# CSV to JSON Converter

A command-line tool to convert data from a CSV file into a JSON format. It reads the CSV, using the first row as headers for keys, and outputs a JSON array of objects.

## Features

* Uses only Python's standard library (`csv`, `json`, `argparse`).
* Converts CSV rows into a JSON array of dictionaries.
* Automatically uses the first row as headers for JSON keys.
* Cleans up header names (strips whitespace, lowercases, replaces spaces with underscores).
* Optionally outputs JSON to a file or prints to standard output.
* Optionally specifies input file encoding (defaults to `utf-8-sig`).
* Optionally pretty-prints JSON output with indentation.
* Includes error handling for common issues (file not found, encoding errors).

## Requirements

* Python 3.6+ (standard library usage)

## Project Structure
