#!/usr/bin/env python3
"""Deterministic cover-letter structure and source-overlap checks.

This intentionally does not claim universal plagiarism detection. It compares a
letter only with the source files supplied on the command line.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path


WORD_RE = re.compile(r"[^\W_]+(?:[-'][^\W_]+)*", re.UNICODE)
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
PLACEHOLDER_RE = re.compile(
    r"\[(?:company|position|name|date|address|recipient|fill|insert|placeholder)[^\]]*\]",
    re.IGNORECASE,
)

BANNED_PHRASES = (
    "delve into",
    "tapestry",
    "revolutionize",
    "in today's fast-paced world",
    "game-changer",
    "unleash",
    "pivotal",
    "seamlessly",
    "furthermore",
    "moreover",
    "holistic",
    "testament",
    "results-driven",
    "dynamic environment",
    "unique blend",
    "leverage my skills",
    "proven track record",
    "i am the perfect candidate",
    "i am writing to apply",
    "hiermit bewerbe ich mich",
    "mit grosem interesse habe ich",
    "mit grossem interesse habe ich",
    "mit großem interesse habe ich",
    "perfekte besetzung",
    "dynamisches umfeld",
    "meine fahigkeiten gewinnbringend einsetzen",
    "meine fähigkeiten gewinnbringend einsetzen",
    "mit meiner einzigartigen kombination",
)


def normalize_words(text: str) -> list[str]:
    return [word.casefold() for word in WORD_RE.findall(text)]


def prose_sentences(text: str) -> list[str]:
    flattened = re.sub(r"^\s{0,3}(?:[#>*+-]|\d+[.)])\s+", "", text, flags=re.MULTILINE)
    return [part.strip() for part in SENTENCE_RE.split(flattened) if part.strip()]


def exact_sentence_overlaps(letter: str, source: str, minimum_words: int = 8) -> list[str]:
    source_sentences = {
        " ".join(normalize_words(sentence))
        for sentence in prose_sentences(source)
        if len(normalize_words(sentence)) >= minimum_words
    }
    matches = []
    for sentence in prose_sentences(letter):
        normalized = " ".join(normalize_words(sentence))
        if len(normalize_words(sentence)) >= minimum_words and normalized in source_sentences:
            matches.append(sentence)
    return matches


def longest_overlap(letter: str, source: str) -> tuple[int, str]:
    letter_words = normalize_words(letter)
    source_words = normalize_words(source)
    match = SequenceMatcher(None, letter_words, source_words, autojunk=False).find_longest_match()
    phrase = " ".join(letter_words[match.a : match.a + match.size])
    return match.size, phrase


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("letter", type=Path)
    parser.add_argument("--source", action="append", default=[], type=Path)
    parser.add_argument("--max-words", type=int, default=300)
    args = parser.parse_args()

    letter = args.letter.read_text(encoding="utf-8")
    raw_letter = letter
    if args.letter.suffix.lower() == ".html":
        letter_prose = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", letter, flags=re.DOTALL | re.IGNORECASE)
        letter_prose = re.sub(r"<[^>]+>", " ", letter_prose)
        letter = re.sub(r"\s+", " ", letter_prose).strip()

    lowered = letter.casefold()
    words = normalize_words(letter)
    errors: list[dict[str, object]] = []

    if len(words) > args.max_words:
        errors.append({"type": "word_limit", "count": len(words), "max": args.max_words})

    placeholders = sorted(set(PLACEHOLDER_RE.findall(raw_letter)))
    if placeholders:
        errors.append({"type": "placeholders", "matches": placeholders})

    banned = [phrase for phrase in BANNED_PHRASES if phrase in lowered]
    if banned:
        errors.append({"type": "banned_phrases", "matches": banned})

    for source_path in args.source:
        source = source_path.read_text(encoding="utf-8")
        sentence_matches = exact_sentence_overlaps(letter, source)
        overlap_count, overlap_phrase = longest_overlap(letter, source)
        if sentence_matches:
            errors.append(
                {
                    "type": "exact_sentence_overlap",
                    "source": str(source_path),
                    "matches": sentence_matches,
                }
            )
        if overlap_count >= 12:
            errors.append(
                {
                    "type": "long_contiguous_overlap",
                    "source": str(source_path),
                    "word_count": overlap_count,
                    "phrase": overlap_phrase,
                }
            )

    result = {
        "status": "pass" if not errors else "fail",
        "word_count": len(words),
        "sources_checked": len(args.source),
        "errors": errors,
        "scope": "source-overlap check only; not universal plagiarism detection",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
