import openai
import time
import os


client = openai.OpenAI(api_key="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")  # 或使用 os.environ["OPENAI_API_KEY"]


few_shot_examples = [
    ("What's Tom doing here anyway?", "እብለ ገብአ ቶም እት እንሰር ሚ ወዴ ሀለ?"),
    ("No one has been able to reach the top of the mountain.", "ዋላ ሓደ ናብቲ ዝበረኸ ክፋል ናይቲ ጎቦ ኣይበጸሐን።"),
    ("The job was completed in one day.", "እቲ ስራሕ ብሓድ መዓልቲ ተፈጺሙ።")
]


def build_few_shot_prompt(input_text, src_lang="English", tgt_lang="Tigrinya"):
    header = f"Translate the following sentences from {src_lang} to {tgt_lang}.\nAvoid repetition. Keep translations accurate and natural.\n\n"
    examples_str = ""
    for src, tgt in few_shot_examples:
        examples_str += f"{src_lang}: {src}\n{tgt_lang}: {tgt}\n\n"
    task_line = f"{src_lang}: {input_text}\n{tgt_lang}:"
    return header + examples_str + task_line


def few_shot_translate(text, src_lang="English", tgt_lang="Tigrinya"):
    prompt = build_few_shot_prompt(text, src_lang, tgt_lang)
    for attempt in range(3):  
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,  
                stop=["\n"]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return ""

input_file = "tir_few_shot_output.txt"
output_file = "back_translation_tir_2.txt"


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
