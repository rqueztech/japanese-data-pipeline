from pathlib import Path
import os
import sys
import re
import csv
import sqlite3
from collections import defaultdict
from janome.tokenizer import Tokenizer

def leave_range(CUSTOM_RANGE, string_to_clean):
    return re.sub(CUSTOM_RANGE, '', string_to_clean)

def read_in_kanji_defined_results(kanji_defined_results):
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
    [print(x, kanji_map[x]) for x in kanji if x in kanji_map]

def prune_all_unique_left_kanji(left_kanji, kanji_map):
    seen = set()
    for x in left_kanji:
        if x in seen:
            continue
        seen.add(x)
    return list(seen)

def check_for_sizes(kanji_defined_results, kanji_map):
    if len(kanji_defined_results) != 2134 or len(kanji_map) != 2134:
        print(f"Data set is too small: {len(kanji_defined_results)}")
        return 1
    
def tokenize_all_japanese(t, left_japanese):
    return [token.surface for token in t.tokenize(left_japanese)]

def define_all_kanji(cleaned_word, kanji_map):
    kanji_load = []
    for kanji_candidate in cleaned_word:
        if kanji_candidate in kanji_map:
            kanji_load.append([kanji_candidate, kanji_map[kanji_candidate]])

    return kanji_load

def display_full_kanji_load(kanji_load, onyomi_doubles_set, onyomi_prefix_set, onyomi_suffix_set, onyomi_repeat_set):
    for current in kanji_load:
        kanji = current[0]
        definition = current[1]
        special_symbols = []

        if kanji in onyomi_doubles_set:
            special_symbols.append("*")
        if kanji in onyomi_prefix_set:
            special_symbols.append("p")
        if kanji in onyomi_suffix_set:
            special_symbols.append("s")
        if kanji in onyomi_repeat_set:
            special_symbols.append("r")

        if not special_symbols:
            print(kanji, " - ", definition)

        print(special_symbols, kanji, " - ", definition)

def word_is_kanji(KANJI_RANGE, word):
    return re.search(KANJI_RANGE, word)

def display_word_payload_kanjis(word, kanji_load, payload, onyomi_doubles_set, kunyomi_roots_to_readings_map, kanji_map, onyomi_prefix_set, onyomi_suffix_set, KANJI_RANGE, onyomi_repeat_set):
    if len(word) == 1 and word_is_kanji(KANJI_RANGE, word):
        print(word, " :: ", kunyomi_roots_to_readings_map[word], " -> ", kanji_map[word])
    else:
        print(word, " :: ", payload)
        if kanji_load and len(kanji_load) > 0:
            display_full_kanji_load(kanji_load, onyomi_doubles_set, onyomi_prefix_set, onyomi_suffix_set, onyomi_repeat_set)

def process_all_tokenized_kanji(kanji_definition_map, tokenized_kanji, kanji_map, onyomi_doubles_set, KANJI_RANGE, kunyomi_roots_to_readings_map, onyomi_prefix_set, onyomi_suffix_set, onyomi_repeat_set):
    full_string = []
    print(len(tokenized_kanji))
    for word in tokenized_kanji:
        separation_lines = "---------------------"
        print(separation_lines)
        full_string.append(separation_lines)
        full_string.append("\n")

        payload = kanji_definition_map[word]
        cleaned_word = leave_range(KANJI_RANGE, word)
        kanji_load = define_all_kanji(cleaned_word, kanji_map)
        display_word_payload_kanjis(word, kanji_load, payload, onyomi_doubles_set, kunyomi_roots_to_readings_map, kanji_map, onyomi_prefix_set, onyomi_suffix_set, KANJI_RANGE, onyomi_repeat_set)
        full_string.append(kanji_load)
    return full_string

def populate_kanji_definition_map(matched_rows):
    kanji_definition_map = defaultdict(list)
    for current in matched_rows:
        kanji = current[0]
        hiragana_and_definition = [current[1], current[2]]
        kanji_definition_map[kanji] = hiragana_and_definition
    return kanji_definition_map

def create_word_set(CURRENT_QUERY, cur):
    cur.execute(CURRENT_QUERY)
    created_result = cur.fetchall()
    return {results[0] for results in created_result}

def create_kunyomi_root_map(cur):
    kunyomi_roots_to_readings_map = defaultdict(list)
    KUNYOMI_ROOT_QUERY = "SELECT kanji, hiragana, definition FROM kunyomi_rootclean_readings"
    cur.execute(KUNYOMI_ROOT_QUERY)
    kunyomi_roots = cur.fetchall()
    for current in kunyomi_roots:
        if len(current) == 3:
            kanji = current[0]
            reading = current[1]
            kunyomi_roots_to_readings_map[kanji].append(reading)
    return kunyomi_roots_to_readings_map
    

def main():
    KANJI_RANGE = re.compile(r'[^\u4e00-\u9fff]')
    HIRAGANA_RANGE = re.compile(r'[^\u3040-\u309f]')
    KATAKANA_RANGE = re.compile(r'[^\u30a0-\u30ff]')
    JAPANESE_RANGE = re.compile(r'[^\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]')

    db_path = os.environ.get("JAPANESE_DB")
    t = Tokenizer()

    print(db_path)
    
    JAPANESE_DB = db_path

    if not Path.exists:
        print("path not found...")
        return 1

    con = sqlite3.connect(JAPANESE_DB)
    cur = con.cursor()

    kunyomi_roots_to_readings_map = create_kunyomi_root_map(cur)
    if not kunyomi_roots_to_readings_map:
        print("kunyomi_roots_to_readings_map failed")

    ONYOMI_DOUBLES_QUERY = "SELECT * FROM onyomidoubles;"
    onyomi_doubles_set = create_word_set(ONYOMI_DOUBLES_QUERY, cur)

    ONYOMI_SUFFIX_QUERY = "SELECT * FROM suffix;"
    onyomi_suffix_set = create_word_set(ONYOMI_SUFFIX_QUERY, cur)

    ONYOMI_PREFIX_QUERY = "SELECT * FROM prefix;"
    onyomi_prefix_set = create_word_set(ONYOMI_PREFIX_QUERY, cur)

    REPEAT_QUERY = "SELECT substr(kanji, 1, 1) FROM onyomi_repeat_footprint;"
    onyomi_repeat_set = create_word_set(REPEAT_QUERY, cur)

    KANJI_QUERY = "SELECT kanji, definition FROM kanji_main;"
    cur.execute(KANJI_QUERY)
    kanji_defined_results = cur.fetchall()

    kanji_map = read_in_kanji_defined_results(kanji_defined_results)
    check_for_sizes(kanji_defined_results, kanji_map)

    here = sys.stdin.read()

    left_japanese = leave_range(JAPANESE_RANGE, here)
    left_kanji = leave_range(KANJI_RANGE, here)
    pruned_kanji = prune_all_unique_left_kanji(left_kanji, kanji_map)

    # display_all_kanji(pruned_kanji, kanji_map)

    tokenized_kanji = tokenize_all_japanese(t, left_japanese)
    print(tokenized_kanji)

    counter = 1

    tokenized_kanji_set = {word.strip() for word in tokenized_kanji if len(word.strip())}
    for current in tokenized_kanji:
        counter += 1
    tokenized_definition_map = defaultdict(str)

    words_list = list(tokenized_kanji_set)
    placeholders = ", ".join(["?"] * len(words_list))

    VOCABULARY_QUERY = f"""
    SELECT kanji, hiragana, definition
    FROM vocabulary_fullstack
    WHERE kanji IN ({placeholders});
    """

    cur.execute(VOCABULARY_QUERY, words_list)
    matched_rows = cur.fetchall()

    con.close()

    kanji_definition_map = populate_kanji_definition_map(matched_rows)
    full_string = process_all_tokenized_kanji(kanji_definition_map, tokenized_kanji, kanji_map, onyomi_doubles_set, KANJI_RANGE, kunyomi_roots_to_readings_map, onyomi_prefix_set, onyomi_suffix_set, onyomi_repeat_set)

    return 0

if __name__ == "__main__":
    main()
