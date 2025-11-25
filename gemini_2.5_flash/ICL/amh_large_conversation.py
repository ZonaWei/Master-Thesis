import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

SYSTEM_INSTRUCTION = """
You are an expert Amharic-to-English machine translator. Your sole function is to provide a direct, high-quality translation of the given Amharic text.
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
        "parts": ["ዝነኛው ካርቲኒስት ማና ናዬስታኒ ማክሰኞ መስከረም 11 ፣ 2012 ራሳቸውን “የእስልምና ወታደሮች” ብለው በሚጠሩ የስርዓቱ ደጋፊ ሰርጎ ገቦች ተመዘበረ፡፡"]
    },
    {
        "role": "model",
        "parts": ["The Facebook page of a leading Iranian leading cartoonist, Mana Nayestani, was hacked on Tuesday, 11 September 2012, by pro-regime hackers who call themselves 'Soldiers of Islam'."]
    },
    {
        "role": "user",
        "parts": ["በሌላ ካርቱን ሚዲያው ለምን ለሶሪያን ዜና ሽፋን እየሰጠ የባህሬን የከለከለበትን ምክንያት ጠይቀዋል፡፡"]
    },
    {
        "role": "model",
        "parts": ["With another cartoon they ask why the news media cover Syria but not Bahrain?"]
    },
    {
        "role": "user",
        "parts": ["የማና ናዬስታኒ ገጽ በስርዓቱ ደጋፊ የፕሮግራም ሰርጎ ገቦች ከተመረጠባቸው ምክንያቶች አንዱ ምንአልባት እንደ ማርዶማክ ባሉ የኢራናውያን መካናት ባሉት ፖለቲካዊ ካርቱኖቹ ሳይሆን አይቀርም፡፡"]
    },
    {
        "role": "model",
        "parts": ["One of the reasons that Mana Nayestani's page was chosen by pro regime hackers may be because of his political cartoons on Iranian sites such as Mardomak. "]
    },
    {
        "role": "user",
        "parts": ["የተቀዋሚን መካነ ድር እና ጦማሮችን መመዝበር አዲስ ስልት አይደለም፡፡ "]
    },
    {
        "role": "model",
        "parts": ["Hacking opposition sites and blogs is not a new tactic."]
    },
    {
        "role": "user",
        "parts": ["በዮርዳኖስ የፕሬስ እና ሕትመት ሕግ በበይነመረብ (Internet) ላይ ሐሳብን የመግለጽ መብትን እንዲያደግድ ተደርጎ ትላንት እንዲሻሻል ተደረገ፡፡"]
    },
    {
        "role": "model",
        "parts": ["Amendments to the press and publications law restricting online expression in Jordan were passed by parliament today. "]
    }
]



def conversational_translate(text_to_translate):
    """
    Employing dialogue history as few-shot examples for translation.
    """

    history = list(CONVERSATION_HISTORY_EXAMPLES)


    history.append({
        "role": "user",
        "parts": [f"Translate the following Amharic to English:\n\n{text_to_translate}"]
    })
    

    for attempt in range(3):
        try:

            response = model.generate_content(history)
            return response.text.strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1) 
    return "" 




input_file = "amh_Ethi.devtest"
output_file = "amh_large_output_ICL.txt" 


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