#!/usr/bin/env python3
"""
Extract text from the complete 1609 Quarto Sonnets page.
Each sonnet is demarcated with a Roman numeral.
"""

import re
import html


def int_to_roman(num):
    """Convert integer to Roman numeral."""
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num


def process_line(html_line):
    """
    Process a line of HTML to extract text while preserving special characters.
    """
    # Replace typeform spans with their data-setting character
    def replace_typeform(match):
        char = match.group(1)
        return char
    
    html_line = re.sub(r'<span class="typeform" data-setting="([^"]+)">[^<]*</span>', replace_typeform, html_line)
    
    # Replace ligature spans
    def replace_ligature(match):
        precomposed = match.group(1)
        if precomposed:
            return precomposed
        content = match.group(2)
        content = re.sub(r'<span class="typeform" data-setting="([^"]+)">[^<]*</span>', replace_typeform, content)
        content = re.sub(r'<[^>]+>', '', content)
        return content
    
    html_line = re.sub(r'<span class="ligature" data-precomposed="([^"]*)">([^<]*)</span>', replace_ligature, html_line)
    
    # Remove remaining HTML tags but keep <i> and <sup> content
    html_line = re.sub(r'<i>([^<]*)</i>', r'\1', html_line)
    html_line = re.sub(r'<sup>([^<]*)</sup>', r'^\1', html_line)
    html_line = re.sub(r'<[^>]+>', '', html_line)
    
    # Unescape HTML entities
    html_line = html.unescape(html_line)
    
    # Clean up multiple spaces and strip
    html_line = ' '.join(html_line.split())
    
    # Remove line numbers at the start (1, 2, 3...) at start of lines
    html_line = re.sub(r'^\d+\s*', '', html_line)
    
    return html_line


def extract_sonnets_with_roman(html_file, output_file):
    """
    Extract sonnets from HTML and mark each with Roman numeral.
    """
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all line divs with their class and content
    line_pattern = r'<div class="line([^"]*)"[^>]*>(.*?)</div>'
    line_matches = re.findall(line_pattern, content, re.DOTALL)
    
    # Process all lines and filter
    all_lines = []
    in_sonnets = False
    
    for cls, html_line in line_matches:
        line_text = process_line(html_line)
        
        # Skip empty lines
        if not line_text:
            continue
        
        # Check if this is a centered line (marker line)
        is_centered = 'center' in cls
        
        # Check if we're entering the sonnet section
        if not in_sonnets:
            if 'FRom faire' in line_text:
                in_sonnets = True
            else:
                continue
        
        # Skip all centered lines (these are markers)
        if is_centered:
            continue
        
        # Skip lines that look like markers (fallback for any we missed)
        # This catches various formats like "II", "III", "I5I", etc.
        if re.match(r'^[\[\]IDVXLMC\.]+$', line_text):
            continue
        
        # Skip FINIS marker
        if line_text == 'FINIS.':
            break
        
        all_lines.append(line_text)
    
    # Now group into sonnets of 14 lines each
    sonnets = []
    for i in range(0, len(all_lines), 14):
        sonnet_lines = all_lines[i:i+14]
        if len(sonnet_lines) == 14:
            sonnets.append(sonnet_lines)
    
    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, sonnet in enumerate(sonnets, 1):
            f.write(f"::{int_to_roman(i)}::\n")
            f.write('\n'.join(sonnet) + '\n\n')
    
    print(f"Extracted {len(sonnets)} sonnets to {output_file}")


if __name__ == '__main__':
    extract_sonnets_with_roman('sonnets_complete.html', 'sonnets_1609_quarto_roman.txt')
