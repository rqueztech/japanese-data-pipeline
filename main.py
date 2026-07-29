from pathlib import Path
import sys
import re
import csv
import sqlite3
from collections import defaultdict
from janome.tokenizer import Tokenizer

KANJI_RANGE = re.compile(r'[^\u4e00-\u9fff]')
HIRAGANA_RANGE = re.compile(r'[^\u3040-\u309f]')
KATAKANA_RANGE = re.compile(r'[^\u30a0-\u30ff]')
JAPANESE_RANGE = re.compile(r'[^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]')

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

def display_all_kanji(kanji, kanji_map):
    for x in kanji:
        if x in kanji_map:
            print(x, kanji_map[x])
    print(len(kanji))

def prune_all_unique_left_kanji(left_kanji, kanji_map):
    cleaned_array = []
    seen = set()
    for x in left_kanji:
        if x in seen:
            continue
        seen.add(x)
        cleaned_array.append(x)
    return cleaned_array

def check_for_sizes(kanji_defined_results, kanji_map):
    if len(kanji_defined_results) != 2134:
        print(f"Data set is too small: {len(kanji_defined_results)}")
        return 1
    else:
        print(f"Length is right {len(kanji_defined_results)}")
    if len(kanji_map) != 2134:
        print(f"Map too small {len(kanji_map)}")

def tokenize_all_japanese(t, left_japanese):
    return [token.surface for token in t.tokenize(left_japanese)]

def main():
    t = Tokenizer()

    script_dir = Path(__file__).resolve().parent
    JAPANESE_DB = script_dir / "../japanese-database/natvocab.db"

    if not Path.exists:
        print("path not found...")
        return 1

    con = sqlite3.connect(JAPANESE_DB)
    cur = con.cursor()
    KANJI_QUERY = "SELECT kanji, definition FROM kanji_main;"
    cur.execute(KANJI_QUERY)
    VOCABULARY_QUERY = "SELECT kanji, definition FROM vocabulary_fullstack;"
    kanji_defined_results = cur.fetchall()
    kanji_map = read_in_csv(kanji_defined_results)
    check_for_sizes(kanji_defined_results, kanji_map)

    here = sys.stdin.read()
    left_japanese = leave_range(JAPANESE_RANGE, here)
    left_kanji = leave_range(KANJI_RANGE, here)
    pruned_kanji = prune_all_unique_left_kanji(left_kanji, kanji_map)
    display_all_kanji(pruned_kanji, kanji_map)
    tokenized_kanji = tokenize_all_japanese(t, left_japanese)
    print(tokenized_kanji)
    cur.execute(VOCABULARY_QUERY)
    allvocabulary = cur.fetchall()




    return 0

if __name__ == "__main__":
    main()





