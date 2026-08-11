#!/usr/bin/env python3
"""
Compare full text generation between transformers and MLX.
Uses chat templates when available.

Usage: python compare_generation.py <model_path> [--message "Your question here"]
"""

import sys
import gc
import time
import argparse


def run_transformers_generation(model_path: str, messages: list, max_new_tokens: int):
    """Run generation with transformers."""
    print("=" * 60)
    print("TRANSFORMERS GENERATION")
    print("=" * 60)

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float32)
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    # Try chat template, fall back to raw prompt
    try:
        inputs = tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True,
        ).to(model.device)
        print("Using chat template")
    except Exception as e:
        print(f"Chat template not available ({e}), using raw text")
        text = messages[0]["content"] if messages else "Hello"
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

    print(f"Input token count: {inputs['input_ids'].shape[1]}")

    print("\nGenerating...")
    start = time.time()
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False,
    )
    gen_time = time.time() - start

    new_tokens = outputs[0][inputs['input_ids'].shape[1]:]
    response = tokenizer.decode(new_tokens, skip_special_tokens=True)

    print(f"Generation time: {gen_time:.1f}s")
    print(f"Generated {len(new_tokens)} tokens ({len(new_tokens)/gen_time:.1f} tok/s)")
    print(f"\n--- TRANSFORMERS RESPONSE ---\n{response}\n")

    # Cleanup to free memory for MLX
    del model
    del inputs
    del outputs
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return response


def run_mlx_generation(model_path: str, messages: list, max_new_tokens: int):
    """Run generation with MLX."""
    print("=" * 60)
    print("MLX GENERATION")
    print("=" * 60)

    import mlx.core as mx
    from mlx_lm import load, generate

    print(f"Loading MLX model from {model_path}...")
    start = time.time()
    model, tokenizer = load(model_path)
    print(f"Model loaded in {time.time() - start:.1f}s")

    # Try chat template, fall back to raw prompt
    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        print("Using chat template")
    except Exception as e:
        print(f"Chat template not available ({e}), using raw text")
        prompt = messages[0]["content"] if messages else "Hello"

    print(f"\nFormatted prompt:\n{repr(prompt[:200])}{'...' if len(prompt) > 200 else ''}\n")

    # Greedy generation
    sampler = lambda x: mx.argmax(x, axis=-1)
    print("Generating...")
    start = time.time()
    response = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=max_new_tokens,
        sampler=sampler,
        verbose=True,
    )
    gen_time = time.time() - start

    print(f"\nTotal generation time: {gen_time:.1f}s")
    print(f"\n--- MLX RESPONSE ---\n{response}\n")

    return response


def main():
    parser = argparse.ArgumentParser(description="Compare generation between transformers and MLX")
    parser.add_argument("model_path", help="Path to the model")
    parser.add_argument("--message", "-m", default="What is 2 + 2?", help="User message to send")
    parser.add_argument("--max-tokens", "-t", type=int, default=100, help="Max new tokens to generate")
    args = parser.parse_args()

    messages = [{"role": "user", "content": args.message}]

    print("Transformers vs MLX Generation Comparison")
    print(f"Model: {args.model_path}")
    print(f"Message: {args.message}")
    print(f"Max new tokens: {args.max_tokens}")
    print()

    # Run transformers first (uses more memory)
    tf_response = run_transformers_generation(args.model_path, messages, args.max_tokens)

    print("\n" + "=" * 60 + "\n")

    # Run MLX
    mlx_response = run_mlx_generation(args.model_path, messages, args.max_tokens)

    # Summary
    print("=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    print(f"\nQuestion: {args.message}")
    print(f"\nTransformers ({len(tf_response)} chars):\n  {tf_response[:500]}")
    print(f"\nMLX ({len(mlx_response)} chars):\n  {mlx_response[:500]}")

    if tf_response.strip() == mlx_response.strip():
        print("\nRESULT: Responses are IDENTICAL")
    else:
        print("\nRESULT: Responses DIFFER (may still be semantically similar)")


if __name__ == "__main__":
    main()
