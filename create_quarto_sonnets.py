#!/usr/bin/env python3
"""
Script to create orig_sonnet_quarto directory from sonnets_1609_quarto_roman.txt

Input: sonnets_1609_quarto_roman.txt (contains all 154 sonnets with ::I::, ::II::, etc. markers)
Output: orig_sonnet_quarto/ directory with individual files sonnet_I.txt, sonnet_II.txt, etc.

Each output file contains the original quarto text exactly as published, with:
- No header line (the ::I:: marker is removed)
- The 14 lines of the sonnet
- Original Elizabethan spelling preserved
- Long ſ character and other original typography preserved
"""

import os
import re

# Configuration
SOURCE_FILE = 'sonnets_1609_quarto_roman.txt'
OUTPUT_DIR = 'orig_sonnet_quarto'


def main():
    # Read the source file
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Split content by sonnet markers
    # Pattern: ::ROMAN_NUMERAL:: followed by sonnet text (14 lines) and blank lines
    sonnet_pattern = r'::([IVXLCDM]+)::\n([\s\S]*?)(?=\n::|$)'
    
    sonnets = re.findall(sonnet_pattern, content)
    
    print(f"Found {len(sonnets)} sonnets to process")
    
    # Process each sonnet
    for roman_num, sonnet_text in sonnets:
        # Clean up the text: remove leading/trailing whitespace
        sonnet_text = sonnet_text.strip()
        
        # Remove any trailing blank lines
        sonnet_text = sonnet_text.rstrip('\n')
        
        # Create filename
        filename = f"sonnet_{roman_num}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Write the sonnet text to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(sonnet_text + '\n')
        
        print(f"Created: {filepath}")
    
    print(f"\nDone! Created {len(sonnets)} sonnet files in {OUTPUT_DIR}/")


if __name__ == '__main__':
    main()
