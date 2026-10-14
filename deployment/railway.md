# Railway deployment

Use the public repository `https://github.com/jozai193/coronary-atlas`, branch `codex/submission-ready`. The root Dockerfile builds the complete frontend and installs both baseline and optional research model dependencies. It includes the public JSON fixtures checked by TypeScript and the evidence files required to load the ensemble. No training or private API key is needed.

For a new service, configure these values in Railway's service UI:

- Builder: Dockerfile (automatically detected from the root Dockerfile).
- Variable: `PORT=8000`.
- Public domain target port: `8000`.
- Readiness health-check path: `/api/health`.
- One replica. Do not enable a paid upgrade without the account owner's approval.

Railway's current UI states that new services can no longer opt in to legacy Config as Code, so this repository does not rely on a `railway.json` file. Existing source package and model hashes remain unchanged by hosting configuration.

Before using a generated URL for judging, check `/`, `/api/health`, `/api/review-profiles`, `/api/model/candidates` and real predictions for A/B across all three variants without cookies or authentication. Verify the heart, explanations, source review, local OCR, public ECG viewer and exports in a fresh browser. Record the deployed commit and actual limits; no clinical accuracy claim follows from deployment checks.

Availability depends on the hosting account's remaining credits/plan. The public source, technical report and unlisted demo video remain independently accessible.
