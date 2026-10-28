#!/usr/bin/env python3
"""Load content/ into Open WebUI and (re)create the NEXR coach model preset.

Idempotent: the knowledge collections and the preset are deleted and recreated
on every run. Written against the Open WebUI v0.6 REST API.
"""
import os
import re
import sys
import time

from nexr_common import CONTENT, ROOT, content_files, split_front_matter, webui_session

COLLECTIONS = [
    ("NEXR HCDM", "NEXR Human-Centred Design Model, one file per phase step.", CONTENT / "hcdm"),
    ("NEXR Resource Library", "Ideation methods, questionnaires, templates and test protocols.", CONTENT / "library"),
]

SUGGESTIONS = [
    "I want to build a VR exercise on hand hygiene. Where do I start?",
    "Which ideation methods can I use with my students?",
    "Welche Fragebögen eignen sich für die Evaluation meiner VR-Übung?",
    "¿Cuándo debo involucrar a los estudiantes en las pruebas?",
]


def build_system_prompt() -> str:
    meta, overview = split_front_matter((CONTENT / "hcdm" / "00_overview.md").read_text("utf-8"))
    if meta.get("status") == "placeholder":
        print("WARNING: content/hcdm/00_overview.md is still a placeholder.", file=sys.stderr)
    prompt = (ROOT / "prompts" / "system_prompt.md").read_text("utf-8")
    prompt = re.sub(r"<!--.*?-->\s*", "", prompt, flags=re.S)
    return (prompt.replace("<<HCDM_OVERVIEW>>", overview.strip())
                  .replace("<<HCDM_VERSION>>", str(meta.get("version", "unknown"))))


def recreate_collection(s, base, name, description, folder):
    r = s.get(f"{base}/api/v1/knowledge/")
    r.raise_for_status()
    existing = r.json()
    if isinstance(existing, dict):
        existing = existing.get("items", [])
    for k in existing:
        if k.get("name") == name:
            s.delete(f"{base}/api/v1/knowledge/{k['id']}/delete").raise_for_status()

    # access_control None = readable by all users.
    r = s.post(f"{base}/api/v1/knowledge/create",
               json={"name": name, "description": description, "access_control": None})
    r.raise_for_status()
    kb = r.json()

    files = content_files(folder)
    for path in files:
        with path.open("rb") as fh:
            r = s.post(f"{base}/api/v1/files/", files={"file": (path.name, fh, "text/markdown")})
        r.raise_for_status()
        file_id = r.json()["id"]
        # The upload may still be processing; retry the attach briefly.
        for attempt in range(5):
            r = s.post(f"{base}/api/v1/knowledge/{kb['id']}/file/add", json={"file_id": file_id})
            if r.ok:
                break
            time.sleep(2 * (attempt + 1))
        else:
            sys.exit(f"Failed to add {path.relative_to(ROOT)}: {r.status_code} {r.text[:300]}")
        print(f"  + {path.relative_to(ROOT)}")
    print(f"{name}: {len(files)} file(s)")
    return r.json() if files else kb


def recreate_model(s, base, knowledge):
    model_id = os.environ.get("NEXR_MODEL_ID", "nexr-coach")
    params = {"system": build_system_prompt(),
              "temperature": float(os.environ.get("LLM_TEMPERATURE", "0.3"))}
    if os.environ.get("NUM_CTX"):
        params["num_ctx"] = int(os.environ["NUM_CTX"])  # Ollama only; ignored by other backends.

    payload = {
        "id": model_id,
        "base_model_id": os.environ.get("BASE_MODEL", "gemma3:12b"),
        "name": os.environ.get("NEXR_MODEL_NAME", "NEXR HCD Coach"),
        "meta": {
            "description": "Phase-aware HCD coach for XR/VR nursing exercises, grounded in the NEXR HCDM.",
            "knowledge": [{**k, "type": "collection"} for k in knowledge],
            "suggestion_prompts": [{"content": c} for c in SUGGESTIONS],
            "capabilities": {"vision": False, "citations": True},
        },
        "params": params,
        "access_control": None,
        "is_active": True,
    }
    s.delete(f"{base}/api/v1/models/model/delete", params={"id": model_id})  # absent on first run
    r = s.post(f"{base}/api/v1/models/create", json=payload)
    if not r.ok:
        sys.exit(f"Model preset creation failed: {r.status_code} {r.text[:300]}")
    print(f"Model preset '{model_id}' on base '{payload['base_model_id']}' ready.")


def main():
    s, base = webui_session()
    knowledge = [recreate_collection(s, base, *c) for c in COLLECTIONS]
    recreate_model(s, base, knowledge)


if __name__ == "__main__":
    main()
