# Code Tokenizer Tool

This Python script (`tokenize_code.py`) processes code files (either a single file or recursively through a directory) and breaks them down into tokens. It offers two distinct modes for tokenization:

1.  **`basic` Mode:** Uses Python's standard library (`re`) to perform a simple split based on whitespace and common programming symbols. This is language-agnostic but does *not* replicate how Large Language Models (LLMs) actually tokenize text.
2.  **`tiktoken` Mode:** Uses the external `tiktoken` library (developed by OpenAI) to tokenize code exactly as models like GPT-4, GPT-3.5-Turbo, and embedding models do. This produces integer token IDs and is the recommended mode if your goal is to prepare code for input into such LLMs. **This mode requires installing `tiktoken` (`pip install tiktoken`).**

The tool reports the token count for each processed file and a total count. It can optionally save the concatenated tokens (for `basic` mode) or token IDs (for `tiktoken` mode) to an output file.

## Features

* Process single files or directories recursively.
* Filter files by common code extensions (customizable).
* Two tokenization modes:
    * `basic`: Standard library regex splitting (simple, no external dependencies).
    * `tiktoken`: LLM-specific tokenization (accurate for OpenAI models, requires `pip install tiktoken`).
* Reports token counts per file and total.
* Optional output to a file:
    * `basic` mode: Concatenated string tokens, space-separated.
    * `tiktoken` mode: JSON list of lists, where each inner list contains the integer token IDs for one file.
* Verbose mode for detailed processing logs.
* Error handling for file access and tokenization issues.

## Requirements

* Python 3.7+ (for standard library features used)
* **Optional (for `tiktoken` mode):** `tiktoken` library (`pip install tiktoken`)

## Project Structure

```
./pytools/code-tokenizer
├── tokenize_code.py   # The main Python script
├── requirements.txt   # Lists tiktoken as optional/recommended
├── sample_code/       # Directory with sample code files
│   ├── example.py
│   └── example.go
└── README.md          # This file
```

## Usage

Run the script from your terminal:

```bash
python tokenize_code.py <input_path> --mode <basic|tiktoken> [options]
```

**Arguments:**

* `input_path`: (Required) Path to the code file or directory to process.
* `--mode` / `-m`: (Required) Choose `basic` or `tiktoken`.
* `--model`: (Optional, `tiktoken` mode only) Specify the OpenAI model name (e.g., `gpt-4`, `gpt-3.5-turbo`) to ensure the correct tokenizer is used. Defaults to `gpt-4`.
* `--output` / `-o`: (Optional) Path to save concatenated tokens/IDs.
* `--extensions`: (Optional) Specify which file extensions to process (e.g., `--extensions .py .js .go`). Defaults to a predefined list of common code extensions.
* `--verbose` / `-v`: (Optional) Enable detailed logging during processing.

**Examples:**

1.  **Basic tokenization of a single file, print counts:**
    ```bash
    python tokenize_code.py sample_code/example.py --mode basic
    ```

2.  **Tiktoken tokenization (default gpt-4 model) of a directory, print counts:**
    *(Requires `pip install tiktoken`)*
    ```bash
    python tokenize_code.py sample_code/ --mode tiktoken
    ```

3.  **Tiktoken tokenization using gpt-3.5-turbo model:**
    ```bash
    python tokenize_code.py sample_code/ --mode tiktoken --model gpt-3.5-turbo
    ```

4.  **Basic tokenization of Python files only in a directory, save concatenated tokens:**
    ```bash
    mkdir -p output # Create output dir if needed
    python tokenize_code.py sample_code/ -m basic --extensions .py -o output/py_basic_tokens.txt -v
    ```

5.  **Tiktoken tokenization, save concatenated token IDs (as JSON list):**
    ```bash
    mkdir -p output # Create output dir if needed
    python tokenize_code.py sample_code/ -m tiktoken -o output/all_token_ids.json
    ```

## Notes on Tokenization Modes

* **Basic Mode:** Useful for simple analysis or if you cannot install external libraries. The token count will differ significantly from LLM token counts. The `BASIC_TOKEN_PATTERN` regex can be adjusted for different splitting behavior.
* **Tiktoken Mode:** This is the most accurate way to measure or prepare code for interaction with OpenAI LLMs. The token counts directly reflect how the model will process the input length. Remember to install the library (`pip install tiktoken`).


