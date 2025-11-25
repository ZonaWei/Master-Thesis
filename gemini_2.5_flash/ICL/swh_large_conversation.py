import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

SYSTEM_INSTRUCTION = """
You are an expert Swahili-to-English machine translator. Your sole function is to provide a direct, high-quality translation of the given Swahili text.
- You MUST NOT provide any explanations, notes, warnings, or commentary.
- Your response MUST ONLY contain the final English translation.
- If the source text contains apparent errors or ambiguities, provide the most logical and fluent translation without mentioning the error.
"""

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "parts": ["Angola na Brazil zina uhusiano maalum baina yao, kutokana na matumizi ya lugha moja na pamoja na historia yao ya kutawaliwa huko nyuma - nchi hizi mbili zilikuwa sehemu ya himaya ya Wareno – na utamaduni wa pamoja unaotoka na historia ya asili moja."]
    },
    {
        "role": "model",
        "parts": ["Angola and Brazil have a special relationship towards each other, partially because of their common language and their shared colonial past - both countries were part of the Portuguese Empire - and the cultural ties that stem from this shared history."]
    },
    {
        "role": "user",
        "parts": ["Mtu mweusi aling'olewa kutoka katika ardhi yake na kuuzwa kama bidhaa, utumwani"]
    },
    {
        "role": "model",
        "parts": ["The Negro was uprooted from his land and sold as merchandise, enslaved."]
    },
    {
        "role": "user",
        "parts": ["Hakuna idadi kamili kuhusiana na watu wangapi wanaabudu Candomblé."]
    },
    {
        "role": "model",
        "parts": ["There are no definitive numbers on how many people in Brazil follow Candomblé. "]
    },
    {
        "role": "user",
        "parts": ["Hapa chini kuna habari zilizopachikwa katika kurasa za blogu mbili zikionyesha mitazamo tofauti baina ya watu wawili kwa kuibua masuala muhimu kama uhamiaji, ubaguzi wa rangi, ukabila na heshima miongoni mwa watu. "]
    },
    {
        "role": "model",
        "parts": ["Below are two entire blog posts showing different perspectives of one people towards the other, raising issues of immigration, racism, ethnicity and mutual respect."]
    },
    {
        "role": "user",
        "parts": ["Jumuiya ya Kiarabu ina msimamo gani kuhusu viongozi wa mapinduzi haya?"]
    },
    {
        "role": "model",
        "parts": ["What is the stance of the Arab League from the leaders of this coup? "]
    }
]


# --- MODIFIED: Translation function using conversation history ---
def fewshot_translate(text_to_translate):

    # 1. Copy the base conversation history to avoid modifying the original list with each call.
    prompt_messages = list(FEW_EXAMPLES_EXAMPLES)

    # 2. At the end of the conversation history, add the new sentence we currently need to translate as the user's latest message.
    prompt_messages.append({
        "role": "user",
        "parts": [f"Translate the following Swahili to English:\n\n{text_to_translate}"]
    })
    
    # 3. Send the entire conversation history to the model
    for attempt in range(3):
        try:
            # generate_content
            response = model.generate_content(history)
            return response.text.strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1) # If the API call fails, please wait a moment and try again.
    return "" # If all three attempts fail, return an empty string.



input_file = "swh_Latn.devtest"
output_file = "swh_large_output_ICL.txt" 


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
        
        translation = fewshot_translate(sentence)
        out.write(translation + "\n")
        out.flush() 
        time.sleep(0.5) 

print("Translation complete!")