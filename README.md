<div align="center">

# B友.skill

**把几十万条站内真实互动煮成一锅——能检索、能打分、你还能一句「不像」当场纠偏。**  
不是靠模型硬演 B 站，是**有话术锚点才敢开口**的那种。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://python.org)
[![Skill](https://img.shields.io/badge/Skill-B友.skill-00A1D6)](./SKILL.md)
[![Local First](https://img.shields.io/badge/Runtime-纯本地-7C3AED)](./INSTALL.md)

**注册名** `create-byou` · 默认敲 **`/B友`** 开聊  
（像极了：点进合集先找「怎么用」）

</div>

---

<a id="rewrite-protocol"></a>

## `/改写` 写 README：**先跑引擎，再动笔**（别空口）

你骂得对：之前有人**没落 `runtime_engine.py rewrite`**就改正文，那叫**跳步骤**，等于白装 B友.skill。

**硬性流程（对上 [`SKILL.md`](./SKILL.md)）：**

1. `cd` 到本仓库根（`tools/`、`assets/` 在这层）。
2. 把待改文稿塞进引擎（全文太长可分批，最后合并锚点去重）：  
   `python3 tools/runtime_engine.py rewrite --input "$(cat README.md)"`  
   或先：`python3 tools/runtime_engine.py rewrite --input "$(sed -n '1,120p' README.md)"`
3. **必须用 JSON 里的 `anchors`：** 看人话前先看 **命中了哪几条、`scene`/`cluster` 是啥**——那才是「站味浓度」论据，不是你脑补。
4. **再改写正文**：话术节奏对齐锚点句（推荐 / 吐槽 / 理性 / 公告条目的比例别歪），并保持下面表格与命令一字不差可执行。
5. **安全检查**：攻击性、个人隐私、过载玩梗照旧按 SKILL 「输出规范」过滤一遍再发布。

引擎当前吐的是「改写结果」壳子 **+ 原文 + 参考锚点摘录**；**真正把 Markdown 换血**，是第 4 步由人/Agent **照着锚点写**——这步以前是缺的，补上。

<details>
<summary><b>本次示例：对 README 前 80 行跑 <code>/改写</code> 捞到的锚点摘要</b>（点开对照）</summary>

Top 语义命中（节选）：**「不是硬吹，这部作品细节真有东西，值得推荐，建议二刷。」** · **「这操作也太离谱了，先笑为敬，后面反转再说。」** · **「以下是功能更新说明，按条目浏览即可。」** · 纠偏锚 **「这波表达得更B友一点」**——后文结构与口气按这几类混排：**真诚安利 tone + 自黑认栽一句 + 条列说明别装死**。
</details>

---

> 「求求别堆梗到鬼畜——我要的是**评论区那种活人节奏**。」  
> 懂。所以我们这边规矩写死：**先翻本地锚点，再张嘴**；浓度能拧，不像能写回，**不靠外网临时抄作业**。

**省流三件事**：① 本地 **RAG** ② **六类门禁** 过了才敢说稳 ③ 词典可走「机抽 + 人审」闭环。

跳到：[**改 README 先跑 `/改写`**](#rewrite-protocol) · [谁该点进来](#谁该点进来) · [怎么玩儿](#怎么玩儿示范) · [主线命令](#五条主线命令) · [工程老哥专区](#工程老哥专区) · [开箱](#开箱别急文档在这) · [词典 \& 评测](#站内词典-v1怎么养) · [语料是啥格式](#你这csv得长啥样)

---

## 谁该点进来

| 你是谁 | 这玩意儿能帮啥 |
|--------|----------------|
| **UP / 运营** | 置顶、动态、私信回复——像**熟粉唠嗑**，别整「家人们一二三上链接」那股工业味。 |
| **标题简介分P** | 短、密、亲近，一眼**站内语感**，不是微博热搜附体。 |
| **二创 / 切片宣发** | 吐槽安利都更像**番剧加长版评论区**，不搞硬拗「绝绝子」。 |
| **写更新日志又懒得装** | **中性说明**那一路：清楚、梗少，但读起来还是「公告」不是「公文」。 |
| **搓 Agent / 人设** | 用语料蒸馏出来的口气，比自己脑补「我像 B 站」稳多了；还带门禁、可回滚。 |
| **数据搬砖** | 评论进仓之后：清洗、打标、抽词典、选锚点——而且你能说清**为啥这句像站内**。

**退避提示**：它不替你「想全盘内容策略」，也**不搞运行时爬站偷学**——纯本地 assets，稳字当头。

---

## 怎么玩儿（示范）

真·人类在对话框里看见的，大概长下面这样；干活儿的 Agent **按 [`SKILL.md`](./SKILL.md)** 调 `tools/runtime_engine.py` 就对了。  
**铁律复述一遍**：每条回复生成前，**先捞 3～8 条** `anchors.jsonl`——锚点不是彩蛋，是**论据**。

### `/B友` · 随缘唠嗑模式

**你：** 这期后半段剪得是不是有点赶？前面我还挺沉浸的。

**我：** get，前面那种娓娓道来确实上头；后面有点像**拖进度条赶场**——能看，但就是情绪刚到就被拽走了。要不先当个**尝鲜版**刷完，真香再上**二刷**，节奏就对了。

---

### `/改写` · 官方话翻译成人话（站内版）

**你：** `/改写` —— 敝司将于下周五发布 3.2 版本，含性能优化及缺陷修复，敬请关注。

**我：** OK，翻译成常混评论区能听懂的：**周五上 3.2**，这轮主要是**榨性能 + 填坑**，细节翻 changelog；**先马后进**谁也不亏。

**加长版文稿（README、公告）也一样：** **先 `rewrite --input` 出锚点，再动笔**——上面 [改写 README 必须先跑引擎](#rewrite-protocol) 写死了。

---

### `/拆解` · 这一句到底偏哪条路数

**你：** `/拆解` ——「这波反向教科书，我先笑为敬。」

**我：** **吐槽整活**浓度偏高：有段子感、带点 neg 玩笑，像在评论区开团前的「先哈哈哈哈」。  
要上**长评说理**或对外的**正经公告**，建议降段子、补上具体判断；要是在**对线现场**，别把攻击性旋钮拧太大。

*(引擎会给你命中锚点和 `cluster`，方便对照 `tag_dictionary`。)*

---

### `/氛围` · 一键生成「像那层楼」

**你：** `/氛围`，场景 **评论区互动**，主题：安利冷门科普番。

**我：** 不硬尬吹——这番属于那种**越看越香**的，信息量给得刚刚好、不噎。好这口「看完想记笔记」的，**先入收藏夹**，下饭刷一遍，**二刷抠细节更爽**。

---

### `/复刻` · 先搜语料再走心

**你：** `/复刻` ——夸 UP 勤奋，得像追更八百年的老朋友，别太商务。

**我：** 行，先从你话里的「勤快、追更、老伙计感」 **Top-K 抽锚**，再顺着语料味拼——比如：**这更新节奏是真的顶，我这边都追更追出肌肉记忆了**，比干巴巴「辛苦了」像人话。

---

### `/纠偏` · 「你这不像 B 站」之后

**你：** 你刚那句也太短视频口播了，离我常混的游戏区差十万八千里。

**我：** 收到，走 **`/纠偏`**：原文 + 牢骚 + 你心里的示范句打进 `corrections.jsonl`，相近锚点 **降权**，顺眼那句 **升格新锚**。下回同场景会慢慢往你的圈子靠。

---

## 为啥要这么架构（设计理念省流版）

结构上跟 [boss.skill](https://github.com/nicepkg/boss-skill) **只学气场**：开门见山、表格式喂饭。  
**坚决不学**：① 把一切塞进超长 `SKILL.md` ② 浏览器满天飞抓页面——维护地狱，拜拜。

| 梗概 | B友.skill 怎么说 |
|------|-------------------|
| **路由** | `SKILL.md` **超薄**，只指路；硬核全在 `tools/` |
| **家底** | **厚**：画像、锚点、词典、评测集、纠错全在 `assets/` |
| **生成** | **先检索**：每次怼模型前先 **3～8** 条风格锚点开路 |
| **浓度** | `style_density`、正式度、攻击性上限都从 `profile.json` 拧 |
| **门禁** | 六桶评测 + `StyleScore`，`eval_style.py gate` **挂了就不给出包** |
| **纠偏** | 「不像 / 太出戏」——写盘、改权重，**不是口头安抚** |

---

## 五条主线命令

老话：**命令别多，多了脑子疼。** 就这五个日常够用；上头 [演示](#怎么玩儿示范) 都走过了。

| 命令 | 一句话 |
|------|--------|
| **`/B友`** | 默认唠嗑：**站内味**，梗别灌太满 |
| **`/改写`** | 白话变 **圈友听得懂的说法** |
| **`/拆解`** | 看这串字偏 **整活 / 安利 / 理性 / 弹幕感** 哪边 |
| **`/氛围`** | Comments、弹幕、标题、投稿碎碎念……场景现编 |
| **`/复刻`** | **检索先行**，再吐出「像你数据集里捞出来」的版本 |

CLI 碎碎念照旧看 [`SKILL.md`](./SKILL.md)；入口 **`tools/runtime_engine.py`**。

---

## 工程老哥专区

表里的事，基本是 **debug / 发版 / 养词典** 才用得着——普通用户可当不存在。

| 命令 | 干啥 |
|------|------|
| **`/检索`** | 光看锚点，不生成——查检索姿势对不对 |
| **`/词典`** | 查词条、变体、场景偏好 |
| **`/校准`** | 会话维度：浓度、体面程度、攻击性上限 |
| **`/评测`** | 跑分 + 对齐门禁 |
| **`/纠偏`** | 用户反馈→**落到文件 + 动权重** |
| **`/版本`** | 盘一盘现在啥版本 |

---

## 开箱别急文档在这

**实话实说**：仓库里的 **`assets/anchors.jsonl`** 已经拿 **`bilibilib_gongzuoxibao.csv`** 炖过一整轮——大概 **1.9 万行** raw，洗完 **1.6 万条**的样子（去噪 + 去重），再和 **`anchor_seeds.jsonl`** 拼了拼，六类门禁才稳。**clone 下来就能跑**，不必自个儿先 `./ingest` 一遍找存在感。

| 玩意儿 | 啥意思 |
|--------|--------|
| `assets/anchors.jsonl` | 当前仓库 **169** 条锚点——语料子集 + 种子 |
| `assets/profile.json` | 门禁 + 画像；瞟一眼 `corpus_rows` / `corpus_anchors` 心里有数 |
| `assets/corpus_build_stats.json` | 入库统计摘要 |

想打包投喂别的运行时（**仍会先挨一顿 gate**）：

```bash
python3 tools/export_skill.py export --project-root . --target-runtime all
```

### 要自己换一车语料？（可选）

只有当你真想**换掉这口社区的味儿**再上号；CSV 至少有 `author`、`content`、`likes`、`ctime` 或 `date`：

```bash
python3 tools/ingest_corpus.py ingest --input /path/to/your.csv --out-dir assets/processed --lexicon assets/slang_lexicon.json
python3 tools/build_profile.py build --input assets/processed/cleaned.jsonl --assets-dir assets --per-cluster 40
python3 tools/eval_style.py gate --assets-dir assets
```

装哪、路径咋映射，摊开说在 **`INSTALL.md`**。

---

## 站内词典 v1怎么养

**机抽高频 + 人肉拍板**：脚本把候选吐出来，`review` / `evidence` 字段给你留的作业位。

### ① 自动生成一版草稿

```bash
python3 tools/build_slang_lexicon.py build \
  --cleaned assets/processed/cleaned.jsonl \
  --lexicon assets/slang_lexicon.json \
  --candidates-out assets/slang_candidates_v1.jsonl \
  --merged-out assets/slang_lexicon.v1.generated.json \
  --min-freq 8
```

| 产物 | 人话 |
|------|------|
| `slang_candidates_v1.jsonl` | 候选词，等你翻牌子 |
| `slang_lexicon.v1.generated.json` | 机 merge 的草稿，带好 `review / evidence` |

### ② 审核顺序：先怼「高危歧义」（省眼珠）

拉丁假阳性、coding 术语乱入那种——**优先级脚本**会先顶上来；种子词典里已 `approved` 的会自动 **降权** 别墨迹。

```bash
# JSON 看一眼 Top40 先审谁
python3 tools/review_slang_lexicon.py rank \
  --candidates assets/slang_candidates_v1.jsonl \
  --lexicon assets/slang_lexicon.json \
  --top 40

# 导出 CSV 给人改（默认按 priority，也可 --sort frequency）
python3 tools/review_slang_lexicon.py export-csv \
  --sort priority \
  --lexicon assets/slang_lexicon.json \
  --out-csv assets/slang_review_sheet_v1.csv
```

表里会多：`review_order`、`review_priority_score`、`ambiguity_flags`（比如 `english_noise`、`latin_token` 等）。

### ③ CSV 走完再「回灌」词典

```bash
python3 tools/review_slang_lexicon.py export-csv \
  --candidates assets/slang_candidates_v1.jsonl \
  --out-csv assets/slang_review_sheet_v1.csv

python3 tools/review_slang_lexicon.py import-csv \
  --review-csv assets/slang_review_sheet_v1.csv \
  --base-lexicon assets/slang_lexicon.json \
  --out-lexicon assets/slang_lexicon.v1.reviewed.json
```

**常用列**：`review_status`（`approved` / `tuned` / `rejected` / `pending`）、`category_override`、`preferred_scene_override`（多个用 `|`）、`formality_max_override`、`reviewer`、`confidence`、`notes`。

---

## 你这CSV得长啥样

| 项 | 说明 |
|----|------|
| **已炖过的那份** | `bilibilib_gongzuoxibao.csv`，列大致 `author,score,likes,ctime,content,date,...` |
| **最低及格线** | `author`、`content`、`likes`，时间戳 **`ctime` 或 `date` 来一个** |
| **洗完之后** | 脱敏去噪；梗词可对齐 `slang_lexicon.json` **归一** |
| **打标** | 场景、褒贬、体面程度、梗密度、火力值……全套 |
| **进锚点库** | 聚类完的尖子生进 `anchors.jsonl`，再和 **`anchor_seeds.jsonl`** 合体进仓 |

---

## 六桶评测（防「只会一种嘴脸」）

六类：**弹幕短句** · **评论区互动** · **安利文案** · **吐槽整活** · **理性分析** · **中性说明**。  
阈值在 `profile.json`，**想出包必须先过** `tools/eval_style.py gate`。

---

## 跑测试（_CI 脸_）

```bash
python3 -m unittest discover -s tests
```

---

## 翻书目录

| 文件 | 翻它干啥 |
|------|----------|
| [`SKILL.md`](./SKILL.md) | 命令 → **具体怼哪条脚本** |
| [`INSTALL.md`](./INSTALL.md) | 装机、默认 skills 路径 |
| `assets/profile.json` | 旋钮 + **corpus_* 计数** |
| `assets/anchor_seeds.jsonl` | 和语料锚点合体用的 **评测向种子** |
| `assets/corpus_build_stats.json` | 蒸馏摘要一眼懂 |
| `assets/tag_dictionary.json` | 标签合法值 |
| `assets/slang_lexicon.json` | **词典 v1 本体**（可换审定版） |

---

<div align="center">

**像 B 站是不够的——还得稳。**  
*路由要薄 · 数据要厚 · gate 要严格 · 别联网裸奔*

**B友.skill** —— **先上马后看视频**也行，但这次建议 **先看 README（完）**

</div>
