"""ESM-2 layer-17 per-residue embedding extraction (frozen weights)."""
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel


def load_model(model_name="facebook/esm2_t33_650M_UR50D", device="cuda"):
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, output_hidden_states=True).to(device).eval()
    return tok, model


@torch.no_grad()
def embed_layer(tok, model, seq, layer=17, device="cuda"):
    """Per-residue hidden states from a single layer. ESM adds <cls> at position 0
    and <eos> at L+1, so residues are tokens[1:L+1]; the assert is the guard against
    a silent off-by-one that would misalign every label."""
    enc = tok(seq, return_tensors="pt").to(device)
    hs = model(**enc).hidden_states[layer][0]          # [T, H], T = L + cls + eos
    res = hs[1:len(seq) + 1].float().cpu().numpy()
    assert res.shape[0] == len(seq), f"residue/label misalignment: {res.shape[0]} vs {len(seq)}"
    return res.astype(np.float16)
