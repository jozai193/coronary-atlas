# Source snapshot ledger

`source_manifest.json` records hashes of official organizer pages/PDFs and anatomy reference files downloaded during local research. It is a record of what was checked on this machine, **not a claim that every listed snapshot is in the public source archive**. Most organizer PDF/HTML/text snapshots are intentionally omitted from the archive by `.gitignore`; the official URLs and claim-level references are in [hackathon_research.md](../hackathon_research.md) and [assets/README.md](../../assets/README.md).

The app does not read these omitted snapshots at runtime. The bundled dataset, model, saved evaluation, and 3D asset checks are covered by `scripts/verify_artifacts.py` and the experiment-specific verifiers. To independently revisit an event rule or license, use the official source link and date in the research documents rather than assuming a missing local snapshot was packaged.
