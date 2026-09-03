#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_material_one_pager.py — 生成 HPV 免费接种家长动员一页纸(个性化, md)

数据从 config/policy.yaml 动态读取（免费口径/预约渠道/热线/携带材料/学校信息），
配合 --school / --class 个性化，保证口径与 config 同步、可批量。

用法：
  python scripts/gen_material_one_pager.py                    # 打印到终端
  python scripts/gen_material_one_pager.py --school "XX中学" --class 六年级 -o 一页纸.md
  python scripts/gen_material_one_pager.py --consent 2026-09-15 --clinic "XX社区门诊"

⚠️ 政策口径以 config 与最新官方公告为准；本页为动员模板，非医疗建议。
"""

import sys, os, re, argparse

sys.stdout.reconfigure(encoding="utf-8")

CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "policy.yaml"
)


def read_config():
    """轻量读 policy.yaml：收集所需键（单次扫描，够用）。"""
    cfg = {"free": {}, "booking": [], "docs": [], "school": {}, "hotlines": []}
    for ln in open(CONFIG, encoding="utf-8"):
        ln = ln.rstrip("\n")
        m = re.search(r"birth_after:\s*[\"']?([\d-]+)", ln)
        if m:
            cfg["free"]["birth_after"] = m.group(1)
        m = re.search(r"age_from:\s*(\d+)", ln)
        if m:
            cfg["free"]["age_from"] = m.group(1)
        m = re.search(r"vaccine_type:\s*[\"']?([^\s\"']+)", ln)
        if m:
            cfg["free"]["vaccine"] = m.group(1)
        m = re.search(r"doses:\s*(\d+)", ln)
        if m:
            cfg["free"]["doses"] = m.group(1)
        m = re.search(r"interval_months:\s*(\d+)", ln)
        if m:
            cfg["free"]["interval"] = m.group(1)
        m = re.search(r"hotline(_sh_health)?:\s*[\"']?([\d-]+)", ln)
        if m:
            cfg["hotlines"].append(m.group(2))
        m = re.match(r"^\s{2}-\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m and any(
            k in m.group(1)
            for k in ["监护", "证件", "接种证", "知情同意书", "身份证", "户口本"]
        ):
            cfg["docs"].append(m.group(1).strip())
        m = re.match(r"^\s{2}([\w_]+):\s*(.*)$", ln)
        if m and m.group(1) in {
            "name",
            "grades",
            "consent_deadline",
            "clinic",
            "contact_person",
            "contact_phone",
        }:
            v = m.group(2).strip().strip("\"'")
            if m.group(1) == "grades" and v.startswith("[") and v.endswith("]"):
                v = v[1:-1].replace('"', "").replace("'", "").replace(" ", "")
            cfg["school"][m.group(1)] = v
        # booking 渠道行
        m = re.match(r"^\s{2}channel_(primary|secondary):\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m:
            cfg["booking"].append(m.group(2).strip())
    return cfg


def main():
    ap = argparse.ArgumentParser(description="生成 HPV 家长动员一页纸(md)")
    ap.add_argument("--school", default="", help="学校名；空则用 config.school.name")
    ap.add_argument("--class", dest="cls", default="", help="班级/年级抬头")
    ap.add_argument("--consent", default="", help="知情同意书回收截止，覆盖 config")
    ap.add_argument("--clinic", default="", help="对口接种门诊，覆盖 config")
    ap.add_argument("-o", "--out", default=None, help="输出 .md；缺省打印终端")
    a = ap.parse_args()

    cfg = read_config()
    free, docs, sch = cfg["free"], cfg["docs"], cfg["school"]
    hot_line = " / ".join(dict.fromkeys(cfg["hotlines"])) or "（见官方公告）"

    school_name = a.school or sch.get("name", "")
    disp = school_name or "本校"
    grade = a.cls or sch.get("grades", "").replace(",", "、")
    consent = a.consent or sch.get("consent_deadline", "")
    clinic = a.clinic or sch.get("clinic", "")
    booking = (
        "；".join(cfg["booking"]) if cfg["booking"] else "随申办 / 健康云 → 智慧接种"
    )

    L = [
        f"# {disp} HPV 疫苗免费接种 · 家长告知与动员一页纸",
    ]
    if grade:
        L.append(f"（适用：{grade}）")
    L += [
        "",
        f"> 政策依据：国家已将 HPV 疫苗纳入国家免疫规划。{free.get('birth_after', '2011-11-10')} 以后出生、满 {free.get('age_from', '13')} 周岁的女孩，免费接种 {free.get('doses', '2')} 剂次 {free.get('vaccine', '国产双价HPV')}，间隔 {free.get('interval', '6')} 个月。",
        "",
        "## 一、为什么现在打",
        "- 13 岁是最佳窗口：免疫反应好，抗体水平约为 15 岁以上人群的 2 倍，保护至少 10 年。",
        "- 在初次性行为前接种，才能最大限度发挥预防作用；宫颈癌是女性常见恶性肿瘤，疫苗是有效的一级预防。",
        "",
        "## 二、免费打的是什么",
        f"- {free.get('vaccine', '国产双价HPV')}，共 {free.get('doses', '2')} 针，间隔 {free.get('interval', '6')} 个月。双价覆盖导致 70% 以上宫颈癌的 HPV16/18 型。",
        "- 已自费全程接种过四价/九价的，视同完成，无需重复接种。",
        "",
        "## 三、安全性",
        "- 疫苗安全性数据优于全国疫苗平均；接种后留观 30 分钟即可。",
        "- 接种不影响发育；月经期不是禁忌。",
        "",
        "## 四、家长常见问题快答",
        "| 问题 | 回答 |",
        "| --- | --- |",
        "| 打了还要做宫颈筛查吗？ | 要！疫苗防大部分型别，有性生活后仍需定期筛查。 |",
        "| 孩子小，会不会太早/影响发育？ | 不早，13 岁正好；不影响发育。 |",
        "| 免费的是不是不如自费的好？ | 纳入国家免疫规划，审批/批签发/监管与自费同一标准。 |",
        "| 怎么预约？ | " + booking + "。 |",
        "| 错过这次还能补吗？ | 能。符合条件可到辖区接种点免费补种。 |",
        "",
        "## 五、行动号召",
        "- 请在随申办/健康云「智慧接种」登记意愿，等待告知短信后预约时间。",
    ]
    if consent:
        L.append(f"- 请于 {consent} 前交回监护人签署的知情同意书。")
    if clinic:
        L.append(f"- 对口接种：{clinic}。")
    L += [
        "",
        "## 六、接种时携带",
    ]
    L += [f"- {d}" for d in docs]
    L += [
        f"- 咨询热线：{hot_line}",
        "",
        "---",
        "*本页为动员参考，政策口径以官方最新公告为准；个体健康问题由接种医生判断。*",
    ]

    md = "\n".join(L)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(md)
        print("已生成：", a.out)
    else:
        print(md)


if __name__ == "__main__":
    main()
