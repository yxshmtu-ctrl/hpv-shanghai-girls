#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diff_policy.py — 政策 config 变更比对 / 当前口径速览

用途：政策(免费范围/预约/热线等)改版时，追踪 policy.yaml 变化并生成"变更说明+生效提醒"，
      避免口径漂移（知识库与最新政策不一致）。

用法：
  python scripts/diff_policy.py               # 打印当前政策要点速览
  python scripts/diff_policy.py snapshot      # 保存当前 policy.yaml 快照到 config/history/
  python scripts/diff_policy.py diff          # 当前 config vs 最近一次快照 → 变更说明
  python scripts/diff_policy.py diff --from 政策-2026-03-01.yaml
"""

import sys, os, re, glob, argparse, datetime

sys.stdout.reconfigure(encoding="utf-8")

CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "policy.yaml"
)
HIST = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "history"
)


def keyvals():
    """提取当前/文件里的关键字段行，供速览与比对。"""
    out = {}
    for ln in open(CONFIG, encoding="utf-8"):
        ln = ln.rstrip("\n")
        m = re.search(r"birth_after:\s*[\"']?([\d-]+)", ln)
        if m:
            out["免费出生起点"] = m.group(1)
        m = re.search(r"age_from:\s*(\d+)", ln)
        if m:
            out["免费年龄"] = m.group(1) + "周岁"
        m = re.search(r"vaccine_type:\s*[\"']?([^\s\"']+)", ln)
        if m:
            out["免费疫苗"] = m.group(1)
        m = re.search(r"doses:\s*(\d+)", ln)
        if m:
            out["剂次"] = m.group(1)
        m = re.search(r"interval_months:\s*(\d+)", ln)
        if m:
            out["间隔"] = m.group(1) + "个月"
        m = re.match(r"^\s{2}channel_primary:\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m:
            out["主预约渠道"] = m.group(1).strip()
        m = re.match(r"^\s{2}hotline_sh_health:\s*\"?([\d-]+)\"?\s*$", ln)
        if m:
            out["卫生健康热线"] = m.group(1).strip()
        m = re.search(r"^\s{2}hotline:\s*\"?([\d-]+)\"?\s*$", ln)
        if m:
            out.setdefault("健康云热线", m.group(1).strip())
        m = re.match(r"^\s{2}name:\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m and m.group(1):
            out.setdefault("school.name", m.group(1).strip())
    return out


def snapshot():
    os.makedirs(HIST, exist_ok=True)
    today = datetime.date.today().isoformat()
    n = len(glob.glob(os.path.join(HIST, f"policy-{today}-*.yaml")))
    dst = os.path.join(HIST, f"policy-{today}-{n + 1}.yaml")
    with open(CONFIG, encoding="utf-8") as f:
        data = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(data)
    print(f"已保存快照：{dst}")
    return dst


def read_kv(path):
    out = {}
    for ln in open(path, encoding="utf-8"):
        m = re.search(r"birth_after:\s*[\"']?([\d-]+)", ln)
        if m:
            out["免费出生起点"] = m.group(1)
        m = re.search(r"age_from:\s*(\d+)", ln)
        if m:
            out["免费年龄"] = m.group(1) + "周岁"
        m = re.search(r"vaccine_type:\s*[\"']?([^\s\"']+)", ln)
        if m:
            out["免费疫苗"] = m.group(1)
        m = re.search(r"doses:\s*(\d+)", ln)
        if m:
            out["剂次"] = m.group(1)
        m = re.search(r"interval_months:\s*(\d+)", ln)
        if m:
            out["间隔"] = m.group(1) + "个月"
        m = re.match(r"^\s{2}channel_primary:\s*\"?([^\"#]+?)\"?\s*$", ln)
        if m:
            out["主预约渠道"] = m.group(1).strip()
        m = re.search(r"^\s{2}hotline_sh_health:\s*\"?([\d-]+)\"?\s*$", ln)
        if m:
            out["卫生健康热线"] = m.group(1).strip()
    return out


def diff(prev_path=None):
    if not os.path.exists(HIST):
        print("无历史快照。先运行：python scripts/diff_policy.py snapshot")
        return
    snaps = sorted(glob.glob(os.path.join(HIST, "*.yaml")))
    prev = prev_path or (snaps[-1] if snaps else None)
    if not prev:
        print("无可用快照。")
        return
    cur = read_kv(CONFIG)
    old = read_kv(prev)
    print(f"对比：{os.path.basename(prev)}  vs  当前 config")
    changed = False
    for k in sorted(set(cur) | set(old)):
        if cur.get(k) != old.get(k):
            changed = True
            print(f"  • {k}: {old.get(k, '(无)')} → {cur.get(k, '(无)')}")
    if not changed:
        print("  无关键字段变化。")
    else:
        print("\n⚠️ 生效提醒：policy.yaml 已变化，以下材料将自动采用新口径：")
        print(
            "  gen_material_one_pager / gen_remind_text / gen_material / SKILL 资格速记"
        )
        print("  请同步复核：本轮宣传/回答是否仍引用旧政策？")


def main():
    ap = argparse.ArgumentParser(description="policy.yaml 速览/快照/变更比对")
    ap.add_argument(
        "cmd", nargs="?", default="view", choices=["view", "snapshot", "diff"]
    )
    ap.add_argument("--from", dest="prev", default=None)
    a = ap.parse_args()

    if a.cmd == "view":
        kv = keyvals()
        print("【当前政策要点速览】")
        for k, v in kv.items():
            print(f"  {k}: {v}")
    elif a.cmd == "snapshot":
        snapshot()
    elif a.cmd == "diff":
        diff(a.prev)


if __name__ == "__main__":
    main()
