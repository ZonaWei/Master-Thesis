import google.generativeai as genai
import time
import os

genai.configure(api_key="AIzaSyBo9slT1CkbBYkpWXGSnYZHKmska1UaaDg")

SYSTEM_INSTRUCTION = """
You are an expert Zulu-to-English machine translator. Your sole function is to provide a direct, high-quality translation of the given Zulu text.
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
        "parts": ["Ngaphezu kwalokho, ngithatha leli thuba ukukhumbula ukuthi uJuni 20 uzoba ..."]
    },
    {
        "role": "model",
        "parts": ["In addition, I take this opportunity to remember that June 20 will be the ..."]
    },
    {
        "role": "user",
        "parts": ["Wayalela isizwe sakhe ukuba sibambelele siqinise eNcwadini ka- Allah (i-Qur'aan); washo nokuthi uma bengakugcina lokho abasoze balahlekiswa."]
    },
    {
        "role": "model",
        "parts": ["He commanded his community to hold fast to the Book of Allah; as long as they did this they would not be misguided, he said."]
    },
    {
        "role": "user",
        "parts": ["Baye bancishwa nethuba lokukhulekela kanye namakholwa abakanye nawo."]
    },
    {
        "role": "model",
        "parts": ["They have also been denied the opportunity to worship with their fellow believers."]
    },
    {
        "role": "user",
        "parts": ["Kuyacaca ukuthi ubufakazi obuvela eBhayibhelini bubonisa ukuthi inkolo ehleliwe iwuhlobo lokukhulekela olwamukelekayo kuNkulunkulu."]
    },
    {
        "role": "model",
        "parts": ["Clearly, evidence from the Bible points to an organized form of worship as the kind that is acceptable to God."]
    },
    {
        "role": "user",
        "parts": ["Impikiswano: amanzi, ukuthi unganikeza kanjani amanzi okuphuza, okungenani isibalo esikhulu kunazo zonke e-Afrika?"]
    },
    {
        "role": "model",
        "parts": ["Debate: water, how to give access to drinking water, at least to the greatest number in Africa?"]
    }
]



def conversational_translate(text_to_translate):
    """
    Using conversation history as few-shot examples for translation。
    """
    history = list(CONVERSATION_HISTORY_EXAMPLES)

    history.append({
        "role": "user",
        "parts": [f"Translate the following Zulu to English:\n\n{text_to_translate}"]
    })

    for attempt in range(3):
        try:
            response = model.generate_content(history)
            return response.text.strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1) 
    return "" 




input_file = "zul_Latn.devtest"
output_file = "zul_large_output_ICL.txt" 


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