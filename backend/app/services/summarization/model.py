import logging
import re
from pathlib import Path

import preprocess
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize pipeline and tokenizer once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
tokenizer = summarizer.tokenizer
# model_max_length is the tokenizer/model encoder max tokens. Reserve a small margin.
MODEL_MAX = getattr(tokenizer, "model_max_length", 1024)
SAFETY_MARGIN = 8
EFFECTIVE_MAX = max(32, MODEL_MAX - SAFETY_MARGIN)


def generate_summary(text, max_length=150, min_length=50):
  return summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)[0]["summary_text"]


def split_to_model_limit(text: str, tokenizer, max_tokens: int = EFFECTIVE_MAX):
  """Yield pieces of `text` whose tokenized length <= max_tokens.

  Strategy: split into sentences, greedily accumulate sentences until the tokenized
  length would exceed max_tokens. If a single sentence is too long, fall back to
  word-level greedy splitting.
  """
  if not text or not text.strip():
    return

  sentences = re.split(r'(?<=[\.\?\!])\s+', text)
  buffer = []

  def flush_buffer():
    if buffer:
      yield " ".join(buffer).strip()

  for sent in sentences:
    if not sent.strip():
      continue
    candidate = " ".join(buffer + [sent]).strip()
    toks = tokenizer(candidate, return_tensors="pt", truncation=False)
    length = toks["input_ids"].shape[1]
    if length <= max_tokens:
      buffer.append(sent)
      continue

    # Candidate would overflow. Flush current buffer first.
    if buffer:
      yield from flush_buffer()
      buffer = []

    # Now handle `sent` itself which might be too long.
    toks_sent = tokenizer(sent, return_tensors="pt", truncation=False)
    if toks_sent["input_ids"].shape[1] <= max_tokens:
      yield sent.strip()
      continue

    # Sentence too long: fallback to word-level greedy splitting.
    words = sent.split()
    start = 0
    while start < len(words):
      # grow window until token length would exceed max_tokens
      end = start
      last_valid_end = None
      while end < len(words):
        piece = " ".join(words[start:end + 1])
        toks_piece = tokenizer(piece, return_tensors="pt", truncation=False)
        if toks_piece["input_ids"].shape[1] <= max_tokens:
          last_valid_end = end + 1
          end += 1
        else:
          break
      if last_valid_end is None:
        # single word tokenized too long (very rare). Skip it.
        logger.warning("A single word tokenized longer than max_tokens; skipping word: %s", words[start])
        start += 1
      else:
        yield " ".join(words[start:last_valid_end]).strip()
        start = last_valid_end

  # flush remaining buffer
  if buffer:
    yield " ".join(buffer).strip()


def main():
  # Load and preprocess the document (path relative to project root as before)
  file_path = Path("backend/app/services/summarization/a.pdf")
  text = preprocess.preprocess_input(file_path)

  # Save raw cleaned text (as before)
  Path("backend/app/services/summarization").mkdir(parents=True, exist_ok=True)
  with open("backend/app/services/summarization/demofile.txt", "a", encoding="utf-8") as f:
    f.write(text + "\n")

  summaries = []
  for chunk in preprocess.chunk_text(text, max_words=400):
    # split chunk into model-sized subchunks
    try:
      for sub in split_to_model_limit(chunk, tokenizer, EFFECTIVE_MAX):
        if not sub or not sub.strip():
          continue
        # final safety check; if still too long, truncate with tokenizer
        tok_len = tokenizer(sub, return_tensors="pt", truncation=False)["input_ids"].shape[1]
        if tok_len > MODEL_MAX:
          logger.warning("Subchunk token length %d > MODEL_MAX %d, truncating", tok_len, MODEL_MAX)
          toks = tokenizer(sub, truncation=True, max_length=EFFECTIVE_MAX, return_tensors="pt")
          sub = tokenizer.decode(toks["input_ids"][0], skip_special_tokens=True)

        try:
          s = generate_summary(sub, max_length=150, min_length=50)
          summaries.append(s)
        except Exception:
          logger.exception("Failed to summarize a subchunk; skipping.")
    except Exception:
      logger.exception("Failed while splitting/summarizing chunk; skipping chunk.")

  final_summary = " ".join(summaries)
  with open("backend/app/services/summarization/demofile1.txt", "a", encoding="utf-8") as f:
    f.write(final_summary + "\n")


if __name__ == "__main__":
  main()
