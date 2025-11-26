import openai
from tqdm import tqdm
import time

from openai import OpenAI


client = OpenAI(api_key="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")


with open("amh_few_shot_test.txt", "r", encoding="utf-8") as f:
    amh_few_shot_test = [line.strip() for line in f if line.strip()]

with open("back_translation_tir.txt", "r", encoding="utf-8") as f:
    back_translation_lines = [line.strip() for line in f if line.strip()]

assert len(amh_few_shot_test) == len(back_translation_lines), "The number of lines in the document is inconsistent!"

results = []


print(f"Commencing comparison of {len(amh_few_shot_test)} sentences...\n")

for idx, (orig, back) in enumerate(tqdm(zip(amh_few_shot_test, back_translation_lines), total=len(amh_few_shot_test))):
    prompt = (
        "Compare the following two Amharic sentences. "
        "Are they semantically equivalent (i.e., do they mean the same thing)? "
        "Answer YES or NO and briefly explain why.\n\n"
        f"Sentence A: {orig}\n"
        f"Sentence B: {back}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful and accurate Amharic language expert."},
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
            "amh_few_shot_test": orig,
            "back_translation": back,
            "semantic_match": match,
            "explanation": reply
        })

    except Exception as e:
        results.append({
            "index": idx + 1,
            "amh_few_shot_test": orig,
            "back_translation": back,
            "semantic_match": "ERROR",
            "explanation": str(e)
        })

    time.sleep(1.1)  


for r in results:
    print(f"\n--- [{r['index']}] ---")
    print(f"Original: {r['amh_few_shot_test']}")
    print(f"Backtrn:  {r['back_translation']}")
    print(f"Match:    {r['semantic_match']}")
    print(f"Reason:   {r['explanation']}")


with open("semantic_result.txt", "w", encoding="utf-8") as f:
     for r in results:
         f.write(f"[{r['index']}]\nOriginal: {r['amh_few_shot_test']}\nBack: {r['back_translation']}\nMatch: {r['semantic_match']}\nExplanation: {r['explanation']}\n\n")


