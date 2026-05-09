# B站文化 Skill

基于本地 B 站语料构建“文化语感引擎”的 Skill 项目。

## 特点

- 薄路由：主 `SKILL.md` 只做命令路由。
- 厚数据：`assets/` 管理画像、锚点、词典、评估集、纠偏记录。
- 强校验：`tools/eval_style.py gate` 通过才允许导出。
- 纯本地：不依赖浏览器抓取和外部站点。

## 主命令（用户层）

- `/站味` 默认对话
- `/改写` 文本改写
- `/拆解` 语感分析
- `/氛围` 场景生成
- `/复刻` 检索后生成

## 专业命令（工程层）

- `/检索`、`/词典`、`/校准`、`/评测`、`/纠偏`、`/版本`

## 快速开始

见 `INSTALL.md`。

## 词典 v1 构建（自动候选 + 人工审核字段）

```bash
python3 tools/build_slang_lexicon.py build \
  --cleaned assets/processed/cleaned.jsonl \
  --lexicon assets/slang_lexicon.json \
  --candidates-out assets/slang_candidates_v1.jsonl \
  --merged-out assets/slang_lexicon.v1.generated.json \
  --min-freq 8
```

输出说明：

- `assets/slang_candidates_v1.jsonl`：自动提取候选术语（待人工审核）
- `assets/slang_lexicon.v1.generated.json`：合并后的词典草案（含 review/evidence 字段）

## 人工审核工作台（CSV）

1. 导出审核表：

```bash
python3 tools/review_slang_lexicon.py export-csv \
  --candidates assets/slang_candidates_v1.jsonl \
  --out-csv assets/slang_review_sheet_v1.csv
```

1. 在 `assets/slang_review_sheet_v1.csv` 中填写：

- `review_status`：`approved/tuned/rejected/pending`
- `category_override`
- `preferred_scene_override`（多个用 `|`）
- `formality_max_override`
- `reviewer/confidence/notes`

1. 回写词典：

```bash
python3 tools/review_slang_lexicon.py import-csv \
  --review-csv assets/slang_review_sheet_v1.csv \
  --base-lexicon assets/slang_lexicon.json \
  --out-lexicon assets/slang_lexicon.v1.reviewed.json
```

## 数据输入

当前示例输入：

- `/Users/jinluo/Downloads/bilibilib_gongzuoxibao.csv`

CSV 字段应包含至少：

- `author`, `ctime`/`date`, `content`, `likes`

## 评估

默认六类评估桶：

- 弹幕短句
- 评论区互动
- 安利文案
- 吐槽整活
- 理性分析
- 中性说明

