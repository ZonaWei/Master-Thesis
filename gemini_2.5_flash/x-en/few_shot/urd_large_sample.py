import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

FEW_SHOT_PREFIX = """
Task: Translate the following Urdu sentences to English. Maintain correct tone and fluency. Just respond with the translation and nothing else.

Example 1:
Urdu: خانہ جنگی کے دوران یہ ایک ظہور شے ہے جوکہ ہمارے ملک میں اور باقی دنیا میں اپنی گرفت قائم کر رہی ہے۔
English: This is a phenomenon that is taking place in our country and the rest of the world.

Example 2:
Urdu: وہاں اپنے حالات کے باوجود ،جبکہ صحافیوں کو ان سے سوالات پوچھنے کی اجازت ہے، ان کو کبھی بھی ایسی صورتحال نہیں دی گئی جو میں وہ لازماً جواب دیں۔
English: While reporters are allowed to ask her questions, she’s never placed in a situation where she has to answer.

Example 3:
Urdu: یہ ان گنت خواتین کی کہانیگزشتہ ۴ ہفتوں میں ، میں نے صرف ۲ صحافی دیکھے ہیں جن کو مس پیلن تک رسائی نصیب ہوئی۔
English: In the past four weeks, I have only seen two reporters who have been blessed with access to Ms. Palin.

Example 4:
Urdu: اور یہاں تیسری وجہ آتی ہے: یونیسکو نے کہا ہے کہ 2025 میں چینل ۱۹ کے ویڈیو وولنٹیرز کی دوسری ویڈیوز بصیرت اور جوش پیدا کرنے والی ہیں۔ عورتیں بھی کھیل سکتی ہیں کے موضوع پر عوامی صحافیوں نے اپنی بستیوں سے پوچھا کہ بچے کھیلنے کیلئے کیا کرتے ہیں۔ے ۔
English: Other videos by the VideoVolunteers of Channel 19 are insightful and inspiring: on Women Can Play Too!, the community journalists ask around their slum about what kids do to play.

Example 5:
Urdu: میرا سوال تھا کہ: کیا والدین کی ترجواب: بنیادی طور پر خیال ایک ایسا ویب ماحول فراہم کرناہے۔
English: Q: Pavel, could you introduce Wikidioms in a couple of sentences?

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

input_file = "urd_Arab.devtest"
output_file = "urd_large_output4.txt"


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