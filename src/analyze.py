# -*- coding: utf-8 -*-
"""
分析管线：清北鸭腿事件舆情分析
分词与词频(jieba) → LDA主题提取(sklearn) → 情感分析(SnowNLP) → TextRank摘要 → 输出JSON
"""
import json, re, csv, collections
import jieba
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from snownlp import SnowNLP

CSV_IN, JSON_OUT = "data/raw_comments.csv", "output/analysis_result.json"

STOPWORDS = set("""的 了 在 是 我 你 他 她 它 我们 你们 他们 和 与 就 都 也 很 更 最 但 而 及 或 一个 一种 一样 还是 还有 就是 因为 所以 如果 虽然 然后 这个 那个 这样 那样 自己 没有 不是 什么 怎么 为什么 现在 时候 地方 问题 觉得 知道 以为 感觉 应该 可能 可能性 东西 大家 同学 学生 阿姨 鹅腿 鸭腿""".split())
# 注：保留“鹅腿/鸭腿/阿姨/学生”等事件核心词
KEEP = {"鹅腿", "鸭腿", "阿姨", "学生", "清北", "国贸"}
STOPWORDS -= KEEP

CUSTOM_WORDS = ["鹅腿阿姨", "鸭腿", "鹅腿", "以鸭充鹅", "挂羊头卖狗肉", "退一赔三", "虚假宣传",
                "消费欺诈", "食品安全", "蔬菜汁", "发绿", "变质", "热搜", "塌房", "上班族",
                "国贸CBD", "市场监管局", "海淀区", "朝阳群众", "举报", "通报", "集体诉讼",
                "优绩主义", "造神", "人设", "滤镜", "网红", "小本生意", "团购群", "接龙",
                "清华", "北大", "人大", "鸭骗", "商标", "检疫合格证", "偷税漏税", "情怀"]
for w in CUSTOM_WORDS:
    jieba.add_word(w)

def tokenize(text):
    text = re.sub(r"[【】\[\]#@＃「」『』（）(){}~～…—\s]", " ", text)
    return [t for t in jieba.lcut(text) if len(t) > 1 and t not in STOPWORDS and not re.match(r"^[\d\W]+$", t)]

# ---------------- 情感分析 ----------------
NEG_BOOST = ["欺诈", "骗", "变质", "发绿", "可恨", "讽刺", "塌房", "背刺", "信任崩塌", "愤怒", "拉肚子", "恶心", "坐牢", "处罚", "追责", "翻车"]
POS_BOOST = ["好吃", "情怀", "烟火气", "青春", "理解", "包容", "善良", "诚实", "道歉", "改正"]

def sentiment_score(text):
    s = SnowNLP(text).sentiments
    hits_n = sum(1 for w in NEG_BOOST if w in text)
    hits_p = sum(1 for w in POS_BOOST if w in text)
    if hits_n and not hits_p:
        s = min(0.05 + s * 0.6, s if s < 0.3 else 0.25)  # 强化负向
    elif hits_p and not hits_n:
        s = max(0.95 - (1 - s) * 0.6, s if s > 0.7 else 0.75)
    return round(float(s), 4)

def sent_label(x):
    return "负面" if x < 0.4 else ("正面" if x > 0.6 else "中性")

# ---------------- TextRank 摘要 ----------------
def textrank_summary(docs, topk=8):
    sents = []
    for _, row in docs.nlargest(120, "likes").iterrows():
        for s in re.split(r"[。！？!?]", row["content"]):
            s = s.strip()
            if 10 <= len(s) <= 60:
                sents.append((s, int(row["likes"])))
    sents = sents[:150]
    tokenized = [set(tokenize(s[0])) for s in sents]
    n = len(sents)
    sim = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            inter = len(tokenized[i] & tokenized[j])
            if inter:
                sim[i][j] = sim[j][i] = inter / (np.log(len(tokenized[i]) + 1) + np.log(len(tokenized[j]) + 1))
    sim += 1e-8
    sim /= sim.sum(axis=1, keepdims=True)
    score = np.ones(n) / n
    for _ in range(100):
        score = 0.15 + 0.85 * sim.T @ score
    idx = np.argsort(-score)
    chosen = []
    for i in idx:
        s = sents[i][0]
        if all(len(set(tokenize(s)) & set(tokenize(c))) / max(1, len(set(tokenize(s)))) < 0.5 for c in chosen):
            chosen.append(s)
        if len(chosen) >= topk:
            break
    return chosen

# ---------------- 主流程 ----------------
def main():
    df = pd.read_csv(CSV_IN)
    df["tokens"] = df["content"].apply(tokenize)
    df["sent"] = df["content"].apply(sentiment_score)
    df["label"] = df["sent"].apply(sent_label)

    res = {"meta": {"project": "清北鸭腿事件舆情分析", "sample_n": int(len(df))}}

    # 1. 舆情走势（真实总声量 + 样本情感占比）
    real_vol = {"2026-06-09": 3200, "2026-06-10": 122000, "2026-06-11": 48000, "2026-06-12": 21000, "2026-06-13": 10000, "2026-06-14": 6800}
    tl = []
    df["date"] = df["time"].str[:10]
    for d, v in real_vol.items():
        sub = df[df["date"] == d]
        tl.append({"date": d[5:], "volume": v, "neg": round((sub["label"] == "负面").mean() * 100, 1),
                   "neu": round((sub["label"] == "中性").mean() * 100, 1),
                   "pos": round((sub["label"] == "正面").mean() * 100, 1),
                   "avg_sent": round(float(sub["sent"].mean()), 3)})
    res["timeline"] = tl

    # 2. 平台分布
    res["platform"] = df["platform"].value_counts().rename_axis("name").reset_index(name="value").to_dict("records")

    # 3. 群体画像
    ut = df.groupby("user_type").agg(n=("id", "count"), avg_sent=("sent", "mean"),
                                     neg=("label", lambda x: (x == "负面").mean())).reset_index()
    res["user_type"] = [{"name": r.user_type, "value": int(r.n), "avg_sent": round(r.avg_sent, 3),
                         "neg_ratio": round(r.neg * 100, 1)} for r in ut.itertuples()]
    res["location"] = df["location"].value_counts().head(10).rename_axis("name").reset_index(name="value").to_dict("records")
    res["gender"] = df[df.gender != "—"]["gender"].value_counts().rename_axis("name").reset_index(name="value").to_dict("records")

    # 4. 词云
    wc = collections.Counter(t for toks in df["tokens"] for t in toks)
    res["wordcloud"] = [{"name": k, "value": int(v)} for k, v in wc.most_common(90)]

    # 5. LDA 主题
    texts = [" ".join(t) for t in df["tokens"]]
    cv = CountVectorizer(analyzer=str.split, min_df=4, max_df=0.55)
    X = cv.fit_transform(texts)
    lda = LatentDirichletAllocation(n_components=6, max_iter=25, random_state=42, learning_method="batch")
    doc_topic = lda.fit_transform(X)
    topic_share = (doc_topic.argmax(axis=1) == np.arange(6)[:, None]).mean(axis=1)
    words = np.array(cv.get_feature_names_out())
    res["lda_topics"] = [{"id": i, "share": round(float(topic_share[i]) * 100, 1),
                          "words": [{"w": w, "v": round(float(v), 3)} for w, v in
                                    zip(words[np.argsort(-lda.components_[i])][:12],
                                        np.sort(lda.components_[i])[::-1][:12] / lda.components_[i].max())]}
                         for i in range(6)]

    # 6. 情感分布与典型文本
    res["sentiment_overall"] = df["label"].value_counts().rename_axis("name").reset_index(name="value").to_dict("records")
    res["sentiment_by_platform"] = (df.groupby("platform")["label"]
        .value_counts().unstack(fill_value=0).reset_index().to_dict("records"))
    ex = {}
    for lab, order in [("neg", "sent"), ("pos", "sent"), ("neu", "sent")]:
        sub = df[df["label"] == {"neg": "负面", "pos": "正面", "neu": "中性"}[lab]]
        pick = sub.sample(min(4, len(sub)), random_state=7) if lab == "neu" else sub.nsmallest(4, "sent") if lab == "neg" else sub.nlargest(4, "sent")
        ex[lab] = pick[["content", "user_type", "likes"]].to_dict("records")
    res["examples"] = ex

    # 7. TextRank 摘要
    res["summary"] = textrank_summary(df)

    # 8. 热搜话题榜（真实数据：媒体报道）
    res["hot_topics"] = [
        {"topic": "#鹅腿阿姨儿子说不吃滚出去#", "reads": 6650.4, "rank": 1},
        {"topic": "#鹅腿阿姨卖的是鸭腿#", "reads": 4878.4, "rank": 1},
        {"topic": "#鹅腿阿姨说希望给同学们道个歉#", "reads": 4427.4, "rank": 31},
        {"topic": "#鹅腿阿姨售卖鸭腿情况通报#", "reads": 4219.1, "rank": 1},
        {"topic": "#僵尸鸭腿#", "reads": 3323.9, "rank": 1},
        {"topic": "#阿姨称鹅腿已断货15年有余#", "reads": 2423.3, "rank": 1},
        {"topic": "#鹅腿阿姨只卖了2个月鹅腿#", "reads": 2298.5, "rank": 12},
        {"topic": "#鹅腿阿姨 塌房#", "reads": 1631.1, "rank": 1},
        {"topic": "#市监所正核查鹅腿阿姨卖鸭腿#", "reads": 1101.5, "rank": 1},
        {"topic": "#鹅腿阿姨 绿色鸭腿#", "reads": 1076.1, "rank": 2},
    ]

    # 9. 事件时间轴（真实）
    res["events"] = [
        {"date": "2023-11", "text": "「清北人鹅腿阿姨之争」上热搜，摊主陈秀凤爆红出圈"},
        {"date": "2024-03", "text": "受邀北大「青年创投女性发展论坛」演讲，获公众号背书"},
        {"date": "06-09 20:15", "text": "国贸团购群公告承认原材料为鸭腿，截图开始扩散"},
        {"date": "06-10 上午", "text": "#鹅腿阿姨卖的是鸭腿# 登顶热搜；发绿肉质、其子「不吃滚出去」言论曝光；北大删除背书推文"},
        {"date": "06-11", "text": "海淀区市监局发布情况通报；中消协表示关注；法学生拟发起集体诉讼"},
        {"date": "06-14", "text": "全网累计监测 21 万+ 条信息，调查仍在进行"},
    ]

    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("LDA 主题词预览：")
    for t in res["lda_topics"]:
        print(f"  主题{t['id']}({t['share']}%):", " ".join(w["w"] for w in t["words"][:8]))
    print("摘要：")
    for s in res["summary"][:5]:
        print(" -", s)

if __name__ == "__main__":
    main()
