# 安装指南

## 1) 克隆

```bash
git clone <this-repo> ~/.claude/skills/create-bilibili-culture
```

## 2) 数据处理

```bash
cd ~/.claude/skills/create-bilibili-culture
python3 tools/ingest_corpus.py ingest --input "/Users/jinluo/Downloads/bilibilib_gongzuoxibao.csv" --out-dir assets/processed
python3 tools/build_profile.py build --input assets/processed/cleaned.jsonl --assets-dir assets
python3 tools/eval_style.py gate --assets-dir assets
```

## 3) 导出安装包

```bash
python3 tools/export_skill.py export --project-root . --out-dir dist --command-name "站味"
```

## 4) 安装到不同运行时

```bash
python3 tools/install_claude_generated_skill.py --package-dir dist/站味
python3 tools/install_openclaw_generated_skill.py --package-dir dist/站味
python3 tools/install_codex_generated_skill.py --package-dir dist/站味
```
