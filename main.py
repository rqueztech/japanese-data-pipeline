from pathlib import Path
import sys
import re
import csv
import sqlite3
from collections import defaultdict

KANJI_RANGE = re.compile(r'[^\u4e00-\u9fff]')
HIRAGANA_RANGE = re.compile(r'[^\u3040-\u309f]')
KATAKANA_RANGE = re.compile(r'[^\u30a0-\u30ff]')

def leave_range(CUSTOM_RANGE, string_to_clean):
    
    return re.sub(CUSTOM_RANGE, '', string_to_clean)

def read_in_csv(kanji_defined_results):
    kanji_mapped = defaultdict(str)
    for current in kanji_defined_results:
        kanji = current[0]
        definition = current[1]
        kanji_mapped[kanji] = definition

    return kanji_mapped

def print_entire_map(kanji_map):
    counter = 1
    for kanji in kanji_map:
        print(f"{kanji} {counter}")
        counter += 1

def main():
    script_dir = Path(__file__).resolve().parent
    JAPANESE_DB = script_dir / "../japanese-database/natvocab.db"

    if not Path.exists:
        print("path not found...")
        return 1

    con = sqlite3.connect(JAPANESE_DB)
    cur = con.cursor()
    KANJI_QUERY = "SELECT kanji, definition FROM kanji_main;"
    cur.execute(KANJI_QUERY)
    kanji_defined_results = cur.fetchall()
    if len(kanji_defined_results) != 2134:
        print(f"Data set is too small: {len(kanji_defined_results)}")
        return 1
    else:
        print(f"Length is right {kanji_defined_results}")
    kanji_map = read_in_csv(kanji_defined_results)
    if len(kanji_map) != 2134:
        print(f"Map too small {len(kanji_map)}")
    here = sys.stdin.read()
    left_kanji = leave_range(KANJI_RANGE, here)
    for x in left_kanji:
        if x in kanji_map:
            print(x, kanji_map[x])
    print(len(left_kanji))

    return 0

if __name__ == "__main__":
    main()
