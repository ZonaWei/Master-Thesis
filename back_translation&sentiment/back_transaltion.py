import openai
import pandas as pd
from tqdm import tqdm
import time


openai.api_key = "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"  


input_path = "llm_few_shot_output_amh.txt"
with open(input_path, "r", encoding="utf-8") as f:
    sentences = [line.strip() for line in f if line.strip()]

results = []

print(f"Begin translating {len(sentences)} sentences...")

for idx, sentence in enumerate(tqdm(sentences)):
    prompt = f"Translate the following sentence into Amharic:\n\nEnglish: {sentence}\nAmharic:"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful and accurate translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        translation = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        translation = f"[ERROR] {e}"

    results.append({
        "original_en": sentence,
        "back_amharic": translation
    })

    time.sleep(1.1)  


df = pd.DataFrame(results)
df.to_csv("backtranslated_amh.csv", index=False, encoding="utf-8-sig")

print("✅ Translation completed, results saved backtranslated_amh.csv")
