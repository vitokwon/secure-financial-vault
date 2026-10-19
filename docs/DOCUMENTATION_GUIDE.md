# Documentation Guide and Version Control

**Owner:** David Williams (Technical Documentation Lead)

This guide defines where project documents live, how they are versioned, and how they are updated so the final report remains consistent with the implementation. The Markdown documents are the source of truth for the project documentation set.

## 1. Document Register

| Document | File | Owner | Reviewer | Version | Status | Last updated |
|---|---|---|---|---|---|---|
| Threat model (STRIDE) | `docs/THREAT_MODEL.md` | David Williams | OhUk Kwon | v0.3 | Draft | 2026-10-18 |
| Documentation guide | `docs/DOCUMENTATION_GUIDE.md` | David Williams | Dhruvi Sorathiya | v0.3 | Draft | 2026-10-18 |
| Test matrix | `docs/TEST_MATRIX.md` | Dhruvi Sorathiya | David Williams | v0.1 | Draft | 2026-10-18 |
| Architecture notes and diagram | `docs/ARCHITECTURE.md` + `docs/diagrams/` | OhUk Kwon | David Williams | v0.1 | Draft | 2026-10-18 |
| Work breakdown structure | `docs/wbs.md` | OhUk Kwon | David Williams | — | Working document | 2026-10-16 |
| Final technical report | `docs/report/` (Word → PDF export) | David Williams | All | — | Not started | — |
| Presentation slides | `docs/presentation/` (`.pptx` / `.pdf`) | David Williams | All | — | Not started | — |
| Setup guide | `README.md`, `setup_guideline.md` | OhUk Kwon | Dhruvi Sorathiya | — | Exists, unversioned | — |

**Status values:** `Not started` → `Draft` → `In review` → `Approved` (approved = `v1.0`, submitted with the final report).

Update the **Version**, **Status**, and **Last updated** columns whenever a document changes. Add new project documents to this register when they are created.

> **Filename consistency:** The repository currently contains `docs/wbs.md`. References should use that exact lowercase path unless the file is deliberately renamed to `docs/WBS.md` in a separate change.

## 2. Version Numbering

| Version | Meaning |
|---|---|
| `v0.x` | Working draft; changes as modules are built (`v0.1`, `v0.2`, …) |
| `v1.0` | Version submitted with the final report |
| `v1.x` | Corrections after submission, for example before the presentation |

**Bump the version when:** a section is added, a threat or finding changes status, a major implementation change is documented, or a submission milestone is reached. Typo fixes and formatting-only changes do not require a new version.

## 3. How to Update a Document

1. Create a branch, for example:
   `git checkout -b docs/threat-model-v0.4`
2. Edit the document and add a row to its **Change Log** table, where the document has one.
3. Update the version number at the top of the document and in this Document Register.
4. Commit with a `docs:` prefix, for example:
   `git commit -m "docs: threat model v0.4 - update verified controls"`
5. Open a Pull Request and ask at least one teammate to review.
6. After merge, verify that cross-document references, IDs, file paths, implementation statuses, and version numbers remain consistent.

## 4. Milestone Tags

Tag the repository at each submission milestone so the exact code and documents can be recovered:

```bash
git tag -a docs-v1.0 -m "Final report submission"
git push origin docs-v1.0
```

Suggested tags:

- `docs-v0.5` — report draft
- `docs-v1.0` — final report
- `docs-v1.1` — presentation or post-submission corrections

## 5. Keeping the Report in Sync

- The Markdown files are the **source of truth**. The final Word report is exported from them, not edited separately.
- Before exporting, confirm that every threat marked `Verified` has a passing test in the test matrix.
- Confirm that threat IDs, finding IDs, and test IDs match across the threat model, test matrix, report, slides, and demo script.
- Record the Git tag and commit ID in the report appendix so reviewers can trace the report to the code.
- When implementation changes affect a documented threat, finding, control, or test, update the relevant documentation in the same change or in a follow-up documentation PR.
- A document may describe planned or proposed work, but it must not describe unimplemented controls as implemented.
- File paths, test locations, phase labels, and implementation statuses must be checked against the current repository before each report export.
- If a test ID is marked as proposed, it must not be counted as formal threat coverage until it is added to the threat register and executed.

## 6. Documentation and Security Rules

- Never paste real keys, passwords, tokens, or `.env` contents into any document.
- Screenshots must not show secrets, tokens, personal information, or sensitive financial data.
- One owner per document approves its changes; anyone may suggest edits through a Pull Request.
- Keep the threat model's status values accurate: `Open`, `Planned`, `Implemented`, or `Verified`.
- Do not mark a control `Verified` until the associated test case has passed and the result is recorded.
- Update `docs/THREAT_MODEL.md` when a new security-relevant module is merged or when a threat, finding, mitigation, residual risk, or test status changes.

## 7. Change Log

| Version | Date | Author | Changes |
|---|---|---|---|
| v0.1 | 2026-10-12 | D. Williams | Initial documentation guide: document register, versioning rules, update workflow, milestone tags, report synchronization, and security rules. |
| v0.1 | 2026-10-18 | D. Williams | Included the initial guide in the repository under `docs/` and synchronized the register with the current threat model version (`v0.3`). |
| v0.2 | 2026-10-18 | D. Williams | Expanded the register with reviewer, status, and last-updated fields; added presentation slides; registered draft `TEST_MATRIX.md` v0.1 and `ARCHITECTURE.md` v0.1; documented Word-to-PDF report export. |
| v0.3 | 2026-10-18 | D. Williams | Added `docs/wbs.md` to the document register; added consistency rules for implementation status, test coverage, repository paths, and proposed test IDs; synchronized the guide with the current documentation set. |
