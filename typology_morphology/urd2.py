import pandas as pd

def count_morphemes(form):
    # Urdu 中很多形态特征由助动词表达，如 "اترا تھا" 有两个子词
    return len(form.strip().split())

def analyze_urdu_fusion(args_path):
    morpheme_counts = []
    feature_counts = []

    with open(args_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue
            lemma, form, features_str = parts
            morpheme_count = count_morphemes(form)
            feature_count = len(features_str.split(";"))

            morpheme_counts.append(morpheme_count)
            feature_counts.append(feature_count)

    df = pd.DataFrame({
        "morpheme_count": morpheme_counts,
        "feature_count": feature_counts,
    })

    df["one_to_one"] = df["morpheme_count"] == df["feature_count"]
    ratio = df["one_to_one"].sum() / len(df)

    print(f"🔢 Total entries: {len(df)}")
    print(f"✅ 1-to-1 matches: {df['one_to_one'].sum()}")
    print(f"📊 Fusion indicator: {(1 - ratio):.2f} (higher = more fusional)")

    return df

# 用法：替换成你的 urd.args 文件路径
df_urdu = analyze_urdu_fusion("urd.txt")

