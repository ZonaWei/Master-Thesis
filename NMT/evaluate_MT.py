import os
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
    """
    Automatically finds the latest checkpoint folder within the base model path.
    If no checkpoint folder is found, it returns the base path itself, assuming
    the model was saved directly without checkpoint naming (e.g., 'checkpoint-XXXX').
    
    Args:
        model_path_base (str): The root directory where checkpoints are saved.
        
    Returns:
        str: Full path to the latest checkpoint or the base path.
    """
    if not os.path.isdir(model_path_base):
        return None
    
    # List all subdirectories that start with "checkpoint-"
    checkpoints = [d for d in os.listdir(model_path_base) if d.startswith("checkpoint-")]
    
    if not checkpoints:
        # If no checkpoint folder, assume the model weights are directly in the base path
        return model_path_base

    # Find the checkpoint with the highest numerical suffix
    try:
        latest_checkpoint = max(checkpoints, key=lambda x: int(x.split('-')[1]))
        return os.path.join(model_path_base, latest_checkpoint)
    except:
        print("Warning: Checkpoint naming convention is inconsistent. Using base path.")
        return model_path_base


def main(args):
    """
    The main evaluation function: loads the fine-tuned model, generates translations,
    calculates metrics (BLEU, chrF++), and saves the predicted translations (MT file).
    """

    # --- 1. Load Base Model and Fine-tuned LoRA Adapter ---
    print("--- 1. Loading base model and LoRA adapter ---")
    base_model_name = args.base_model_name
    
    # Load model with 8-bit quantization to save GPU memory
    quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    base_model = AutoModelForSeq2SeqLM.from_pretrained(
        base_model_name,
        quantization_config=quantization_config,
        device_map={"": 0} # Map the model to the first visible GPU
    )
    
    # Determine the full path to the fine-tuned model checkpoint
    model_path_base = args.model_path_base if args.model_path_base else f"./{args.lang}-{args.data_size}-finetune"
    lora_model_path = find_latest_checkpoint(model_path_base)
    
    if not lora_model_path or not os.path.exists(lora_model_path):
        raise FileNotFoundError(f"Error: Could not find a valid checkpoint in {model_path_base}. Please check the path.")
            
    print(f"Loading LoRA adapter from: {lora_model_path}")
    
    # Load the LoRA adapter
    model = PeftModel.from_pretrained(base_model, lora_model_path)
    
    # Merge the LoRA weights into the base model for faster inference
    print("--- Merging LoRA adapter into the base model ---")
    model = model.merge_and_unload()
    
    model.eval() # Set model to evaluation mode

    tokenizer = AutoTokenizer.from_pretrained(base_model_name)

    # --- 2. Load Test Data ---
    print(f"--- 2. Loading source test file: {args.test_file_src} ---")
    
    source_texts = []
    with open(args.test_file_src, 'r', encoding='utf-8') as f:
        for line in f:
            source_texts.append(line.strip())
            
    references = []
    with open(args.test_file_ref, 'r', encoding='utf-8') as f:
        for line in f:
            references.append(line.strip())
    
    # Sacrebleu expects a list of lists for references
    sacrebleu_references = [references]

    # --- 3. Generate Translations ---
    print("--- 3. Generating translations ---")
    predictions = []
    
    # Process in batches to manage memory
    for i in tqdm(range(0, len(source_texts), args.batch_size)):
        batch = source_texts[i:i + args.batch_size]
        
        # Must set source language before tokenization
        tokenizer.src_lang = args.src_lang_code
        inputs = tokenizer(batch, return_tensors="pt", padding=True, truncation=True, max_length=128).to(model.device)

        with torch.no_grad(): # Disable gradient calculation for inference
            generated_tokens = model.generate(
                **inputs,
                # Force the BOS token to be the target language code token
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(args.tgt_lang_code),
                max_new_tokens=128
            )
        
        # Set target language before decoding
        tokenizer.tgt_lang = args.tgt_lang_code
        with tokenizer.as_target_tokenizer():
            decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        
        predictions.extend(decoded_preds)
        
    # --- 4. Calculate and Print Metrics ---
    print("\n--- 4. Calculating metrics ---")

    # BLEU Score
    bleu = sacrebleu.corpus_bleu(predictions, sacrebleu_references)
    print(f"BLEU Score: {bleu.score:.2f}")

    # chrF++ Score
    chrf = sacrebleu.corpus_chrf(predictions, sacrebleu_references)
    print(f"chrF++ Score: {chrf.score:.2f}")

    # --- 5. Save Predicted Translations (MT File) ---
    mt_output_path = args.mt_output_path
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(mt_output_path), exist_ok=True) 
    with open(mt_output_path, 'w', encoding='utf-8') as f:
        for pred in predictions:
            f.write(pred + '\n')
    print(f"\n--- 5. Machine Translation (MT) predictions successfully saved to: {mt_output_path} ---")


    # COMET Score (Optional)
    try:
        from unbabel_comet import load_from_checkpoint
        print("Loading COMET model...")
        comet_model = load_from_checkpoint("wmt22-comet-da/checkpoints/model.ckpt")
        
        comet_data = []
        for src, mt, ref in zip(source_texts, predictions, references):
            comet_data.append({"src": src, "mt": mt, "ref": ref})

        # Calculate COMET score on GPU
        model_output = comet_model.predict(comet_data, batch_size=args.batch_size, gpus=1)
        
        print(f"COMET Score: {model_output.system_score:.4f}")
    except ImportError:
        print("\nCOMET not installed. Skipping. Install with: pip install unbabel-comet")
    except Exception as e:
        print(f"\nError calculating COMET score: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a fine-tuned NMT model and save predicted translations")

    # Model and Data Paths
    parser.add_argument("--base_model_name", type=str, default="facebook/nllb-200-distilled-600M", help="Name of the base pretrained model.")
    parser.add_argument("--lang", type=str, required=True, help="Language code of the trained model (e.g., 'sw').")
    parser.add_argument("--data_size", type=str, required=True, help="Data size identifier (e.g., '25k').")
    parser.add_argument("--test_file_src", type=str, required=True, help="Path to the source language test file.")
    parser.add_argument("--test_file_ref", type=str, required=True, help="Path to the reference language test file.")
    parser.add_argument("--model_path_base", type=str, default=None, help="Optional: Base path to the checkpoint directory (e.g., ./ur-25k-forward-finetune).")
    parser.add_argument("--mt_output_path", type=str, required=True, help="Path to save the generated Machine Translation (MT) text file.")
    
    # Language Codes
    parser.add_argument("--src_lang_code", type=str, required=True, help="NLLB source language code (e.g., 'eng_Latn').")
    parser.add_argument("--tgt_lang_code", type=str, required=True, help="NLLB target language code (e.g., 'urd_Arab').")
    
    # Inference Hyperparameters
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for evaluation.")

    args = parser.parse_args()
    
    # Basic check for CUDA availability before starting the main process
    if torch.cuda.is_available():
        main(args)
    else:
        print("CUDA devices not detected. Evaluation requires a GPU.")
