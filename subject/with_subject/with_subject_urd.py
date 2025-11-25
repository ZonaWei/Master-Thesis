import openai
import time
import os


client= openai.OpenAI(api_key="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")# 设置环境变量后使用


FEW_SHOT_PREFIX = """
Task: Translate the following Urdu sentences to English. Respond with **only** the English translation. Do not add explanations or extra responses.

Example 1:
Urdu: تمھارے پاس اتنا تجربہ نہیں ہے۔
English: You don't have enough experience.

Example 2:
Urdu: آپ نے پھول کہاں سے خریدے؟
English: Where did you buy flowers?

Example 3:
Urdu: پہلے کھائیں گے، پھر جائیں گے۔
English: First we'll eat, and then we'll go.

Now translate the following:
"""

def few_shot_translate(text):
    prompt = FEW_SHOT_PREFIX + "\n" + text
    for attempt in range(3):  
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return ""

input_file = "with_subject_urd.txt"
output_file = "with_subject_urd_output.txt"


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
        translation = few_shot_translate(sentence)
        out.write(translation + "\n")
        time.sleep(0.2) 