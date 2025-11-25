import stanza
import json
import os

#loading stanza language codes
LANG_CODE = {
    "amharic": "am",
    "swahili": "sw",
    "urdu": "ur",
    "zulu": "zu"
}

def load_lookup(path):
    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f).keys())


def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def extract_verbs(text, nlp):
    doc = nlp(text)
    return set(word.text for sent in doc.sentences for word in sent.words if word.upos == "VERB")


def analyze_inflection_verbs(language, lookup_path, mt_path, ref_path):
    print(f"\n {language.upper()} Verb Inflection Analysis")

    lang_code = LANG_CODE[language]
    if not os.path.exists(os.path.expanduser(f"~/stanza_resources/{lang_code}")):
    	stanza.download(lang_code, processors="tokenize,pos", verbose=False)
    nlp = stanza.Pipeline(lang=lang_code, processors="tokenize,pos", tokenize_no_ssplit=True, verbose=False)

    lookup = load_lookup(lookup_path)

    mt_text = load_text(mt_path)
    ref_text = load_text(ref_path)

    mt_verbs = extract_verbs(mt_text, nlp)
    ref_verbs = extract_verbs(ref_text, nlp)

    mt_used = mt_verbs & lookup
    ref_used = ref_verbs & lookup

    print(f"🔢 Total known verb forms: {len(lookup)}")
    print(f"📥 MT verb matches: {len(mt_used)} ({len(mt_used)/len(lookup):.2%})")
    print(f"📗 REF verb matches: {len(ref_used)} ({len(ref_used)/len(lookup):.2%})")
    print(f"❌ MT inflection loss: {1 - len(mt_used)/len(lookup):.2%}")
    print(f"❌ REF inflection loss: {1 - len(ref_used)/len(lookup):.2%}")
    print(f"🔍 Sample MT verbs: {list(mt_used)[:10]}")
    print(f"🔍 Sample REF verbs: {list(ref_used)[:10]}")


langs = ["urdu"]  
base_dir = "inflection" 

for lang in langs:
    analyze_inflection_verbs(
        language=lang,
        lookup_path=os.path.join(base_dir, f"{lang}_inflection_lookup.json"),
        mt_path=os.path.join(base_dir, f"{lang}_MT.txt"),
        ref_path=os.path.join(base_dir, f"{lang}_ref.txt")
    )
