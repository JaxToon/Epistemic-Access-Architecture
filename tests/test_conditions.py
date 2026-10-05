import pytest

from eaa.conditions import LEVELS, plan_item, question_class
from eaa.evaluate import is_correct, label, normalize_answer, parse_reader, response_class


def _item(answer="France"):
    ctx = [{"title": "Gold A", "sentences": ["Alice was born in Lyon.", "She was a painter."]},
           {"title": "Gold B", "sentences": ["Lyon is a city in France.", "It hosts a museum."]}]
    for k in range(6):
        ctx.append({"title": f"Distractor {k}",
                    "sentences": [f"Distractor {k} sentence {j} about something else." for j in range(3)]})
    return {"id": "x1", "question": "Which country was Alice born in?", "answer": answer,
            "context": ctx,
            "supporting_facts": [{"title": "Gold A", "sent_id": 0}, {"title": "Gold B", "sent_id": 0},
                                 {"title": "Gold A", "sent_id": 1}]}


def wc(s):
    return len(s.split())


@pytest.fixture
def plan():
    p = plan_item(_item(), seed=1, n_extra=4, length_fn=wc)
    assert p is not None
    return p


def test_slot_count_constant(plan):
    assert len({len(plan.packet(lv)) for lv in LEVELS}) == 1


def test_answer_paragraph_identified(plan):
    assert plan.answer_para_defined
    assert plan.answer_in_packet("full") == 1
    assert plan.answer_in_packet("drop_ans") == 0      # answer gone with its paragraph
    assert plan.answer_in_packet("drop_other") == 1
    assert plan.answer_in_packet("drop_all") == 0


def test_levels_and_nesting(plan):
    gold = {lv: {i for i, u in enumerate(plan.packet(lv)) if u.gold} for lv in LEVELS}
    assert gold["drop_all"] == set()
    assert gold["drop_ans"] <= gold["full"] and gold["drop_other"] <= gold["full"]
    assert gold["drop_ans"].isdisjoint(gold["drop_other"])
    assert plan.gold_kept_frac("full") == 1.0 and plan.gold_kept_frac("drop_all") == 0.0


def test_non_gold_slots_unchanged(plan):
    full = plan.packet("full")
    for lv in LEVELS:
        for i, u in enumerate(plan.packet(lv)):
            if not full[i].gold:
                assert u == full[i]


def test_deterministic():
    a = plan_item(_item(), seed=1, n_extra=4, length_fn=wc)
    b = plan_item(_item(), seed=1, n_extra=4, length_fn=wc)
    assert [u.text for u in a.packet("drop_ans")] == [u.text for u in b.packet("drop_ans")]


def test_no_answer_in_fillers():
    it = _item()
    it["context"][2]["sentences"][0] = "France is mentioned here."
    p = plan_item(it, seed=1, n_extra=4, length_fn=wc)
    assert not any("France" in u.text for u in p.packet("drop_all"))


def test_question_class():
    assert question_class(_item("yes")) == "yesno"
    assert question_class(_item("Alice")) == "answer_in_question"
    assert question_class(_item()) == "open"


def test_labels():
    assert normalize_answer("The France!") == "france"
    assert response_class("INSUFFICIENT EVIDENCE.") == "abstain"
    assert response_class("The evidence does not mention her birthplace.") == "non_answer"
    assert response_class("The Unknown Soldier") == "substantive"      # no substring false positive
    assert is_correct("Paris, France", "France") and not is_correct("Michelle Obama", "Barack Obama")
    assert is_correct("Yes, both are", "yes")
    assert label("Germany", "France")["hallucination"] == 1
    assert label("INSUFFICIENT EVIDENCE", "France")["hallucination"] == 0
    assert parse_reader('{"verdict": "INSUFFICIENT", "missing": "x"}') == ("INSUFFICIENT", "x")
    assert parse_reader("garbage")[0] == "PARSE_ERROR"
