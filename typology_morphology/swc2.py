import pandas as pd

def analyze_fusion_corrected(args_path):
    feature_counts = []

    with open(args_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue
            _, _, features_str = parts
            feature_count = len(features_str.split(";"))
            feature_counts.append(feature_count)

    df = pd.DataFrame({
        "feature_count": feature_counts,
    })

    agglutinative_like = (df["feature_count"] >= 3).sum()
    ratio = agglutinative_like / len(df)

    print(f"🔢 Total entries: {len(df)}")
    print(f"✅ Entries with ≥3 features: {agglutinative_like}")
    print(f"📊 Agglutination proxy ratio: {ratio:.2f} (higher = more agglutinative)")

    return df

# 运行：
df_swc = analyze_fusion_corrected("swc.txt")


