import pandas as pd
import os


INPUT_DIR = "output_tsv"
OUTPUT_DIR = "final_data"
LANG_CODES = ["sw", "zu", "am", "ur"]
MULTI_LEVELS = [1000, 5000, 25000, 50000, 100000] 
VALIDATION_SIZE_LARGE = 1000
VALIDATION_SIZE_SMALL = 300
RANDOM_STATE = 42


if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("Starting data cleaning and splitting process...\n")

for lang in LANG_CODES:
    print(f"--- Processing language: {lang} ---")
    
    input_file = os.path.join(INPUT_DIR, f"{lang}.tsv")
    lang_output_dir = os.path.join(OUTPUT_DIR, lang)
    
    if not os.path.exists(lang_output_dir):
        os.makedirs(lang_output_dir)
        
    if not os.path.exists(input_file):
        print(f"Warning: Input file not found at {input_file}. Skipping.")
        continue


    source_lines = []
    target_lines = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):

            parts = line.strip().split('\t', 1) 

            if len(parts) == 2:
                source, target = parts
                if source and target:
                    source_lines.append(source)
                    target_lines.append(target)
            else:
                print(f"  - Warning: Skipping malformed line {line_num} in {input_file}")

    df = pd.DataFrame({'source': source_lines, 'target': target_lines})

    initial_count = len(df)
    print(f"Successfully read and parsed pairs: {initial_count}")
    
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    
    df_shuffled = df.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    clean_count = len(df_shuffled)
    print(f"Cleaned and shuffled pair count: {clean_count}")

    if clean_count > (max(MULTI_LEVELS) + VALIDATION_SIZE_LARGE):
        print("Applying multi-level splitting strategy...")
        
        validation_df = df_shuffled.head(VALIDATION_SIZE_LARGE)
        train_pool_df = df_shuffled.iloc[VALIDATION_SIZE_LARGE:]
        
        validation_df.to_csv(os.path.join(lang_output_dir, "validation.tsv"), sep='\t', header=False, index=False)
        print(f"  - Created validation.tsv with {len(validation_df)} pairs.")
        
        for level in MULTI_LEVELS:
            if len(train_pool_df) >= level:
                subset_df = train_pool_df.head(level)
                filename = f"train_{level//1000}k.tsv"
                subset_df.to_csv(os.path.join(lang_output_dir, filename), sep='\t', header=False, index=False)
                print(f"  - Created {filename} with {len(subset_df)} pairs.")
        
        full_train_filename = f"train_full.tsv"
        train_pool_df.to_csv(os.path.join(lang_output_dir, full_train_filename), sep='\t', header=False, index=False)
        print(f"  - Created {full_train_filename} with {len(train_pool_df)} pairs.")

    else:
        print("Applying single-point (extremely low-resource) splitting strategy...")
        
        if clean_count > VALIDATION_SIZE_SMALL:
            train_size = clean_count - VALIDATION_SIZE_SMALL

            validation_df = df_shuffled.head(VALIDATION_SIZE_SMALL)
            train_df = df_shuffled.iloc[VALIDATION_SIZE_SMALL:]
            
            validation_df.to_csv(os.path.join(lang_output_dir, "validation.tsv"), sep='\t', header=False, index=False)
            train_df.to_csv(os.path.join(lang_output_dir, "train.tsv"), sep='\t', header=False, index=False)
            print(f"  - Created validation.tsv with {len(validation_df)} pairs.")
            print(f"  - Created train.tsv with {len(train_df)} pairs.")
        else:
            print("  - Not enough data to create a validation set. Only a single train file will be created.")
            df_shuffled.to_csv(os.path.join(lang_output_dir, "train.tsv"), sep='\t', header=False, index=False)

    print("-" * 25 + "\n")

print("All tasks completed.")
