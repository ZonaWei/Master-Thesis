import re

file_path = "amh.txt"

total_forms = 0
total_features = 0
total_morphemes = 0
perfect_matches = 0

def estimate_morphemes(word_form):
    """
    粗略地以非埃塞文字、标点、数字为分割符划分形态边界。
    可根据语言具体结构替换为更精确的规则（如 BPE 切分）。
    """
    # 将字符按简单规则划分（适用于字符边界很清晰的语言）
    return max(1, len(re.findall(r'[^\u1200-\u137F]+', word_form)) + 1)

with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or "\t" not in line:
            continue
        lemma, form, features = line.split("\t")
        feats = features.split(";")
        n_feats = len(feats)
        n_morphs = estimate_morphemes(form)

        total_forms += 1
        total_features += n_feats
        total_morphemes += n_morphs

        if n_feats == n_morphs:
            perfect_matches += 1

# 计算指标
fusion_ratio = total_features / total_morphemes if total_morphemes else 0
agglutination_score = perfect_matches / total_forms if total_forms else 0

# 输出结果
print(f"🔢 Total entries: {total_forms}")
print(f"🧩 Total features: {total_features}")
print(f"🧩 Total morphemes (estimated): {total_morphemes}")
print(f"✅ 1-to-1 matches: {perfect_matches}")
print(f"📊 Fusion ratio (features per morpheme): {fusion_ratio:.2f}")
print(f"📊 Agglutination indicator (1-to-1 match ratio): {agglutination_score:.2f}")
