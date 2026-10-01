# geniusbot specifications

This tracked directory contains public, owner-native build contracts for the desktop
cockpit client. A contributor can implement a spec from this repository and its linked
public contracts without access to private notes or infrastructure.

## Structure and index

Each `specs/<lower-kebab-name>/` directory contains `spec.md` (behavior and acceptance),
`plan.md` (architecture and reuse), `test-spec.md` (positive, negative, quality and
release proof), `tasks.md` (implementation order), `requirements.md` (the definition of
every requirement ID the spec owns), and `status.json` (machine-readable state and
evidence, with one entry per requirement ID in its `requirements` array, each carrying
its own `delivery_state` and evidence). Start from [`_template/`](_template/). A stable
requirement ID remains in the documents and status file even when the directory has a
descriptive name. A requirement counts as delivered only once its evidence includes a
merged-head commit on the default branch.

| Spec | Requirement | Delivery | Acceptance | Scope |
|---|---|---|---|---|
| [Desktop GraphOS operation client](desktop-client/spec.md) | GENIUSBOT-CLIENT-001 | SPECIFIED | NOT_AUDITED | Desktop cockpit's gateway transport, cockpit/dashboard surfaces, approval boundary and packaging |

## State legend

The report reads `status.json` as the source of truth. Delivery states are `UNKNOWN`
(not classified), `SPECIFIED` (complete design awaiting verified build), `BUILDING`
(implementation in progress), `BUILT` (implementation exists but is not merged),
`LANDED` (merged revision recorded), `CLOSED` (delivered and closed), `DEFERRED`
(postponed), and `REJECTED` (not proceeding). Acceptance states are `NOT_AUDITED` (no
complete evidence review), `PENDING` (review in progress or missing proof), `ACCEPTED`
(all specified checks and consumer receipts pass), and `FAILED` (a required check
failed). Delivery and acceptance are independent; a merge never implies acceptance.

`LANDED` requires a public merged revision in the evidence array. `ACCEPTED` also
requires checked-in test, installed-package, live contract, consumer and release
receipts specified by the feature. Do not promote state from an isolated source branch,
a local test pass, or a generated report alone.

## Contribution path

Propose the user behavior first, then document the existing implementation and public
interfaces, write the test contract, and implement the smallest complete task set. Reuse
the existing gateway client facade and backend-adapter seam. Apply CCCC, jscpd,
Dupehound and KISS requirements where configured; record a missing command or threshold
as a gap rather than a pass. Include exact public revisions and check links when
updating status. The ecosystem's [spec generator](https://github.com/Knuckles-Team/universal-skills/tree/main/universal_skills/development/spec-generator),
[spec verifier](https://github.com/Knuckles-Team/universal-skills/tree/main/universal_skills/development/spec-verifier),
and [Graph OS development skill](https://github.com/Knuckles-Team/graph-os/tree/main/graph_os/skills/graph-os-development)
describe the same workflow.
