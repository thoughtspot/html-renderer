import argparse
import os
import re
import sys
import json
from collections import defaultdict

# --- Configuration ---

# Basic tokenizer: split by whitespace and common programming punctuation/operators
# Keeps delimited sequences like '==' '!=' '->' together somewhat.
# Adjust this regex based on desired granularity for the basic mode.
BASIC_TOKEN_PATTERN = re.compile(r'\s+|([(){}\[\].,;:"\'`~]|->|==|!=|<=|>=|&&|\|\||\+=|-=|\*=|/=|%=|^=|\/\/|<<|>>|\*\*|[-+*/%<>=&|!^])')

# Common code file extensions to process by default
CODE_EXTENSIONS = {
    '.py', '.go', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.rb', '.php', '.swift', '.kt', '.scala', '.rs', '.lua', '.sh', '.bash',
    '.html', '.css', '.scss', '.sql', '.yaml', '.yml', '.json', '.md', '.txt'
}

# Attempt to import tiktoken, fail gracefully if not installed
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None # Define it as None so checks don't fail

# --- Helper Functions ---

def basic_tokenizer(text):
    """
    Performs basic tokenization using regex splitting.

    Args:
        text (str): The input text (code).

    Returns:
        list[str]: A list of basic tokens.
    """
    tokens = []
    # Split by the pattern, keeping the delimiters if they are captured
    parts = BASIC_TOKEN_PATTERN.split(text)
    for part in parts:
        if part: # Ignore empty strings resulting from split
            tokens.append(part.strip()) # Strip whitespace just in case
    # Filter out any purely whitespace tokens that might remain
    return [token for token in tokens if token and not token.isspace()]

def tiktoken_tokenizer(text, model_name="gpt-4"):
    """
    Performs tokenization using the tiktoken library.

    Args:
        text (str): The input text (code).
        model_name (str): The name of the model to get the tokenizer for
                          (e.g., "gpt-4", "gpt-3.5-turbo").

    Returns:
        list[int]: A list of token IDs.
        object: The tiktoken encoding object (for decoding if needed).
    """
    if not TIKTOKEN_AVAILABLE:
        raise ImportError("tiktoken library is not installed. Cannot use 'tiktoken' mode.")
    try:
        # Get the encoding for the specified model
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        print(f"Warning: Model '{model_name}' not found by tiktoken. Falling back to 'cl100k_base'.", file=sys.stderr)
        # cl100k_base is the encoding used by gpt-4, gpt-3.5-turbo, text-embedding-ada-002
        encoding = tiktoken.get_encoding("cl100k_base")

    token_ids = encoding.encode(text)
    return token_ids, encoding

def process_file(file_path, mode, model_name):
    """
    Reads a file and tokenizes its content based on the selected mode.

    Args:
        file_path (str): Path to the file.
        mode (str): Tokenization mode ('basic' or 'tiktoken').
        model_name (str): Tiktoken model name (if mode is 'tiktoken').

    Returns:
        tuple: (list_of_tokens_or_ids, token_count, error_message or None)
               Returns (None, 0, error_message) if reading fails.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if mode == 'basic':
            tokens = basic_tokenizer(content)
            return tokens, len(tokens), None
        elif mode == 'tiktoken':
            if not TIKTOKEN_AVAILABLE:
                 return None, 0, "tiktoken library not installed"
            token_ids, _ = tiktoken_tokenizer(content, model_name)
            return token_ids, len(token_ids), None
        else:
            # Should not happen with argparse choices
            return None, 0, f"Invalid mode: {mode}"

    except FileNotFoundError:
        return None, 0, f"File not found: {file_path}"
    except Exception as e:
        return None, 0, f"Error processing file {file_path}: {e}"

def find_code_files(start_path, allowed_extensions):
    """
    Recursively finds files with specified extensions in a directory,
    or returns the path itself if it's a single file.

    Args:
        start_path (str): The directory or file path to start searching from.
        allowed_extensions (set): A set of lowercase file extensions (e.g., {'.py', '.go'}).

    Returns:
        list[str]: A list of absolute paths to the found code files.
    """
    code_files = []
    abs_start_path = os.path.abspath(start_path)

    if not os.path.exists(abs_start_path):
        print(f"Error: Input path does not exist: {abs_start_path}", file=sys.stderr)
        return []

    if os.path.isfile(abs_start_path):
        _, ext = os.path.splitext(abs_start_path)
        if ext.lower() in allowed_extensions:
            code_files.append(abs_start_path)
        else:
            print(f"Warning: Skipping file with unsupported extension: {abs_start_path}", file=sys.stderr)
    elif os.path.isdir(abs_start_path):
        for root, _, files in os.walk(abs_start_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower() in allowed_extensions:
                    code_files.append(os.path.join(root, file))
    else:
         print(f"Error: Input path is neither a file nor a directory: {abs_start_path}", file=sys.stderr)

    return code_files

# --- Main Execution ---

def main():
    parser = argparse.ArgumentParser(
        description="Tokenize code files for analysis or LLM input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic tokenization of a single file, print counts
  python tokenize_code.py sample_code/example.py --mode basic

  # Tiktoken tokenization (gpt-4 model) of a directory, print counts
  python tokenize_code.py sample_code/ --mode tiktoken --model gpt-4

  # Basic tokenization, save concatenated tokens to a file
  python tokenize_code.py sample_code/ -m basic -o output/basic_tokens.txt

  # Tiktoken tokenization, save concatenated token IDs (as JSON list) to a file
  python tokenize_code.py sample_code/ -m tiktoken -o output/token_ids.json
"""
    )

    parser.add_argument(
        "input_path",
        help="Path to the code file or directory containing code files."
    )
    parser.add_argument(
        "-m", "--mode",
        choices=['basic', 'tiktoken'],
        required=True,
        help="Tokenization mode: 'basic' (simple regex split) or 'tiktoken' (LLM-specific, requires tiktoken library)."
    )
    parser.add_argument(
        "--model",
        default="gpt-4",
        help="Model name for tiktoken tokenizer (e.g., 'gpt-4', 'gpt-3.5-turbo'). Used only if mode is 'tiktoken'."
    )
    parser.add_argument(
        "-o", "--output",
        metavar="OUTPUT_FILE",
        help="Optional path to save the concatenated tokens or token IDs. "
             "Basic mode saves tokens separated by spaces. "
             "Tiktoken mode saves a JSON list of lists (one list per file)."
    )
    parser.add_argument(
        "--extensions",
        nargs='+',
        default=list(CODE_EXTENSIONS),
        help=f"List of file extensions to process (default: {' '.join(sorted(CODE_EXTENSIONS))})."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed information about each file processed."
    )

    args = parser.parse_args()

    # --- Input Validation ---
    if args.mode == 'tiktoken' and not TIKTOKEN_AVAILABLE:
        print("Error: Mode 'tiktoken' selected, but the 'tiktoken' library is not installed.", file=sys.stderr)
        print("Please install it: pip install tiktoken", file=sys.stderr)
        sys.exit(1)

    allowed_extensions = {ext.lower() if ext.startswith('.') else '.' + ext.lower() for ext in args.extensions}
    print(f"Processing files with extensions: {', '.join(sorted(allowed_extensions))}")

    # --- Find Files ---
    code_files = find_code_files(args.input_path, allowed_extensions)
    if not code_files:
        print("No code files found to process.", file=sys.stderr)
        sys.exit(0)

    print(f"Found {len(code_files)} code file(s) to process.")

    # --- Process Files ---
    all_results = {}
    total_token_count = 0
    errors = []

    for file_path in sorted(code_files):
        if args.verbose:
            print(f"Processing: {file_path}...")

        tokens_or_ids, count, error = process_file(file_path, args.mode, args.model)

        if error:
            errors.append(f"{file_path}: {error}")
            if args.verbose:
                print(f"  Error: {error}", file=sys.stderr)
            all_results[file_path] = {"count": 0, "error": error}
        else:
            total_token_count += count
            all_results[file_path] = {"count": count, "tokens": tokens_or_ids} # Store tokens/IDs temporarily
            if args.verbose:
                print(f"  Tokens ({args.mode}): {count}")

    # --- Report Results ---
    print("\n--- Summary ---")
    for file_path, result in all_results.items():
         if "error" in result:
              print(f"{file_path}: Error ({result['error']})")
         else:
              print(f"{file_path}: {result['count']} tokens ({args.mode})")

    print(f"\nTotal tokens across all processed files: {total_token_count} ({args.mode})")

    if errors:
        print(f"\nEncountered {len(errors)} error(s) during processing.")
        # Optionally print all errors again here if not verbose
        # for err in errors:
        #     print(f"  - {err}", file=sys.stderr)

    # --- Save Output (if requested) ---
    if args.output:
        abs_output_path = os.path.abspath(args.output)
        output_dir = os.path.dirname(abs_output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists

        print(f"\nSaving concatenated output to: {abs_output_path}")
        try:
            with open(abs_output_path, 'w', encoding='utf-8') as outfile:
                if args.mode == 'basic':
                    # Concatenate all basic tokens with spaces
                    all_tokens_flat = []
                    for file_path in sorted(all_results.keys()): # Ensure consistent order
                         result = all_results[file_path]
                         if "tokens" in result:
                              all_tokens_flat.extend(result["tokens"])
                    outfile.write(" ".join(all_tokens_flat))
                elif args.mode == 'tiktoken':
                    # Save as a JSON list containing one list of IDs per file
                    output_data = []
                    for file_path in sorted(all_results.keys()): # Ensure consistent order
                        result = all_results[file_path]
                        if "tokens" in result: # 'tokens' here actually holds token IDs
                            output_data.append(result["tokens"])
                        else:
                            # Optionally include placeholder for errored files, e.g., None or []
                            output_data.append({"error": result.get("error", "Unknown error"), "file": file_path})
                    json.dump(output_data, outfile, indent=None) # Compact JSON for IDs

            print("Output saved successfully.")
        except IOError as e:
            print(f"Error writing output file '{abs_output_path}': {e}", file=sys.stderr)
            errors.append(f"Output Error: {e}") # Add to error summary
        except Exception as e:
            print(f"An unexpected error occurred during output saving: {e}", file=sys.stderr)
            errors.append(f"Output Error: {e}")

    # --- Final Exit Status ---
    if errors and not args.output: # Exit with error if errors occurred and we didn't attempt/fail output
         sys.exit(1)
    elif errors and args.output and any("Output Error" in e for e in errors): # Exit with error if output failed
         sys.exit(1)
    else: # Exit successfully if no errors, or only processing errors but output succeeded
         sys.exit(0)


if __name__ == "__main__":
    main()

