import google.generativeai as genai
import time
import os


API_KEY = "AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg" 


BATCH_SIZE = 20

try:
    genai.configure(api_key=API_KEY)
except ValueError as e:
    print(f"API Key configuration error: {e}\nPlease ensure “YOUR_API_KEY” has been replaced with your actual key.")
    exit()

SYSTEM_INSTRUCTION = """
You are an expert Zulu-to-English machine translator. Your sole function is to provide a direct, high-quality translation of the given Zulu text.
- You MUST NOT provide any explanations, notes, warnings, or commentary.
- Your response MUST ONLY contain the final English translation.
- If the source text contains apparent errors or ambiguities, provide the most logical and fluent translation without mentioning the error.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)


input_file = "zul_Latn.devtest"
output_file = "zul_output_batched_history.txt" 

if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        completed_lines = len(f.readlines())
else:
    completed_lines = 0

try:
    with open(input_file, "r", encoding="utf-8") as f:
        source_sentences = [line.strip() for line in f.readlines()]
except FileNotFoundError:
    print(f"Error: Input file “{input_file}” not found. Please ensure the file exists in the correct path.")
    exit()



print(f"Commencing translation using dynamic history with batch processing ({BATCH_SIZE} sentences per batch)...")

chat = None 

if completed_lines > 0:
    print(f"The output file has been detected; translation will resume from line {completed_lines + 1}.")

with open(output_file, "a", encoding="utf-8") as out:
    
    for idx, sentence in enumerate(source_sentences[completed_lines:], start=completed_lines + 1):
        

        current_run_index = idx - 1 - completed_lines
        if current_run_index % BATCH_SIZE == 0:
            print(f"\n--- Start a new batch (sentences {idx} to {idx + BATCH_SIZE -}) ---")
            
            chat = model.start_chat(history=[])
        
        translation = ""
        print(f"Translating sentence {idx}/{len(source_sentences)} (Batch item {current_run_index % BATCH_SIZE + 1}/{BATCH_SIZE})...")
        
       
        for attempt in range(3):
            try:
                if chat is None: 
                    raise ValueError("Chat session is not initialized.")
                
                response = chat.send_message(sentence)
                translation = response.text.strip()
                break 
            except Exception as e:
                print(f"  Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    
                    retry_delay = 5 
                    if "retry_delay" in str(e):
                        try:
                            
                            delay_str = str(e).split('retry_delay {\n  seconds: ')[1].split('\n}')[0]
                            retry_delay = int(delay_str) + 1 
                        except (IndexError, ValueError):
                            pass
                    print(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("  The maximum retry count has been reached; skip this line.")
                    translation = "TRANSLATION_FAILED"

        out.write(translation + "\n")
        out.flush()
        
        time.sleep(1) 

print("Translation complete!")