#!/usr/bin/env python3
"""
Simplified paste2mark script for use with Karabiner-Elements.
This script is called by Karabiner when Option+V is pressed.
It converts rich text clipboard content to markdown and pastes it.
"""

import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import os
import subprocess

import AppKit
import Foundation
import Quartz
from markdownify import markdownify
import html2text

# Setup logging
LOG_DIR = os.path.expanduser("~/Library/Logs/paste2mark")
os.makedirs(LOG_DIR, exist_ok=True)

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = os.path.join(LOG_DIR, 'paste2mark_karabiner.log')
file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
file_handler.setFormatter(log_formatter)

logger = logging.getLogger('paste2mark_karabiner')
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class ClipboardMarkdownConverter:
    def __init__(self):
        self.pasteboard = AppKit.NSPasteboard.generalPasteboard()
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0
        self.h2t.protect_links = True
        self.h2t.wrap_links = False
        
    def get_clipboard_content(self):
        """Get rich text content from clipboard and convert to markdown"""
        types = self.pasteboard.types()
        logger.info(f"Available clipboard types: {types}")
        
        # Try HTML first
        if AppKit.NSPasteboardTypeHTML in types:
            html_data = self.pasteboard.dataForType_(AppKit.NSPasteboardTypeHTML)
            if html_data:
                html_string = html_data.decode('utf-8', errors='ignore')
                logger.info(f"Found HTML content: {html_string[:200]}...")
                return self.convert_html_to_markdown(html_string)
        
        # Try RTF
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
        
        # Fall back to plain text
        if AppKit.NSPasteboardTypeString in types:
            plain_text = self.pasteboard.stringForType_(AppKit.NSPasteboardTypeString)
            logger.info("Only plain text found in clipboard")
            return plain_text
        
        logger.warning("No supported content found in clipboard")
        return None
    
    def convert_html_to_markdown(self, html_string):
        """Convert HTML to clean markdown"""
        try:
            # Ensure HTML is well-formed
            cleaned_html = html_string
            if '<html>' not in cleaned_html.lower():
                cleaned_html = f'<html><body>{cleaned_html}</body></html>'
            
            # Convert to markdown
            markdown = markdownify(cleaned_html, 
                                 heading_style="ATX",
                                 bullets="-",
                                 strip=['style', 'script'])
            
            # Clean up extra blank lines
            lines = markdown.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.rstrip()
                if line:
                    cleaned_lines.append(line)
                elif cleaned_lines and cleaned_lines[-1]:
                    cleaned_lines.append('')
            
            # Remove trailing blank lines
            while cleaned_lines and not cleaned_lines[-1]:
                cleaned_lines.pop()
            
            markdown = '\n'.join(cleaned_lines)
            
            logger.info(f"Converted to markdown: {markdown[:200]}...")
            return markdown
            
        except Exception as e:
            logger.error(f"Error converting HTML to markdown: {e}")
            # Try fallback converter
            try:
                markdown = self.h2t.handle(html_string)
                return markdown.strip()
            except Exception as e2:
                logger.error(f"Fallback conversion also failed: {e2}")
                return html_string
    
    def paste_as_markdown(self):
        """Convert clipboard content to markdown and paste it"""
        try:
            logger.info("Called by Karabiner - converting clipboard to markdown")
            
            # Get and convert content
            markdown_content = self.get_clipboard_content()
            if not markdown_content:
                logger.warning("No content to convert")
                return
            
            # Save original clipboard content
            original_types = self.pasteboard.types()
            original_data = {}
            for type_ in original_types:
                data = self.pasteboard.dataForType_(type_)
                if data:
                    original_data[type_] = data
            
            # Set markdown content to clipboard
            self.pasteboard.clearContents()
            self.pasteboard.setString_forType_(markdown_content, AppKit.NSPasteboardTypeString)
            
            logger.info("Clipboard updated with markdown, triggering paste")
            
            # Use Quartz event posting (doesn't require accessibility permissions)
            # Key codes and flags
            v_key_code = 0x09  # 'v' key
            cmd_flag = 0x100000  # Command key flag (kCGEventFlagMaskCommand)
            
            # Create an event source
            source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateCombinedSessionState)
            
            # Create and post Cmd+V
            key_down = Quartz.CGEventCreateKeyboardEvent(source, v_key_code, True)
            key_up = Quartz.CGEventCreateKeyboardEvent(source, v_key_code, False)
            
            Quartz.CGEventSetFlags(key_down, cmd_flag)
            Quartz.CGEventSetFlags(key_up, cmd_flag)
            
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_down)
            time.sleep(0.01)
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, key_up)
            
            # Small delay to ensure paste completes
            time.sleep(0.1)
            
            # Restore original clipboard
            self.pasteboard.clearContents()
            for type_, data in original_data.items():
                self.pasteboard.setData_forType_(data, type_)
            
            logger.info("Paste completed and original clipboard restored")
            
        except Exception as e:
            logger.error(f"Error in paste_as_markdown: {e}", exc_info=True)

def main():
    """Main entry point when called by Karabiner"""
    converter = ClipboardMarkdownConverter()
    converter.paste_as_markdown()

if __name__ == "__main__":
    main()