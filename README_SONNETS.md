# Shakespeare's Sonnets - 1609 Quarto Edition

## Overview

This directory contains the complete text of Shakespeare's 154 sonnets as published in the original 1609 Quarto edition, extracted from the **Internet Shakespeare Editions (ISE)**.

## Source

- **Source URL**: https://internetshakespeare.uvic.ca/doc/Son_Q1/complete/index.html
- **Source Name**: Internet Shakespeare Editions (ISE)
- **Institution**: University of Victoria, British Columbia, Canada
- **Founder**: Michael Best (Coordinating Editor, founded 1996)
- **Status**: Non-profit scholarly project providing open-access, peer-reviewed editions
- **Support**: University of Victoria and the Social Sciences and Humanities Research Council of Canada

The ISE is an international scholarly project that publishes high-quality, freely accessible digital editions of Shakespeare's works for students, scholars, actors, and the general public. The editorial process involves an international team of scholars and is overseen by an Editorial Board of distinguished academics.

## Date:  May 21, 2026 - extraction done
## Files

### Primary Output

- **`sonnets_1609_quarto_roman.txt`**: The complete 154 sonnets with Roman numeral demarcation
  - Format: Each sonnet prefixed with `::I::`, `::II::`, `::III::`, ..., `::CLIV::`
  - Each sonnet contains exactly 14 lines
  - Total: 154 sonnets × 14 lines = 2156 lines of verse

### Extraction Script

- **`extract_sonnets_1609.py`**: Python script that extracts and formats the sonnets from the ISE HTML
  - Preserves all original 1609 Quarto spelling
  - Preserves special characters (long s, ligatures)
  - Filters out HTML markup and navigation elements
  - Properly handles sonnet marker lines

### Historical Files (for reference)

- **`sonnets_complete.html`**: The complete HTML source downloaded from ISE
- **`sonnets_1609_quarto_complete.txt`**: Earlier extraction without Roman numeral demarcation
- **`sonnets_1609_quarto_full.txt`**: Another earlier extraction variant

## Textual Features Preserved

The extraction maintains the following features from the original 1609 Quarto:

1. **Original Spelling**: All early modern English spelling is preserved (e.g., "deſire", "increaſe", "beauties")

2. **Long S Character (ſ)**: The original long s character (U+017F) is preserved throughout

3. **Ligatures**: Precomposed ligatures are preserved:
   - ﬅ (st ligature, U+FB05): 750 occurrences
   - ﬂ (fl ligature, U+FB02): 44 occurrences
   - ﬁ (fi ligature, U+FB01): 99 occurrences

4. **Original Punctuation**: All punctuation from the 1609 edition is maintained

## Structure

Each sonnet in `sonnets_1609_quarto_roman.txt` follows this format:

```
::I::
FRom faireﬅ creatures we deſire increaſe,
That thereby beauties Roſe might neuer die,
But as the riper ſhould by time deceaſe,
...
To eate the worlds due, by the graue and thee.

::II::
VVHen fortie Winters ſhall beſeige thy brow,
...
```

## Verification

The extraction has been verified to ensure:
- ✅ Exactly 154 sonnets extracted
- ✅ Each sonnet has exactly 14 lines
- ✅ Roman numerals range from I to CLIV (1 to 154)
- ✅ All special characters (ſ, ﬅ, ﬂ, ﬁ) preserved
- ✅ Original 1609 spelling maintained
- ✅ No HTML markup or navigation content included

## Usage

To re-extract the sonnets from the source HTML:

```bash
python3 extract_sonnets_1609.py
```

This will read `sonnets_complete.html` and generate `sonnets_1609_quarto_roman.txt`.

## Technical Notes

### HTML Structure

The ISE complete page contains:
- Title page and dedication (centered lines, skipped during extraction)
- 154 sonnets with 14 lines each
- 153 centered marker lines between sonnets (indicating sonnet numbers)
- markers use various formats: Arabic numerals ("2", "3"), Roman numerals ("II", "III"), and mixed formats ("I45", "I52", "I5I")
- All sonnet text lines have TLN (Through Line Number) anchors
- Special characters encoded as `<span class="typeform" data-setting="...">` and `<span class="ligature" data-precomposed="...">`

### Extraction Logic

The script:
1. Parses all `<div class="line...">` elements from the HTML
2. Processes HTML to extract text and preserve special characters
3. Skips all centered lines (sonnet markers)
4. Skips lines before "FRom faire" (start of Sonnet 1)
5. Stops at "FINIS." marker (end of sonnets)
6. Groups remaining lines into 14-line sonnets
7. Prefixes each sonnet with Roman numeral in `::N::` format

## References

- [Internet Shakespeare Editions](https://internetshakespeare.uvic.ca/)
- [Wikipedia: Internet Shakespeare Editions](https://en.wikipedia.org/wiki/Internet_Shakespeare_Editions)
- [ISE Corporate Information](https://hcmc.uvic.ca/eol/internetshakespeare.uvic.ca/Foyer/corporate/index.html)

## License

The text of Shakespeare's sonnets is in the public domain. The Internet Shakespeare Editions provides open-access content. This extraction maintains the scholarly work of the ISE project.
