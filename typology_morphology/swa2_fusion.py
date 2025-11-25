def count_morphemes(word: str) -> int:
    """
    粗略估算 Swahili 词形中的黏着词素数量
    方法：每次元音+辅音交替段记为一个 morpheme（非常粗糙）
    更好的做法应结合规则（ni-, ku-, -a等）构建前缀词典
    """
    import re
    # 尝试根据小写连写分段、元音-辅音切分
    word = re.sub(r"[^a-z]", "", word.lower())  # 清理非字母
    segments = re.split(r'(?<=[aeiou])(?=[bcdfghjklmnpqrstvwxyz])', word)
    return max(1, len(segments))


def main():
    input_path = "swc.txt"

    total_entries = 0
    total_features = 0
    total_morphemes = 0
    one_to_one_matches = 0

    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 3:
                continue
            lemma, form, feats = parts
            feat_list = feats.split(";")
            feature_count = len(feat_list)

            morpheme_count = count_morphemes(form)
            total_entries += 1
            total_features += feature_count
            total_morphemes += morpheme_count

            if feature_count == morpheme_count:
                one_to_one_matches += 1

    print(f"🔢 Total entries: {total_entries}")
    print(f"🔣 Estimated morphemes: {total_morphemes}")
    print(f"🧬 Total features: {total_features}")
    print(f"✅ 1-to-1 matches: {one_to_one_matches}")
    print(f"📊 Fusion ratio (features per morpheme): {total_features / total_morphemes:.2f}")
    print(f"📊 Agglutination indicator (1-to-1 match ratio): {one_to_one_matches / total_entries:.2f}")


if __name__ == "__main__":
    main()

