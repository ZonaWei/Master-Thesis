import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# === Step 1: Load the UniMorph file ===
with open("urd.txt", encoding="utf-8") as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# === Step 2: Parse into a DataFrame ===
data = [line.split("\t") for line in lines]
df = pd.DataFrame(data, columns=["lemma", "form", "features"])

# === Step 3: Count inflected forms and features per lemma ===
lemma_stats = defaultdict(lambda: {"n_forms": 0, "n_feats": 0})

for _, row in df.iterrows():
    lemma = row["lemma"]
    features = row["features"].split(";")
    lemma_stats[lemma]["n_forms"] += 1
    lemma_stats[lemma]["n_feats"] += len(features)

# === Step 4: Build a statistics table ===
stats_df = pd.DataFrame([
    {
        "lemma": lemma,
        "n_forms": stat["n_forms"],
        "n_feats": stat["n_feats"],
        "fusion_ratio": stat["n_feats"] / stat["n_forms"] if stat["n_forms"] > 0 else 0
    }
    for lemma, stat in lemma_stats.items()
])

# === Step 5: Print overall statistics ===
avg_forms = stats_df["n_forms"].mean()
avg_feats = stats_df["n_feats"].mean()
avg_fusion_ratio = stats_df["fusion_ratio"].mean()

print(f"🔢 Average number of inflected forms per lemma: {avg_forms:.2f}")
print(f"🔢 Average number of total features per lemma: {avg_feats:.2f}")
print(f"🔬 Average fusion ratio (features per form): {avg_fusion_ratio:.2f}")

# === Step 6: Plot distribution of fusion ratios ===
plt.hist(stats_df["fusion_ratio"], bins=30, edgecolor="black")
plt.title("Fusion Ratio Distribution (Features per Form)")
plt.xlabel("Features per Form")
plt.ylabel("Number of Lemmas")
plt.grid(True)
plt.savefig("urd_fusion_plot.png")

