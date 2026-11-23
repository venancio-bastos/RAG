"""Check the Markdown chunker on the real corpus (not part of the project).

Run from the project root:  uv run python scratch/test_markdown_chunker.py
"""

import json
import os
import sys

sys.path.insert(0, ".")
from src.chunking import chunk_markdown  # noqa: E402

RAW = "data/raw/vllm-0.10.1"
DATASET = "data/datasets/AnsweredQuestions/dataset_docs_public.json"
MAX = 2000


def iou(a_start: int, a_end: int, b_start: int, b_end: int) -> float:
    """Intersection over union of two character ranges."""
    inter = max(0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    return inter / union if union else 0.0


# 1. Chunk every .md and .txt file and check the two golden rules.
chunks_by_file = {}
for folder, _, files in os.walk(RAW):
    for name in files:
        if name.endswith((".md", ".txt")):
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            chunks = chunk_markdown(text, path, MAX)
            for c in chunks:
                assert text[c.start:c.end] == c.text, f"offsets: {path}"
                assert c.end - c.start <= MAX, f"too big: {path}"
            chunks_by_file[path] = chunks

total = sum(len(c) for c in chunks_by_file.values())
print(f"{len(chunks_by_file)} files -> {total} chunks, all rules OK")

# 2. Show the chunks of lora.md.
print("\nlora.md:")
for c in chunks_by_file[f"{RAW}/docs/features/lora.md"]:
    title = c.text.strip().splitlines()[0][:50]
    print(f"  {c.start:6} -> {c.end:6} ({c.end - c.start:4})  {title}")

# 3. Best recall possible: does SOME chunk match each answer?
with open(DATASET, encoding="utf-8") as f:
    questions = json.load(f)["rag_questions"]
found = 0
for q in questions:
    src = q["sources"][0]
    for c in chunks_by_file.get(src["file_path"], []):
        if iou(c.start, c.end, src["first_character_index"],
               src["last_character_index"]) >= 0.05:
            found += 1
            break
print(f"\nAnswers covered by at least one chunk: {found}/{len(questions)}")
