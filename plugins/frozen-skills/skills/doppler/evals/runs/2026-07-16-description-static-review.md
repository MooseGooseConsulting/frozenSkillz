# 2026-07-16 — static description routing review

Not a live multi-run agent eval. This is a first-pass judgment of the rewritten frontmatter description against `triggers.json` before Cursor fresh-session runs.

## Description under test

> Manage secrets with the Doppler CLI: doppler run injection, names-only diagnostics, set/upload secrets, service tokens for CI, and no-print hygiene. Use when the user mentions Doppler, doppler run, service tokens, secret injection, or asks to store, rotate, or verify API keys, tokens, passwords, or .env credentials. Do not use for ordinary non-secret environment variables or general app config unrelated to credentials.

## Train

| Query | Expected | Static judgment | Notes |
|---|---|---|---|
| Store this API key in Doppler for the dev config | true | likely trigger | Doppler + API key |
| Run pytest with secrets injected via doppler | true | likely trigger | doppler + secret injection |
| Is DATABASE_URL set in Doppler without printing it? | true | likely trigger | Doppler + credential-ish var |
| Create a CI service token for the prd config | true | likely trigger | service token |
| dont paste this token in chat, put it in doppler | true | likely trigger | token + doppler |
| Rotate the webhook secret and update Doppler | true | likely trigger | secret + Doppler |
| List secret names in the current Doppler project | true | likely trigger | Doppler + secrets |
| Add a DEBUG=true flag to our Node config | false | likely skip | negative boundary (non-secret config) |
| What's the difference between process.env and dotenv? | false | likely skip | general env education |
| Update the Dockerfile ENV for NODE_ENV=production | false | likely skip | non-secret ENV |
| Document our public API base URL env var | false | likely skip | public/non-secret |
| Refactor how the app reads PORT | false | likely skip | ordinary app config |

## Validation

| Query | Expected | Static judgment | Notes |
|---|---|---|---|
| Upload our local .env credentials into Doppler staging | true | likely trigger | .env credentials + Doppler |
| Verify the Stripe API key exists in Doppler names-only | true | likely trigger | API key + Doppler + names-only |
| Wire GitHub Actions to use DOPPLER_TOKEN and doppler run | true | likely trigger | DOPPLER_TOKEN + doppler run |
| Set LOG_LEVEL=info in the app's default config object | false | likely skip | ordinary config |
| Explain how Kubernetes ConfigMaps differ from Secrets | false | watch | shares “Secrets” word; negative boundary should help |
| Change the compose file to pass NODE_ENV from the host | false | likely skip | ordinary env pass-through |

## Held out

| Query | Expected | Static judgment |
|---|---|---|
| I accidentally pasted a GHCR token in chat — get it into Doppler silently… | true | likely trigger |
| Rename the FEATURE_FLAG_FOO env key in our TypeScript settings module | false | likely skip |

## Next

Run live Cursor fresh-session 3× passes per query; log results beside this file. Watch especially the ConfigMaps vs Secrets validation case for false positives.
