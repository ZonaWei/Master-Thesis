import stanza
import json
import os

# loading stanza language code
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


def extract_pos_tokens(text, nlp, upos_tags={"VERB"}):
    doc = nlp(text)
    selected_words = []
    all_tokens = []
    for sent in doc.sentences:
        for word in sent.words:
            token = word.text
            all_tokens.append(token)
            if word.upos in upos_tags:
                selected_words.append(token)
    return set(selected_words), all_tokens  


def analyze_inflection_pos(language, lookup_path, mt_path, ref_path, upos_tags={"VERB"}):
    print(f"\n📘 {language.upper()} {' + '.join(upos_tags)} Inflection Coverage Analysis")

    lang_code = LANG_CODE[language]
    if not os.path.exists(os.path.expanduser(f"~/stanza_resources/{lang_code}")):
        stanza.download(lang_code, processors="tokenize,pos", verbose=False)
    nlp = stanza.Pipeline(lang=lang_code, processors="tokenize,pos", tokenize_no_ssplit=True, verbose=False)

    lookup = load_lookup(lookup_path)


    mt_text = load_text(mt_path)
    mt_words, mt_tokens = extract_pos_tokens(mt_text, nlp, upos_tags)
    mt_used = mt_words & lookup


    ref_text = load_text(ref_path)
    ref_words, ref_tokens = extract_pos_tokens(ref_text, nlp, upos_tags)
    ref_used = ref_words & lookup


    print(f"Total known inflected forms: {len(lookup)}")
    print(f"Total tokens in MT: {len(mt_tokens)}")
    print(f"MT matches in known forms: {len(mt_used)} ({len(mt_used)/len(mt_tokens):.2%})")
    print(f"MT inflection loss: {1 - len(mt_used)/len(mt_tokens):.2%}")
    print(f"Total tokens in REF: {len(ref_tokens)}")
    print(f"REF matches in known forms: {len(ref_used)} ({len(ref_used)/len(ref_tokens):.2%})")
    print(f"REF inflection loss: {1 - len(ref_used)/len(ref_tokens):.2%}")
    print(f"Sample MT forms: {list(mt_used)[:10]}")
    print(f"Sample REF forms: {list(ref_used)[:10]}")


langs = ["urdu"]
base_dir = "inflection"

for lang in langs:
    analyze_inflection_pos(
        language=lang,
        lookup_path=os.path.join(base_dir, f"{lang}_inflection_lookup.json"),
        mt_path=os.path.join(base_dir, f"{lang}_large_MT1.txt"),
        ref_path=os.path.join(base_dir, f"{lang}_large_ref.txt"),
        upos_tags={"VERB", "NOUN"}  
    )

