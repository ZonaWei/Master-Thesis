import re

def estimate_morpheme_count(wordform):
    """
    粗略估算 morpheme 数量，用于粘合语言（Zulu）
    使用元音-辅音组合作为启发式分界
    """
    morphemes = re.findall(r'[aeiou]?[bcdfghjklmnpqrstvwxyz]*[aeiou]+|[^aeiou\s]+', wordform, flags=re.IGNORECASE)
    return max(1, len(morphemes))

def analyze_zulu_fusional_level(file_path):
    total_entries = 0
    total_features = 0
    total_morphemes = 0
    one_to_one_matches = 0

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) != 3:
                continue
            lemma, form, feats = parts
            features = feats.split(';')
            num_features = len(features)
            num_morphemes = estimate_morpheme_count(form)

            total_entries += 1
            total_features += num_features
            total_morphemes += num_morphemes

            if num_features == num_morphemes:
                one_to_one_matches += 1

    fusion_ratio = total_features / total_morphemes if total_morphemes else 0
    agglutination_ratio = one_to_one_matches / total_entries if total_entries else 0

    print(f"🔢 Total entries: {total_entries}")
    print(f"🧩 Total features: {total_features}")
    print(f"🧩 Estimated morphemes (heuristic): {total_morphemes}")
    print(f"✅ 1-to-1 matches: {one_to_one_matches}")
    print(f"📊 Fusion ratio (features per morpheme): {fusion_ratio:.2f}")
    print(f"📊 Agglutination indicator (1-to-1 match ratio): {agglutination_ratio:.2f}")

# 运行
if __name__ == "__main__":
    analyze_zulu_fusional_level("zul.txt")


