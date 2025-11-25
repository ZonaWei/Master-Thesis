import pandas as pd
import numpy as np
import re
import random

# ========== Input File Path ==========
paths = {
    "Amharic": "amharic_inflection_table.csv",
    "Swahili": "swahili_inflection_table.csv",
    "Urdu": "urdu_inflection_table.csv",
    "Zulu": "zulu_inflection_table.csv",
}

# ========== Basic parameters ==========
POS_TAGS = {"N", "V", "ADJ", "AUX", "PRON", "DET", "NUM", "ADV", "PART",
            "ADP", "CCONJ", "SCONJ", "INTJ", "PROPN"}

# List of Bantu Languages
BANTU_LANGS = {"Swahili", "Zulu"}

# Common Zulu prefixes
ZULU_PREFIXES = [
    "ngi", "u", "si", "ni", "li", "ba", "lu", "ku", "m", "wa",
    "nga", "ma", "ka", "za", "yi", "le", "se"
]

# Swahili Extended Prefix Table
SWAHILI_PREFIXES = [
    "ni", "u", "a", "tu", "m", "wa", "si",
    "ni", "ku", "m", "wa", "tu", "ki", "vi", "li", "zi", "pa", "mu",
    "na", "ta", "li", "me", "ka", "ki", "nge", "ngali", "hu", "ha"
]

# ---- helper: greedy longest-first prefix stripping ----
def greedy_prefix_count(word, pref_list):
    """
    Return (count, matched_any) where count is the number of prefixes stripped
    using a greedy, longest-first, iterative scan. Lowercases the word.
    """
    w = str(word).lower()
    # unique prefixes, longest-first to avoid partial shadowing
    prefs = sorted(set(pref_list), key=len, reverse=True)
    count = 0
    matched_any = False
    while True:
        matched = False
        for p in prefs:
            if w.startswith(p):
                w = w[len(p):]
                count += 1
                matched = True
                matched_any = True
                break  # restart from the longest prefix again
        if not matched:
            break
    return count, matched_any


# ========== Feature Count ==========
def count_features(feature_str, language=None):
    if pd.isna(feature_str) or feature_str == "":
        return 0
    # UniMorph conventionally uses ';' as delimiter
    feats = [f.strip() for f in str(feature_str).split(";") if f.strip()]
    # remove POS-category labels and implementation-specific tags
    feats = [f for f in feats if f not in POS_TAGS and not f.startswith("LGSPEC")]
    # collapse BANTU* tags to a single AGR feature for Bantu languages
    if language in BANTU_LANGS:
        if any(f.startswith("BANTU") for f in feats):
            feats = [f for f in feats if not f.startswith("BANTU")]
            feats.append("BANTU")
    return len(feats)

# ========== Morpheme Count Estimation ==========
def approx_morphemes(form, language=None):
    if pd.isna(form):
        return 0
    s = str(form).strip()
    if not s or " " in s:
        return 0
    
    morphs = re.split(r"[+\-–—'’]+", s)
    morphs = [m for m in morphs if m]
    
    if language == "Swahili":
        word = s.lower()
        prefix_count = 0
        for pref in SWAHILI_PREFIXES:
            if word.startswith(pref):
                prefix_count += 1
                word = word[len(pref):]
        return prefix_count + 1 if prefix_count > 0 else len(morphs)
    
    if language == "Zulu":
        word = s.lower()
        prefix_count = 0
        for pref in ZULU_PREFIXES:
            if word.startswith(pref):
                prefix_count += 1
                word = word[len(pref):]
        return prefix_count + 1 if prefix_count > 0 else len(morphs)
    
    return len(morphs) if morphs else 1

# ========== bootstrap confidence interval ==========
def bootstrap_ci(data, n_iter=1000, ci=95):
    data = [d for d in data if d is not None]
    if not data:
        return (None, None)
    means = []
    for _ in range(n_iter):
        sample = random.choices(data, k=len(data))
        means.append(np.mean(sample))
    lower = np.percentile(means, (100-ci)/2)
    upper = np.percentile(means, 100 - (100-ci)/2)
    return round(lower,3), round(upper,3)

# ========== Main Computation Loop ==========
results = []
for lang, path in paths.items():
    try:
        df = pd.read_csv(path)
    except:
        df = pd.read_csv(path, sep="\t")
    
    # compute per-item features & morphemes
    df["feature_count"] = df["Features"].apply(lambda x: count_features(x, lang))
    df["morpheme_count"] = df["InflectedForm"].apply(lambda x: approx_morphemes(x, lang))

    # drop unusable rows (spaces/missing → 0 were already encoded)
    df = df[(df["morpheme_count"] > 0) & (df["feature_count"] > 0)]

    # fusion proxy per item
    df["fusion_ratio_item"] = df["feature_count"] / df["morpheme_count"]
    fusion_mean = df["fusion_ratio_item"].mean()

    # agglutination indicator per item
    if lang in BANTU_LANGS:
        aggl_series = (abs(df["feature_count"] - df["morpheme_count"]) <= 1).astype(int)
    else:
        aggl_series = (df["feature_count"] == df["morpheme_count"]).astype(int)

    agglutination = aggl_series.mean()

    # CIs
    ci_fusion = bootstrap_ci(df["fusion_ratio_item"].tolist())
    ci_aggl = bootstrap_ci(aggl_series.tolist())

    results.append({
        "Language": lang,
        "FusionRatio_mean": round(fusion_mean, 3),
        "FusionRatio_CI": ci_fusion,
        "Agglutination_mean": round(agglutination, 3),
        "Agglutination_CI": ci_aggl,
        "N": len(df)
    })

summary_df = pd.DataFrame(results).sort_values("Language")
print(summary_df)
