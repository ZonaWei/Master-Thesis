import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

FEW_SHOT_PREFIX = """
Task: Translate the following Swahili sentences to English. Maintain correct tone and fluency. Follow the structure of the examples. Just respond with the translation and nothing else

Example 1:
Swahili: Angola na Brazil zina uhusiano maalum baina yao, kutokana na matumizi ya lugha moja na pamoja na historia yao ya kutawaliwa huko nyuma - nchi hizi mbili zilikuwa sehemu ya himaya ya Wareno – na utamaduni wa pamoja unaotoka na historia ya asili moja.
English: Angola and Brazil have a special relationship towards each other, partially because of their common language and their shared colonial past - both countries were part of the Portuguese Empire - and the cultural ties that stem from this shared history.

Example 2:
Swahili: Mtu mweusi aling'olewa kutoka katika ardhi yake na kuuzwa kama bidhaa, utumwani
English: The Negro was uprooted from his land and sold as merchandise, enslaved.

Example 3:
Swahili: Hakuna idadi kamili kuhusiana na watu wangapi wanaabudu Candomblé.
English: There are no definitive numbers on how many people in Brazil follow Candomblé.

Example 4:
Swahili: Hapa chini kuna habari zilizopachikwa katika kurasa za blogu mbili zikionyesha mitazamo tofauti baina ya watu wawili kwa kuibua masuala muhimu kama uhamiaji, ubaguzi wa rangi, ukabila na heshima miongoni mwa watu.
English: Below are two entire blog posts showing different perspectives of one people towards the other, raising issues of immigration, racism, ethnicity and mutual respect.

Example 5:
Swahili: Jumuiya ya Kiarabu ina msimamo gani kuhusu viongozi wa mapinduzi haya?
English: What is the stance of the Arab League from the leaders of this coup?


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

input_file = "swh_Latn.devtest"
output_file = "swh_large_output5.txt"


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