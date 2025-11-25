import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

FEW_SHOT_PREFIX = """
Task: Translate the following English sentences to Urdu. Maintain correct tone and fluency. Just respond with the translation and nothing else.

Example 1:
English: In large parts of the world, higher education is unattainable for an average citizen.
Urdu: وہ بینچدنیا کے بڑے حصوں میں ، اعلی تعلیم حاصل کرنا ناممکن ہے ایک عام شہری کے لیے ۔

Example 2:
English: The students were not allowed to leave the campus, or communicate with their parents.
Urdu: کیا وہ کالا اور سٹوڈنٹس کو کیمپس سے باہر جانے کی اجازت نہ تھی ۔ اور نہ ہی والدین سے بات کرنے کی ۔

Example 3:
English: Their days were meticulously mapped out, and any free time they had was devoted to honoring their Great Leader.
Urdu: اس نے کہا ہر دن مکمل طور پر پلان کیا جاتا تھا ، اور اگر اسمیں کوئی فالتو وقت بچ جاتا تو وہ عظیم لیڈر کو خراج تحسین کے لیے استعمال کیا جاتا تھا 

Example 4:
English: While it is true that those things are going on, there's an Africa that you don't hear about very much.
Urdu: اگرچہ یہ سچ ہے کہ یہ سب کچھ وہاں ہو رہا ہے ، لیکن افریقہ کا ایک پہلو ایسا بھی ہے جس کے متعلق آپ زیادہ نہیں سنتے ۔

Example 5:
English: In this country, if you receive stolen goods, are you not prosecuted?
Urdu: اس ملک میں ، اگر آپ چوری کا سامان خریدیں ، تو کیا آپ کو سزا نہیں دی جاتی ؟

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

input_file = "eng_Latn.devtest"
output_file = "urd_large_MT1.txt"

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