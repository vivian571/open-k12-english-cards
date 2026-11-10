# Painless English Challenge Cards (初中英语无痛闯关卡)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub Pages](https://img.shields.io/badge/GitHub_Pages-Online-emerald.svg)](https://vivian571.github.io/open-k12-english-cards/)
[![Cards Count](https://img.shields.io/badge/Cards_Count-76_Cards-purple.svg)](https://github.com/vivian571/open-k12-english-cards)
[![Synced with KB](https://img.shields.io/badge/Synced_with-open--k12--english--kb-blue.svg)](https://github.com/vivian571/open-k12-english-kb)

本项目是独立开源的**初中英语无痛闯关卡与 Anki 记忆牌组**项目。每张卡片遵循认知减负原则，彻底告别机械死记硬背，通过**三大关卡递进体系**帮助中学生无痛攻克英语重难点。

🌐 **在线 3D 翻转与闯关工作台**：[https://vivian571.github.io/open-k12-english-cards/](https://vivian571.github.io/open-k12-english-cards/)  
📚 **对应父级全量知识库**：[vivian571/open-k12-english-kb](https://github.com/vivian571/open-k12-english-kb)

---

## 🌟 核心理念：何为“无痛闯关”？

传统语法卡片常常直接罗列冰冷枯燥的规则公式，造成孩子强烈的抵触情绪。本项目每张卡片均被重构为三个无痛台阶：

```
       [🏆 关卡 3 · 登顶闯关实战]   ➔ 真实语境单步破题、拒绝剧透、防粗心
                  ▲
       [⚡ 关卡 2 · 避坑雷达与口诀] ➔ 识别中考出题套路、手绘级速记法则
                  ▲
       [🌊 关卡 1 · 心智生活隐喻]   ➔ 将抽象概念生活具象化（乐高积木/收纳衣柜/相机快门）
```

- **心智隐喻破壁**：例如将*从句*比喻为“被收纳进大衣柜的折叠衣物（必须叠整齐成陈述语序）”；将*瞬间动词*比喻为“相机快门（咔嚓一下，不能按住快门长达三年）”。
- **避坑雷达**：直接标红命题人高频挖坑词（如 *advice* 不可数、*between you and me* 介宾结构、*the more..., the more...* 齿轮效应）。
- **登顶闯关**：提供启发式无痛提示（Hint），引导孩子自主推导得出答案。

---

## 🔄 与知识库的动态同步机制 (Dynamic Sync)

本卡片项目与上游知识库 [open-k12-english-kb](https://github.com/vivian571/open-k12-english-kb) 深度解耦但保持**全自动化动态同步**：

1. **上游知识库更新时**（新增中考语法考点、新增教材单元如外研七上 Starter, Family ties, Emma 等）：
2. **运行同步引擎**：
   ```bash
   python3 scripts/sync_from_kb.py
   ```
   同步引擎会自动拉取最新的考点结构、教材真实例句与练习题，重新生成 76+ 张全新的无痛卡片，并自动同步更新：
   - 结构化数据：[`data/cards.json`](data/cards.json)
   - Anki 牌组文件：[`exports/anki_deck.tsv`](exports/anki_deck.tsv)
   - 可打印 Markdown：[`exports/cards_printable.md`](exports/cards_printable.md)
   - 网页工作台：[`index.html`](index.html)
3. **CI/CD 自动化流水线**：项目配置了 [`.github/workflows/sync_kb.yml`](.github/workflows/sync_kb.yml)，支持定时巡检或一键触发远程自动合流。

---

## 📂 仓库资产一览

```
open-k12-english-cards/
├── index.html                 # 在线 3D 翻转卡片与登顶闯关平台 (GitHub Pages 部署)
├── README.md                  # 本说明文档
├── LICENSE                    # Apache-2.0 开源许可
├── .gitignore
├── .github/
│   └── workflows/
│       └── sync_kb.yml        # GitHub Actions 动态同步流水线
├── data/
│   └── cards.json             # 76 张全量无痛卡片完整数据
├── exports/
│   ├── anki_deck.tsv          # 一键导入 Anki 软件的 TSV 格式牌组
│   └── cards_printable.md     # 适合打印或导入 Obsidian/Notion 的 Markdown 版
└── scripts/
    └── sync_from_kb.py        # 知识库驱动的卡片生成与同步引擎
```

---

## 📱 导入 Anki 手机/电脑端使用

1. 下载 [`exports/anki_deck.tsv`](exports/anki_deck.tsv)。
2. 打开 Anki 客户端，点击菜单栏 **【文件】➔【导入】**。
3. 字段映射默认支持【正面：考点与闯关问题】/【反面：心智隐喻 + 避坑雷达 + 通关答案解析】。
4. 即可在手机或平板端进行碎片化艾宾浩斯复习打卡。

---

## 📄 开源许可

本项目遵循 [Apache License 2.0](LICENSE) 开源协议。欢迎 Fork、提交 Pull Request 或根据所在地区教材版本扩展微专题卡片！
