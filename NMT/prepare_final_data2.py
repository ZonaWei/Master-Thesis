import pandas as pd
import os
INPUT_DIR = "output_tsv2" 


OUTPUT_DIR = "final_data2"


LANGUAGE_CONFIG = {
    "sw": {"file": "sw.tsv", "levels": [1000, 5000, 25000, 100000, 500000, 1000000], "val_size": 5000},
    "zu": {"file": "zu.tsv", "levels": [1000, 5000, 25000, 100000, 500000, 1000000], "val_size": 5000},
    "am": {"file": "am.tsv", "levels": [1000, 5000, 25000, 100000, 500000, 1000000], "val_size": 5000},
    "ur": {"file": "ur.tsv", "levels": [1000, 5000, 25000, 100000, 500000, 1000000], "val_size": 5000},
}


def read_large_tsv_safely(filepath):
    """A more robust function for reading TSV files that may contain formatting issues."""
    source_lines = []
    target_lines = []
    print(f"Safely reading and parsing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t', 1)
            if len(parts) == 2:
                source, target = parts
                source_lines.append(source)
                target_lines.append(target)
    
    return pd.DataFrame({'source': source_lines, 'target': target_lines})

def clean_data(df):
    """Perform a series of cleaning operations on the DataFrame."""
    print(f"Initial rows: {len(df)}")
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    df = df[df['source'] != df['target']]
    
    df['source_len'] = df['source'].str.split().str.len()
    df['target_len'] = df['target'].str.split().str.len()
    df = df[(df['source_len'] > 1) & (df['source_len'] < 250)]
    df = df[(df['target_len'] > 1) & (df['target_len'] < 250)]
    df = df.drop(columns=['source_len', 'target_len'])
    
    print(f"Rows after cleaning: {len(df)}")
    return df

print("Starting data preparation process (will skip existing files)...\n")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

for lang_code, config in LANGUAGE_CONFIG.items():
    print(f"--- Processing language: {lang_code} ---")
    
    input_file = os.path.join(INPUT_DIR, config["file"])
    lang_output_dir = os.path.join(OUTPUT_DIR, lang_code)

    if not os.path.exists(lang_output_dir):
        os.makedirs(lang_output_dir)

    if not os.path.exists(input_file):
        print(f"Warning: Input file not found for {lang_code} at {input_file}. Skipping.")
        continue

    df = read_large_tsv_safely(input_file)
    df_cleaned = clean_data(df)
    df_shuffled = df_cleaned.sample(frac=1, random_state=42).reset_index(drop=True)

    val_size = config["val_size"]
    validation_file_path = os.path.join(lang_output_dir, "validation.tsv")
    
    if os.path.exists(validation_file_path):
        print(f"Validation set for {lang_code} already exists. Skipping.")
    else:
        if len(df_shuffled) < val_size:
            print(f"Warning: Not enough data for {lang_code} to create a validation set. Skipping.")
            continue
        validation_df = df_shuffled.head(val_size)
        validation_df.to_csv(validation_file_path, sep='\t', header=False, index=False)
        print(f"Created validation set for {lang_code} with {len(validation_df)} pairs.")

    train_pool_df = df_shuffled.iloc[val_size:]
    
    print(f"Checking for tiered training sets for {lang_code}...")
    for level in config["levels"]:
        level_name = f"{level // 1000}k" if level < 1000000 else f"{level // 1000000}M"
        output_filename = os.path.join(lang_output_dir, f"train_{level_name}.tsv")
        
        if os.path.exists(output_filename):
            print(f"  -> Skipping {output_filename}, already exists.")
            continue
            
        if len(train_pool_df) >= level:
            subset_df = train_pool_df.head(level)
            subset_df.to_csv(output_filename, sep='\t', header=False, index=False)
            print(f"  -> Created {output_filename} with {len(subset_df)} pairs.")
        else:
            print(f"  -> Not enough data to create training set of size {level}. Stopping for {lang_code}.")
            break
    
    print("-" * 30 + "\n")

print("All data preparation tasks completed.")

