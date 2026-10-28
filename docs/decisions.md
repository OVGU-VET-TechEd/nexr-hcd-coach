# Decisions

## Open: needs the project team

| Decision | Scaffold default | What changes if decided otherwise |
|---|---|---|
| Hosted demo or local only | Local only (`WEBUI_BIND=127.0.0.1`) | Hosted: reverse proxy and TLS, privacy notice, operator becomes data controller, account approval workflow. See the README section on hosting. |
| First-release languages | All five (EN/ES/DE/FI/NL) supported. Eval questions need native-speaker authors. | Fewer languages means fewer eval sets and raters. The model choice may get easier if FI is deferred. |
| Hardware | `gemma3:12b` (GPU, ≥12 GB VRAM). `gemma3:4b` for CPU. | CPU only: expect slow answers and weaker FI. Consider BYO API for the demo. |
| File uploads | Off (`ALLOW_FILE_UPLOADS=false`) | On: users may upload learner data. Needs a GDPR assessment and retention rules. |
| Code licence | MIT | Apache-2.0 adds an explicit patent grant. Swap `LICENSE` and the `license` fields in `CITATION.cff` and `.zenodo.json`. |

## Made in the scaffold

- **Open WebUI's built-in RAG** (Knowledge collections and a model preset), not a custom retrieval service. This keeps the MVP small. A custom UI with a phase selector can later call the same collections, or replace them.
- **HCDM overview in the system prompt, details by retrieval.** Phase detection needs the full phase map in every turn. Step and card details are too long for small models' context, so they are retrieved.
- **ID-prefixed filenames and IDs repeated in headings.** Open WebUI cites by filename, so the model can cite only IDs it actually retrieved.
- **bge-m3 via Ollama** for embeddings. It is multilingual and runs on CPU, and Ollama is already in the stack.
- **`num_ctx=8192`.** Ollama's default of 2048 tokens would silently truncate the system prompt and the retrieved sources.
- **Pinned image versions.** `bootstrap.py` uses the Open WebUI v0.6 REST API. Bump the versions deliberately and re-run the eval set after each bump.

## To verify on first deployment
- [ ] Bootstrap API calls work against the pinned Open WebUI version (knowledge create, file add, model create).
- [ ] The coach preset applies its knowledge collections when called via `/api/chat/completions`, which the eval runner uses.
- [ ] Citations in the chat UI show the ID-prefixed filenames.
- [ ] FI answer quality with the chosen model, rated with the rubric.
