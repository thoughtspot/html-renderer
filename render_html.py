# render_html.py
import http.server
import socketserver
import os
import argparse
import webbrowser
import functools
import sys

DEFAULT_PORT = 8000

def serve_html(file_path, port):
    """
    Serves the directory containing the specified HTML file via a local HTTP server
    and opens the file in the default web browser.

    Args:
        file_path (str): The path to the HTML file.
        port (int): The port number to run the server on.
    """
    try:
        # Ensure the file path is absolute and exists
        abs_file_path = os.path.abspath(file_path)
        if not os.path.isfile(abs_file_path):
            print(f"Error: File not found at '{abs_file_path}'", file=sys.stderr)
            sys.exit(1) # Exit with error code

        # Determine the directory to serve and the filename
        directory_to_serve = os.path.dirname(abs_file_path)
        file_to_open = os.path.basename(abs_file_path)

        print(f"Attempting to serve directory: '{directory_to_serve}' on port {port}...")

        # Create a handler that serves files from the specific directory
        # Uses functools.partial to pass the 'directory' argument (Python 3.7+)
        Handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                    directory=directory_to_serve)

        # Set up the TCP server
        # Allow address reuse to prevent "Address already in use" errors on quick restarts
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", port), Handler) as httpd:
            server_address = f"http://localhost:{port}/{file_to_open}"
            print(f"Serving file '{file_to_open}'")
            print(f"Access it at: {server_address}")
            print(f"Serving files from: {directory_to_serve}")
            print("Press Ctrl+C to stop the server.")

            # Attempt to open the browser automatically
            try:
                webbrowser.open(server_address)
            except Exception as e:
                print(f"Warning: Could not automatically open web browser: {e}", file=sys.stderr)

            # Keep the server running until interrupted
            httpd.serve_forever()

    except OSError as e:
        if e.errno == 98: # Address already in use (Linux/macOS)
             print(f"Error: Port {port} is already in use. Try a different port using --port.", file=sys.stderr)
        elif e.errno == 10048: # Address already in use (Windows)
             print(f"Error: Port {port} is already in use. Try a different port using --port.", file=sys.stderr)
        else:
             print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1) # Exit with error code
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.")
        sys.exit(0) # Exit successfully
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1) # Exit with error code


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Render a local HTML file by serving its directory via HTTP and opening it in a browser."
    )
    parser.add_argument(
        "html_file",
        help="Path to the HTML file to render."
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port number to use for the local server (default: {DEFAULT_PORT})."
    )

    # Parse arguments
    args = parser.parse_args()

    # Run the server function
    serve_html(args.html_file, args.port)
