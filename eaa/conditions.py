"""Evidence packets with a controllable reader->generator channel (v0.2: paragraph level).

Every HotpotQA item has exactly two gold paragraphs. The channel manipulation removes
whole gold paragraphs (all their supporting sentences, hence also their title), giving
four levels with identical meaning for every item:

  full        both gold paragraphs delivered
  drop_ans    the paragraph that carries the answer string is removed
  drop_other  the other (bridge / comparison) paragraph is removed
  drop_all    no gold evidence delivered

Design invariants (tests/test_conditions.py):
  * Same slot count and order at every level; removed gold units are replaced *in place*
    by length-matched filler units (question, position and ~token budget held fixed).
  * Removal is nested: drop_all ⊇ drop_ans, drop_other ⊇ full.
  * Filler/extra units never contain the normalized gold answer.
  * answer_in_packet is computed on the rendered packet (titles included), so the oracle
    reflects what actually crossed the channel.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from .evaluate import normalize_answer

LEVELS = ["full", "drop_ans", "drop_other", "drop_all"]
KEPT_FRAC = {"full": 1.0, "drop_ans": 0.5, "drop_other": 0.5, "drop_all": 0.0}


@dataclass
class Unit:
    title: str
    text: str
    gold: bool
    para: int = -1  # 0/1 for gold paragraphs, -1 otherwise


@dataclass
class ItemPacketPlan:
    item_id: str
    answer: str
    slots: list[Unit]
    answer_para: int                  # gold paragraph index treated as answer-bearing
    answer_para_defined: bool         # True iff the answer string occurs in exactly one gold paragraph
    filler_for_slot: dict[int, Unit] = field(default_factory=dict)

    def removed_paras(self, level: str) -> set[int]:
        a, o = self.answer_para, 1 - self.answer_para
        return {"full": set(), "drop_ans": {a}, "drop_other": {o}, "drop_all": {0, 1}}[level]

    def packet(self, level: str) -> list[Unit]:
        rm = self.removed_paras(level)
        return [self.filler_for_slot[i] if u.gold and u.para in rm else u
                for i, u in enumerate(self.slots)]

    def gold_kept_frac(self, level: str) -> float:
        units = self.packet(level)
        return sum(u.gold for u in units) / sum(u.gold for u in self.slots)

    def answer_in_packet(self, level: str) -> int | None:
        """None for yes/no answers (no string to find)."""
        a = normalize_answer(self.answer)
        if a in {"yes", "no"}:
            return None
        return int(_contains(render_units(self.packet(level)), a))


def _contains(text: str, answer_norm: str) -> bool:
    return bool(answer_norm) and f" {answer_norm} " in f" {normalize_answer(text)} "


def question_class(item: dict) -> str:
    a, q = normalize_answer(item["answer"]), normalize_answer(item["question"])
    if a in {"yes", "no"}:
        return "yesno"
    if _contains(q, a):
        return "answer_in_question"
    return "open"


def plan_item(
    item: dict,
    seed: int,
    n_extra: int,
    length_fn: Callable[[str], int],
) -> ItemPacketPlan | None:
    """Return None if the item cannot be built cleanly (logged as exclusion)."""
    rng = random.Random(f"{seed}-{item['id']}")
    ans = normalize_answer(item["answer"])
    by_title = {p["title"]: p["sentences"] for p in item["context"]}
    gold_titles = list(dict.fromkeys(sf["title"] for sf in item["supporting_facts"]))
    if len(gold_titles) != 2:
        return None

    gold: list[Unit] = []
    seen = set()
    for sf in item["supporting_facts"]:
        sents = by_title.get(sf["title"], [])
        key = (sf["title"], sf["sent_id"])
        if sf["sent_id"] < len(sents) and key not in seen and sents[sf["sent_id"]].strip():
            seen.add(key)
            gold.append(Unit(sf["title"], sents[sf["sent_id"]].strip(), True,
                             gold_titles.index(sf["title"])))
    if {u.para for u in gold} != {0, 1}:
        return None

    # Which gold paragraph carries the answer (title or delivered sentences)?
    hits = [p for p in (0, 1)
            if ans not in {"yes", "no"}
            and _contains(gold_titles[p] + " " + " ".join(u.text for u in gold if u.para == p), ans)]
    answer_para_defined = len(hits) == 1
    answer_para = hits[0] if answer_para_defined else rng.randrange(2)

    pool = [
        Unit(p["title"], s.strip(), False)
        for p in item["context"]
        if p["title"] not in gold_titles
        for s in p["sentences"]
        if s.strip() and not _contains(s, ans) and not _contains(p["title"], ans)
    ] if ans not in {"yes", "no"} else [
        Unit(p["title"], s.strip(), False)
        for p in item["context"] if p["title"] not in gold_titles
        for s in p["sentences"] if s.strip()
    ]
    rng.shuffle(pool)
    if len(pool) < n_extra + len(gold):
        return None

    extras, pool = pool[:n_extra], pool[n_extra:]
    slots = gold + extras
    rng.shuffle(slots)

    pool_lens = [length_fn(f"{u.title} {u.text}") for u in pool]
    used: set[int] = set()
    filler_for_slot: dict[int, Unit] = {}
    for i, u in enumerate(slots):
        if not u.gold:
            continue
        target = length_fn(f"{u.title} {u.text}")
        best = min((j for j in range(len(pool)) if j not in used),
                   key=lambda j: (abs(pool_lens[j] - target), j))
        used.add(best)
        filler_for_slot[i] = pool[best]

    return ItemPacketPlan(item["id"], item["answer"], slots, answer_para,
                          answer_para_defined, filler_for_slot)


def render_units(units: list[Unit]) -> str:
    return "\n".join(f"[e{k}] ({u.title}) {u.text}" for k, u in enumerate(units, 1))
