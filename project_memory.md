# Project Memory

## Purpose
This project provides a macOS background utility that intercepts the Option+V keyboard shortcut to paste clipboard content as markdown instead of rich text. It's designed for users who frequently need to convert formatted text from web pages or documents into clean markdown format.

## Key Technologies
- Python 3
- PyObjC (for macOS clipboard and system integration)
- pynput (for global keyboard shortcut handling)
- markdownify & html2text (for HTML to markdown conversion)
- AppKit/Foundation (macOS frameworks)

## Architecture Overview
The app runs as a background Python process that:
1. Listens for the Option+V keyboard combination using pynput
2. Accesses clipboard content via NSPasteboard (AppKit)
3. Converts HTML/RTF content to markdown using markdownify
4. Temporarily replaces clipboard with markdown text
5. Triggers a system paste event (Cmd+V)
6. Restores the original clipboard content

## Development Notes
- Requires macOS accessibility permissions for keyboard monitoring
- Logs are written to ~/Library/Logs/paste2mark/ for debugging
- The app preserves the original clipboard after pasting
- Handles both HTML and RTF rich text formats
- Uses suppress=True in keyboard listener to prevent the original Option+V from being processed

## Keyboard Shortcuts
- Option+V: Convert clipboard to markdown and paste