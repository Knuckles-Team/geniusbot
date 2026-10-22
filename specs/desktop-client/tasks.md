# GENIUSBOT-CLIENT implementation tasks

- [ ] Review the existing `GatewayClient` facade, `BackendAdapter` seam, `AgentBridgeWorker`
      dispatch, and panel-loading dispatch table against this spec; preserve unrelated
      concurrent edits and reuse every existing path instead of adding a parallel one.
- [x] Add the typed `OperationRegistryEntry`/`OperationRegistry` model and `build_registry`
      validator (closes `GENIUSBOT-CLIENT-R002.1`).
- [ ] Confirm Arbora's public generated operation registry and endpoint in an installed
      wheel; wire specialist/slash-command invocation to validate against it before any
      network call (closes `GENIUSBOT-CLIENT-R002.2`).
- [ ] Decide and implement `ToolGuardDialog`'s wiring: either route specialist execution and
      governed slash commands through it before dispatch, or explicitly scope it out of this
      release with a recorded reason (closes the open question under `GENIUSBOT-CLIENT-R006`).
- [ ] Add or confirm the positive and negative unit, contract, and Qt tests listed in
      [`test-spec.md`](test-spec.md) for every requirement, including the worker signal
      contract (`GENIUSBOT-CLIENT-R004`) and the tray/close-event behavior
      (`GENIUSBOT-CLIENT-R010`), which currently have no dedicated test file.
- [ ] Run the repository's configured Ruff, mypy and pytest checks; define and run CCCC,
      `jscpd` and Dupehound commands/thresholds or document their explicit acceptance
      exception.
- [x] Add the typed `PackagingManifest`/`PackagingTarget` model and `build_manifest`
      validator (closes `GENIUSBOT-CLIENT-R012.1`).
- [ ] Build and smoke-test each packaged artifact (PyInstaller onefile, Windows installer,
      Linux desktop entry) from a tagged revision against both a reachable and an
      unreachable Arbora gateway (closes `GENIUSBOT-CLIENT-R012.2`).
- [ ] Reconcile the `pip install geniusbot[all]` instruction in `README.md` with
      `pyproject.toml`'s actual optional-dependency groups (`dev`, `test`, `types`; no `all`
      group is currently defined), and reconcile the supported Python range stated in
      `AGENTS.md` (`>=3.11, <3.14`) with `pyproject.toml`'s `requires-python`
      (`>=3.12, <3.15`).
- [ ] Publish the exact merged revision, checks, and packaging/consumer receipts in
      `status.json`; move a requirement to `LANDED` only after merge, and to `ACCEPTED` only
      after the served end-to-end approval and packaging proof.

- [ ] Generated design-token colors. (closes `GENIUSBOT-CLIENT-R013`; proof `tests/test_design_tokens.py::test_colors_match_generated_output`).
- [ ] Finance cockpit panel contract. (closes `GENIUSBOT-CLIENT-R014`; proof `tests/test_finance_cockpit.py::test_panel_unavailable_state`).
- [ ] Packaged `geniusbot-development` skill. (closes `GENIUSBOT-CLIENT-R015`; proof `tests/test_development_skill.py::test_skill_packaged_and_valid`).
- [ ] Spec and docs hooks in pre-commit. (closes `GENIUSBOT-CLIENT-R016`; proof `tests/test_precommit_hooks.py::test_required_pipelines_hook_ids_present`).
- [ ] Docs layout parity. (closes `GENIUSBOT-CLIENT-R017`; proof `tests/test_docs_layout.py::test_nav_lists_every_page`).
- [ ] AGENTS.md section parity. (closes `GENIUSBOT-CLIENT-R018`; proof `tests/test_agents_md_sections.py::test_required_headings_present`).

## Decomposition children (tracked)

- [x] **GENIUSBOT-CLIENT-R002:** Typed registry-entry model and validator (rollup of 1, 2)
- [x] **GENIUSBOT-CLIENT-R012:** Typed packaging manifest model and validator (rollup of 1, 2)
- [ ] **GENIUSBOT-CLIENT-R019:** Run harness surface (rollup of 1 to 6)
- [ ] **GENIUSBOT-CLIENT-R019.1:** Run operation wiring; implement the planned positive and negative served tests.
- [ ] **GENIUSBOT-CLIENT-R019.2:** Applied configuration; implement the planned positive and negative served tests.
- [ ] **GENIUSBOT-CLIENT-R019.3:** Context and cost; implement the planned positive and negative served tests.
- [ ] **GENIUSBOT-CLIENT-R019.4:** Read-only current plan; implement the planned positive and negative served tests.
- [ ] **GENIUSBOT-CLIENT-R019.5:** Distinct terminal reasons; implement the planned positive and negative served tests.
- [ ] **GENIUSBOT-CLIENT-R019.6:** Served surface proof; implement the planned positive and negative served tests.

## Source quality obligations

- [ ] **GENIUSBOT-CLIENT-R020:** Complete each child with current source and acceptance evidence.
- [ ] **GENIUSBOT-CLIENT-R020.1:** The desktop test adapter dependency must satisfy the supported test matrix. Source obligation: `T001`.
- [ ] **GENIUSBOT-CLIENT-R020.2:** The desktop UI dependency must satisfy the supported platform matrix. Source obligation: `T002`.
- [ ] **GENIUSBOT-CLIENT-R020.3:** The desktop dependency contract must use the supported served-client boundary. Source obligation: `T003`.
- [ ] **GENIUSBOT-CLIENT-R020.4:** The Windows dependency marker must resolve on supported platforms. Source obligation: `T004`.
- [ ] **GENIUSBOT-CLIENT-R020.5:** The formatter dependency must satisfy the supported source-check configuration. Source obligation: `T005`.
- [ ] **GENIUSBOT-CLIENT-R020.6:** The main-window initialization must meet the shared function-size checks. Source obligation: `T006`.
- [ ] **GENIUSBOT-CLIENT-R020.7:** The desktop entry module must meet the shared complexity checks. Source obligation: `T007`.
- [ ] **GENIUSBOT-CLIENT-R020.8:** Desktop tests must cover positive, negative and failure behavior. Source obligation: `T008`.
- [ ] **GENIUSBOT-CLIENT-R020.9:** Documentation examples must match the tested desktop behavior. Source obligation: `T009`.
- [ ] **GENIUSBOT-CLIENT-R020.10:** The README must cover each supported desktop entry point. Source obligation: `T010`.
- [ ] **GENIUSBOT-CLIENT-R020.11:** The contributor guide must describe the desktop source structure. Source obligation: `T011`.
- [ ] **GENIUSBOT-CLIENT-R020.12:** Documentation file references must resolve to tracked targets. Source obligation: `T012`.
- [ ] **GENIUSBOT-CLIENT-R020.13:** Desktop modules must meet the shared module-size checks. Source obligation: `T013`.
- [ ] **GENIUSBOT-CLIENT-R020.14:** The desktop must separate presentation from its served client adapter. Source obligation: `T014`.
- [ ] **GENIUSBOT-CLIENT-R020.15:** The desktop must trace each declared concept to its owning implementation. Source obligation: `T015`.
- [ ] **GENIUSBOT-CLIENT-R020.16:** The desktop must resolve each orphaned concept reference. Source obligation: `T016`.
- [ ] **GENIUSBOT-CLIENT-R020.17:** Desktop tests must bind their owning contract identifiers. Source obligation: `T017`.
- [ ] **GENIUSBOT-CLIENT-R020.18:** Significant desktop functions must identify their owning contracts. Source obligation: `T018`.
- [ ] **GENIUSBOT-CLIENT-R020.19:** The desktop source must retain a clean configured lint result. Source obligation: `T019`.
- [ ] **GENIUSBOT-CLIENT-R020.20:** The desktop source must pass the configured type checks. Source obligation: `T020`.
- [ ] **GENIUSBOT-CLIENT-R020.21:** The repository must validate its pinned formatter hook version. Source obligation: `T021`.
- [ ] **GENIUSBOT-CLIENT-R020.22:** The changelog must follow its declared parseable format. Source obligation: `T022`.
- [ ] **GENIUSBOT-CLIENT-R020.23:** The changelog must describe each shipped desktop change. Source obligation: `T023`.
- [ ] **GENIUSBOT-CLIENT-R020.24:** The changelog validation environment must supply its required parser. Source obligation: `T024`.
- [ ] **GENIUSBOT-CLIENT-R020.25:** Desktop tests must parameterize repeated input cases with observable assertions. Source obligation: `T025`.
- [ ] **GENIUSBOT-CLIENT-R020.26:** The documentation must cover every supported desktop environment variable. Source obligation: `T026`.
- [ ] **GENIUSBOT-CLIENT-R020.27:** The documentation must explain terminal and bundled-runtime environment inputs. Source obligation: `T027`.
- [ ] **GENIUSBOT-CLIENT-R020.28:** The environment example must document desktop platform inputs without credentials. Source obligation: `T028`.
- [ ] **GENIUSBOT-CLIENT-R020.29:** The desktop analysis command must use supported served interfaces without importing removed graph internals. Source obligation: `T029`.
- [ ] **GENIUSBOT-CLIENT-R020.30:** The desktop must score at least 80 in test coverage. Source obligation: `User story 1`.
- [ ] **GENIUSBOT-CLIENT-R020.31:** The desktop must score at least 80 in architecture & design patterns. Source obligation: `User story 2`.
- [ ] **GENIUSBOT-CLIENT-R020.32:** The desktop must score at least 80 in concept traceability. Source obligation: `User story 3`.
- [ ] **GENIUSBOT-CLIENT-R020.33:** The desktop must score at least 80 in test execution. Source obligation: `User story 4`.
- [ ] **GENIUSBOT-CLIENT-R020.34:** The desktop must score at least 80 in changelog audit. Source obligation: `User story 5`.
- [ ] **GENIUSBOT-CLIENT-R020.35:** The desktop must score at least 80 in environment variables. Source obligation: `User story 6`.
- [ ] **GENIUSBOT-CLIENT-R020.36:** The desktop must score at least 80 in analyze_xdg_kg. Source obligation: `User story 7`.
- [ ] **GENIUSBOT-CLIENT-R020.37:** The desktop must achieve an overall source-quality grade of at least 3.0. Source obligation: `Overall GPA`.
- [ ] **GENIUSBOT-CLIENT-R020.38:** The desktop must achieve grade B or higher in all 17 source-quality domains. Source obligation: `Domains at B or above`.
- [ ] **GENIUSBOT-CLIENT-R020.39:** The desktop must resolve all 29 actionable source findings. Source obligation: `Actionable findings`.
- [ ] **GENIUSBOT-CLIENT-R020.40:** Source-quality repairs must preserve the installed command path through `geniusbot/geniusbot.py:686`.
- [ ] **GENIUSBOT-CLIENT-R020.41:** A served integration test must launch the installed command and observe client behavior after source-quality repairs. It must distinguish a denied request from an authenticated empty result.

- [x] Implement R001.2 served dashboard transport and R001.3 cancellable off-thread refresh.
- [x] Preserve R001.1 and migrate six required checks to canonical owners under R016.
- [ ] Complete full declared-environment, live-gateway and packaging qualification; local transport and Qt fixtures do not establish release acceptance.

- [x] Repair bounded signal lifetime under R004.2 and console stream lifetime under R010.2.
- [ ] Preserve generic R004.1 and R010.1 acceptance gaps independently of these repairs.

- [x] R016.2 migrates the six required checks to immutable canonical owners. R016.1 retains docs-hook acceptance.

- [x] Define R005.1 and R005.2 for the client behavior already implemented in #42 and bind its regressions.
- [ ] Retain generic facade, live-gateway, Qt and release qualification gaps; do not infer those passes from the scoped graph tests.

R005.3 retains the prior generic R005 obligation and its LANDED state with no test evidence. The generated R005 rollup must not promote that unresolved coverage from the two scoped children.

- [ ] `GENIUSBOT-CLIENT-R016.3`: Install the locked test extra and headless Qt prerequisites for full CI tests.
