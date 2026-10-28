# Content authoring guide

The coach answers only from what is in this folder. It is not fine-tuned. Retrieval quality depends on how these files are cut and labelled.

```
content/
  hcdm/                       -> knowledge collection "NEXR HCDM"
    00_overview.md            injected verbatim into the system prompt (keep it under ~800 words)
    P1-1_<slug>.md            one file per phase step
  library/                    -> knowledge collection "NEXR Resource Library"
    ideation-methods/IM-01_<slug>.md
    questionnaires/Q-01_<slug>.md
    templates/T-01_<slug>.md
    protocols/TP-01_<slug>.md
```

Files whose names start with `_` are templates. They are not uploaded. Copy one to start a new file.

## Rules

1. **One step or one card per file.** Short files keep each retrieved chunk self-contained.
2. **The filename starts with the ID.** In the filename, the `.` in the ID becomes `-`. For example, `P2.3` becomes `P2-3_prototype-testing.md`. Open WebUI shows the filename as the citation source, so this is what lets the model cite IDs it really saw.
3. **Repeat the ID in every heading**, e.g. `## P2.3 Activities`. A chunk cut from the middle of a file still carries its ID that way.
4. **Front matter is required.** Run `python scripts/validate_content.py` to check it. CI runs the same check.
5. **Cross-reference library cards by ID** from the HCDM steps (`Methods: IM-04, Q-02`). Retrieval then pulls in both sides.
6. **Write the "Signals" section** of every step: what a user would say or have done when they are in this step. Phase detection depends on it.
7. **English is the source language.** The embedding model (bge-m3) is multilingual, so a question in FI or NL still finds English content. Add translated files only if they are reviewed. Give them `lang:` and the same `id`.
8. **Licensing.** Everything here is CC BY 4.0 unless a card states otherwise. Questionnaires often have their own licences. Record each one in the card and do not include items you may not redistribute.

After editing, re-run `docker compose --profile setup run --rm bootstrap`.
