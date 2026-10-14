# Temporary doctor review access — 12 October 2026

**13 October update:** the user manually started the first tunnel and later explicitly requested a restart. That restart succeeded through the normal tool approval path. The current URL is `https://evans-idaho-asn-networks.trycloudflare.com`; authenticated remote health, predictions and browser flows have passed. It serves the current 104-mesh/dash-unknown build after refresh. The earlier blocked-launch state below is historical. Access remains temporary and requires the host laptop, gateway and tunnel to stay running; credentials remain only in ignored local state and chat.

The current application can run behind `scripts/reviewer_access.py`, a separate password gate. It serves the actual app, models, 3D assets and evidence. It does not change fitted models or metrics. Use synthetic profiles and the saved case challenge for expert feedback. No clinical review has yet occurred.

## Current state

The local review gate is running at `http://127.0.0.1:8011/review`. A random password and independent session token are in ignored `tmp/reviewer-access/access.json`; they are excluded from Git and the source bundle. The session expires 24 hours after creation, including previously authenticated clients. The password is shared directly in chat, not this tracked document.

**Remote link not created:** automatic approval review rejected the command that would start a Cloudflare Quick Tunnel, stating only `blocked by policy`. The agent did not retry through another tool or launch path. The user can choose to run the following command manually in PowerShell, with the existing local gate running:

```powershell
& 'E:\Multimodal AI Hackathon (heart)\tmp\reviewer-access\cloudflared.exe' tunnel --url http://127.0.0.1:8011 --protocol http2
```

The official [Cloudflare Quick Tunnel documentation](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/) describes the temporary HTTPS address printed by that command. Share the generated `https://...trycloudflare.com` address and the review password with the reviewer. Keep that terminal open and the laptop awake and online. Stopping the tunnel ends remote access. This is temporary review access, without an uptime guarantee or a permanent deployment. External HTTPS functionality has not been verified because the tunnel launch was blocked.

The downloaded binary is the official Cloudflare 2026.10.0 Windows amd64 executable. Its SHA-256 matches the [published release checksum](https://github.com/cloudflare/cloudflared/releases/tag/2026.10.0): `86aee4017b26625cee8484c113558f48effa4cd47f7aa05fcf425604e5d2b23c`. Windows Authenticode reports a valid Cloudflare, Inc. signature. The binary is under ignored `tmp/` and is not part of the release package.

## Review instructions to send with the link

Open in Chrome, Edge or Safari; a laptop/tablet provides more room for the 3D controls. Enter the review password, then:

1. Choose **Explore profile A** to obtain an actual prediction from synthetic observations.
2. Rotate the heart and inspect LAD, LCX and RCA, their labels and the meaning of their colors.
3. Read a probability and its feature explanation. Note any confusing or medically misleading wording.
4. Use **Try four cases** to inspect a saved model error.
5. Open **Model evidence** to see the evaluation and population limitations.

Ask for exact corrections and the screen/field involved. A screenshot or voice note can help, without identifiable patient information. The [clinical review packet](clinical_review_packet.md) supplies focused questions. Do not label feedback as clinical validation or quote the reviewer publicly without permission.

## Verification

Four focused tests passed: protected API/assets cannot be read without authentication; wrong/forged credentials fail; successful login sets a Secure, HttpOnly, SameSite=Lax cookie; protected responses are not cached; session expiry applies to all requests; oversized password bodies and repeated failed login attempts are bounded. Lifespan is forwarded to the actual app so model integrity/loading behavior is retained.

Real local Chromium logged in successfully, ran Profile A to **Prediction ready**, rendered a 3D canvas and opened the current operating-point evidence. Desktop 1440x1000 and mobile 390x844 screenshots were inspected; document width was 380 at viewport 390. Browser console reported zero errors/warnings. Screenshots: `output/playwright/2026-10-12-review-gateway-desktop.png` and `2026-10-12-review-gateway-mobile.png`. This verifies the local gated app, not remote tunnel availability.

## Stopping or restarting

The current gateway process ID is stored in ignored `tmp/reviewer-access/processes.json`. Stop only that verified process when the review ends; the ordinary local app is separate. For a new session, stop the old gateway first, explicitly rotate the ignored access file, then run `python scripts/reviewer_access.py create` and `python scripts/reviewer_access.py serve` from this workspace. The serve command binds only to loopback port 8011. A remote link requires the separate tunnel step.
