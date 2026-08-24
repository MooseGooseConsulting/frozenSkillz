# Goose

Configuration snapshot checked 2026-07-07. AgentsView `v0.40.1` has no Goose registry entry, so
current raw transcript facts remain unknown here. Verify live state for current questions.

## Identity

Goose is the client/harness. Its configured provider and model are separate settings.

- CLI snapshot: `goose` -> `C:\Users\pmacl\.local\bin\goose.exe`, version `1.38.0`.
- Config root candidate: `C:\Users\pmacl\.config\goose`.
- No `config.yaml` existed at the expected default path in the recovered snapshot.

The current Windows configuration file and the behavior of `goose configure` remain unverified.
Inspect the live root and current CLI help before assuming a Linux-default path.

## Diagnostics

```powershell
goose --version
Get-ChildItem "$env:USERPROFILE\.config\goose" -Force
Get-ChildItem $env:APPDATA,$env:LOCALAPPDATA -Directory -Filter Goose
```

The canonical transcript status and unknown fields are in
[Raw transcripts and field availability](transcripts-and-fields.md). Use `chat-history` to retrieve
or analyze prior Goose sessions.
