import sys
import re

KANJI_RANGE = re.compile(r'[^\u4e00-\u9fff]')
HIRAGANA_RANGE = re.compile(r'[^\u3040-\u309f]')
KATAKANA_RANGE = re.compile(r'[^\u30a0-\u30ff]')

def leave_range(CUSTOM_RANGE, string_to_clean):
    cleaned_string = re.sub(CUSTOM_RANGE, '', string_to_clean)
    return ''.join(set(cleaned_string))

def main():
    here = sys.stdin.read()
    print(leave_range(KANJI_RANGE, here))
    print(leave_range(KATAKANA_RANGE, here))
    print(leave_range(HIRAGANA_RANGE, here))

    return 0

if __name__ == "__main__":
    main()
