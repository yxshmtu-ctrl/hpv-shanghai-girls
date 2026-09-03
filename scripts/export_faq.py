#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export_faq.py — 把 03-谣言库(12条疑虑) 导出为问答机器人知识包

从 references/03-谣言与反误区库.md 解析每条「疑虑N：问题 / 应答 / 一句话」，
输出两种格式供下游使用：
  - --json out.json  结构化 [{q, short_ans, source, tags}]
  - --md   out.md   公众号/FAQ 平铺问答（可直接粘贴）
  - 缺省打印 JSON 到终端

适用：把技能知识接入公众号/群机器人/网页 FAQ。

用法：
  python scripts/export_faq.py --json faq.json
  python scripts/export_faq.py --md faq.md
"""

import sys, os, re, json, argparse

sys.stdout.reconfigure(encoding="utf-8")

REF = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "references",
    "03-谣言与反误区库.md",
)


def parse():
    """解析谣言库：返回 [ {no, title, has_source, has_consensus, lines} ]"""
    txt = open(REF, encoding="utf-8").read()
    items = []
    cur = None
    for ln in txt.split("\n"):
        m = re.match(r"^###\s*疑虑(\d+)：(.+)$", ln.strip())
        if m:
            cur = {
                "no": int(m.group(1)),
                "title": m.group(2).strip(),
                "source": None,
                "one_liner": None,
                "body": [],
            }
            items.append(cur)
            continue
        if cur is None:
            continue
        s = ln.strip()
        if not s:
            continue
        if s.startswith("- 【原文有据】"):
            cur["source"] = "官方科普"
            cur["body"].append(s[len("- 【原文有据】") :].strip())
        elif s.startswith("- 【通用共识】"):
            cur["source"] = cur["source"] or "通用共识"
            cur["body"].append(s[len("- 【通用共识】") :].strip())
        elif s.startswith("- 一句话"):
            cur["one_liner"] = s[len("- 一句话") :].lstrip("：:").strip()
        elif (
            s.startswith("- 实操")
            or s.startswith("- 关键")
            or s.startswith("- 再给")
            or s.startswith("- 接种")
            or s.startswith("- ")
        ):
            cur["body"].append(s[2:].strip())
        elif re.match(r"^1\.|^2\.|^3\.|^4\.", s):
            cur["body"].append(s.strip())
    return items


def _clean(s):
    return s.replace("**", "").replace("`", "")


def to_qa(items):
    out = []
    for it in items:
        q = it["title"]
        a_lines = [_clean(x) for x in it["body"]]
        if it["one_liner"]:
            a_lines.append("一句话：" + _clean(it["one_liner"]))
        answer = "\n".join(a_lines)
        if not answer:
            answer = "（本条为补充说明，建议引用谣言库原文）"
        out.append(
            {
                "q": _clean(q),
                "short_q": q.split("（")[0].strip(),
                "a": answer,
                "source": it["source"] or "见官方口径",
                "tags": ["hpv", "shanghai", "faq"],
                "id": it["no"],
            }
        )
    return out


def main():
    ap = argparse.ArgumentParser(description="导出 FAQ 问答知识包")
    ap.add_argument("--json", dest="jout", default=None)
    ap.add_argument("--md", dest="mout", default=None)
    a = ap.parse_args()

    items = parse()
    qa = to_qa(items)
    if not qa:
        sys.exit("未解析到疑虑条目，请检查 03-谣言库 格式。")

    if a.mout:
        lines = ["# HPV 接种 FAQ（由 hpv-shanghai-girls 谣言库导出）", ""]
        for it in qa:
            lines.append(f"## Q{it['id']} {it['q']}")
            lines.append("")
            lines.append(it["a"])
            lines.append("")
            lines.append(f"（依据：{it['source']}）")
            lines.append("")
        with open(a.mout, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"已生成 FAQ(md)：{a.mout}（{len(qa)}条）")
    else:
        data = json.dumps(qa, ensure_ascii=False, indent=2)
        if a.jout:
            with open(a.jout, "w", encoding="utf-8") as f:
                f.write(data)
            print(f"已生成 FAQ(json)：{a.jout}（{len(qa)}条）")
        else:
            print(data)


if __name__ == "__main__":
    main()
