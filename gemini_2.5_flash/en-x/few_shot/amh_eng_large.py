import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

FEW_SHOT_PREFIX = """
Task: Translate the following English sentences to Amharic. Maintain correct tone and fluency. Just respond with the translation and nothing else.

Example 1:
English: Participants wore black to the funeral-themed demonstration.
Amharic: የበይነመረብ ቀብር ለተባለለት ለዚህ አዋጅ ሰልፈኞቹ ጥቁር ልብስ ለብሰው ነበር፡፡

Example 2: 
English: Owners of websites will also be made responsible for the content of comments published by readers on their sites.
English: የድረአምባዎች ባለቤቶች አንባቢዎቸው ድረአምባዎቻቸው ላይ ለሚለጥፏቸው አስተያየቶች ሳይቀር ኃላፊነቱን ይወስዳሉ፡፡

Example 3:
English: Will this law create new financial skirmishes between wives and husbands?
Amharic: ይህ ሕግ በሚስቶችና ባሎች መካከል አዲስ የገንዘብ ጦርነት አያጭርም?

Example 4:
English: The gross income remaining the same, the household economy is not changed.
Amharic: ድምር ገቢው ዞሮ ዞሮ አንድ ስለሚሆን በቤትውስጥ ኢኮኖሚው ላይ ለውጥ አይኖርም፡፡

Example 5:
English: While angry patriots are in the street protesting, cooler heads do prevail online as the Tea Leaf Nation pointed out.
Amharic: የተበሳጩ አገርወዳዶች በየጎዳናው ሲያምጹ፣ ቲ ሊፍ ኔሽን እንደጠቆመው ፣ ደህነኞቹ አሳቢዎች በመስመር ላይ ጥያቄያቸውን እያቀረቡ ነው፡፡


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
output_file = "amh_large_MT1.txt"

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