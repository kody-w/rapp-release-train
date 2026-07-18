# 🚂 rapp-release-train

**Live dashboard + static API for the RAPP pre-grail release train:**
`rapp-canary → rapp-nightly → rapp-alpha → rapp-beta → rapp-installer (the grail, human-only merge)`.

**Dashboard:** https://kody-w.github.io/rapp-release-train/

Every number on the page is fetched in your browser from static
`raw.githubusercontent.com` data published by the train repos themselves —
versions, ring identity (`.ring/ring.json`), train topology (`.ring/train.json`),
preflight status badges, and an in-browser SHA-256 payload-convergence matrix.
No server anywhere. The pattern is
[`rapp-static-api/1.0`](https://github.com/kody-w/rapp-static-apis).

## The static API

```bash
RAW=https://raw.githubusercontent.com/kody-w/rapp-release-train/main
curl -s $RAW/registry.json          # index: every tracked file, per-ring hashes, drift flags
curl -s $RAW/api/v1/status.json     # is the train converged?
curl -s $RAW/api/v1/badge.json      # shields.io endpoint
```

`manifest.json` is the only hand-authored file; `python3 build.py` is the only
build step (idempotent, stable-write). Each distinct version of every tracked
file is captured as an immutable content-addressed frame under
`versions/<name>/<sha8>` — pin one and it works forever. CI rebuilds on push and
every 6 hours, committing only real changes.

A payload file showing **drift** across rings is not an error — it is the train
photographed mid-journey (a change promoted partway, or a release the grail has
not yet taken). The ring operations doc is the canary repo's
[`.ring/RUNBOOK.md`](https://github.com/kody-w/rapp-canary/blob/main/.ring/RUNBOOK.md).

MIT © Kody Wildfeuer. Part of the [RAPP ecosystem](https://github.com/kody-w/rapp-map).
