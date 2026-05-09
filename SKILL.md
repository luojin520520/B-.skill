---
name: create-bilibili-culture
description: "B站文化 skill 创建器：薄路由、厚数据、强校验、纯本地。"
argument-hint: "[站味|改写|拆解|氛围|复刻|检索|词典|校准|评测|纠偏|版本]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# B站文化 Skill

## 设计原则

- 只做路由，不塞入复杂实现细节。
- 所有生成都必须先检索 `assets/anchors.jsonl`。
- 默认只用本地资产，不依赖网页抓取。
- 风格参数与阈值只从 `assets/profile.json` 读取。

## 启动时必须读取

1. `assets/profile.json`
2. `assets/tag_dictionary.json`
3. `assets/slang_lexicon.json`
4. `assets/anchors.jsonl`
5. `assets/corrections.jsonl`

## 命令路由

### `/站味`（默认）

- 目标：普通对话时带 B 站语感，但不过度玩梗。
- 操作：
  1. 用 `python3 tools/runtime_engine.py chat --input "<用户文本>"` 获取候选输出。
  2. 输出前再做一次安全检查（攻击性与过载梗）。

### `/改写`

- 目标：把现代文本改写为 B 站文化语感。
- 操作：
  1. 用 `python3 tools/runtime_engine.py rewrite --input "<用户文本>"`。
  2. 默认 `style_density=med`，可通过 `/校准` 改写会话参数。

### `/拆解`

- 目标：解释文本属于什么文化层（整活/安利/理性等）。
- 操作：
  1. 用 `python3 tools/runtime_engine.py analyze --input "<用户文本>"`。
  2. 输出标签、触发词、风险项和建议场景。

### `/氛围`

- 目标：生成场景文案（评论区、弹幕、简介、标题、投稿说明、互动回复）。
- 操作：
  1. 用 `python3 tools/runtime_engine.py vibe --scene "<场景>" --input "<主题>"`。
  2. 若用户未提供场景，默认 `评论区互动`。

### `/复刻`

- 目标：先检索锚点，再生成高相似表达。
- 操作：
  1. 用 `python3 tools/runtime_engine.py mimic --input "<用户文本>" --top-k 8`。
  2. 显示命中锚点摘要与相似度。

## 专业命令

### `/检索`

- 只检索，不生成。
- `python3 tools/runtime_engine.py retrieve --input "<查询>" --top-k 8`

### `/词典`

- 查询术语释义、变体、使用限制。
- `python3 tools/runtime_engine.py lexicon --term "<术语>"`

### `/校准`

- 设置会话参数：文化浓度、正式度、攻击性上限。
- `python3 tools/runtime_engine.py calibrate --style-density med --formality mid --max-aggression low`

### `/评测`

- 对当前文本进行风格评分。
- `python3 tools/eval_style.py score --text "<文本>"`

### `/纠偏`

- 结构化写回纠错，而不是口头说明。
- `python3 tools/runtime_engine.py correct --input "<原句>" --feedback "<反馈>" --expected "<期望改写>"`

### `/版本`

- 查看资产版本信息。
- `python3 tools/runtime_engine.py version`

## 运行时约束

- 每次生成必须检索 3-8 条锚点。
- 无锚点时降级为中性表达，并说明证据不足。
- 术语过载时自动回退到低浓度版本。

## 数据更新流程

1. 新语料导入：`python3 tools/ingest_corpus.py ingest --input "/Users/jinluo/Downloads/bilibilib_gongzuoxibao.csv" --out-dir assets/processed`
2. 重建画像：`python3 tools/build_profile.py build --input assets/processed/cleaned.jsonl --assets-dir assets`
3. 运行评测：`python3 tools/eval_style.py gate --assets-dir assets`
4. 通过后导出：`python3 tools/export_skill.py export --project-root . --target-runtime all`

## 输出规范

- 优先保证语义准确，再加文化语感。
- 不强制堆梗；保持可读性。
- 涉及攻击性表达时自动降级。
- 涉及敏感信息时禁止复刻原文。
