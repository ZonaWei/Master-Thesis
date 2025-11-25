import csv
import os

def convert_unimorph_to_csv(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        writer = csv.writer(outfile)
        writer.writerow(["Lemma", "InflectedForm", "Features"])

        for line in infile:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # skip empty or comment lines

            parts = line.split("\t")
            if len(parts) == 3:
                lemma, form, features = parts
                writer.writerow([lemma, form, features])
            else:
                print(f"Skipping malformed line: {line}")


language_files = {
    "amharic": "amh.txt",
    "swahili": "swc.txt",
    "urdu": "urd.txt",
    "zulu": "zul.txt"
}


for lang, filename in language_files.items():
    input_path = filename
    output_path = f"{lang}_inflection_table.csv"
    if os.path.exists(input_path):
        print(f"Processing {lang}...")
        convert_unimorph_to_csv(input_path, output_path)
    else:
        print(f"File not found: {input_path}")

