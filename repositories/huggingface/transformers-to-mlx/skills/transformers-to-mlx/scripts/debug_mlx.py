#!/usr/bin/env python3
"""
Debug script for MLX model - compare with transformers implementation.
Analyzes embeddings, logits, and top predictions.

Usage: python debug_mlx.py <model_path> [prompt]
"""

import sys
import mlx.core as mx
from mlx_lm import load

def debug_mlx(model_path: str, prompt: str = "The"):
    print("=== MLX DEBUG ===")
    print(f"Model: {model_path}")
    print(f"Prompt: '{prompt}'")

    # Load model and tokenizer
    print("\nLoading model...")
    model, tokenizer = load(model_path)

    print(f"Model type: {model.args.model_type}")

    # Display key config values
    print("\nKey config values:")
    config_attrs = [
        'embedding_multiplier', 'attention_multiplier', 'logits_scaling',
        'residual_multiplier', 'position_embedding_type', 'layer_types',
        'rope_interleave', 'rope_theta', 'rms_norm_eps'
    ]
    for attr in config_attrs:
        if hasattr(model.args, attr):
            value = getattr(model.args, attr)
            if isinstance(value, list) and len(value) > 10:
                print(f"  {attr}: {value[:10]}... ({len(value)} items)")
            else:
                print(f"  {attr}: {value}")

    # Tokenize
    tokens = tokenizer.encode(prompt)
    print(f"\nTokens: {tokens}")

    # Forward pass
    inputs = mx.array([tokens])

    # Embeddings analysis
    if hasattr(model.model, 'embed_tokens'):
        embeddings = model.model.embed_tokens(inputs)
        print(f"\nEmbedding analysis:")
        print(f"  Shape: {embeddings.shape}")
        print(f"  Mean: {mx.mean(embeddings).item():.6f}")
        print(f"  Std: {mx.std(embeddings).item():.6f}")

        # Check for embedding multiplier
        if hasattr(model.model, 'embedding_multiplier'):
            mult = model.model.embedding_multiplier
            scaled = embeddings * mult
            print(f"  After embedding_multiplier ({mult}):")
            print(f"    Mean: {mx.mean(scaled).item():.6f}")
            print(f"    Std: {mx.std(scaled).item():.6f}")

    # Full forward pass
    logits = model(inputs)

    print(f"\nLogits analysis:")
    print(f"  Shape: {logits.shape}")
    print(f"  Mean: {mx.mean(logits).item():.6f}")
    print(f"  Std: {mx.std(logits).item():.6f}")
    print(f"  Min: {mx.min(logits).item():.6f}")
    print(f"  Max: {mx.max(logits).item():.6f}")

    # Top predictions
    last_logits = logits[0, -1, :]
    probs = mx.softmax(last_logits)
    top_indices = mx.argpartition(-last_logits, 10)[:10]

    print(f"\nTop 10 predictions:")
    for i, idx in enumerate(top_indices):
        idx_val = idx.item()
        prob = probs[idx].item()
        token_text = repr(tokenizer.decode([idx_val]))
        print(f"  {i+1:2d}. Token {idx_val:6d}: {token_text:20s} (prob: {prob:.6f})")

    return {
        'tokens': tokens,
        'top_indices': [idx.item() for idx in top_indices],
        'top_probs': [probs[idx].item() for idx in top_indices],
        'logits_mean': mx.mean(logits).item(),
        'logits_std': mx.std(logits).item(),
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_mlx.py <model_path> [prompt]")
        sys.exit(1)

    model_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else "The"

    results = debug_mlx(model_path, prompt)
    print(f"\n=== SUMMARY ===")
    print(f"Top token: {results['top_indices'][0]} (prob: {results['top_probs'][0]:.6f})")
    print(f"Logits mean: {results['logits_mean']:.6f}")
    print(f"Logits std: {results['logits_std']:.6f}")
