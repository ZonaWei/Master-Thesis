import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

SYSTEM_INSTRUCTION = """
You are an expert Urdu-to-English machine translator. Your sole function is to provide a direct, high-quality translation of the given Urdu text.
- You MUST NOT provide any explanations, notes, warnings, or commentary.
- Your response MUST ONLY contain the final English translation.
- If the source text contains apparent errors or ambiguities, provide the most logical and fluent translation without mentioning the error.
"""


model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)


CONVERSATION_HISTORY_EXAMPLES = [
    {
        "role": "user",
        "parts": ["خانہ جنگی کے دوران یہ ایک ظہور شے دنیا کے بڑے حصوں میں ، اعلی تعلیم حاصل کرنا ناممکن ہے ایک عام شہری کے لیے ۔"]
    },
    {
        "role": "model",
        "parts": ["In large parts of the world, higher education is unattainable for an average citizen."]
    },
    {
        "role": "user",
        "parts": ["وہاں اپاور سٹوڈنٹس کو کیمپس سے باہر جانے کی اجازت نہ تھی ۔ اور نہ ہی والدین سے بات کرنے کی ۔"]
    },
    {
        "role": "model",
        "parts": ["The students were not allowed to leave the campus, or communicate with their parents."]
    },
    {
        "role": "user",
        "parts": ["یہ انہر دن مکمل طور پر پلان کیا جاتا تھا ، اور اگر اسمیں کوئی فالتو وقت بچ جاتا تو وہ عظیم لیڈر کو خراج تحسین کے لیے استعمال کیا جاتا تھا "]
    },
    {
        "role": "model",
        "parts": ["Their days were meticulously mapped out, and any free time they had was devoted to honoring their Great Leader."]
    },
    {
        "role": "user",
        "parts": ["چینل ۱۹ کے ویڈیو وولنٹیرز کی دوسری ویڈیوز بصیرت اور جوش پیدا کرنےاگرچہ یہ سچ ہے کہ یہ سب کچھ وہاں ہو رہا ہے ، لیکن افریقہ کا ایک پہلو ایسا بھی ہے جس کے متعلق آپ زیادہ نہیں سنتے ۔"]
    },
    {
        "role": "model",
        "parts": ["While it is true that those things are going on, there's an Africa that you don't hear about very much."]
    },
    {
        "role": "user",
        "parts": ["اس ملک میں ، اگر آپ چوری کا سامان خریدیں ، تو کیا آپ کو سزا نہیں دی جاتی ؟"]
    },
    {
        "role": "model",
        "parts": ["In this country, if you receive stolen goods, are you not prosecuted?"]
    }
]



def conversational_translate(text_to_translate):
    """
    Employing conversation history as few-shot examples for translation.
    """

    history = list(CONVERSATION_HISTORY_EXAMPLES)


    history.append({
        "role": "user",
        "parts": [f"Translate the following Urdu to English:\n\n{text_to_translate}"]
    })
    

    for attempt in range(3):
        try:

            response = model.generate_content(history)
            return response.text.strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1) 
    return ""


input_file = "urd_Arab.devtest"
output_file = "urd_large_output_ICL.txt" 


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

        translation = conversational_translate(sentence)
        out.write(translation + "\n")
        out.flush() 
        time.sleep(0.5) 

print("Translation complete!")