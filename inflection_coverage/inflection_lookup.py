import pandas as pd
import json
import os

language_files = {
    "amharic": "amharic_inflection_table.csv",
    "swahili": "swahili_inflection_table.csv",
    "urdu": "urdu_inflection_table.csv",
    "zulu": "zulu_inflection_table.csv"
}

for lang, path in language_files.items():
    if not os.path.exists(path):
        print(f"⚠️ File not found for {lang}: {path}")
        continue

    df = pd.read_csv(path)
    lookup = {}

    for _, row in df.iterrows():
        form = row["InflectedForm"]
        lookup[form] = {
            "lemma": row["Lemma"],
            "features": row["Features"]
        }

    output_path = f"{lang}_inflection_lookup.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(lookup, f, ensure_ascii=False, indent=2)

    print(f"✅ {lang.capitalize()} lookup saved to {output_path}")

