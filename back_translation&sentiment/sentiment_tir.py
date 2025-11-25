import openai
from tqdm import tqdm
import time

from openai import OpenAI


client = OpenAI(api_key="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")


with open("tir_zero_shot.txt", "r", encoding="utf-8") as f:
    tir_zero_shot = [line.strip() for line in f if line.strip()]

with open("back_translation_tir.txt", "r", encoding="utf-8") as f:
    back_translation_tir_lines = [line.strip() for line in f if line.strip()]

assert len(tir_zero_shot) == len(back_translation_tir_lines), "Inconsistent number of lines in the document！"

results = []


print(f"Commencing comparison of {len(tir_zero_shot)} sentences...\n")

for idx, (orig, back) in enumerate(tqdm(zip(tir_zero_shot, back_translation_tir_lines), total=len(tir_zero_shot))):
    prompt = (
        "Compare the following two Tigrinya sentences. "
        "Are they semantically equivalent (i.e., do they mean the same thing)? "
        "Answer YES or NO and briefly explain why.\n\n"
        f"Sentence A: {orig}\n"
        f"Sentence B: {back}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful and accurate Tigrinya language expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        reply = response.choices[0].message.content.strip()


        if "YES" in reply.upper():
            match = "YES"
        elif "NO" in reply.upper():
            match = "NO"
        else:
            match = "UNKNOWN"

        results.append({
            "index": idx + 1,
            "tir_zero_shot": orig,
            "back_translation_tir": back,
            "semantic_match": match,
            "explanation": reply
        })

    except Exception as e:
        results.append({
            "index": idx + 1,
            "tir_zero_shot": orig,
            "back_translation_tir": back,
            "semantic_match": "ERROR",
            "explanation": str(e)
        })

    time.sleep(1.1)  


for r in results:
    print(f"\n--- [{r['index']}] ---")
    print(f"Original: {r['tir_zero_shot']}")
    print(f"Backtrn:  {r['back_translation_tir']}")
    print(f"Match:    {r['semantic_match']}")
    print(f"Reason:   {r['explanation']}")

with open("sentiment_result.txt", "w", encoding="utf-8") as f:
     for r in results:
         f.write(f"[{r['index']}]\nOriginal: {r['tir_zero_shot']}\nBack: {r['back_translation_tir']}\nMatch: {r['semantic_match']}\nExplanation: {r['explanation']}\n\n")


