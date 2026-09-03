#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_remind_text.py — 漏种名单 → 分版本提醒话术

输入：漏种名单 .xlsx/.csv（自动识别 姓名/手机/漏种类型 列）
漏种类型取值：no_first(未首剂) / miss_second(缺第2剂)；列名也可写中文
  "未首剂"/"缺2剂"/"缺第2剂"
输出：
  - 默认打印逐条文案到终端
  - --out remind.txt  每条一段
  - --csv  out.csv    生成"姓名,手机,文案"便于群发系统导入
渠道与热线从 config/policy.yaml 动态读取。

用法：
  python scripts/gen_remind_text.py 漏种名单.csv
  python scripts/gen_remind_text.py 漏种名单.csv --out remind.txt
  python scripts/gen_remind_text.py 漏种名单.csv --csv 群发.csv

⚠️ 个人信息合规：名单含未成年人及其监护人手机号，仅限授权环境使用，禁止上传公开仓库。
"""

import sys, os, re, argparse, csv

sys.stdout.reconfigure(encoding="utf-8")

CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "policy.yaml"
)

TYPE_ALIAS = {
    "no_first": {"未首剂", "未接种首剂", "no_first", "0剂", "未打"},
    "miss_second": {"缺第2剂", "缺2剂", "miss_second", "缺第二剂", "只打1剂"},
}


def read_config():
    cfg = {"booking": [], "hotlines": [], "school_name": ""}
    for ln in open(CONFIG, encoding="utf-8"):
        m = re.match(r"^\s{2}channel_(primary|secondary):\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m:
            cfg["booking"].append(m.group(2).strip())
        m = re.search(r"hotline(_sh_health)?:\s*[\"']?([\d-]+)", ln)
        if m:
            cfg["hotlines"].append(m.group(2))
        m = re.match(r"^\s{4}name:\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m:
            cfg["school_name"] = m.group(1).strip()
    return cfg


def normalize_type(v):
    s = str(v).strip()
    low = s.lower()
    for t, aliases in TYPE_ALIAS.items():
        if s in aliases or low in {x.lower() for x in aliases}:
            return t
    return None


def build_text(name, ttype, booking, hotline, school=""):
    head = f"【{school}】" if school else ""
    if ttype == "no_first":
        return (
            f"{head}{name}家长您好：国家已将HPV疫苗纳入免费免疫规划，孩子已满13周岁，"
            f"可免费接种2剂次双价HPV疫苗。请尽快通过{booking}登记接种意愿并预约，"
            f"预防宫颈癌从接种开始。咨询{hotline}。"
        )
    # miss_second
    return (
        f"{head}{name}家长您好：孩子第2剂HPV疫苗已到接种时间，请尽快通过{booking}预约补种，"
        f"完成全程才能获得最佳保护。咨询{hotline}。"
    )


def resolve_col(df, cands):
    cols = {str(c).strip().lower(): c for c in df.columns}
    for c in cands:
        if c.lower() in cols:
            return cols[c.lower()]
    return None


def main():
    import argparse

    ap = argparse.ArgumentParser(description="漏种名单 → 提醒话术")
    ap.add_argument("roster", help="漏种名单 .xlsx/.csv")
    ap.add_argument("--out", default=None, help="输出 .txt 逐条")
    ap.add_argument(
        "--csv", dest="csvout", default=None, help="输出 .csv(姓名,手机,文案)"
    )
    a = ap.parse_args()

    try:
        import pandas as pd
    except ImportError:
        sys.exit("需要 pandas：pip install pandas openpyxl")

    df = (
        pd.read_csv(a.roster, dtype=str)
        if a.roster.lower().endswith(".csv")
        else pd.read_excel(a.roster, dtype=str)
    )

    c_name = resolve_col(df, ["姓名", "名字", "学生姓名", "name"])
    c_phone = resolve_col(
        df, ["手机", "手机号", "电话", "监护人电话", "phone", "mobile"]
    )
    c_type = resolve_col(df, ["漏种类型", "类型", "漏种情况", "status", "type"])
    if not c_name or not c_type:
        sys.exit(
            f"未识别到必要列。现有列：{list(df.columns)}\n需含 姓名 与 漏种类型 列。"
        )

    cfg = read_config()
    booking = "；".join(cfg["booking"]) if cfg["booking"] else "随申办/健康云→智慧接种"
    hotline = " / ".join(dict.fromkeys(cfg["hotlines"])) or "见官方公告"
    school = cfg["school_name"]

    lines = []
    rows = []
    for _, r in df.iterrows():
        name = str(r[c_name]).strip()
        phone = str(r[c_phone]).strip() if c_phone and pd.notna(r[c_phone]) else ""
        ttype = normalize_type(r[c_type]) if c_type and pd.notna(r[c_type]) else None
        if not ttype:
            ttype = "no_first"  # 未识别默认按未首剂提醒，避免漏发
        text = build_text(name, ttype, booking, hotline, school)
        lines.append(text)
        rows.append({"姓名": name, "手机": phone, "文案": text})

    if a.csvout:
        with open(a.csvout, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["姓名", "手机", "文案"])
            w.writeheader()
            w.writerows(rows)
        print("已生成群发csv：", a.csvout)
    elif a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("\n\n".join(lines))
        print("已生成：", a.out)
    else:
        for i, t in enumerate(lines, 1):
            print(f"[{i}] {t}\n")


if __name__ == "__main__":
    main()
