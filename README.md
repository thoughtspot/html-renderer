# Simple Python HTML Renderer

This project provides a command-line Python script (`render_html.py`) that takes a path to an HTML file, serves its containing directory using Python's built-in HTTP server, and attempts to open the specified HTML file in your default web browser.

## Features

* Uses only Python's standard library (no external dependencies needed).
* Serves the entire directory of the HTML file, allowing relative links (CSS, JS, images) to function.
* Opens the specific HTML file in the browser automatically.
* Configurable server port.
* Basic error handling (file not found, port in use).
* Graceful shutdown on Ctrl+C.

## Requirements

* Python 3.7+ (due to usage of `functools.partial` with `http.server.SimpleHTTPRequestHandler`)
