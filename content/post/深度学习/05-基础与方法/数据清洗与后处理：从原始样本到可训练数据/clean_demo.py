"""Small, auditable cleaner for natural-language, single-turn QA JSONL.

Python 3.9+, standard library only. This does not verify answer correctness.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import platform
import unicodedata


FIELDS = {"id", "source_id", "split", "prompt", "answer"}
RULE_VERSION = "single-turn-qa-v1"


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("duplicate_json_key")
        obj[key] = value
    return obj


def reject_constant(value):
    raise ValueError("nonstandard_json_number")


def strict_loads(text):
    return json.loads(
        text, object_pairs_hook=unique_object, parse_constant=reject_constant,
    )


def normalize_text(text):
    # This policy is for natural-language QA, not whitespace-sensitive code.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", text).strip()


def clean_lines(lines, blocked_sources):
    candidates, audit = [], []
    input_rows = 0

    def log(line, row, decision, reason=None, kept_id=None):
        event = {"line": line, "decision": decision}
        if row is not None:
            event.update(id=row["id"], source_id=row["source_id"])
        if reason:
            event["reason"] = reason
        if kept_id:
            event["kept_id"] = kept_id
        audit.append(event)

    for line, raw in enumerate(lines, 1):
        input_rows += 1
        try:
            row = strict_loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError, RecursionError) as error:
            reason = str(error) if str(error) in {
                "duplicate_json_key", "nonstandard_json_number",
            } else "invalid_encoding_or_json"
            log(line, None, "rejected", reason)
            continue
        if (not isinstance(row, dict) or set(row) != FIELDS
                or any(not isinstance(row[key], str) for key in FIELDS)):
            log(line, None, "rejected", "schema_invalid")
            continue
        try:
            for key in FIELDS:
                row[key].encode("utf-8")
        except UnicodeEncodeError:
            log(line, None, "rejected", "invalid_unicode_scalar")
            continue
        if any(not row[key] or row[key] != row[key].strip()
               for key in ("id", "source_id", "split")):
            log(line, None, "rejected", "schema_invalid")
            continue
        row["prompt"] = normalize_text(row["prompt"])
        row["answer"] = normalize_text(row["answer"])
        if not row["prompt"] or not row["answer"]:
            log(line, row, "rejected", "empty_text")
        elif row["split"] != "train":
            log(line, row, "rejected", "non_train_input")
        elif row["source_id"] in blocked_sources:
            log(line, row, "rejected", "holdout_source_overlap")
        else:
            candidates.append((line, row))

    id_counts = Counter(row["id"] for _, row in candidates)
    groups = defaultdict(list)
    for line, row in candidates:
        if id_counts[row["id"]] > 1:
            log(line, row, "rejected", "duplicate_id")
        else:
            groups[row["prompt"]].append((line, row))

    kept = []
    for group in groups.values():
        if len({row["answer"] for _, row in group}) > 1:
            for line, row in group:
                log(line, row, "rejected", "conflicting_target")
            continue
        first_line, representative = group[0]
        output = dict(representative)
        output["provenance"] = [
            {"id": row["id"], "source_id": row["source_id"], "line": line}
            for line, row in group
        ]
        kept.append(output)
        log(first_line, representative, "accepted")
        for line, row in group[1:]:
            log(line, row, "rejected", "exact_duplicate", representative["id"])

    audit.sort(key=lambda event: event["line"])
    reasons = Counter(e["reason"] for e in audit if e["decision"] == "rejected")
    report = {
        "input_rows": input_rows, "kept_rows": len(kept),
        "rejected_rows": sum(reasons.values()),
        "reason_counts": dict(sorted(reasons.items())),
    }
    return kept, audit, report


def demo_lines():
    def row(i, prompt, answer="教学答案", source=None, split="train"):
        return {"id": i, "source_id": source or "doc-" + i,
                "split": split, "prompt": prompt, "answer": answer}

    rows = [
        row("ok-1", " café 的首字母是什么？ ", "c"),
        row("dup-1", "cafe\u0301 的首字母是什么？", "c"),
        row("conflict-1", "教学题：2 + 2 等于几？", "4"),
        row("conflict-2", "教学题：2 + 2 等于几？", "5"),
        row("bad-schema", "请分类", answer=123),
        row("heldout", "隔离来源的题目", source="holdout-doc"),
        row("validation", "验证集题目", split="validation"),
        row("ok-2", "输出一个 JSON 对象。", '{"ok": true}'),
        row("ok-3", "解释负数是什么。", "小于零的数。"),
        row("same-id", "问题甲"),
        row("same-id", "问题乙"),
    ]
    lines = [(json.dumps(row, ensure_ascii=False) + "\n").encode("utf-8")
             for row in rows]
    lines.append(b'{"id":"first","id":"second"}\n')
    return lines


def write_jsonl(path, records):
    path.write_text("".join(json.dumps(row, ensure_ascii=False, allow_nan=False)
                            + "\n" for row in records), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--demo", action="store_true")
    mode.add_argument("--input", type=Path)
    parser.add_argument("--blocked-sources", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.input and args.blocked_sources is None:
        parser.error("--input requires --blocked-sources (a JSON string list)")
    if args.demo and args.blocked_sources is not None:
        parser.error("--demo uses its built-in holdout source manifest")
    if args.demo:
        raw_bytes = b"".join(demo_lines())
        blocked = ["holdout-doc"]
    else:
        raw_bytes = args.input.read_bytes()
        blocked = strict_loads(args.blocked_sources.read_text(encoding="utf-8"))
    if (not isinstance(blocked, list) or any(
            not isinstance(x, str) or not x or x != x.strip() for x in blocked)):
        parser.error("blocked sources must be nonempty strings without edge whitespace")
    blocked = sorted(set(blocked))
    kept, audit, report = clean_lines(raw_bytes.splitlines(keepends=True), set(blocked))
    report.update(
        rule_version=RULE_VERSION,
        input_sha256=hashlib.sha256(raw_bytes).hexdigest(),
        blocked_sources_sha256=hashlib.sha256(
            json.dumps(blocked, ensure_ascii=False).encode("utf-8")).hexdigest(),
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        python_version=platform.python_version(),
        unicode_version=unicodedata.unidata_version,
    )
    # Refuse to replace an existing output directory.
    args.out_dir.mkdir(parents=True, exist_ok=False)
    if args.demo:
        (args.out_dir / "demo-raw.jsonl").write_bytes(raw_bytes)
    write_jsonl(args.out_dir / "clean.jsonl", kept)
    write_jsonl(args.out_dir / "audit.jsonl", audit)
    (args.out_dir / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
