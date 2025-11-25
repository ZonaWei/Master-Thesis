import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

FEW_SHOT_PREFIX = """
Task: Translate the following Amharic sentences to English. Maintain correct tone and fluency. Follow the structure of the examples. Just respond with the translation and nothing else.

Example 1:
Amharic: ዝነኛው ካርቲኒስት ማና ናዬስታኒ ማክሰኞ መስከረም 11 ፣ 2012 ራሳቸውን “የእስልምና ወታደሮች” ብለው በሚጠሩ የስርዓቱ ደጋፊ ሰርጎ ገቦች ተመዘበረ፡፡
English: The Facebook page of a leading Iranian leading cartoonist, Mana Nayestani, was hacked on Tuesday, 11 September 2012, by pro-regime hackers who call themselves "Soldiers of Islam".

Example 2: 
Amharic: በሌላ ካርቱን ሚዲያው ለምን ለሶሪያን ዜና ሽፋን እየሰጠ የባህሬን የከለከለበትን ምክንያት ጠይቀዋል፡፡
English: With another cartoon they ask why the news media cover Syria but not Bahrain?

Example 3:
Amharic: የማና ናዬስታኒ ገጽ በስርዓቱ ደጋፊ የፕሮግራም ሰርጎ ገቦች ከተመረጠባቸው ምክንያቶች አንዱ ምንአልባት እንደ ማርዶማክ ባሉ የኢራናውያን መካናት ባሉት ፖለቲካዊ ካርቱኖቹ ሳይሆን አይቀርም፡፡
English: One of the reasons that Mana Nayestani's page was chosen by pro regime hackers may be because of his political cartoons on Iranian sites such as Mardomak. 

Example 4:
Amharic: የተቀዋሚን መካነ ድር እና ጦማሮችን መመዝበር አዲስ ስልት አይደለም፡፡ 
English: Hacking opposition sites and blogs is not a new tactic.

Example 5:
Amharic: በዮርዳኖስ የፕሬስ እና ሕትመት ሕግ በበይነመረብ (Internet) ላይ ሐሳብን የመግለጽ መብትን እንዲያደግድ ተደርጎ ትላንት እንዲሻሻል ተደረገ፡፡
English: Amendments to the press and publications law restricting online expression in Jordan were passed by parliament today. 

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

input_file = "amh_Ethi.devtest"
output_file = "amh_large_output5.txt"

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
        
        
        
        
        