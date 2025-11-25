import os
import csv
from tqdm import tqdm


INPUT_DIR = "final_data2"


OUTPUT_DIR = "final_data2_reversed"



def reverse_tsv_columns(input_path, output_path):
    """
  Read a TSV file, swap the contents of its two columns, and write the result to a new file.
    """
    try:
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.reader(infile, delimiter='\t')
            writer = csv.writer(outfile, delimiter='\t')
            
            for row in reader:

                if len(row) == 2:
                    writer.writerow([row[1], row[0]])
        return True
    except Exception as e:
        print(f"  -> Error processing file {input_path}: {e}")
        return False

def main():
    """
    Traverse the input directory, locate all .tsv files, and perform the reversal operation.
    """
    print(f"Starting to reverse all .tsv files from '{INPUT_DIR}' into '{OUTPUT_DIR}'...")
    
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found. Please check the path.")
        return


    for dirpath, _, filenames in os.walk(INPUT_DIR):
        for filename in filenames:
            if filename.endswith(".tsv"):
                
                input_file_path = os.path.join(dirpath, filename)

                relative_path = os.path.relpath(dirpath, INPUT_DIR)
                output_dir_path = os.path.join(OUTPUT_DIR, relative_path)
                
                if not os.path.exists(output_dir_path):
                    os.makedirs(output_dir_path)

                output_file_path = os.path.join(output_dir_path, filename)
                
                print(f"\nProcessing: {input_file_path}")
                if reverse_tsv_columns(input_file_path, output_file_path):
                    print(f"  -> Successfully created reversed file: {output_file_path}")

    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()
