"""Frozen prompt templates (version-tagged; change => bump PROMPT_VERSION)."""
from __future__ import annotations

PROMPT_VERSION = "v0.2"

ABSTAIN_TOKEN = "INSUFFICIENT EVIDENCE"

SYSTEM = "You are a careful question-answering assistant."

CLOSED_BOOK = (
    "Answer the question with a short answer (a few words), no explanation. "
    "If you do not know, reply exactly: I DON'T KNOW.\n\n"
    "Question: {question}\nAnswer:"
)

GENERATOR = (
    "Answer the question using only the evidence below. If the evidence is not sufficient "
    f"to answer, reply exactly: {ABSTAIN_TOKEN}.\n"
    "Give only the short answer (a few words), no explanation.\n\n"
    "Evidence:\n{evidence}\n\n"
    "{advisory}"
    "Question: {question}\nAnswer:"
)

OPEN = (   # Study 2: no "use only the evidence" restriction; same abstention rule
    "Here is some evidence that may or may not be relevant.\n\n"
    "Evidence:\n{evidence}\n\n"
    "Question: {question}\n"
    f"If you cannot determine the answer, reply exactly: {ABSTAIN_TOKEN}. "
    "Otherwise give only the short answer (a few words), no explanation.\nAnswer:"
)

ADVISORY ="Evidence reader assessment: {verdict}.{missing}\n\n"

READER = (
    "You are the evidence reader of a question-answering system. Do NOT answer the question.\n"
    "Decide whether the evidence below contains ALL the information needed to answer it.\n"
    'Return JSON only: {{"verdict": "SUFFICIENT" or "INSUFFICIENT", '
    '"missing": "<what information is missing, empty if none>"}}\n\n'
    "Evidence:\n{evidence}\n\nQuestion: {question}\nJSON:"
)

RESTORE_FOLLOWUP = (
    "Update: the evidence channel has been restored. Full evidence:\n{evidence}\n\n"
    "Answer the question again using only the evidence. If the evidence is not sufficient, "
    f"reply exactly: {ABSTAIN_TOKEN}. Give only the short answer.\n\n"
    "Question: {question}\nAnswer:"
)


def advisory_block(verdict: str, missing: str = "", include_missing: bool = False) -> str:
    """Primary advisory = verdict only (no free text from the reader => no answer leakage)."""
    missing = missing.strip() if include_missing else ""
    return ADVISORY.format(verdict=verdict, missing=f" Missing: {missing}" if missing else "")
