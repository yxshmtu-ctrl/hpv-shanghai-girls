# 沪苗守护 · hpv-shanghai-girls

上海未成年女性 HPV 疫苗接种促进技能。

## 用途
覆盖三类场景：
- **家长/学生咨询**：该不该打、免费资格、打哪种、去哪约、顾虑破除
- **接种门诊工作辅助**：资格速查、程序核对、家长沟通话术
- **公卫/学校宣讲策划**：讲座大纲、常见异议预答
- **推广/批量（校医·门诊·公卫）**：花名册筛适龄名单、生成家长会一页纸、漏种提醒话术

## 目录
```
hpv-shanghai-girls/
├── SKILL.md                  # 主入口（分流逻辑 + 推广模式 + 内容路由）
├── config/
│   └── policy.yaml           # ★可更新政策配置（含 school 个性化块）
├── references/
│   ├── 01-医学知识库.md       # HPV/疫苗医学 + 特殊人群章
│   ├── 02-政策速查与本地资源.md
│   ├── 03-谣言与反误区库.md   # 12条
│   ├── 04-沟通话术库.md
│   └── 05-政策原文参考.md     # 国家16号通知 + 上海1号方案
└── scripts/
    ├── check_eligibility.py         # 出生日期→免费资格判断
    ├── gen_class_list.py            # 花名册→免费适龄名单 Excel
    ├── gen_material_one_pager.py    # 生成家长会动员一页纸 md
    ├── gen_remind_text.py           # 漏种名单→分版本提醒话术
    ├── export_faq.py                # 谣言库→FAQ 问答知识包 json/md
    └── gen_material.py              # 宣传物料文案 折页/海报/推文
docs/
    └── HPV推广批量模式_5需求演示.docx   # 5需求触发与结果演示
examples/
    ├── 花名册样例.xlsx               # 测试用花名册（假数据）
    └── 漏种名单样例.csv              # 测试用漏种名单（假数据）
```

## 脚本用法（推广/批量）
```bash
# 适龄名单（自动识别列名，免费者高亮）
python scripts/gen_class_list.py 花名册.xlsx --out 名单.xlsx
python scripts/gen_class_list.py 花名册.xlsx --class "六年级(1)班"

# 家长会一页纸（口径来自 config）
python scripts/gen_material_one_pager.py --school XX中学 --class 六年级 -o 一页纸.md

# 漏种提醒（分版本：未首剂/缺第2剂）
python scripts/gen_remind_text.py 漏种名单.csv --csv 群发.csv

# FAQ 问答知识包（公众号/机器人）
python scripts/export_faq.py --json faq.json
python scripts/export_faq.py --md faq.md

# 宣传物料文案
python scripts/gen_material.py flier
python scripts/gen_material.py all -o material.md
```
依赖：`pip install pandas openpyxl`
完整演示见 `docs/HPV推广批量模式_5需求演示.docx`；样例数据见 `examples/`。

## 知识来源
疾控U健康（浦东疾控官方）HPV疫苗科普三篇：
1. HPV疫苗系列科普问答（10问）
2. 家长请查收：HPV疫苗接种重要提醒
3. 14问14答：免费HPV疫苗怎么接种

## 核心政策快照
- 免费对象：2011-11-10 后出生 + 满 13 周岁女孩
- 免费疫苗：国产双价 2 剂（间隔 6 个月）
- 预约：随申办/健康云"智慧接种"
- 客服：400-9216-519

⚠️ 政策会更新 → 时效内容一律以 config/policy.yaml + 官方公告为准。
⚠️ 健康科普工具，不替代接种门诊个体化咨询。

整理日期：2026-08-28
