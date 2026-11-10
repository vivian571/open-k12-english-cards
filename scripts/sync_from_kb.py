#!/usr/bin/env python3
"""
Sync and generate Painless Challenge Cards (无痛闯关卡) from Open K-12 English KB.
Supports local repository data and remote GitHub raw data fallback.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
LOCAL_KB_DIR = ROOT.parent / "open-k12-english-kb" / "data"

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/vivian571/open-k12-english-kb/main/data"

# Standard pedagogical metaphors mapping for English grammar modules
METAPHORS_MAP = {
    "chap_01": {
        "concept": "名词体系",
        "metaphor": "名词就像‘乐高积木’：可数名词是独立散装积木，加一个就多一块 (-s/-es)；不可数名词是‘面粉和水’，流体抓不住，必须装进特定的碗或杯子里（数词+计量词+of）才能称重计量。",
        "radar": "【避坑雷达】：警惕 news, advice, information 这三颗‘地雷’，虽然意思重要或带 s，但本质是散装不可数，绝不能加 a 或加 s！"
    },
    "chap_02": {
        "concept": "冠词体系",
        "metaphor": "冠词就像名词的‘通行证标签’：a/an 是临时临时访客证（泛指某一个），the 是实名制专属 VIP 门票（你我皆知的那个特指目标）。",
        "radar": "【避坑雷达】：千万别被英文字母骗了眼睛，开门的不是字母，而是‘元音音素的发音钥匙’！hour 敲的是元音门 (an hour)，university 敲的是辅音门 (a university)。"
    },
    "chap_03": {
        "concept": "代词体系",
        "metaphor": "代词就像片场的‘替身演员’：主格只演主角（站在动词前发号施令），宾格演挨打的受众（站在动词或介词身后接招）。名词性物主代词是‘全职合体战士’(mine = my + pen)，身后绝不允许再跟小兵。",
        "radar": "【避坑雷达】：介词后面一律是宾格的地盘（between you and me），叫错名字直接出戏！"
    },
    "chap_04": {
        "concept": "数词体系",
        "metaphor": "数词就像‘尺子与标尺’：基数词是数豆子算个数，序数词是排队抢位次。大数词 hundred/thousand 像大箱子，前面有数字就是固定规格不加 s，成千上万没数字才散架加 s (thousands of)。",
        "radar": "【避坑雷达】：基变序口诀牢记八去 t 九去 e，遇到复合形容词 an 8-year-old boy，中间的 year 永远保持单数不变大！"
    },
    "chap_05": {
        "concept": "介词体系",
        "metaphor": "介词就像空间与时间的‘GPS定位锚’：at 是精准瞄准的小红点（几点钟、小地点），on 是平铺的表面或具体某一天日历，in 是包容一切的大箱子或长岁月（年/月/季节）。",
        "radar": "【避坑雷达】：泛指早晨用 in the morning，一旦有了限定词变成‘具体某一天的阳光早晨’，立刻升级为 on a sunny morning！"
    },
    "chap_06": {
        "concept": "动词与非谓语",
        "metaphor": "非谓语动词就像‘分身术’：一个句子只能有一个真正的谓语心脏。想要表达多个动作，其他动词必须戴面具——to do 代表将要去做的目标，doing 代表正在享受或正在发生的过程。",
        "radar": "【避坑雷达】：感官使役动词（make/see）主动语态把 to 藏起来，但一旦变成被动语态被押送，身上的 to 必须立刻原形毕露 (was made to work)！"
    },
    "chap_07": {
        "concept": "形容词与副词",
        "metaphor": "比较级就像‘两台天平’：A 和 B 称重找差额 (than)；最高级是‘冠军领奖台’(the -est of all)。想要修饰比较级，只能请出 much/even 这样的重磅砝码，千万别用 very！",
        "radar": "【避坑雷达】：the more..., the more... 是连环齿轮，前面齿轮转得越快，后面的齿轮转得越多！"
    },
    "chap_08": {
        "concept": "时态与语态",
        "metaphor": "时态就像‘时空穿梭机’：一般现在时是永恒规律与日常惯性；现在完成时是‘过去扔的石头在现在激起的涟漪’。瞬间动词像照相机快门（咔嚓一下就结束），不能按住快门长达三年！",
        "radar": "【避坑雷达】：buy/die/join 是快门动词，遇到 for three years 必须变成延续性状态 (have/be dead/be in)！"
    },
    "chap_09": {
        "concept": "简单句与主谓一致",
        "metaphor": "主谓一致就像‘天平校准’：左边放什么重量的主语，右边就要摆对应尺寸的谓语动词。遇到 There be 和 either...or，动词很现实，只看离自己最近的‘邻居’是谁！",
        "radar": "【避坑雷达】：with / as well as 只是插队的外带挂件，主语天平只认最前面的第一领头羊！"
    },
    "chap_10": {
        "concept": "复合句体系",
        "metaphor": "从句就像‘被收纳进大衣柜的折叠衣物’：在外面当独立问句时可以随手倒装甩开，一旦被请进主句当宾语，必须叠得整整齐齐（主语在前，动词在后，陈述语序）。",
        "radar": "【避坑雷达】：千万别在宾语从句里使用 does/did 倒装！主将从现四大从句，主句开出将来时跑车，从句只坐现在时马车！"
    }
}

def load_json_data():
    """Load KB data from local directory or remote fallback."""
    details_path = LOCAL_KB_DIR / "knowledge_details.json"
    topics_path = LOCAL_KB_DIR / "grammar_topics.json"
    textbooks_path = LOCAL_KB_DIR / "textbooks_catalog.json"

    if details_path.exists() and topics_path.exists():
        print(f"Loading data from local KB directory: {LOCAL_KB_DIR}")
        details = json.loads(details_path.read_text(encoding="utf-8"))
        topics = json.loads(topics_path.read_text(encoding="utf-8"))
        textbooks = json.loads(textbooks_path.read_text(encoding="utf-8")) if textbooks_path.exists() else {}
        return details, topics, textbooks

    print("Local KB directory not found, fetching from GitHub raw...")
    req_details = urllib.request.urlopen(f"{GITHUB_RAW_BASE}/knowledge_details.json")
    details = json.loads(req_details.read().decode("utf-8"))

    req_topics = urllib.request.urlopen(f"{GITHUB_RAW_BASE}/grammar_topics.json")
    topics = json.loads(req_topics.read().decode("utf-8"))

    try:
        req_tb = urllib.request.urlopen(f"{GITHUB_RAW_BASE}/textbooks_catalog.json")
        textbooks = json.loads(req_tb.read().decode("utf-8"))
    except Exception:
        textbooks = {}

    return details, topics, textbooks

def generate_painless_cards():
    details, topics, textbooks = load_json_data()

    cards = []
    topics_dict = details.get("topics", {})
    materials_dict = details.get("materials", {})

    # 1. Process Grammar Topics into Painless Cards
    for tid, tinfo in topics_dict.items():
        ch_prefix = tid.split("_")[0] + "_" + tid.split("_")[1] if "_" in tid else "chap_01"
        meta_info = METAPHORS_MAP.get(ch_prefix, METAPHORS_MAP["chap_01"])

        # Determine level / difficulty
        category = tinfo.get("chapter", "初中英语语法")
        name = tinfo.get("name", "语法考点")
        page_ref = tinfo.get("page_ref", "中考核心考点")
        
        # Best citation
        citations = tinfo.get("citations", [])
        sample_cite = citations[0]["text"] if citations else "Please practice with your partner."
        cite_src = citations[0]["source"] if citations else "教材例句"

        # Rules & Pitfall
        rules = tinfo.get("rules", [])
        rule_summary = " · ".join(rules[:2]) if rules else "掌握核心概念与语境用法。"
        pitfall = tinfo.get("pitfalls", meta_info["radar"])

        # Challenge step
        exercises = tinfo.get("exercises", [])
        primary_ex = exercises[0] if exercises else {
            "question": f"关于【{name}】，在真实中考语篇中应该如何识别并准确作答？",
            "options": ["A. 根据语境证据与句式规律推导", "B. 机械字面直译", "C. 凭感觉猜测", "D. 忽略时间状语"],
            "answer": 0,
            "explanation": "抓住标志词与句子核心结构，紧扣语义逻辑。"
        }

        card = {
            "card_id": f"card_{tid}",
            "topic_id": tid,
            "type": "grammar_checkpoint",
            "title": name,
            "category": category,
            "page_ref": page_ref,
            "level": "中考必考 · 无痛通关",
            "stage_1_metaphor": {
                "name": "关卡 1 · 心智隐喻破壁",
                "content": meta_info["metaphor"]
            },
            "stage_2_radar": {
                "name": "关卡 2 · 避坑雷达与口诀",
                "formula": rule_summary,
                "pitfall": pitfall,
                "citation": {
                    "source": cite_src,
                    "text": sample_cite
                }
            },
            "stage_3_challenge": {
                "name": "关卡 3 · 登顶闯关实战",
                "question": primary_ex["question"],
                "options": primary_ex["options"],
                "answer_index": primary_ex["answer"],
                "painless_hint": "💡 提示：先抓句子主干成分，注意时间状语与主谓一致，排除倒装与时态干扰项。",
                "explanation": primary_ex["explanation"]
            }
        }
        cards.append(card)

    # 2. Process Textbook Materials into Painless Reading/Application Cards
    for mid, minfo in materials_dict.items():
        exercises = minfo.get("exercises", [])
        primary_ex = exercises[0] if exercises else {
            "question": f"精读《{minfo['title']}》，下列关于课文主旨与核心句型的理解完全正确的是：",
            "options": ["A. 正确理解课文语境与核心语法", "B. 机械死记单词", "C. 脱离上下文", "D. 忽略情感主题"],
            "answer": 0,
            "explanation": "结合课文真实语篇与主旨思想进行综合推断。"
        }

        cit_list = minfo.get("citations", [])
        cit_text = cit_list[0]["content"] if cit_list else minfo.get("overview", "")
        cit_speaker = cit_list[0]["speaker"] if cit_list else "课文精读对白"

        card = {
            "card_id": f"card_{mid}",
            "topic_id": mid,
            "type": "textbook_checkpoint",
            "title": minfo.get("title"),
            "category": f"教材精读 · {minfo.get('textbook', '外研七上')}",
            "page_ref": minfo.get("source_file"),
            "level": "课本同步 · 语境闯关",
            "stage_1_metaphor": {
                "name": "关卡 1 · 真实语境浸润",
                "content": minfo.get("overview")
            },
            "stage_2_radar": {
                "name": "关卡 2 · 课文原声精读",
                "formula": "🎯 语法要点：" + " · ".join(minfo.get("grammar_focus", [])),
                "pitfall": "【精读避坑】：关注真实对话中的习惯搭配与代词指代，避免望文生义。",
                "citation": {
                    "source": cit_speaker,
                    "text": cit_text
                }
            },
            "stage_3_challenge": {
                "name": "关卡 3 · 登顶闯关实战",
                "question": primary_ex["question"],
                "options": primary_ex["options"],
                "answer_index": primary_ex["answer"],
                "painless_hint": "💡 提示：回顾课文中李明、Emma 或家庭瞬间的情感走向与时态线索。",
                "explanation": primary_ex["explanation"]
            }
        }
        cards.append(card)

    print(f"Generated {len(cards)} Painless Challenge Cards ({len(topics_dict)} grammar + {len(materials_dict)} textbooks).")
    return cards

def export_all(cards):
    """Export cards to JSON, Anki TSV, and Markdown formats."""
    data_dir = ROOT / "data"
    exports_dir = ROOT / "exports"
    data_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)

    # 1. JSON
    cards_json_path = data_dir / "cards.json"
    cards_json_path.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported JSON: {cards_json_path}")

    # 2. Anki TSV
    anki_lines = []
    for c in cards:
        front = (
            f"<div style='font-size:16px; font-weight:bold; color:#2563eb;'>【{c['category']}】{c['title']}</div>"
            f"<div style='margin-top:8px; font-size:14px;'><b>🎯 闯关挑战：</b><br>{c['stage_3_challenge']['question'].replace(chr(10), '<br>')}</div>"
            f"<div style='margin-top:6px; font-size:12px; color:#6b7280;'>{c['level']} · 难度：★★☆</div>"
        )
        back = (
            f"<div style='border-left:3px solid #3b82f6; padding-left:8px; margin-bottom:8px;'>"
            f"<b>💡 关卡1 心智隐喻：</b><br>{c['stage_1_metaphor']['content']}</div>"
            f"<div style='border-left:3px solid #f59e0b; padding-left:8px; margin-bottom:8px;'>"
            f"<b>⚡ 关卡2 避坑雷达与口诀：</b><br>{c['stage_2_radar']['formula']}<br>"
            f"<span style='color:#dc2626;'>{c['stage_2_radar']['pitfall']}</span></div>"
            f"<div style='border-left:3px solid #10b981; padding-left:8px;'>"
            f"<b>🚀 关卡3 破题答案与推导：</b><br>"
            f"<b>正确选项：</b> {c['stage_3_challenge']['options'][c['stage_3_challenge']['answer_index']]}<br>"
            f"<b>详细解析：</b> {c['stage_3_challenge']['explanation']}</div>"
        )
        # TSV: replace tabs with space in content
        safe_front = front.replace("\t", " ")
        safe_back = back.replace("\t", " ")
        anki_lines.append(f"{safe_front}\t{safe_back}\t{c['category']}")

    anki_path = exports_dir / "anki_deck.tsv"
    anki_path.write_text("\n".join(anki_lines), encoding="utf-8")
    print(f"Exported Anki TSV: {anki_path}")

    # 3. Printable Markdown
    md_lines = [
        "# 初中英语全量无痛闯关卡 (Painless English Challenge Cards)",
        "",
        "> 基于《初中英语全量知识库》动态同步生成 · 拒绝死记硬背 · 心智隐喻 + 避坑雷达 + 登顶闯关",
        "",
        "---",
        ""
    ]
    for idx, c in enumerate(cards, 1):
        md_lines.append(f"## Card #{idx:02d} | 【{c['category']}】{c['title']}")
        md_lines.append(f"- **考点标识**：`{c['topic_id']}` | **定位出处**：{c['page_ref']}")
        md_lines.append(f"### 🌊 关卡 1 · 心智隐喻破壁")
        md_lines.append(f"> {c['stage_1_metaphor']['content']}\n")
        md_lines.append(f"### ⚡ 关卡 2 · 避坑雷达与速记口诀")
        md_lines.append(f"- **规则公式**：{c['stage_2_radar']['formula']}")
        md_lines.append(f"- **避坑警示**：`{c['stage_2_radar']['pitfall']}`")
        if c['stage_2_radar'].get('citation'):
            md_lines.append(f"- **原句出处**：*{c['stage_2_radar']['citation']['source']}* —— *“{c['stage_2_radar']['citation']['text']}”*")
        md_lines.append(f"\n### 🏆 关卡 3 · 登顶闯关实战")
        md_lines.append(f"**题目**：{c['stage_3_challenge']['question']}")
        for opt in c['stage_3_challenge']['options']:
            md_lines.append(f"- {opt}")
        md_lines.append(f"\n> **正确答案**：{c['stage_3_challenge']['options'][c['stage_3_challenge']['answer_index']]}")
        md_lines.append(f"> **答案解析**：{c['stage_3_challenge']['explanation']}\n")
        md_lines.append("---\n")

    md_path = exports_dir / "cards_printable.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Exported Printable Markdown: {md_path}")

def main():
    parser = argparse.ArgumentParser(description="Painless Challenge Cards Sync Engine")
    parser.add_argument("--sync", action="store_true", default=True, help="Sync cards from Knowledge Base")
    args = parser.parse_args()

    cards = generate_painless_cards()
    export_all(cards)
    print("\n✓ Sync completed successfully! All cards updated with latest KB data.")

if __name__ == "__main__":
    main()
