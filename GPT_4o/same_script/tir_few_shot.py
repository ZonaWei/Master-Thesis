import openai
import time
import os


client= openai.OpenAI(api_key="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")# 设置环境变量后使用


FEW_SHOT_PREFIX = """
Task: Translate the following Tigrinya sentences to English. Maintain correct tone and fluency. Follow the structure of the examples. Just respond with the translation and nothing else.

Example 1:
Tigrinya: ሱፍ መደበኛ ናይ ስራሕ ንግዲ ክዳውንቲ አዮም፣ ናይ ስራሕ መሳርሕቲ ሕድሕዶም ብናይ በተሰብ ሹም ወይክዓ ብናይ ስራሕ ማኣርግ ይጽውዑ።
English: Suits are standard business attire, and coworkers call each other by their family names or by job titles.

Example 2:
Tigrinya: ኣብ ክንዲ ናይ ውልወሰባት ዓወት ናይ ጉድለ ጻዕሪ ምድናቕ ንስኒት ናይ ስራሕ ቦታ ኣዝዩ ኣገዳሲ እዩ።
English: Workplace harmony is crucial, emphasizing group effort rather than praising individual accomplishments.

Example 3:
Tigrinya: ሰራሕተኛታት ንዝገብርዎም ምንም ዓይነት ውሳነታት ብዙሕ ግዘ ናይ ሓለቓታቶም ፍቓድ ክረኽቡ ኣለዎም፤ ብዘይ ምንም ሕቶ ናይ ሓለቓታቶም መምርሒ ንከኽብሩ ትጽቢት ይግበር።
English: Workers must often get their superiors' approval for any decisions they make, and are expected to obey their superiors' instructions without question.

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

input_file = "tir_zero_shot.txt"
output_file = "tir_few_shot_output.txt"


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