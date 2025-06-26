**Warning**: The below was entirely written by Claude Code, use at your own risk.

# paste2markdown

Convert rich text to Markdown when pasting on macOS using Karabiner-Elements.

## What it does

paste2mark intercepts the Option+V keyboard shortcut and automatically converts rich text content from your clipboard to clean Markdown before pasting. This is perfect for:

- Pasting from web pages into Markdown editors
- Converting formatted emails to Markdown
- Cleaning up rich text from Word/Google Docs
- Any workflow where you want Markdown instead of formatted text

## How it works

1. Copy any rich text (from a website, document, etc.)
2. Press **Option+V** instead of Cmd+V
3. The rich text is automatically converted to Markdown and pasted

The original clipboard content is preserved, so you can still use regular Cmd+V if needed.

## Installation

### Prerequisites

- macOS (tested on macOS 12+)
- Python 3.7+
- [Homebrew](https://brew.sh/) (for installing Karabiner-Elements)

### Step 1: Install Dependencies

```bash
# Install Karabiner-Elements
brew install --cask karabiner-elements

# Clone this repository
git clone https://github.com/yourusername/paste2mark.git
cd paste2mark

# Install Python dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Karabiner-Elements

1. **Copy the Karabiner rule** to your config directory:
   ```bash
   mkdir -p ~/.config/karabiner/assets/complex_modifications
   cp karabiner/paste2mark.json ~/.config/karabiner/assets/complex_modifications/
   ```

2. **Update the script path** in the rule:
   ```bash
   # Edit the rule file
   nano ~/.config/karabiner/assets/complex_modifications/paste2mark.json
   
   # Update the path to point to where you cloned the repo
   # Change: "/Users/neelnanda/Code/paste2mark/paste2mark_karabiner.py"
   # To: "/path/to/your/paste2mark/paste2mark_karabiner.py"
   ```

3. **Enable the rule in Karabiner-Elements**:
   - Open Karabiner-Elements
   - Go to "Complex Modifications" tab
   - Click "Add rule"
   - Find "Paste as Markdown" and click "Enable"

### Step 3: Make the Script Executable

```bash
chmod +x paste2mark_karabiner.py
```

## Usage

1. Copy any rich text content (select and Cmd+C)
2. Press **Option+V** to paste as Markdown
3. The content is converted and pasted automatically

## Features

- Converts HTML and RTF to clean Markdown
- Preserves links, headings, lists, and emphasis
- Handles complex formatting gracefully
- Falls back to plain text if no rich content is available
- Restores original clipboard after pasting

## Troubleshooting

### Option+V doesn't work

1. Check that the Karabiner rule is enabled (Complex Modifications tab)
2. Verify the script path in the rule points to the correct location
3. Check the logs: `tail -f ~/Library/Logs/paste2mark/paste2mark.log`

### Permission errors

If you see permission errors, you may need to grant accessibility permissions:
1. System Preferences → Security & Privacy → Privacy → Accessibility
2. Add Terminal.app or your terminal emulator
3. Add Karabiner-Elements if not already present

### Python import errors

Ensure PyObjC is installed:
```bash
pip install -r requirements.txt
```

## How It's Built

paste2mark uses:
- **Karabiner-Elements** to intercept Option+V at the system level
- **PyObjC** to access macOS clipboard APIs
- **markdownify** and **html2text** for HTML→Markdown conversion
- **Quartz** framework for simulating the paste keystroke

## Why Karabiner-Elements?

Using Karabiner-Elements instead of a keyboard listener provides:
- **Safety**: No risk of blocking all keyboard input
- **Reliability**: Kernel-level key interception
- **No conflicts**: Prevents the default Option+V (√) character
- **Easy control**: Disable anytime from Karabiner's menu bar

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Inspired by various clipboard managers and text conversion tools
- Thanks to the Karabiner-Elements team for the powerful customization framework
