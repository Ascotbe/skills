#!/usr/bin/env python3
"""
Debug script for transformers model - compare with MLX implementation.
Analyzes embeddings, logits, and top predictions.

Usage: python debug_transformers.py <model_path> [prompt]
"""

import sys
import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def debug_transformers(model_path: str, prompt: str = "The"):
    print("=== TRANSFORMERS DEBUG ===")
    print(f"Model: {model_path}")
    print(f"Prompt: '{prompt}'")

    # Load model and tokenizer
    print("\nLoading model...")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, dtype=torch.float32)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Model type: {model.config.model_type}")

    # Display key config values
    with open(f'{model_path}/config.json', 'r') as f:
        config = json.load(f)

    print("\nKey config values:")
    key_params = [
        'embedding_multiplier', 'attention_multiplier', 'logits_scaling',
        'residual_multiplier', 'position_embedding_type', 'layer_types',
        'rope_interleave', 'rope_theta', 'rms_norm_eps'
    ]
    for param in key_params:
        if param in config:
            value = config[param]
            if isinstance(value, list) and len(value) > 10:
                print(f"  {param}: {value[:10]}... ({len(value)} items)")
            else:
                print(f"  {param}: {value}")

    # Tokenize
    tokens = tokenizer.encode(prompt)
    print(f"\nTokens: {tokens}")

    # Forward pass
    inputs = torch.tensor([tokens])

    with torch.no_grad():
        # Embeddings analysis
        if hasattr(model.model, 'embed_tokens'):
            embeddings = model.model.embed_tokens(inputs)
            print(f"\nEmbedding analysis:")
            print(f"  Shape: {embeddings.shape}")
            print(f"  Mean: {embeddings.mean().item():.6f}")
            print(f"  Std: {embeddings.std().item():.6f}")

            # Check for embedding multiplier
            if hasattr(model.config, 'embedding_multiplier'):
                mult = model.config.embedding_multiplier
                scaled = embeddings * mult
                print(f"  After embedding_multiplier ({mult}):")
                print(f"    Mean: {scaled.mean().item():.6f}")
                print(f"    Std: {scaled.std().item():.6f}")

        # Full forward pass
        outputs = model(inputs)
        logits = outputs.logits

        print(f"\nLogits analysis:")
        print(f"  Shape: {logits.shape}")
        print(f"  Mean: {logits.mean().item():.6f}")
        print(f"  Std: {logits.std().item():.6f}")
        print(f"  Min: {logits.min().item():.6f}")
        print(f"  Max: {logits.max().item():.6f}")

        # Top predictions
        last_logits = logits[0, -1, :]
        probs = torch.softmax(last_logits, dim=-1)
        top_probs, top_indices = torch.topk(probs, 10)

        print(f"\nTop 10 predictions:")
        for i, (idx, prob) in enumerate(zip(top_indices, top_probs)):
            token_text = repr(tokenizer.decode([idx.item()]))
            print(f"  {i+1:2d}. Token {idx.item():6d}: {token_text:20s} (prob: {prob.item():.6f})")

    return {
        'tokens': tokens,
        'top_indices': top_indices.tolist(),
        'top_probs': top_probs.tolist(),
        'logits_mean': logits.mean().item(),
        'logits_std': logits.std().item(),
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_transformers.py <model_path> [prompt]")
        sys.exit(1)

    model_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "The"

    results = debug_transformers(model_path, prompt)
    print(f"\n=== SUMMARY ===")
    print(f"Top token: {results['top_indices'][0]} (prob: {results['top_probs'][0]:.6f})")
    print(f"Logits mean: {results['logits_mean']:.6f}")
    print(f"Logits std: {results['logits_std']:.6f}")
