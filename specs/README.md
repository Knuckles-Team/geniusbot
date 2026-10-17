# geniusbot specifications

These specs follow the ecosystem [spec standard](https://github.com/Knuckles-Team/pipelines/blob/main/reference/spec-standard.md): one owning spec per capability, extend an existing spec before creating one, audits and reviews land in the owning spec, one ID and title form, one file set. The `spec-standard` gate enforces it.

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

| Spec | Requirement family | Scope |
|---|---|---|
| [Desktop Arbora operation client](desktop-client/spec.md) | GENIUSBOT-CLIENT | Desktop cockpit's gateway transport, cockpit/dashboard surfaces, approval boundary and packaging |

## State legend

Generated `status.json` records `SPECIFIED`, `LANDED` or `VERIFIED`, according to the ecosystem spec standard.
Planned acceptance paths must not count as passed tests.

## Contribution path

Propose the user behavior first, then document the existing implementation and public
interfaces, write the test contract, and implement the smallest complete task set. Reuse
the existing gateway client facade and backend-adapter seam. Apply CCCC, jscpd,
Dupehound and KISS requirements where configured; record a missing command or threshold
as a gap rather than a pass. Include exact public revisions and check links when
updating status. The ecosystem's [spec generator](https://github.com/Knuckles-Team/universal-skills/tree/main/universal_skills/development/spec-generator),
[spec verifier](https://github.com/Knuckles-Team/universal-skills/tree/main/universal_skills/development/spec-verifier),
and [Arbora development skill](https://github.com/Knuckles-Team/arbora/tree/main/arbora/skills/arbora-development)
describe the same workflow.

- [`GENIUSBOT-CLIENT`](desktop-client/spec.md) — Desktop Arbora operation client

`GENIUSBOT-CLIENT-R019` includes children `.1` through `.6` for run observation, producer wiring and served refusal evidence.
