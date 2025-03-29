#!/usr/bin/env python3
import sys
from pathlib import Path

import chardet
import yaml


def is_binary(file_path):
    """Check if a file is binary by reading its first chunk."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            if not chunk:  # Empty file
                return False

            # Check for null bytes which typically indicate binary file
            if b"\x00" in chunk:
                return True

            # Try to decode as text
            try:
                # Detect encoding
                result = chardet.detect(chunk)
                encoding = result["encoding"] or "utf-8"
                chunk.decode(encoding)
                return False
            except UnicodeDecodeError:
                return True
    except Exception as e:
        print(f"Error checking if {file_path} is binary: {str(e)}", file=sys.stderr)
        return True


def read_file_content(file_path):
    """Read file content with proper encoding detection."""
    try:
        # First read as binary to detect encoding
        with open(file_path, "rb") as f:
            content = f.read()

        if not content:
            return ""

        # Detect encoding
        result = chardet.detect(content)
        encoding = result["encoding"] or "utf-8"

        # Decode using detected encoding
        text_content = content.decode(encoding, errors="replace")
        return text_content
    except Exception as e:
        print(f"Error reading {file_path}: {str(e)}", file=sys.stderr)
        return f"ERROR: Could not read file - {str(e)}"


def main():
    """Main function to process files and output YAML."""
    # Get current directory
    current_dir = Path(".")

    # Get list of files (excluding hidden, .pyc, and directories)
    files = []
    try:
        for item in current_dir.iterdir():
            if (
                item.is_file()
                and not item.name.startswith(".")
                and not item.name.endswith(".pyc")
                and item.name != "format_files_to_yaml.py"
            ):  # Skip this script itself
                files.append(item)
    except Exception as e:
        print(f"Error listing directory: {str(e)}", file=sys.stderr)
        return 1

    # Process each file
    first_file = True
    for file_path in sorted(files):
        try:
            # Skip binary files
            if is_binary(file_path):
                print(f"Skipping binary file: {file_path}", file=sys.stderr)
                continue

            # Read file content
            content = read_file_content(file_path)

            # If not the first file, print separator
            if not first_file:
                print("---")
            else:
                first_file = False

            # Output as YAML
            yaml_content = {str(file_path): content}
            print(yaml.dump(yaml_content, default_flow_style=False, allow_unicode=True), end="")

        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
