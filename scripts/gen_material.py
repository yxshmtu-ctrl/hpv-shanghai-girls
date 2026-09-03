#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_material.py — 生成 HPV 宣传物料文案（折页 / 海报 / 公众号推文）

从 config/policy.yaml 读政策口径，配 03-谣言库 常见疑虑要点，输出三种物料骨架。
用法：
  python scripts/gen_material.py flier          # 折页
  python scripts/gen_material.py poster         # 海报/易拉宝
  python scripts/gen_material.py article        # 公众号推文骨架
  python scripts/gen_material.py all -o out.md  # 全部写入一个 md
口径来自 config，改 config 即全局更新。

⚠️ 本脚本只生成文案骨架；配图/版式由使用者完成。非医疗建议。
"""

import sys, os, re, argparse

sys.stdout.reconfigure(encoding="utf-8")

CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "policy.yaml"
)
MYTH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "references",
    "03-谣言与反误区库.md",
)


def read_config():
    cfg = {}
    for ln in open(CONFIG, encoding="utf-8"):
        m = re.search(r"birth_after:\s*[\"']?([\d-]+)", ln)
        if m:
            cfg["birth"] = m.group(1)
        m = re.search(r"age_from:\s*(\d+)", ln)
        if m:
            cfg["age"] = m.group(1)
        m = re.search(r"vaccine_type:\s*[\"']?([^\s\"']+)", ln)
        if m:
            cfg["vaccine"] = m.group(1)
        m = re.search(r"doses:\s*(\d+)", ln)
        if m:
            cfg["doses"] = m.group(1)
        m = re.match(r"^\s{2}channel_primary:\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m:
            cfg["ch1"] = m.group(1).strip()
        m = re.search(r"hotline(_sh_health)?:\s*[\"']?([\d-]+)", ln)
        if m:
            cfg.setdefault("hot", []).append(m.group(2))
    return cfg


def myth_titles():
    t = []
    for ln in open(MYTH, encoding="utf-8"):
        m = re.match(r"^###\s*疑虑\d+：(.+)$", ln.strip())
        if m:
            raw = m.group(1).strip()
            s = raw.split("（")[0].strip().rstrip("？? ")
            # 主干太短则退回完整标题（去尾部问号），保证问题可读
            if len(s) < 6:
                s = raw.rstrip("？? ").strip()
            if len(s) > 22:
                s = s[:22] + "…"
            t.append(s)
    return t


def header(cfg):
    return (
        f"HPV 疫苗已纳入国家免疫规划：{cfg.get('birth')} 以后出生、"
        f"满 {cfg.get('age')} 周岁的女孩，可免费接种 {cfg.get('doses')} 剂次 {cfg.get('vaccine')}。"
    )


def build(cfg, myths):
    ch = cfg.get("ch1", "随申办/健康云 → 智慧接种")
    hot = " / ".join(dict.fromkeys(cfg.get("hot", [])))
    base = header(cfg)
    top_q = myths[:5] if myths else []

    flier = [
        "【HPV 免费接种 · 家长折页文案】",
        "",
        f"标题：{cfg.get('birth', '')}后出生的女孩，免费打 HPV！",
        "",
        base,
        "",
        "Q&A（印背面/下方）：",
    ]
    for i, q in enumerate(top_q, 1):
        flier.append(f"{i}. {q}？")
    flier += [
        "",
        f"预约：{ch}",
        f"咨询：{hot}",
        "",
        "详细问答见随申办/健康云「智慧接种」专区。",
    ]

    poster = [
        "【HPV 免费接种 · 海报/易拉宝文案】",
        "",
        "主标题：免费 2 针，守护她未来",
        "",
        "副题：" + base,
        "",
        "要点：",
        "· 13 岁左右打，抗体是 15 岁以上人群 2 倍",
        "· 预防 70% 以上宫颈癌相关型别（16/18）",
        "· 国家免疫规划疫苗，安全有保障",
        "",
        f"行动：{ch}",
        f"热线：{hot}",
    ]

    article = [
        "【HPV 免费接种 · 公众号推文骨架】",
        "",
        "标题候选：国家免费 HPV 疫苗开打！这 5 个问题家长最关心",
        "",
        "引言（2-3 句）：宫颈癌离我们不远……国家已把 HPV 疫苗纳入免费免疫规划……",
        "",
        "一、" + base,
        "",
        "二、为什么 13 岁打最好（抗体 2 倍 / 保护≥10 年 / 性行为前建立保护）",
        "",
        "三、常见疑虑快答：",
    ]
    for i, q in enumerate(top_q, 1):
        article.append(f"{i}. {q}？——详见疾控官方科普。")
    article += [
        "",
        f"四、预约方式：{ch}",
        "",
        f"五、咨询：{hot}",
        "",
        "结尾呼吁：请监护人及时带孩子接种，预防宫颈癌从一针开始。",
    ]

    return {
        "flier": "\n".join(flier),
        "poster": "\n".join(poster),
        "article": "\n".join(article),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "kind", nargs="?", default="all", choices=["flier", "poster", "article", "all"]
    )
    ap.add_argument("-o", "--out", default=None)
    a = ap.parse_args()

    cfg = read_config()
    myths = myth_titles()
    mats = build(cfg, myths)

    if a.kind == "all":
        out = "\n\n---\n\n".join(mats.values())
    else:
        out = mats[a.kind]
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(out)
        print("已生成：", a.out)
    else:
        print(out)


if __name__ == "__main__":
    main()
