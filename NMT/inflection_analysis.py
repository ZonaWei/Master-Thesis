import json
import os
import re
from typing import Set, List

def load_words(path: str) -> List[str]:
    """
    Loads text from a file, converts it to lowercase, removes basic punctuation,
    and tokenizes it into a list of words.

    Args:
        path: The file path to the text document.

    Returns:
        A list of tokenized words.
    """
    with open(path, "r", encoding="utf-8") as f:
        text = f.read().lower()
        # Remove punctuation. Note: This uses a simple regex; complex scripts
        # might require more advanced tokenization/normalization.
        text = re.sub(r"[^\w\s]", "", text)  
        return text.split()

def analyze_inflection(language: str, lookup_path: str, mt_path: str, ref_path: str) -> None:
    """
    Analyzes the inflection coverage for the Machine Translation (MT) output and 
    the Human Reference (REF) text against a known inflection lookup table.

    Args:
        language: The language being analyzed (e.g., "swahili").
        lookup_path: Path to the JSON file containing known inflected forms.
        mt_path: Path to the Machine Translation output text file.
        ref_path: Path to the Human Reference text file.
    """
    print(f"\n{'='*5} {language.upper()} Inflection Coverage Analysis {'='*5}")

    # Load the known inflected forms (the lookup table)
    try:
        with open(lookup_path, "r", encoding="utf-8") as f:
            lookup = json.load(f)
        known_forms: Set[str] = set(lookup.keys())
    except FileNotFoundError:
        print(f"Error: Lookup file not found at {lookup_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {lookup_path}")
        return

    # Load and tokenize MT and REF texts
    mt_tokens: List[str] = load_words(mt_path)
    ref_tokens: List[str] = load_words(ref_path)
    
    # Use sets for fast lookup of unique words used in the texts
    mt_words: Set[str] = set(mt_tokens)
    ref_words: Set[str] = set(ref_tokens)

    # Calculate coverage (intersection of unique words used and known forms)
    mt_used: Set[str] = mt_words.intersection(known_forms)
    ref_used: Set[str] = ref_words.intersection(known_forms)

    # --- Analysis for MT (Model Translation) ---
    total_mt_tokens: int = len(mt_tokens)
    mt_coverage: int = len(mt_used)
    mt_coverage_ratio: float = mt_coverage / total_mt_tokens if total_mt_tokens else 0
    mt_loss: float = 1 - mt_coverage_ratio
    
    print(f"\n[MT Analysis] - Model Translation")
    print(f"Total tokens in MT: {total_mt_tokens}")
    print(f"MT unique forms matching known inflections: {mt_coverage}")
    print(f"MT Inflection Coverage (ratio of matched unique forms to total tokens): {mt_coverage_ratio:.2%}")
    print(f"MT Inflection Loss: {mt_loss:.2%}")

    # --- Analysis for REF (Reference) ---
    total_ref_tokens: int = len(ref_tokens)
    ref_coverage: int = len(ref_used)
    ref_coverage_ratio: float = ref_coverage / total_ref_tokens if total_ref_tokens else 0
    ref_loss: float = 1 - ref_coverage_ratio

    print(f"\n[REF Analysis] - Human Reference")
    print(f"Total tokens in REF: {total_ref_tokens}")
    print(f"REF unique forms matching known inflections: {ref_coverage}")
    print(f"REF Inflection Coverage (ratio of matched unique forms to total tokens): {ref_coverage_ratio:.2%}")
    print(f"REF Inflection Loss (Baseline): {ref_loss:.2%}")
    
    print(f"\nSample MT forms that match: {list(mt_used)[:5]}")
    print(f"Sample REF forms that match: {list(ref_used)[:5]}")
    print("="*40)


# --- Execution Block ---
# Hardcoded execution block to run the analysis for all four languages.
langs = ["swahili", "zulu", "amharic", "urdu"]
base_dir = "inflection"

for lang in langs:
    # Constructing the file paths based on the established directory structure
    analyze_inflection(
        language=lang,
        lookup_path=os.path.join(base_dir, f"{lang}_inflection_lookup.json"),
        mt_path=os.path.join(base_dir, f"{lang}_large_MT.txt"),
        ref_path=os.path.join(base_dir, f"{lang}_large_ref.txt")
    )
