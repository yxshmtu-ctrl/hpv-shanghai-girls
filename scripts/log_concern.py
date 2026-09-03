#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""log_concern.py — 效果统计：登记门诊/家长遇到的疑虑

目的：把推广过程中遇到的新疑虑/家长反馈沉淀下来，供后续补入 03-谣言库。
用法：
  python scripts/log_concern.py add --q "孩子爸爸说打这个没用" --ctx 家长会 --by 王校医
      # 若该问题已命中 03-谣言库某条 → 提示已有条目（可 --force 仍记录）
      # 否则写入 concerns.csv（status=pending）
  python scripts/log_concern.py list [--pending] [--no N]
  python scripts/log_concern.py mark --no N        # 标记第N条已沉淀入谣言库(status=done)
  python scripts/log_concern.py stats              # 汇总：总量/未沉淀/最常见关键词
日志：<技能>/logs/concerns.csv（UTF-8-sig，可用 Excel 打开）
⚠️ 日志可能含咨询内容，仅限授权环境；导出分享前注意脱敏。
"""

import sys, os, re, csv, argparse, datetime

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(HERE, "..", "logs")
CSV = os.path.join(LOGS, "concerns.csv")
MYTH = os.path.join(HERE, "..", "references", "03-谣言与反误区库.md")
FIELDS = ["no", "datetime", "question", "context", "by", "matched", "status"]


def myth_titles():
    """返回 {序号: 疑虑标题}"""
    out = {}
    for ln in open(MYTH, encoding="utf-8"):
        m = re.match(r"^###\s*疑虑(\d+)：(.+)$", ln.strip())
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def match_title(q, titles):
    """关键词命中：标题与问题的公共字符足够多或标题关键词在问题中。返回序号或 None。"""
    best, best_score = None, 0
    for no, t in titles.items():
        # 去括号注后取主干关键词比对
        core = t.split("（")[0].strip()
        # 计算重叠：取标题去掉标点后的词在问题里出现比例
        chars = set(re.sub(r"[，。？？、/ ]", "", core))
        if not chars:
            continue
        qset = set(re.sub(r"[，。？？、/ ]", "", q))
        score = len(chars & qset) / len(chars)
        if score > best_score:
            best_score, best = score, no
    return best if best_score >= 0.5 else None


def ensure_csv():
    os.makedirs(LOGS, exist_ok=True)
    if not os.path.exists(CSV):
        with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writeheader()


def read_rows():
    ensure_csv()
    with open(CSV, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_rows(rows):
    ensure_csv()
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="家长疑虑登记/统计")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--q", required=True)
    a.add_argument("--ctx", default="")
    a.add_argument("--by", default="")
    a.add_argument("--force", action="store_true", help="命中已有条目仍记录")
    b = sub.add_parser("list")
    b.add_argument("--pending", action="store_true")
    c = sub.add_parser("mark")
    c.add_argument("--no", type=int, required=True)
    s = sub.add_parser("stats")
    args = ap.parse_args()

    titles = myth_titles()

    if args.cmd == "add":
        rows = read_rows()
        no = (max([int(r["no"]) for r in rows], default=0)) + 1
        hit = match_title(args.q, titles)
        if hit and not args.force:
            print(f"提示：此疑虑与 03-谣言库『疑虑{hit}』高度相似，建议先引用该条。")
            print(f"  如需仍登记请加 --force")
            sys.exit(0)
        rows.append(
            {
                "no": no,
                "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "question": args.q,
                "context": args.ctx,
                "by": args.by,
                "matched": f"疑虑{hit}" if hit else "",
                "status": "done" if hit else "pending",
            }
        )
        write_rows(rows)
        print(f"已登记 #{no}：{args.q}")
        if not hit:
            print(
                "状态=pending：建议整理后补入 references/03-谣言与反误区库.md 新疑虑条目。"
            )
        else:
            print("状态=done（命中已有条目，仅记录发生频次）。")

    elif args.cmd == "list":
        rows = read_rows()
        for r in rows:
            if args.pending and r["status"] != "pending":
                continue
            print(
                f"#{r['no']} [{r['datetime']}] {r['question']} | ctx:{r['context']} | 匹配:{r['matched'] or '-'} | {r['status']}"
            )
        if not rows:
            print("（暂无记录）")

    elif args.cmd == "mark":
        rows = read_rows()
        for r in rows:
            if int(r["no"]) == args.no:
                r["status"] = "done"
                print(f"#{args.no} 已标记为 done（已沉淀入谣言库）")
                break
        else:
            sys.exit(f"未找到 #{args.no}")
        write_rows(rows)

    elif args.cmd == "stats":
        rows = read_rows()
        pend = sum(1 for r in rows if r["status"] == "pending")
        print(
            f"总登记：{len(rows)}  未沉淀(pending)：{pend}  已沉淀(done)：{len(rows) - pend}"
        )
        if rows:
            from collections import Counter

            c = Counter()
            for r in rows:
                for ch in r["question"]:
                    if ch in "吗？？是不是要不要能不能怎么样为什么":
                        pass
            # 简易：按命中的既有条目聚合
            hit_c = Counter(r["matched"] for r in rows if r["matched"])
            if hit_c:
                print("按命中条目分布：", dict(hit_c))


if __name__ == "__main__":
    main()
