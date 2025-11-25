
import os
import sys


INPUT_BASE_DIR = "raw2" 


OUTPUT_DIR = "output_tsv2"


LANG_CODES = ["sw", "zu", "am", "ur"]


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("Starting TSV conversion process...\n")


for lang in LANG_CODES:
    print(f"--- Processing language: {lang} ---")
    
    # --- MODIFIED SECTION START ---

    source_filename = f"{lang}.txt"

    target_filename = "en.txt"

    source_file_path = os.path.join(INPUT_BASE_DIR, lang, source_filename)
    target_file_path = os.path.join(INPUT_BASE_DIR, lang, target_filename)
    # --- MODIFIED SECTION END ---
    
    output_tsv_path = os.path.join(OUTPUT_DIR, f"{lang}.tsv")
    

    if not os.path.exists(source_file_path):
        print(f"Error: Source file not found at {source_file_path}. Skipping.")
        continue
    if not os.path.exists(target_file_path):
        print(f"Error: Target file not found at {target_file_path}. Skipping.")
        continue

    line_count = 0
    
    try:

        with open(source_file_path, 'r', encoding='utf-8') as f_source, \
             open(target_file_path, 'r', encoding='utf-8') as f_target, \
             open(output_tsv_path, 'w', encoding='utf-8') as f_output:


            for src_line, tgt_line in zip(f_source, f_target):
                
                src_clean = src_line.strip()
                tgt_clean = tgt_line.strip()

                if src_clean and tgt_clean:
                    f_output.write(f"{src_clean}\t{tgt_clean}\n")
                    line_count += 1

        print(f"Successfully created '{output_tsv_path}' with {line_count} sentence pairs.")

    except Exception as e:
        print(f"An error occurred while processing {lang}: {e}")
    
    print("-" * 25 + "\n")

print("All tasks completed.")
