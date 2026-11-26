#!/usr/bin/env python3
"""Select stylistically relevant user-authored blog articles from bundled corpus.

This script does NOT validate factual currency of the source articles.
"""
import argparse
import math
import re
from collections import Counter
from pathlib import Path

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "references" / "stock-articles.md"
WORD_RE = re.compile(r"[가-힣]+|[A-Za-z]+|[0-9]+")
PARTICLES = ("으로부터", "으로는", "으로도", "에서는", "에게서", "이라면", "에서", "에게", "으로", "부터", "까지", "보다", "에게", "처럼", "만큼", "라도", "하고", "와", "과", "은", "는", "이", "가", "을", "를", "의", "도", "만", "로")
HEADING_RE = re.compile(r"(?m)^#\s+(.+?)\s*$")
STOP = {"이", "그", "에", "의", "하는", "대해서", "그리고", "방법", "알아보기", "있을까", "것", "수", "왜", "이런", "관련", "2026", "2027"}
MODE = {
    "issue": ["주가", "전망", "실적", "사태", "이슈", "논란", "하락", "급락", "발표", "사임", "관련주", "매출"],
    "explain": ["뜻", "의미", "용어", "사용법", "쉽게", "초딩", "설명", "세금", "세율", "조건", "특징"],
    "compare": ["비교", "장점", "단점", "차이", "vs", "무얼", "선택"],
    "howto": ["방법", "개설", "시작", "후기", "신청", "실제로", "계좌", "설치"],
}


def tokenize(text):
    out = []
    for match in WORD_RE.findall(text):
        word = match.lower()
        if len(word) < 2 or word in STOP:
            continue
        out.append(word)
        if re.search(r"[가-힣]", word):
            for particle in PARTICLES:
                if word.endswith(particle) and len(word) > len(particle) + 1:
                    root = word[:-len(particle)]
                    if root not in STOP:
                        out.append(root)
                    break
    return out


def read_articles(path):
    text = path.read_text(encoding="utf-8-sig")
    headings = list(HEADING_RE.finditer(text))
    out = []
    for idx, item in enumerate(headings):
        title = item.group(1).strip()
        end = headings[idx + 1].start() if idx + 1 < len(headings) else len(text)
        body = text[item.end():end].strip()
        if not body:
            continue
        out.append((title, body))
    return out


def rank(articles, query, mode="auto"):
    q = set(tokenize(query))
    if not q:
        raise ValueError("query contains no searchable tokens")
    doc_terms = []
    df = Counter()
    for title, body in articles:
        title_tokens = set(tokenize(title))
        body_tokens = set(tokenize(body[:9000]))
        doc_terms.append((title_tokens, body_tokens))
        df.update(title_tokens | body_tokens)
    modes = list(MODE) if mode == "auto" else [mode]
    mode_tokens = set(MODE[mode]) if mode != "auto" else set()
    scores = []
    for i, (title, body) in enumerate(articles):
        tt, bt = doc_terms[i]
        score = 0.0
        for token in q:
            idf = math.log(1 + (len(articles) + 1) / (df[token] + 1))
            if token in tt:
                score += 6.0 + 2.0 * idf
            elif token in bt:
                score += 1.0 + idf
        if mode_tokens:
            score += 0.3 * len(tt & mode_tokens)
        # Boost exact company/topic phrase and matches in the lead.
        for phrase in re.findall(r"[가-힣A-Za-z0-9]{3,}", query):
            if phrase.lower() in title.lower():
                score += 2.0
        score += 0.3 * len(q & set(tokenize(body[:550])))
        scores.append((score, i))
    return [(round(score, 2), articles[idx]) for score, idx in sorted(scores, reverse=True) if score > 0]


def main():
    parser = argparse.ArgumentParser(description="Retrieve relevant writing samples from the bundled article corpus")
    parser.add_argument("--query", required=True, help="Korean keyword and topic prompt")
    parser.add_argument("--mode", choices=["auto", *MODE], default="auto")
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=4800, help="max output chars per selected sample")
    parser.add_argument("--titles-only", action="store_true")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    args = parser.parse_args()
    if args.top < 1 or args.top > 10:
        parser.error("--top must be 1..10")
    if args.max_chars < 100:
        parser.error("--max-chars must be at least 100")
    articles = read_articles(args.corpus)
    if not articles:
        parser.error("no articles found; inspect corpus headings")
    matches = rank(articles, args.query, args.mode)
    print(f"# 문체 참고 글 {min(args.top,len(matches))}편 (전체 {len(articles)}편)\n")
    print("주의: 과거 글은 문체 참고용이며 현재 사실관계를 보증하지 않습니다.\n")
    for n, (score, (title, body)) in enumerate(matches[:args.top], 1):
        print(f"## [{n}] {title} (유사도 {score})")
        if not args.titles_only:
            if len(body) > args.max_chars:
                body = body[:args.max_chars].rsplit("\n", 1)[0] + "\n[참고 글 일부 생략]"
            print(body)
        print()


if __name__ == "__main__":
    main()
