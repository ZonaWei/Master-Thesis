import pandas as pd
import re

def estimate_morphemes(surface_form):
    # 简化估算：用大写字母边界（prefix变化）+元音-辅音切分估计
    # Zulu 中前缀通常紧凑连缀，例如: "ngifikile" ≈ ngi + fika + ile
    return len(re.findall(r'[aeiou]?[^aeiou\s]+', surface_form))

def analyze_fusion_ratio(file_path):
    morpheme_counts = []
    feature_counts = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue
            lemma, surface_form, features_str = parts
            features = features_str.split(";") if features_str else []
            feature_count = len(features)

            morpheme_count = estimate_morphemes(surface_form)

            morpheme_counts.append(morpheme_count)
            feature_counts.append(feature_count)

    df = pd.DataFrame({
        "morpheme_count": morpheme_counts,
        "feature_count": feature_counts,
    })

    df["one_to_one"] = df["morpheme_count"] == df["feature_count"]
    total = len(df)
    match_count = df["one_to_one"].sum()
    ratio = match_count / total if total > 0 else 0

    print(f"🔢 Total entries: {total}")
    print(f"✅ 1-to-1 matches: {match_count}")
    print(f"📊 Fusion indicator: {(1 - ratio):.2f} (higher = more fusional)")

    return df

# 用法：替换成你的 zul.args 文件路径
df = analyze_fusion_ratio("zul.txt")
