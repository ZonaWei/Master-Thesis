import os
import torch
import argparse
from datasets import load_dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, TaskType


def main(args):
    print("--- 1. Loading model and tokenizer ---")
    model_name = args.model_name
    quantization_config = BitsAndBytesConfig(load_in_8bit=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_name,
        quantization_config=quantization_config,
        device_map={"": 0}
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # --- 2. Configure LoRA (PEFT) ---
    print("--- 2. Configuring LoRA (PEFT) ---")
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.SEQ_2_SEQ_LM
    )
    model = get_peft_model(model, lora_config)
    print("Trainable parameters:")
    model.print_trainable_parameters()

    # --- 3. Load and Preprocess Data ---
    print(f"--- 3. Loading and preprocessing data for language: {args.lang} ---")
    data_folder = os.path.join(args.data_base_path, args.lang)
    train_file = os.path.join(data_folder, f"train_{args.data_size}.tsv")
    validation_file = os.path.join(data_folder, "validation.tsv")

    if not os.path.exists(train_file):
        train_file_alt = os.path.join(data_folder, "train.tsv")
        if os.path.exists(train_file_alt):
            train_file = train_file_alt
        else:
            raise FileNotFoundError(f"Training file not found: {train_file}")

    if not os.path.exists(validation_file):
        raise FileNotFoundError(f"Validation file not found: {validation_file}")

    print(f"Using training file: {train_file}")
    print(f"Using validation file: {validation_file}")

    data_files = {"train": train_file, "validation": validation_file}
    dataset = load_dataset("csv", data_files=data_files, delimiter="\t", column_names=["source", "target"])

    def preprocess_function(examples):
        tokenizer.src_lang = args.src_lang_code
        tokenizer.tgt_lang = args.tgt_lang_code
        inputs = [ex for ex in examples["source"]]
        targets = [ex for ex in examples["target"]]
        return tokenizer(inputs, text_target=targets, max_length=128, truncation=True)

    print("--- Applying preprocessing ---")
    tokenized_datasets = dataset.map(preprocess_function, batched=True, num_proc=1)

    # --- 4. Training Arguments ---
    print("--- 4. Configuring training arguments ---")
    output_dir = f"./{args.lang}-{args.data_size}-finetune"
    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size * 2,
        gradient_accumulation_steps=args.accumulation_steps,
        predict_with_generate=True,
        learning_rate=args.learning_rate,
        num_train_epochs=args.epochs,
        bf16=True,
        logging_steps=20,
        eval_steps=args.eval_steps,
        save_total_limit=2,

        # ✅ New settings
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="bleu",  # you can adjust this to your eval metric
        greater_is_better=True,
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    # --- 5. Trainer ---
    print("--- 5. Initializing Trainer and starting training ---")
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["validation"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train()

    print("--- 6. Training complete ---")
    print(f"Checkpoints saved under {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune an NMT model with LoRA")
    parser.add_argument("--model_name", type=str, default="facebook/nllb-200-distilled-600M")
    parser.add_argument("--data_base_path", type=str, default="./final_data2")
    parser.add_argument("--lang", type=str, required=True)
    parser.add_argument("--data_size", type=str, required=True)
    parser.add_argument("--src_lang_code", type=str, required=True)
    parser.add_argument("--tgt_lang_code", type=str, default="eng_Latn")

    # ✅ Increased from 3 → 5 epochs
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")

    parser.add_argument("--batch_size", type=int, default=2)
    parser.add_argument("--accumulation_steps", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=2e-4)
    parser.add_argument("--eval_steps", type=int, default=500)
    args = parser.parse_args()

    main(args)
