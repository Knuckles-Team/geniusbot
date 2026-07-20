# KG Extraction cockpit (AU-ECO.connector.git-task-resolver)

The **🧬 KG Extraction** sidebar tab (`geniusbot/qt/extraction_cockpit.py`,
view 12) turns a document or URL into a live, force-directed knowledge graph on
the Qt cockpit — backed by the real gateway, not mock data.

## What it does

- **Ingest** — paste text or enter a URL, click **Extract**.
- **Stream** — facts stream onto a native `QGraphicsView` force graph
  (`geniusbot/qt/force_graph.py`) as they generate. The layout
  (`relax_layout`, a pure Fruchterman-Reingold step) is unit-tested without a
  display. Node keys are NFKC-normalized so variants merge.
- **Inspect** — click an edge to open its fact card: title, triple, description,
  confidence %, tags, evidence span, and source file.
- **Export** — the **JSONL** button downloads the job's facts.

## How it works

`GatewayClient.submit_and_stream_extraction` submits to
`/api/enhanced/extract/submit`, then streams
`/api/enhanced/extract/stream/{job_id}`. Each event is forwarded to the panel on
the UI thread via the `AgentBridgeWorker` `progress` signal, so facts render live
and thread-safely. The backend (KG-2.64 extractor, KG-2.65 GPU-slot scheduler,
KG-2.66 readability reader) is documented in agent-utilities
`docs/architecture/document_fact_extraction.md`.
