import os
# This line MUST be at the very top of the script, before importing other libraries.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
import argparse
import sacrebleu
from tqdm import tqdm
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    BitsAndBytesConfig
)
from peft import PeftModel

def find_latest_checkpoint(model_path_base):
    """Automatically find the latest checkpoint folder."""
    if not os.path.isdir(model_path_base):
        return None
    
    checkpoints = [d for d in os.listdir(model_path_base) if d.startswith("checkpoint-")]
    
    if not checkpoints:
        # If no checkpoint folder, it means the model was saved directly
        return model_path_base

    # Find the checkpoint with the highest number
    latest_checkpoint = max(checkpoints, key=lambda x: int(x.split('-')[1]))
    return os.path.join(model_path_base, latest_checkpoint)

def main(args):
    """
    Main evaluation function.
    """

    # --- 1. Load Base Model and Fine-tuned LoRA Adapter ---
    print("--- 1. Loading base model and LoRA adapter ---")
    base_model_name = args.base_model_name
    
    quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_name,
        quantization_config=quantization_config,
        device_map={"": 0} 
    )
    
    model_path_base = f"./{args.lang}-{args.data_size}-finetune"
    lora_model_path = find_latest_checkpoint(model_path_base)
    
    if not lora_model_path or not os.path.exists(lora_model_path):
        raise FileNotFoundError(f"Could not find a valid checkpoint in {model_path_base}. Please check the path.")
        
    print(f"Loading LoRA adapter from: {lora_model_path}")
    
    # Load the LoRA adapter
    model = PeftModel.from_pretrained(base_model, lora_model_path)
    
    # Merge the LoRA weights into the base model to prevent errors during inference
    print("--- Merging LoRA adapter into the base model ---")
    model = model.merge_and_unload()
    
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(base_model_name)

    # --- 2. Load Test Data ---
    print(f"--- 2. Loading test data from {args.test_file_src} ---")
    
    source_texts = []
    with open(args.test_file_src, 'r', encoding='utf-8') as f:
        for line in f:
            source_texts.append(line.strip())
            
    references = []
    with open(args.test_file_ref, 'r', encoding='utf-8') as f:
        for line in f:
            references.append(line.strip())
    
    # Sacrebleu expects a list of lists for references
    references = [references]

    # --- 3. Generate Translations ---
    print("--- 3. Generating translations ---")
    predictions = []
    
    # Process in batches to manage memory
    for i in tqdm(range(0, len(source_texts), args.batch_size)):
        batch = source_texts[i:i + args.batch_size]
        
        tokenizer.src_lang = args.src_lang_code
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=128).to("cuda")

        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(args.tgt_lang_code),
            max_new_tokens=128
        )
        
        # We must explicitly set the target language before decoding
        tokenizer.tgt_lang = args.tgt_lang_code
        # Using the recommended `text_target` argument is not applicable for decoding,
        # so `as_target_tokenizer` context is still the way to go here.
        with tokenizer.as_target_tokenizer():
            decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        
        predictions.extend(decoded_preds)
        
    # --- 4. Calculate and Print Metrics ---
    print("\n--- 4. Calculating metrics ---")

    # BLEU Score
    bleu = sacrebleu.corpus_bleu(predictions, references)
    print(f"BLEU Score: {bleu.score:.2f}")

    # chrF++ Score (sacrebleu's default)
    chrf = sacrebleu.corpus_chrf(predictions, references)
    print(f"chrF++ Score: {chrf.score:.2f}")

    # COMET Score
    try:
        from unbabel_comet import load_from_checkpoint
        print("Loading COMET model...")
        comet_model = load_from_checkpoint("wmt22-comet-da/checkpoints/model.ckpt")
        
        comet_data = []
        # Correctly access the single list of references
        for src, mt, ref in zip(source_texts, predictions, references[0]):
            comet_data.append({"src": src, "mt": mt, "ref": ref})

        model_output = comet_model.predict(comet_data, batch_size=args.batch_size, gpus=1)
        
        print(f"COMET Score: {model_output.system_score:.4f}")
    except ImportError:
        print("\nCOMET not installed. Skipping. To install: pip install unbabel-comet")
    except Exception as e:
        print(f"\nCould not calculate COMET score due to an error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a fine-tuned NMT model")

    # Model and Data Paths
    parser.add_argument("--base_model_name", type=str, default="facebook/nllb-200-distilled-600M", help="Base pretrained model name")
    parser.add_argument("--lang", type=str, required=True, help="Language code of the trained model (e.g., 'sw')")
    parser.add_argument("--data_size", type=str, required=True, help="Data size identifier (e.g., '1k', '100k', '1M')")
    parser.add_argument("--test_file_src", type=str, required=True, help="Path to the source language test file")
    parser.add_argument("--test_file_ref", type=str, required=True, help="Path to the reference language test file")
    
    # Language Codes
    parser.add_argument("--src_lang_code", type=str, required=True, help="NLLB source language code (e.g., 'swh_Latn')")
    parser.add_argument("--tgt_lang_code", type=str, default="eng_Latn", help="NLLB target language code")
    
    # Inference Hyperparameters
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for evaluation")

    args = parser.parse_args()
    main(args)
