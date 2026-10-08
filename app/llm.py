"""N-ATLaS language model: through a vLLM server, in-process with transformers,
or a mock for working without a GPU."""

import logging
import threading

import httpx

from .config import Settings

log = logging.getLogger(__name__)


class VllmLLM:
    """Calls `vllm serve NCAIR1/N-ATLaS` through its OpenAI-compatible API."""

    def __init__(self, settings: Settings):
        self.url = settings.vllm_url.rstrip("/") + "/chat/completions"
        self.model = settings.llm_model
        self.client = httpx.Client(timeout=120)

    def chat(self, messages: list[dict], max_tokens: int = 400) -> str:
        r = self.client.post(self.url, json={
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0,  # deterministic answers are easier to check
        })
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


class TransformersLLM:
    """Loads N-ATLaS inside this process (slower than vLLM, fewer moving parts)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.tok = None
        self.model = None
        self.lock = threading.Lock()  # one generation at a time on the in-process model

    def _load(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        s = self.settings
        log.info("Loading %s", s.llm_model)
        kwargs = {"device_map": "auto", "token": s.hf_token or None}
        if s.load_in_4bit:
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.bfloat16
            )
        else:
            kwargs["torch_dtype"] = torch.bfloat16
        self.tok = AutoTokenizer.from_pretrained(s.llm_model, token=kwargs["token"])
        self.model = AutoModelForCausalLM.from_pretrained(s.llm_model, **kwargs).eval()

    def chat(self, messages: list[dict], max_tokens: int = 400) -> str:
        with self.lock:
            return self._chat(messages, max_tokens)

    def _chat(self, messages: list[dict], max_tokens: int) -> str:
        import torch

        if self.model is None:
            self._load()
        tok = self.tok
        inputs = tok.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
        ).to(self.model.device)
        eos = [tok.eos_token_id]
        eot = tok.convert_tokens_to_ids("<|eot_id|>")  # Llama-3 end-of-turn token
        if isinstance(eot, int) and eot != tok.unk_token_id:
            eos.append(eot)
        with torch.no_grad():
            out = self.model.generate(
                **inputs, max_new_tokens=max_tokens, do_sample=False,
                eos_token_id=eos, pad_token_id=tok.eos_token_id,
            )
        return tok.decode(out[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True).strip()


class MockLLM:
    """Predictable outputs for each pipeline step, keyed on the prompt's task line."""

    def chat(self, messages: list[dict], max_tokens: int = 400) -> str:
        system = messages[0]["content"]
        user = messages[-1]["content"]
        if system.startswith("TASK: translate"):
            return f"(translated) {user}"
        if system.startswith("TASK: route"):
            return "money"
        return "1. This is a mock answer. 2. Run with a real model to get real answers. (Source: mock)"


def make_llm(settings: Settings):
    if settings.mock:
        return MockLLM()
    if settings.llm_backend == "transformers":
        return TransformersLLM(settings)
    return VllmLLM(settings)
