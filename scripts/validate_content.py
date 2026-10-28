#!/usr/bin/env python3
"""Check content/ front matter, IDs and filenames. Exit 1 on errors."""
import re
import sys

from nexr_common import CONTENT, ROOT, content_files, split_front_matter

COMMON = {"id", "kind", "title", "status"}
KINDS = {
    "hcdm-overview": (r"P0", {"version"}),
    "hcdm-step": (r"P\d+\.\d+", {"phase", "phase_name", "step", "version", "lang"}),
    "ideation-method": (r"IM-\d{2,}", {"phases", "source", "licence", "lang"}),
    "questionnaire": (r"Q-\d{2,}", {"phases", "construct", "validated_languages", "source", "licence", "lang"}),
    "template": (r"T-\d{2,}", {"phases", "licence", "lang"}),
    "protocol": (r"TP-\d{2,}", {"phases", "licence", "lang"}),
}


def main() -> int:
    errors, warnings = [], []
    seen_ids, seen_names = {}, {}

    for path in content_files(CONTENT):
        rel = path.relative_to(ROOT)
        meta, body = split_front_matter(path.read_text("utf-8"))
        if not meta:
            errors.append(f"{rel}: missing front matter")
            continue
        missing = COMMON - meta.keys()
        kind = meta.get("kind")
        if kind not in KINDS:
            errors.append(f"{rel}: unknown kind {kind!r}")
            continue
        pattern, required = KINDS[kind]
        missing |= required - meta.keys()
        if missing:
            errors.append(f"{rel}: missing fields {sorted(missing)}")

        id_ = str(meta.get("id", ""))
        lang = meta.get("lang", "en")
        if not re.fullmatch(pattern, id_):
            errors.append(f"{rel}: id {id_!r} does not match {pattern}")
        elif kind != "hcdm-overview" and not path.name.startswith(id_.replace(".", "-") + "_"):
            errors.append(f"{rel}: filename must start with '{id_.replace('.', '-')}_'")
        if (id_, lang) in seen_ids:
            errors.append(f"{rel}: duplicate id {id_} ({lang}), also in {seen_ids[(id_, lang)]}")
        seen_ids[(id_, lang)] = rel
        if path.name in seen_names:
            errors.append(f"{rel}: duplicate filename, also {seen_names[path.name]}")
        seen_names[path.name] = rel

        if meta.get("status") in ("placeholder", "draft") or "TODO" in body:
            warnings.append(f"{rel}: status={meta.get('status')} / contains TODO")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error:   {e}")
    print(f"{len(seen_names)} file(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
