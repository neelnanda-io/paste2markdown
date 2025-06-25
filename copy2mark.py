#!/usr/bin/env python3
import subprocess
import time
import sys


def get_html_from_clipboard():
    """Get HTML content from clipboard, if available"""
    try:
        # Try to get HTML first
        result = subprocess.run(
            ["osascript", "-e", "the clipboard as «class HTML»"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout:
            # Extract the hex data and convert to string
            hex_data = result.stdout.strip()
            # Convert from hex to bytes to string
            html = bytes.fromhex(
                hex_data.replace("«data HTML", "").replace("»", "")
            ).decode("utf-8")
            return html
    except:
        pass

    # Fall back to RTF if HTML not available
    try:
        result = subprocess.run(
            ["osascript", "-e", "the clipboard as «class RTF»"], capture_output=True
        )
        if result.returncode == 0:
            # Convert RTF to HTML using textutil
            html = subprocess.run(
                ["textutil", "-convert", "html", "-stdin", "-stdout"],
                input=result.stdout,
                capture_output=True,
                text=True,
            ).stdout
            return html
    except:
        pass

    return None


def html_to_markdown(html):
    """Convert HTML to markdown"""
    try:
        # Use pandoc if available (best quality)
        result = subprocess.run(
            ["pandoc", "-f", "html", "-t", "markdown", "--wrap=none"],
            input=html,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass

    # Fallback to Python library
    try:
        from markdownify import markdownify as md

        return md(html, heading_style="ATX", bullets="-")
    except ImportError:
        print(
            "Install pandoc (brew install pandoc) or markdownify (pip install markdownify)"
        )
        sys.exit(1)


# Save current clipboard
old_clipboard = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout

# Copy current selection
subprocess.run(
    [
        "osascript",
        "-e",
        'tell application "System Events" to keystroke "c" using command down',
    ]
)

# Give it a moment to populate clipboard
time.sleep(0.1)

# Check if clipboard changed (i.e., something was selected)
new_clipboard = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout
if old_clipboard == new_clipboard:
    print("No text selected")
    sys.exit(1)

# Get formatted content
html = get_html_from_clipboard()

if html:
    # Convert to markdown
    markdown = html_to_markdown(html)

    # Put markdown on clipboard
    subprocess.run(["pbcopy"], input=markdown.encode("utf-8"))

    # Optional: Show notification
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "Copied as markdown" with title "Formatted Copy"',
        ]
    )
else:
    # No formatting available, keep plain text
    print("No formatted text found, keeping plain text")
