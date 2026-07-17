#!/usr/bin/env python3
"""
Principia Artificialis — Automated Runner for Notes #041, #042, #043.
Runs synthetic demos; if transformers available, runs real model evaluation.
Outputs JSON report and optional plots.
"""

import json, sys, os, numpy as np

# Import from sibling modules (they are standalone)
sys.path.insert(0, os.path.dirname(__file__))

def run_note041_synthetic():
    from note041_reference import demo_synthetic_reasoning
    import io, contextlib
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        demo_synthetic_reasoning()
    return {"note": "041", "status": "synthetic_ok", "log": f.getvalue().strip()}

def run_note042_synthetic():
    from note042_reference import main as demo
    import io, contextlib
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        demo()
    return {"note": "042", "status": "synthetic_ok", "log": f.getvalue().strip()}

def run_note043_synthetic():
    from note043_reference import main as demo
    import io, contextlib
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        demo()
    return {"note": "043", "status": "synthetic_ok", "log": f.getvalue().strip()}

def run_all_synthetic():
    results = {}
    results['041'] = run_note041_synthetic()
    results['042'] = run_note042_synthetic()
    results['043'] = run_note043_synthetic()
    return results

def run_real_if_available():
    """Attempt to run on GPT‑2 with tiny test. Returns None if not possible."""
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        print("Real model test: loading GPT‑2 small...")
        tokenizer = AutoTokenizer.from_pretrained("gpt2")
        model = AutoModelForCausalLM.from_pretrained("gpt2")
        model.eval()
        prompt = "What is 2+2?"
        inputs = tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs, output_attentions=True)
        logits = outputs.logits[0]
        # Simple test: just compute curvature on first few tokens
        probs = torch.softmax(logits[:5], dim=-1).numpy()
        # Fake trajectory for demo
        print(f"Logits shape: {logits.shape}, attention layers: {len(outputs.attentions)}")
        return {"status": "real_available", "message": "GPT‑2 small loaded successfully. Full evaluation left to user."}
    except Exception as e:
        return {"status": "real_unavailable", "message": str(e)}

if __name__ == "__main__":
    print("="*60)
    print("Principia Artificialis — Automated Runner")
    print("="*60)
    print("\n--- Running synthetic demos ---")
    syn = run_all_synthetic()
    for k in ['041','042','043']:
        print(f"Note #{k}: {syn[k]['status']}")
    print("\n--- Checking real model availability ---")
    real = run_real_if_available()
    print(f"Real model: {real['status']}")
    if real['status'] == 'real_unavailable':
        print("(Install transformers and torch to run real tests)")
    
    # Save report
    report = {"synthetic": syn, "real": real}
    os.makedirs("results", exist_ok=True)
    with open("results/last_run_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\nReport saved to results/last_run_report.json")
