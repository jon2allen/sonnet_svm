import re
import os

def parse_sonnets(filepath):
    """
    Parses a large text file containing sonnets separated by Roman numerals and blank lines.

    Args:
        filepath (str): The path to the text file.

    Yields:
        tuple: A tuple containing the Roman numeral identifier (e.g., "I", "II") and the text of the sonnet.
    """
    with open(filepath, 'r', encoding='utf-8') as f:  # Specify encoding for broader compatibility
        text = f.read()

    # Regular expression to find Roman numeral followed by text until a blank line
    pattern = re.compile(r"([IVXLCDM]+)\s*\n(.*?)(?=\n[IVXLCDM]+\s*\n|\Z)", re.DOTALL)

    matches = pattern.finditer(text)

    for match in matches:
        roman_numeral = match.group(1)
        sonnet_text = match.group(2).strip()  # Remove leading/trailing whitespace
        yield roman_numeral, sonnet_text

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Parse the sonnets from the file
    sonnet_generator = parse_sonnets("sonnets.txt")

    # Iterate through the sonnets and print them
    try:
        while True:
            roman_numeral, sonnet_text = next(sonnet_generator)
            print(f"Sonnet {roman_numeral}:\n{sonnet_text}\n---")

            # Save sonnet to file 
            sonnet_file = "sonnet_" + roman_numeral + ".txt"
            with open(os.path.join("data", sonnet_file), 'w', encoding='utf-8') as f:
                    f.write(f"Sonnet {roman_numeral}:\n{sonnet_text}")

    except StopIteration:
        print("No more sonnets.")
