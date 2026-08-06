#!/usr/bin/env python3
import os
import re

def roman_to_int(s):
    """Converts a Roman numeral to an integer."""
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
            int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
        else:
            int_val += rom_val[s[i]]
    return int_val

def main():
    mix_dir = 'mix_sonnet'
    sonnets = []

    print(f"Scanning directory: {mix_dir}...")
    
    # 1. Read and parse all sonnet files
    for filename in os.listdir(mix_dir):
        match = re.match(r'sonnet_([A-Z]+)\.txt', filename)
        if match:
            roman = match.group(1)
            num = roman_to_int(roman)
            filepath = os.path.join(mix_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            sonnets.append((num, roman, content))

    # 2. Sort numerically (1, 2, 3...)
    sonnets.sort()

    # 3. Output to the bundled text file
    output_path = os.path.join(mix_dir, 'all_154_sonnets.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        for num, roman, content in sonnets:
            f.write(content + '\n\n\n')

    print(f"Successfully bundled {len(sonnets)} sonnets into {output_path}!")

if __name__ == '__main__':
    main()
