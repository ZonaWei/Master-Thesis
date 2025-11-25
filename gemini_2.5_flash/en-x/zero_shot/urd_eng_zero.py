import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

def zero_shot_translate(text, src_lang="English", tgt_lang="Urdu"):
    prompt = f"Translate the following from {src_lang} to {tgt_lang}. Just respond with the translation and nothing else:\n{text}"
    for attempt in range(3):  
        try:
            response = model.generate_content(prompt)
            result = response.text.strip()

            if result.lower().startswith("english:"):
                result = result[len("english:"):].strip()

            return result.replace("\n", " ").strip()

        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return "[TRANSLATION FAILED]"
 


input_file = "eng_Latn.devtest"
output_file = "urd_eng_zero.txt"


if os.path.exists(output_file):
    with open(output_file, "r", encoding="utf-8") as f:
        completed_lines = len(f.readlines())
else:
    completed_lines = 0

with open(input_file, "r", encoding="utf-8") as f:
    source_sentences = [line.strip() for line in f.readlines()]

with open(output_file, "a", encoding="utf-8") as out:
    for idx, sentence in enumerate(source_sentences[completed_lines:], start=completed_lines + 1):
        print(f"Translating sentence {idx}/{len(source_sentences)}...")
        translation = zero_shot_translate(sentence)
        out.write(translation + "\n")
        time.sleep(0.2)