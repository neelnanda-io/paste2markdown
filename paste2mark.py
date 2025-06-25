#!/usr/bin/env python3
"""
IMPORTANT: This script uses pynput keyboard listener which has limitations.
For a more reliable solution, use the Karabiner-Elements integration:
- See paste2mark_karabiner.py and the Karabiner rule in ~/.config/karabiner/
- Instructions in KARABINER_SETUP.md

This version uses Option+M to avoid conflicts with macOS's Option+V (√).
Press Option+Q to quit.
"""
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

import AppKit
import Foundation
from pynput import keyboard
from markdownify import markdownify
import html2text

LOG_DIR = os.path.expanduser("~/Library/Logs/paste2mark")
os.makedirs(LOG_DIR, exist_ok=True)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = os.path.join(LOG_DIR, 'paste2mark.log')
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(log_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger('paste2mark')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class RichTextToMarkdownConverter:
    def __init__(self):
        self.pasteboard = AppKit.NSPasteboard.generalPasteboard()
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0
        self.h2t.protect_links = True
        self.h2t.wrap_links = False
        
        self.current_keys = set()
        self.option_pressed = False
        
    def get_clipboard_content(self):
        """Get rich text content from clipboard and convert to markdown"""
        types = self.pasteboard.types()
        logger.info(f"Available clipboard types: {types}")
        
        if AppKit.NSPasteboardTypeHTML in types:
            html_data = self.pasteboard.dataForType_(AppKit.NSPasteboardTypeHTML)
            if html_data:
                html_string = html_data.decode('utf-8', errors='ignore')
                logger.info(f"Found HTML content: {html_string[:200]}...")
                return self.convert_html_to_markdown(html_string)
        
        if AppKit.NSPasteboardTypeRTF in types:
            rtf_data = self.pasteboard.dataForType_(AppKit.NSPasteboardTypeRTF)
            if rtf_data:
                logger.info("Found RTF content, converting to HTML first")
                attributed_string = AppKit.NSAttributedString.alloc().initWithRTF_documentAttributes_(
                    rtf_data, None
                )[0]
                if attributed_string:
                    html_data = attributed_string.dataFromRange_documentAttributes_error_(
                        Foundation.NSMakeRange(0, attributed_string.length()),
                        {AppKit.NSDocumentTypeDocumentAttribute: AppKit.NSHTMLTextDocumentType},
                        None
                    )[0]
                    if html_data:
                        html_string = html_data.decode('utf-8', errors='ignore')
                        return self.convert_html_to_markdown(html_string)
        
        if AppKit.NSPasteboardTypeString in types:
            plain_text = self.pasteboard.stringForType_(AppKit.NSPasteboardTypeString)
            logger.info("Only plain text found in clipboard")
            return plain_text
        
        logger.warning("No supported content found in clipboard")
        return None
    
    def convert_html_to_markdown(self, html_string):
        """Convert HTML to clean markdown"""
        try:
            cleaned_html = html_string
            if '<html>' not in cleaned_html.lower():
                cleaned_html = f'<html><body>{cleaned_html}</body></html>'
            
            markdown = markdownify(cleaned_html, 
                                 heading_style="ATX",
                                 bullets="-",
                                 strip=['style', 'script'])
            
            lines = markdown.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.rstrip()
                if line:
                    cleaned_lines.append(line)
                elif cleaned_lines and cleaned_lines[-1]:
                    cleaned_lines.append('')
            
            while cleaned_lines and not cleaned_lines[-1]:
                cleaned_lines.pop()
            
            markdown = '\n'.join(cleaned_lines)
            
            logger.info(f"Converted to markdown: {markdown[:200]}...")
            return markdown
            
        except Exception as e:
            logger.error(f"Error converting HTML to markdown: {e}")
            try:
                markdown = self.h2t.handle(html_string)
                return markdown.strip()
            except Exception as e2:
                logger.error(f"Fallback conversion also failed: {e2}")
                return html_string
    
    def paste_as_markdown(self):
        """Convert clipboard content to markdown and paste it"""
        try:
            logger.info("Option+V pressed, converting clipboard to markdown")
            
            markdown_content = self.get_clipboard_content()
            if not markdown_content:
                logger.warning("No content to convert")
                return
            
            original_types = self.pasteboard.types()
            original_data = {}
            for type_ in original_types:
                data = self.pasteboard.dataForType_(type_)
                if data:
                    original_data[type_] = data
            
            self.pasteboard.clearContents()
            self.pasteboard.setString_forType_(markdown_content, AppKit.NSPasteboardTypeString)
            
            logger.info("Clipboard updated with markdown, triggering paste")
            
            from Quartz import CGEventCreateKeyboardEvent, CGEventPost, kCGHIDEventTap
            
            v_key_code = 0x09
            
            key_down = CGEventCreateKeyboardEvent(None, v_key_code, True)
            key_up = CGEventCreateKeyboardEvent(None, v_key_code, False)
            
            CGEventSetFlags(key_down, 0x100000)
            CGEventSetFlags(key_up, 0x100000)
            
            CGEventPost(kCGHIDEventTap, key_down)
            time.sleep(0.01)
            CGEventPost(kCGHIDEventTap, key_up)
            
            time.sleep(0.1)
            
            self.pasteboard.clearContents()
            for type_, data in original_data.items():
                self.pasteboard.setData_forType_(data, type_)
            
            logger.info("Paste completed and original clipboard restored")
            
        except Exception as e:
            logger.error(f"Error in paste_as_markdown: {e}", exc_info=True)
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            if key == keyboard.Key.alt:
                self.option_pressed = True
                self.current_keys.add('option')
            elif hasattr(key, 'char') and key.char == 'm' and self.option_pressed:
                logger.info("Detected Option+M combination (for Markdown)")
                self.paste_as_markdown()
                # Don't return False - that would stop the listener
            elif hasattr(key, 'char') and key.char == 'q' and self.option_pressed:
                logger.info("Detected Option+Q - Exiting paste2mark")
                return False  # This will stop the listener and exit the program
        except Exception as e:
            logger.error(f"Error in on_press: {e}")
    
    def on_release(self, key):
        """Handle key release events"""
        try:
            if key == keyboard.Key.alt:
                self.option_pressed = False
                self.current_keys.discard('option')
        except Exception as e:
            logger.error(f"Error in on_release: {e}")
    
    def run(self):
        """Run the keyboard listener"""
        logger.info("Starting paste2mark - Press Option+M to paste as markdown, Option+Q to quit")
        logger.info(f"Logs are being written to: {log_file}")
        logger.warning("SAFETY: This script uses suppress=False. NEVER change this to suppress=True!")
        
        # CRITICAL WARNING: NEVER set suppress=True here!
        # suppress=True will block ALL keyboard input system-wide
        with keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=False  # MUST be False to avoid blocking all keyboard input
        ) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                logger.info("Paste2mark stopped by user")
                sys.exit(0)

def main():
    converter = RichTextToMarkdownConverter()
    converter.run()

if __name__ == "__main__":
    main()