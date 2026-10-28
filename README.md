# NEXR HCD Coach

A phase-aware coaching chatbot for **nurse educators who design XR/VR learning exercises** with any authoring tool. It answers design-process questions, such as which ideation method to use, which evaluation questionnaire fits, or when to involve learners in testing. It grounds every answer in the **NEXR Human-Centred Design Model (HCDM)** and the NEXR resource library.

- **Grounded, not fine-tuned.** It works from a system prompt, an HCDM overview, and retrieval over curated markdown. To change what it knows, edit `content/`.
- **Self-hostable.** Ollama and Open WebUI run in Docker Compose. You can also bring your own API key or vLLM server.
- **Multilingual.** Tested in EN, ES, DE, FI, and NL, using multilingual embeddings (bge-m3).
- **Tool-agnostic and privacy-conscious.** File uploads are off by default and telemetry is disabled. The coach gives consent and GDPR reminders.

> Status: **MVP scaffold.** The HCDM and the resource library are placeholders until the final content is added. See [docs/decisions.md](docs/decisions.md).

## Quick start

```bash
cp .env.example .env            # set WEBUI_SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD
docker compose up -d            # first start pulls the models (~10 GB for gemma3:12b + bge-m3)
docker compose logs -f ollama-pull   # wait until it exits
docker compose --profile setup run --rm bootstrap
```

Open <http://localhost:3000>, sign in with the admin account, and choose **NEXR HCD Coach**.

| Hardware | Setting |
|---|---|
| NVIDIA GPU, at least 12 GB VRAM | `BASE_MODEL=gemma3:12b`, and add `-f docker-compose.gpu.yml` |
| CPU only, or a small GPU | `BASE_MODEL=gemma3:4b`. Slower, and noticeably weaker in Finnish. |
| macOS (Apple Silicon) | Run [Ollama](https://ollama.com) natively. In compose, point `OLLAMA_BASE_URL` and `RAG_OLLAMA_BASE_URL` to `http://host.docker.internal:11434`. |
| No GPU, but an API key or vLLM server | Set `ENABLE_OPENAI_API=true`, `OPENAI_API_BASE_URL`, `OPENAI_API_KEY`, `BASE_MODEL=<provider model id>`, and `OLLAMA_PULL_MODELS=bge-m3` |

**Vector store:** Open WebUI's built-in Chroma is the default. For Qdrant or pgvector, set `VECTOR_DB` in `.env` and start with `--profile qdrant` or `--profile pgvector`.

## How it works

```
content/hcdm/00_overview.md ──► system prompt (phase map, always in context)
prompts/system_prompt.md   ──┘  role · scope · citation · no invention · tool-agnostic · ethics/GDPR · language
content/hcdm/*.md          ──► knowledge collection "NEXR HCDM"            ┐ retrieved per question
content/library/**.md      ──► knowledge collection "NEXR Resource Library" ┘ (bge-m3 embeddings)
                                    ▼
                    Open WebUI model preset "nexr-coach" on BASE_MODEL
```

`scripts/bootstrap.py` is idempotent. Run it again after any change to `content/` or `prompts/`.

> Open WebUI saves most settings to its database on first start. Changing `.env` later may have no effect. Change the setting in **Admin Settings** instead, or remove the `open-webui` volume.

## Editing content

See [content/README.md](content/README.md). In short: one phase step or one library card per file, the filename starts with its ID, and front matter is required. Check with:

```bash
pip install -r scripts/requirements.txt
python scripts/validate_content.py
```

## Evaluation

```bash
docker compose --profile eval run --rm eval      # writes eval/results/run-<timestamp>.csv
```

Raters score the CSV with [eval/rubric.md](eval/rubric.md). Question sets live in `eval/questions/`: `guardrails.yaml` for phase-independent checks, plus one file per phase, copied from `_TEMPLATE_phase.yaml`.

## Hosting a public demo

The defaults bind to `127.0.0.1` only. For a hosted demo:
- Put it behind a TLS reverse proxy and set `WEBUI_BIND=0.0.0.0`.
- Keep `DEFAULT_USER_ROLE=pending` so that the admin approves each account.
- Keep uploads off.
- Publish a privacy notice. Chats are stored in the Open WebUI database, and the operator is the data controller.
- With a BYO API key, chat content goes to that provider. Check whether you need a data processing agreement.

## Releases and citation

- Releases are tagged `vMAJOR.MINOR.PATCH`. The GitHub–Zenodo integration archives each release and mints a DOI (metadata in `.zenodo.json`).
- Archive the eval CSV and the image, model, and content versions with each release.
- Cite this project using [CITATION.cff](CITATION.cff).

## Licences

- **Code** (`scripts/`, `eval/*.py`, compose files): [MIT](LICENSE)
- **Content** (`content/`, `prompts/`, `eval/questions/`, `eval/rubric.md`, docs): [CC BY 4.0](LICENSE-CONTENT.md). Individual questionnaires may carry their own licence, which their card states.
- Third-party components (Open WebUI, Ollama, the models) are under their own licences. Check the model licence (e.g. the Gemma Terms of Use) before redistributing.

## Funding

<!-- TODO: confirm the exact wording and project number with the project coordinator / granting authority,
     and add the official "Co-funded by the European Union" emblem as docs/eu-emblem.png:
     ![Co-funded by the European Union](docs/eu-emblem.png) -->

Co-funded by the European Union under project **TODO-PROJECT-NUMBER** (NEXR). Views and opinions expressed are, however, those of the author(s) only and do not necessarily reflect those of the European Union or TODO-GRANTING-AUTHORITY. Neither the European Union nor the granting authority can be held responsible for them.
