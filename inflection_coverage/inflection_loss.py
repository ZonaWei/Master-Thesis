import json
import os
import re

def load_words(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().lower()
        text = re.sub(r"[^\w\s]", "", text)  # 去除标点
        return text.split()

def analyze_inflection(language, lookup_path, mt_path, ref_path):
    print(f"\n {language.upper()} Inflection Coverage Analysis")

    with open(lookup_path, "r", encoding="utf-8") as f:
        lookup = json.load(f)
    known_forms = set(lookup.keys())

    mt_tokens = load_words(mt_path)
    ref_tokens = load_words(ref_path)
    mt_words = set(mt_tokens)
    ref_words = set(ref_tokens)

    mt_used = mt_words & known_forms
    ref_used = ref_words & known_forms

    print(f"Total tokens in MT: {len(mt_tokens)}")
    print(f"MT matches in known forms: {len(mt_used)} ({len(mt_used)/len(mt_tokens):.2%})")
    print(f"MT inflection loss: {1 - len(mt_used)/len(mt_tokens):.2%}")

    print(f"Total tokens in REF: {len(ref_tokens)}")
    print(f"REF matches in known forms: {len(ref_used)} ({len(ref_used)/len(ref_tokens):.2%})")
    print(f"REF inflection loss: {1 - len(ref_used)/len(ref_tokens):.2%}")

    print(f"Sample MT forms: {list(mt_used)[:10]}")
    print(f"Sample REF forms: {list(ref_used)[:10]}")

langs = ["swahili", "zulu", "amharic", "urdu"]
base_dir = "inflection"

for lang in langs:
    analyze_inflection(
        language=lang,
        lookup_path=os.path.join(base_dir, f"{lang}_inflection_lookup.json"),
        mt_path=os.path.join(base_dir, f"{lang}_large_MT2.txt"),
        ref_path=os.path.join(base_dir, f"{lang}_large_ref.txt")
    )

