# -*- coding: utf-8 -*-
"""
真实微博数据采集脚本（升级用）
=================================
当前沙箱环境微博搜索接口需登录态，故使用 generate_corpus.py 的半真实语料。
如需接入实时真实数据：
  1. 浏览器登录 weibo.com → F12 → 复制 Cookie 填入下方 COOKIE；
  2. 运行本脚本（python spider_weibo.py）；
  3. 输出 data/raw_comments.csv（字段与模拟语料完全一致），
     然后依次运行 analyze.py → build_report.py 即可，下游代码无需改动。
"""
import csv, re, time, random
import requests

COOKIE = ""  # ← 粘贴你的微博 Cookie
KEYWORD = "鹅腿阿姨 鸭腿"          # 检索词（可换 #鹅腿阿姨卖的是鸭腿#）
MAX_PAGE = 50                      # 每个接口最多翻页数

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
    "Referer": "https://m.weibo.cn/",
}

def fetch_search():
    """综合搜索：m.weibo.cn 容器接口，需 Cookie"""
    out = []
    for page in range(1, MAX_PAGE + 1):
        url = "https://m.weibo.cn/api/container/getIndex"
        params = {"containerid": f'100103type=1&q={KEYWORD}&page_type=searchall', "page": page}
        try:
            data = requests.get(url, params=params, headers=HEADERS, cookies=_parse_cookie(),
                                timeout=10).json()
        except Exception as e:
            print("page", page, "failed:", e); break
        cards = data.get("data", {}).get("cards", [])
        if not cards:
            break
        for card in cards:
            for mb in card.get("card_group", [card]):
                weibo = mb.get("mblog")
                if weibo and "鸭" in weibo.get("text", "") + KEYWORD:
                    out.append(_parse_weibo(weibo))
        time.sleep(random.uniform(2, 4))  # 反爬限速
    return out

def fetch_comments(mid, max_page=10):
    """抓取某条微博下的评论（二次传播的网民声音）"""
    out = []
    for page in range(1, max_page + 1):
        url = "https://m.weibo.cn/api/comments/show"
        params = {"id": mid, "page": page, "mid": mid}
        try:
            data = requests.get(url, params=params, headers=HEADERS, cookies=_parse_cookie(),
                                timeout=10).json()
        except Exception:
            break
        for c in data.get("data", {}).get("data", []):
            text = re.sub(r"<[^>]+>", "", c.get("text", ""))
            if text:
                out.append({"time": c.get("created_at", ""), "content": text,
                            "user_type": _infer_type(c.get("user", {}).get("description", "")),
                            "location": (c.get("user", {}).get("location") or "其他").split(" ")[0],
                            "reposts": 0, "comments": c.get("comments_count", 0),
                            "likes": c.get("like_count", 0)})
        time.sleep(random.uniform(1.5, 3))
    return out

def _parse_weibo(weibo):
    text = re.sub(r"<[^>]+>", "", weibo.get("text", ""))
    return {"time": weibo.get("created_at", ""), "content": text,
            "user_type": _infer_type(weibo.get("user", {}).get("description", "")),
            "location": (weibo.get("user", {}).get("location") or "其他").split(" ")[0],
            "reposts": weibo.get("reposts_count", 0), "comments": weibo.get("comments_count", 0),
            "likes": weibo.get("attitudes_count", 0)}

def _infer_type(desc):
    if any(k in desc for k in ["律师", "法官", "法学"]): return "法律/时评博主"
    if any(k in desc for k in ["美食", "探店", "吃"]): return "美食探店博主"
    if "媒体" in desc or "新闻" in desc: return "媒体蓝V(新华社/澎湃等)"
    return "普通路人网友"

def _parse_cookie():
    return dict(kv.split("=", 1) for kv in COOKIE.split("; ") if "=" in kv)

def main():
    if not COOKIE:
        print("⚠️ 请先填写 COOKIE 后再运行真实采集；当前可先用 generate_corpus.py 的演示语料。")
        return
    posts = fetch_search()
    rows = list(posts)
    for p in posts[:20]:  # 对热帖抓取评论
        mid = re.search(r"id=(\d+)", str(p)) or None
        rows += fetch_comments(mid.group(1)) if mid else []
    with open("data/raw_comments.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["id", "time", "platform", "user_type", "gender",
                                          "location", "stance", "real_quote", "content", "reposts", "comments", "likes"])
        w.writeheader()
        for i, r in enumerate(rows):
            r.update(id=f"R{i:05d}", platform="微博", gender="—", stance="—", real_quote="yes")
            w.writerow(r)
    print(f"✅ 采集完成，共 {len(rows)} 条 → data/raw_comments.csv")

if __name__ == "__main__":
    main()
