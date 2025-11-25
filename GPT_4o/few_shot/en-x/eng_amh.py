import openai
import time
import os


client= openai.OpenAI(api_key="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")


FEW_SHOT_PREFIX = """
Task: Translate the following English sentences to Amharic. Maintain correct tone and fluency. Follow the structure of the examples. Just respond with the translation and nothing else.

Example 1:
English: What language do they want to learn?
Amharic: የትኛውን ቋንቋ መማር ይፈልጋሉ?

Example 2: 
English: I can't live abroad.
English: ውጭ ሀገር መኖር አልችልም።

Example 3:
English: The woman is eating bread.
Amharic: ሴቷ ዳቦ እየበላች ነው።

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

input_file = "eng_few_shot_test.txt"
output_file = "few_shot_eng_amh.txt"


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