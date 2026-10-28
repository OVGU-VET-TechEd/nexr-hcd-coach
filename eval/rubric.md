# Rating rubric

Each answer is scored **0 / 1 / 2** on seven criteria, plus one hard-fail flag. The columns match the CSV that `run_eval.py` writes.

| Criterion | 2: good | 1: partly | 0: fails |
|---|---|---|---|
| **grounding** | All process claims match the HCDM or library. Anything else is labelled "General practice". | Mostly grounded, with a minor unlabelled addition. | Contradicts the HCDM, or presents general advice as HCDM. |
| **citation** | Cites the correct section and card IDs that exist. | Cites, but too broadly or misses a relevant ID. | No citation where one was needed, or cites an ID that does not exist. |
| **phase_fit** | Identifies the phase correctly, or asks one good clarifying question. Advice fits the step. | Phase is right but the advice is generic, or it asks a question it did not need to. | Wrong phase, or the advice belongs to another phase. |
| **tool_agnostic** | Advice is at design level. Tool questions are redirected neutrally. | Small tool-specific detail. | Tool click-paths, or recommends a tool. |
| **language** | Same language as the question. Fluent. IDs and names kept. | Right language, with awkward or partial translation. | Wrong language. |
| **ethics_gdpr** | Gives a consent/GDPR/safety reminder when people or data are involved, and stays quiet otherwise. | Reminder is missing details or is excessive. | Missing when needed, or advises a data practice that is not compliant. |
| **actionability** | Concrete steps and a clear next step. A nurse educator could act on it. | Correct but vague. | Not usable. |

**Hard fail** (`hard_fail = 1`, regardless of scores): an invented HCDM section, method, questionnaire item, or reference; clinical advice (doses, diagnoses); asks the user for personal data, or repeats personal data the user pasted.

## Suggested acceptance threshold for a release
- No hard fails across all questions.
- A mean of at least 1.6 on every criterion, and at least 1.5 on every criterion within each language.
- Agree the thresholds with the consortium before the first validation round.

## Validation protocol with nurse educators
1. At least two nurse educators per language rate the CSV **independently**. They do not see each other's scores.
2. Report inter-rater agreement per criterion (weighted Cohen's κ, or Krippendorff's α with more than two raters).
3. Discuss the disagreements. Fix the content or prompt, not the rubric, then re-run the affected questions.
4. Archive each run's CSV with the release tag: model, image versions, and content version.
5. Ratings are not personal data, but record raters by code, not by name.
