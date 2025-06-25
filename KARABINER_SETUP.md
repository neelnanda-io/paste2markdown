# Karabiner-Elements Setup for paste2mark

This is the recommended way to use paste2mark. It's more reliable and safer than the pynput-based approach.

## Installation

1. **Install Karabiner-Elements** (if not already installed):
   ```bash
   brew install --cask karabiner-elements
   ```

2. **The configuration is already set up** at:
   - Rule file: `~/.config/karabiner/assets/complex_modifications/paste2mark.json`
   - Python script: `/Users/neelnanda/Code/paste2mark/paste2mark_karabiner.py`

3. **Enable the rule in Karabiner-Elements**:
   - Open Karabiner-Elements
   - Go to "Complex Modifications" tab
   - Click "Add rule"
   - Find "Paste as Markdown" and click "Enable"

## How It Works

1. **Option+V** is intercepted by Karabiner at the kernel level
2. The original √ character is prevented
3. Karabiner runs the Python script
4. The script:
   - Reads the clipboard
   - Converts rich text/HTML to markdown
   - Temporarily replaces clipboard content
   - Triggers Cmd+V to paste
   - Restores original clipboard

## Advantages Over pynput Version

- **No risk of blocking all keyboard input**
- **No √ character conflicts**
- **More reliable key interception**
- **Survives script crashes**
- **Can be easily disabled in Karabiner UI**

## Logs

Logs are written to: `~/Library/Logs/paste2mark/paste2mark_karabiner.log`

## Troubleshooting

1. **If Option+V doesn't work**:
   - Check that the rule is enabled in Karabiner-Elements
   - Check the log file for errors
   - Ensure the Python script has execute permissions
   - Make sure PyObjC is installed: `pip install -r requirements.txt`

2. **VSCode import errors**:
   - VSCode may show false errors for `AppKit`, `Foundation`, and `Quartz` imports
   - These are PyObjC bindings that VSCode's Python extension may not recognize
   - The code will still run correctly despite the warnings
   - To fix: ensure VSCode is using the correct Python interpreter with PyObjC installed

3. **Accessibility permissions**:
   - The script uses Quartz events which shouldn't require special permissions
   - If you still get permission errors, you may need to grant Terminal/iTerm accessibility permissions in System Preferences > Security & Privacy > Privacy > Accessibility

4. **To disable temporarily**:
   - Just quit Karabiner-Elements from the menu bar

5. **To uninstall**:
   - Remove the rule in Karabiner-Elements UI
   - Or delete `~/.config/karabiner/assets/complex_modifications/paste2mark.json`