# GENIUSBOT-CLIENT-001 implementation tasks

- [ ] Review the existing `GatewayClient` facade, `BackendAdapter` seam, `AgentBridgeWorker`
      dispatch, and panel-loading dispatch table against this spec; preserve unrelated
      concurrent edits and reuse every existing path instead of adding a parallel one.
- [ ] Confirm Graph OS's public generated operation registry and endpoint in an installed
      wheel; wire specialist/slash-command invocation to validate against it before any
      network call (closes `GENIUSBOT-CLIENT-R002`).
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
- [ ] Build and smoke-test each packaged artifact (PyInstaller onefile, Windows installer,
      Linux desktop entry) from a tagged revision against both a reachable and an
      unreachable Graph OS gateway (closes `GENIUSBOT-CLIENT-R012`).
- [ ] Reconcile the `pip install geniusbot[all]` instruction in `README.md` with
      `pyproject.toml`'s actual optional-dependency groups (`dev`, `test`, `types`; no `all`
      group is currently defined), and reconcile the supported Python range stated in
      `AGENTS.md` (`>=3.11, <3.14`) with `pyproject.toml`'s `requires-python`
      (`>=3.12, <3.15`).
- [ ] Publish the exact merged revision, checks, and packaging/consumer receipts in
      `status.json`; move a requirement to `LANDED` only after merge, and to `ACCEPTED` only
      after the served end-to-end approval and packaging proof.
