import re

def is_valid_line(line):
    return line.count('\t') == 2 and ';' in line

def count_morphemes(form):
    """
    基于形态变化后的形式（inflected form）估算词素数量。
    Swahili 多为前缀变化，我们简单用元音和辅音交替 + 分词特征估算。
    这里采用最保守做法：按词根变化位置简单用子串数量估计。
    """
    # 可以自行替换为更复杂的切分规则
    return max(1, len(re.findall(r'[aeiou]?[^aeiou\s]+', form)))

def count_features(feat_str):
    return len(feat_str.strip().split(';'))

total_entries = 0
total_morphemes = 0
total_features = 0
ratios = []

with open("swc.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not is_valid_line(line):
            continue

        lemma, form, feats = line.split('\t')
        morpheme_count = count_morphemes(form)
        feature_count = count_features(feats)

        # 跳过无效样本
        if morpheme_count == 0 or feature_count == 0:
            continue

        ratio = feature_count / morpheme_count
        ratios.append(ratio)
        total_entries += 1
        total_morphemes += morpheme_count
        total_features += feature_count

# 输出融合度统计
avg_ratio = total_features / total_morphemes if total_morphemes else 0
print(f"🔢 Total entries: {total_entries}")
print(f"🔣 Total morphemes: {total_morphemes}")
print(f"🧬 Total features: {total_features}")
print(f"📊 Average fusion ratio (features per morpheme): {avg_ratio:.2f}")
