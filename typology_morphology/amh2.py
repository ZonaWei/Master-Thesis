import pandas as pd
import re

def analyze_fusion_ratio(file_path):
    morpheme_counts = []
    feature_counts = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue  # 跳过格式不正确的行
            lemma, surface_form, features_str = parts
            features = features_str.split(";") if features_str else []
            feature_count = len(features)

            # 估计 morpheme 数：以+或标点切分
            morpheme_candidates = re.split(r'[+\-]', surface_form)
            morpheme_count = len([m for m in morpheme_candidates if m.strip() != ""])

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

# 使用方法（将文件名替换成你的实际路径）
df = analyze_fusion_ratio("amh.txt")
