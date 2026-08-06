import sys

# Lists derived from mix_sonnet/manifest.txt
REAL_SONNETS = {
    "CIX", "XCIV", "X", "XXXIII", "LXII", "CIV", "CXLIV", "XC", "CXXXII", "LXX",
    "XCVII", "IX", "CXXI", "XLII", "LXXXVI", "CXXVIII", "CXIII", "CXLVIII", "XLVII",
    "CVI", "LXIV", "VI", "XXX", "LXXVIII", "CVII", "LXXXII", "LV", "CXXIV", "LXXXV",
    "XCIX", "XCI", "C", "LXXII", "XCIII", "CXXXI", "LXVIII", "CXVI", "CXXXIV", "LVI",
    "CXL", "LXXIV", "CXXXIX", "LXIII", "XLIII", "CXXXVI", "LXXVII", "CXV", "LXXI",
    "XLV", "LXVII", "LXIX", "I", "VIII", "CXXXVIII", "LXXIII", "LX", "CX", "XCVI",
    "LXXXIII", "CXLV", "CXII", "CXXII", "XLIX", "LXXXI", "XXVI", "LIV", "XIV", "LXV",
    "IV", "LII", "XCVIII", "LXVI", "LXXXVIII", "CVIII", "XXXV", "CXI", "L", "XCV",
    "V", "CXLIII", "XXII", "CLI", "CXX", "LI", "XXXVIII", "XI", "CXXIX", "CXLII",
    "LIX", "XV", "LXXX", "LXXXIV", "CXIV", "LXXIX", "XXXII", "LVII", "CI", "XLIV",
    "XXXVII", "XIII", "CXVIII", "XXVIII", "III", "CXXXIII", "LVIII", "CXVII", "CXXIII",
    "XXI", "CL", "CXLIX", "CXLVII", "XXIII", "XVII", "CXXVII", "CXXX", "LXXVI",
    "CLII", "XXXVI", "XXIV", "CLIV", "XXV", "CXXXVII", "CXLVI", "XL"
}

FAKE_SONNETS = {
    "XII", "XXXIV", "XX", "LXXV", "XXXI", "XCII", "XLVI", "CXXV", "CV", "CIII",
    "LXXXVII", "LIII", "LXXXIX", "VII", "XLVIII", "CXXVI", "XXIX", "CLIII", "II",
    "XVI", "XXVII", "CXIX", "LXI", "CII", "XVIII", "XIX", "CXXXV", "XLI", "XXXIX",
    "CXLI"
}

def arabic_to_roman(n):
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
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

def classify_sonnet(input_val):
    # Handle filename: sonnet_CIII.txt -> CIII
    if input_val.startswith("sonnet_") and input_val.endswith(".txt"):
        roman = input_val[7:-4]
    # Handle arabic numeral: "103" -> CIII
    elif input_val.isdigit():
        roman = arabic_to_roman(int(input_val))
    # Handle roman numeral directly
    else:
        roman = input_val.upper()

    if roman in REAL_SONNETS:
        return "Real"
    elif roman in FAKE_SONNETS:
        return "Fake"
    else:
        return "Unknown"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_mix.py <filename|roman|arabic>")
        sys.exit(1)
    
    result = classify_sonnet(sys.argv[1])
    print(result)
