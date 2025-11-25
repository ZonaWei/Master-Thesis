#!/bin/bash
# ============================================================
# Run multilingual experiments for different dataset sizes.
# This script works with data organized as:
#   final_data2/<lang>/train_1k.tsv, train_5k.tsv, ..., validation.tsv
# ============================================================

# --------- Base data directory ---------
DATA_BASE_PATH="./final_data2"
# You can change this to "./final_data3" or another path if needed.

# --------- Training hyperparameters ---------
EPOCHS=5
BATCH_SIZE=8
LEARNING_RATE=5e-5

# --------- Language codes mapping (for FLORES or NLLB) ---------
declare -A SRC_CODES
SRC_CODES["sw"]="swh_Latn"   # Swahili
SRC_CODES["zu"]="zul_Latn"   # Zulu
SRC_CODES["am"]="amh_Ethi"   # Amharic
SRC_CODES["ur"]="urd_Arab"   # Urdu

# --------- Dataset sizes to loop over ---------
DATA_SIZES=("1k" "5k" "25k" "100k" "500k" "1M")

# --------- Output file to summarize all results ---------
RESULT_FILE="results_summary.txt"
echo "========== EXPERIMENT RESULTS ==========" > $RESULT_FILE

# ============================================================
# Main experiment loop
# ============================================================

for lang in "${!SRC_CODES[@]}"; do
    src_code=${SRC_CODES[$lang]}
    echo "========== Language: $lang ($src_code) ==========" | tee -a $RESULT_FILE

    for data_size in "${DATA_SIZES[@]}"; do
        echo "----- Training $lang $data_size -----" | tee -a $RESULT_FILE

        # ------------------- TRAIN -------------------
        python train.py \
            --lang $lang \
            --data_size $data_size \
            --src_lang_code $src_code \
            --data_dir ${DATA_BASE_PATH}/${lang}/train_${data_size}.tsv \
            --validation_file ${DATA_BASE_PATH}/${lang}/validation.tsv \
            --epochs $EPOCHS \
            --batch_size $BATCH_SIZE \
            --learning_rate $LEARNING_RATE

        echo "✅ Finished training ${lang}-${data_size}" | tee -a $RESULT_FILE

        # ------------------- EVALUATE -------------------
        echo "----- Evaluating $lang $data_size -----" | tee -a $RESULT_FILE

        python evaluate.py \
            --lang $lang \
            --data_size $data_size \
            --src_lang_code $src_code \
            --test_file_src ./test_data/flores200_${lang}.txt \
            --test_file_ref ./test_data/flores200_en.txt

        echo "✅ Finished evaluating ${lang}-${data_size}" | tee -a $RESULT_FILE
        echo "" | tee -a $RESULT_FILE
    done
done

echo "========== All Experiments Completed ✅ ==========" | tee -a $RESULT_FILE

