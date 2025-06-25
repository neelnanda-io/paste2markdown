# Paste2Mark

A macOS background utility that converts rich text in your clipboard to markdown when you press Option+V.

## What It Does

When you copy rich text (from web pages, Word documents, etc.) and press Option+V, this app:
1. Reads the rich text from your clipboard
2. Converts it to clean markdown format
3. Pastes the markdown text at your cursor
4. Restores your original clipboard content

## Setup

1. Install dependencies:
   ```bash
   ./run.sh
   ```

2. Grant accessibility permissions:
   - Go to System Preferences → Security & Privacy → Privacy → Accessibility
   - Add Terminal (or your terminal app) to the allowed apps
   - This is required for the app to detect keyboard shortcuts and simulate paste

## Usage

1. Run the app:
   ```bash
   ./run.sh
   ```

2. Copy any rich text (from a webpage, document, etc.)

3. Press **Option+V** to paste as markdown

4. Press **Ctrl+C** to stop the app

## Logs

Logs are saved to: `~/Library/Logs/paste2mark/paste2mark.log`

## Technical Details

- Uses PyObjC to access macOS clipboard APIs
- Handles both HTML and RTF rich text formats
- Preserves links, headings, lists, and other formatting as markdown
- Temporarily replaces clipboard content during paste, then restores original

## Keyboard Shortcuts

- **Option+V**: Paste clipboard content as markdown

## Troubleshooting

If Option+V doesn't work:
1. Check that Terminal has accessibility permissions
2. Check the logs for any errors
3. Make sure no other app is intercepting Option+V