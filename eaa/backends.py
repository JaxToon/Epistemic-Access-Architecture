"""Generation backends. All decoding is greedy and frozen by config."""
from __future__ import annotations

import json
import re

Messages = list[dict]


class MockBackend:
    """Deterministic, GPU-free backend for pipeline tests."""

    name = "mock"

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def prompt_tokens(self, messages: Messages) -> int:
        return sum(self.count_tokens(m["content"]) for m in messages)

    def generate(self, batch: list[Messages], max_new_tokens: int) -> list[str]:
        outs = []
        for msgs in batch:
            last = msgs[-1]["content"]
            if last.rstrip().endswith("JSON:"):
                n_ev = len(re.findall(r"^\[e\d+\]", last, flags=re.M))
                outs.append(json.dumps({"verdict": "SUFFICIENT" if n_ev % 2 else "INSUFFICIENT",
                                        "missing": ""}))
            elif "Evidence:" in last:
                m = re.search(r"\[e1\] \((.*?)\)", last)
                outs.append(m.group(1) if m else "INSUFFICIENT EVIDENCE")
            else:
                outs.append("I DON'T KNOW")
        return outs

    def score_continuations(self, batch: list[Messages], prefix: str, options: list[str]) -> list[list[float]]:
        return [[-1.0 - (len(m[-1]["content"]) % 3 == i) for i in range(len(options))] for m in batch]


class HFBackend:
    def __init__(self, model_id: str, dtype: str = "float16", load_in_4bit: bool = False):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.name = model_id
        self.tok = AutoTokenizer.from_pretrained(model_id, padding_side="left")
        if self.tok.pad_token is None:
            self.tok.pad_token = self.tok.eos_token
        kwargs = {"device_map": "cuda"}
        if load_in_4bit:
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16, bnb_4bit_quant_type="nf4"
            )
        else:
            kwargs["dtype"] = getattr(torch, dtype)
        self.model = AutoModelForCausalLM.from_pretrained(model_id, **kwargs).eval()
        self.torch = torch

    def count_tokens(self, text: str) -> int:
        return len(self.tok(text, add_special_tokens=False)["input_ids"])

    def _render(self, messages: Messages) -> str:
        return self.tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    def prompt_tokens(self, messages: Messages) -> int:
        return self.count_tokens(self._render(messages))

    def generate(self, batch: list[Messages], max_new_tokens: int) -> list[str]:
        texts = [self._render(m) for m in batch]
        enc = self.tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        with self.torch.inference_mode():
            out = self.model.generate(
                **enc,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
                pad_token_id=self.tok.pad_token_id,
            )
        gen = out[:, enc["input_ids"].shape[1]:]
        return [s.strip() for s in self.tok.batch_decode(gen, skip_special_tokens=True)]

    def score_continuations(self, batch: list[Messages], prefix: str, options: list[str]) -> list[list[float]]:
        """Sum log-prob of each option string continuing (assistant turn + prefix).
        Used for the reader's P(SUFFICIENT): a continuous epistemic score instead of a hard verdict."""
        torch = self.torch
        bases = [self._render(m) + prefix for m in batch]
        n_base = [len(self.tok(b, add_special_tokens=False)["input_ids"]) for b in bases]
        texts = [b + o for b in bases for o in options]
        self.tok.padding_side = "right"
        try:
            enc = self.tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
        finally:
            self.tok.padding_side = "left"
        ids, mask = enc["input_ids"], enc["attention_mask"]
        scores = []
        with torch.inference_mode():
            # only project the few continuation positions through lm_head (full-vocab logits over
            # the whole prompt would be ~GBs and spill out of VRAM)
            hidden = self.model.model(**enc).last_hidden_state
            for r in range(len(texts)):
                nb, end = n_base[r // len(options)], int(mask[r].sum())
                pos = torch.arange(nb, end, device=ids.device)
                logp = torch.log_softmax(self.model.lm_head(hidden[r, pos - 1]).float(), dim=-1)
                scores.append(float(logp[torch.arange(len(pos)), ids[r, pos]].sum()))
        return [scores[i * len(options):(i + 1) * len(options)] for i in range(len(batch))]


def make_backend(cfg: dict):
    if cfg["backend"] == "mock":
        return MockBackend()
    return HFBackend(cfg["model_id"], cfg.get("dtype", "float16"), cfg.get("load_in_4bit", False))
