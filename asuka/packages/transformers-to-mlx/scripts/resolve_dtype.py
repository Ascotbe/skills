#!/usr/bin/env python3
"""Resolve the expected runtime dtype for a model.

Resolution order:
  1. config.json fields (text_config.dtype, dtype, *.torch_dtype)
  2. Most common dtype in the safetensors header
  3. Fail loudly

Reports both the dtype and where it came from so the conversion report
can be explicit about the basis for downstream dtype checks.

Usage:
    python resolve_dtype.py <model_path>
    python resolve_dtype.py <model_path> --json
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path


SAFETENSORS_TO_DTYPE = {
    "F64": "float64",
    "F32": "float32",
    "F16": "float16",
    "BF16": "bfloat16",
}


def from_config(model_dir):
    """Return (dtype_name, source) if found in config.json, else None."""
    config_path = model_dir / "config.json"
    if not config_path.exists():
        return None
    with open(config_path) as f:
        config = json.load(f)
    text_config = config.get("text_config", {})
    candidates = [
        ("config.text_config.dtype", text_config.get("dtype")),
        ("config.text_config.torch_dtype", text_config.get("torch_dtype")),
        ("config.dtype", config.get("dtype")),
        ("config.torch_dtype", config.get("torch_dtype")),
    ]
    for source, value in candidates:
        if value:
            return value.replace("torch.", ""), source
    return None


def from_safetensors(model_dir):
    """Return (dtype_name, source) by reading the safetensors header.

    Counts dtypes across all tensors in the first shard and picks the
    most common.  This avoids being fooled by stray float32 norm weights
    in an otherwise bf16 model.
    """
    from safetensors import safe_open

    index_path = model_dir / "model.safetensors.index.json"
    if index_path.exists():
        with open(index_path) as f:
            first_shard = next(iter(json.load(f)["weight_map"].values()))
        st_path = model_dir / first_shard
    else:
        st_path = model_dir / "model.safetensors"

    if not st_path.exists():
        return None

    with safe_open(st_path, framework="numpy") as f:
        dtypes = Counter(f.get_slice(k).get_dtype() for k in f.keys())

    storage, _ = dtypes.most_common(1)[0]
    if storage not in SAFETENSORS_TO_DTYPE:
        return None

    total = sum(dtypes.values())
    dist = ", ".join(f"{k}={v}/{total}" for k, v in dtypes.most_common())
    return SAFETENSORS_TO_DTYPE[storage], f"safetensors header ({dist})"


def resolve(model_path):
    model_dir = Path(model_path)
    if not model_dir.is_dir():
        sys.exit(f"Not a directory: {model_path}")

    for resolver in (from_config, from_safetensors):
        result = resolver(model_dir)
        if result:
            dtype, source = result
            return {"dtype": dtype, "source": source}

    sys.exit(f"Could not resolve dtype for {model_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Resolve expected runtime dtype for a local model.")
    parser.add_argument("model_path", help="Path to the local model directory")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON for programmatic use")
    args = parser.parse_args()

    result = resolve(args.model_path)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"dtype: {result['dtype']}")
        print(f"source: {result['source']}")


if __name__ == "__main__":
    main()
