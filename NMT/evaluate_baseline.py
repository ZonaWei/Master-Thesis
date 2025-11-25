import argparse
import os
import re
from typing import List, Dict, Tuple, Any

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
# IMPORTANT: Import sacrebleu directly for static method calls
import sacrebleu
import torch

# --- Metrics Setup ---
# NLLB Model ID (fixed)
NLLB_MODEL_ID = "facebook/nllb-200-distilled-600M"

# Map project language identifiers to NLLB's specific language tags
LANG_MAP: Dict[str, str] = {
    "eng": "eng_Latn",
    "ur": "urd_Arab", # Urdu
    "am": "amh_Ethi", # Amharic
    "sw": "swh_Latn", # Swahili
    "zu": "zul_Latn", # Zulu
}

def compute_metrics(predictions: List[str], references: List[str]) -> Dict[str, float]:
    """
    Computes BLEU and ChrF++ metrics using the latest sacrebleu static methods.
    
    Uses direct function calls: sacrebleu.corpus_bleu() and sacrebleu.corpus_chrf().
    """
    # SacreBLEU expects references as a list of lists of strings
    references_for_sacrebleu = [[ref] for ref in references]
    
    # Use sacrebleu.corpus_bleu()
    bleu_score = sacrebleu.corpus_bleu(predictions, references_for_sacrebleu).score
    
    # Use sacrebleu.corpus_chrf()
    # Removed incompatible keyword argument 'chrf_word_order'
    chrf_score = sacrebleu.corpus_chrf(predictions, references_for_sacrebleu).score
    
    return {"BLEU": round(bleu_score, 2), "ChrF++": round(chrf_score, 2)}

def load_data(src_path: str, ref_path: str) -> Tuple[List[str], List[str]]:
    """Loads source and reference data from text files."""
    try:
        with open(src_path, "r", encoding="utf-8") as f:
            sources = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Source file not found at {src_path}")
        return [], []
        
    try:
        with open(ref_path, "r", encoding="utf-8") as f:
            references = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Reference file not found at {ref_path}")
        return [], []
        
    if len(sources) != len(references):
        print(f"Warning: Source ({len(sources)}) and reference ({len(references)}) file line counts do not match. Using minimum length.")
        min_len = min(len(sources), len(references))
        sources = sources[:min_len]
        references = references[:min_len]

    return sources, references

def run_evaluation(src_lang: str, tgt_lang: str, test_file_src: str, test_file_ref: str, device: torch.device, model: Any, tokenizer: Any) -> None:
    """Runs a single evaluation task for a given language pair and prints the metrics."""
    
    nllb_src_lang = LANG_MAP[src_lang]
    nllb_tgt_lang = LANG_MAP[tgt_lang]

    print("\n" + "="*80)
    print(f"STARTING EVALUATION: {src_lang.upper()} -> {tgt_lang.upper()} (NLLB Baseline)")
    print(f"Source file: {test_file_src}")
    print(f"Reference file: {test_file_ref}")
    print("="*80)
    
    # Reload the tokenizer for the new source language
    tokenizer.src_lang = nllb_src_lang
    
    # Use convert_tokens_to_ids to get the ID for the target language tag
    tgt_lang_id = tokenizer.convert_tokens_to_ids(nllb_tgt_lang)
    
    # Set the target language for the model config
    model.config.forced_bos_token_id = tgt_lang_id 

    sources, references = load_data(test_file_src, test_file_ref)
    if not sources:
        print("Skipping evaluation due to data loading error.")
        return
    
    # --- Inference ---
    predictions: List[str] = []
    
    # Use a small batch size
    batch_size = 32 
    
    print(f"Total test samples loaded: {len(sources)}")
    print(f"Starting generation (batch size: {batch_size})...")

    model.eval()
    
    with torch.no_grad():
        for i in range(0, len(sources), batch_size):
            batch_sources = sources[i:i + batch_size]
            
            # Tokenize the batch
            inputs = tokenizer(
                batch_sources, 
                return_tensors="pt", 
                padding=True, 
                truncation=True,
                max_length=512
            ).to(device)

            # Generate translations
            generated_ids = model.generate(
                **inputs,
                forced_bos_token_id=tgt_lang_id,
                max_length=512,
            )

            # Decode translations
            batch_predictions = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
            predictions.extend(batch_predictions)

    # --- Compute Metrics ---
    metrics = compute_metrics(predictions, references)
    
    print("\n" + "-"*50)
    print(f"| FINAL METRICS ({src_lang.upper()} -> {tgt_lang.upper()})")
    print("-" * 50)
    print(f"| BLEU: {metrics['BLEU']:.2f}")
    print(f"| ChrF++: {metrics['ChrF++']:.2f}")
    print("-" * 50)
    print("FINISHED EVALUATION.")


def main():
    # --- FIXED CONFIGURATION ---
    # Fix device to use the first CUDA GPU (index 0)
    os.environ['CUDA_VISIBLE_DEVICES'] = '0' 
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # --- Load Model and Tokenizer ONCE ---
    print(f"Loading NLLB Baseline Model: {NLLB_MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(NLLB_MODEL_ID)
    model = AutoModelForSeq2SeqLM.from_pretrained(NLLB_MODEL_ID).to(device)
    
    # --- DEFINE ALL 8 TASKS ---
    test_data_dir = "./test_data"
    
    tasks = [
        # FORWARD: EN -> LR
        ("eng", "ur", os.path.join(test_data_dir, "flores200_en.txt"), os.path.join(test_data_dir, "flores200_ur.txt")),
        ("eng", "am", os.path.join(test_data_dir, "flores200_en.txt"), os.path.join(test_data_dir, "flores200_am.txt")),
        ("eng", "sw", os.path.join(test_data_dir, "flores200_en.txt"), os.path.join(test_data_dir, "flores200_sw.txt")),
        ("eng", "zu", os.path.join(test_data_dir, "flores200_en.txt"), os.path.join(test_data_dir, "flores200_zu.txt")),
        
        # REVERSE: LR -> EN
        ("ur", "eng", os.path.join(test_data_dir, "flores200_ur.txt"), os.path.join(test_data_dir, "flores200_en.txt")),
        ("am", "eng", os.path.join(test_data_dir, "flores200_am.txt"), os.path.join(test_data_dir, "flores200_en.txt")),
        ("sw", "eng", os.path.join(test_data_dir, "flores200_sw.txt"), os.path.join(test_data_dir, "flores200_en.txt")),
        ("zu", "eng", os.path.join(test_data_dir, "flores200_zu.txt"), os.path.join(test_data_dir, "flores200_en.txt")),
    ]
    
    # --- EXECUTE ALL TASKS SEQUENTIALLY ---
    for src, tgt, src_file, ref_file in tasks:
        run_evaluation(src, tgt, src_file, ref_file, device, model, tokenizer)


if __name__ == "__main__":
    main()
