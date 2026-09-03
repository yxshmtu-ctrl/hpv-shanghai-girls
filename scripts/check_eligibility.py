import sys, os, json
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

CONFIG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config", "policy.yaml"
)


def parse_date(s):
    return date(*map(int, s.split("-")))


def check_eligibility(birth_str, today=None):
    """判断出生日期是否在免费HPV接种范围内。

    Args:
        birth_str: 出生日期字符串 YYYY-MM-DD
        today: date，测试用，默认今天
    Returns:
        dict: {eligible, reason, age, birth_after_ok, next_year_date}
    """
    # 读 yaml 简化（无 yaml 库时按 key 取行）——这里用轻量解析
    birth_after = "2011-11-10"
    age_from = 13
    import re

    for line in open(CONFIG, encoding="utf-8"):
        m = re.match(r"\s*birth_after:\s*[\"']?([\d-]+)", line)
        if m:
            birth_after = m.group(1)
        m = re.match(r"\s*age_from:\s*(\d+)", line)
        if m:
            age_from = int(m.group(1))

    today = today or date.today()
    bd = parse_date(birth_str)
    cutoff = parse_date(birth_after)

    # 年龄（周岁）
    age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    birth_after_ok = bd >= cutoff

    if birth_after_ok and age >= age_from:
        eligible = True
        reason = f"符合免费条件：{birth_str} 出生（晚于{cutoff}）且已满{age_from}周岁（现{age}周岁）"
    else:
        eligible = False
        problems = []
        if not birth_after_ok:
            problems.append(f"出生日期{birth_str}早于免费范围起始{cutoff}")
        if age < age_from:
            problems.append(
                f"当前{age}周岁，未满{age_from}周岁（每年满{age_from}周岁时符合）"
            )
        reason = "；".join(problems) if problems else "条件未知"

    # 预计到达免费年龄的日期（若现在未满13）
    next_eligible = None
    if not eligible and age < age_from:
        # 满13周岁那年的生日
        y = bd.year + age_from
        # 若今年已过生日则明年
        if (bd.month, bd.day) <= (today.month, today.day) or (
            bd.year + age_from
        ) <= today.year:
            y += (
                0
                if (bd.month, bd.day) > (today.month, today.day)
                and bd.year + age_from == today.year
                else 0
            )
        # 简化：满13周岁的日期
        nd = date(bd.year + age_from, bd.month, bd.day)
        if nd < today:
            nd = date(today.year + 1, bd.month, bd.day)  # fallback
        next_eligible = nd.isoformat()

    return {
        "eligible": eligible,
        "reason": reason,
        "age": age,
        "birth_after_ok": birth_after_ok,
        "estimated_eligible_date": next_eligible,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_eligibility.py YYYY-MM-DD [今天YYYY-MM-DD(测试)]")
        sys.exit(1)
    birth = sys.argv[1]
    t = parse_date(sys.argv[2]) if len(sys.argv) > 2 else None
    r = check_eligibility(birth, t)
    print(json.dumps(r, ensure_ascii=False, indent=2))
