import re

file_path = "urd.txt"

total_entries = 0
total_features = 0
total_morphemes = 0
one_to_one_matches = 0

def estimate_morphemes(wordform):
    # 使用空格或连字符分割估算 morpheme 数量（适用于 Urdu 多词复合形式）
    return len(re.findall(r"[\w]+", wordform))

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) != 3:
            continue
        lemma, wordform, feats = parts
        feat_list = feats.split(";")
        morphemes = estimate_morphemes(wordform)

        total_entries += 1
        total_features += len(feat_list)
        total_morphemes += morphemes

        if len(feat_list) == morphemes:
            one_to_one_matches += 1

fusion_ratio = total_features / total_morphemes if total_morphemes > 0 else 0
agglutination_ratio = one_to_one_matches / total_entries if total_entries > 0 else 0

print(f"🔢 Total entries: {total_entries}")
print(f"🧩 Total features: {total_features}")
print(f"🧩 Total morphemes (estimated): {total_morphemes}")
print(f"✅ 1-to-1 matches: {one_to_one_matches}")
print(f"📊 Fusion ratio (features per morpheme): {fusion_ratio:.2f}")
print(f"📊 Agglutination indicator (1-to-1 match ratio): {agglutination_ratio:.2f}")
