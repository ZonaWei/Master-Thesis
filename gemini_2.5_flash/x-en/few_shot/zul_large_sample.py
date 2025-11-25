import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

FEW_SHOT_PREFIX = """
Task: Translate the following Zulu sentences to English. Maintain correct tone and fluency. Just respond with the translation and nothing else.

Example 1:
Zulu: Ngaphezu kwalokho, ngithatha leli thuba ukukhumbula ukuthi uJuni 20 uzoba ...
English: In addition, I take this opportunity to remember that June 20 will be the ...

Example 2:
Zulu: Wayalela isizwe sakhe ukuba sibambelele siqinise eNcwadini ka- Allah (i-Qur'aan); washo nokuthi uma bengakugcina lokho abasoze balahlekiswa.
English: He commanded his community to hold fast to the Book of Allah; as long as they did this they would not be misguided, he said.

Example 3:
Zulu: Baye bancishwa nethuba lokukhulekela kanye namakholwa abakanye nawo.
English: They have also been denied the opportunity to worship with their fellow believers.

Example 4:
Zulu: Kuyacaca ukuthi ubufakazi obuvela eBhayibhelini bubonisa ukuthi inkolo ehleliwe iwuhlobo lokukhulekela olwamukelekayo kuNkulunkulu.
English: Clearly, evidence from the Bible points to an organized form of worship as the kind that is acceptable to God.


Example 5:
Zulu: Impikiswano: amanzi, ukuthi unganikeza kanjani amanzi okuphuza, okungenani isibalo esikhulu kunazo zonke e-Afrika?
English: Debate: water, how to give access to drinking water, at least to the greatest number in Africa?


Now translate the following:
"""

def few_shot_translate(text):
    prompt = FEW_SHOT_PREFIX + "\n" + text
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)
    return ""

input_file = "zul_Latn.devtest"
output_file = "zul_large_output3.txt"


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