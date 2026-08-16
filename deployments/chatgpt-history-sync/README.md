# ChatGPT history synchronization sidecar

`tools.chatgpt_history_sync` is an organizer-oriented raw-history sidecar, not a
general ChatGPT backup product. It stores immutable export snapshots and an SQLite
WAL index at `history.sqlite3`.

- Windows: `%LOCALAPPDATA%\frozenSkillz\chatgpt-history\`
- Linux: `$XDG_DATA_HOME/frozenSkillz/chatgpt-history/`, or
  `~/.local/share/frozenSkillz/chatgpt-history/`

It requires an explicit authenticated endpoint contract through
`CHATGPT_HISTORY_SESSION_COOKIE`. Expired authentication, schema drift, timeout,
incomplete pagination, malformed manifests, and hash mismatches fail the run; no
alternate acquisition method is attempted. Attachment metadata and mapping branches
are preserved, but binary attachment backup is not a v1 feature.

Install the Linux user timer after placing the CLI at the service path or changing
`ExecStart` to its installed absolute path:

```sh
mkdir -p ~/.config/systemd/user
cp chatgpt-history-sync.service chatgpt-history-sync.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now chatgpt-history-sync.timer
```

Run a controlled export/import with `python -m tools.chatgpt_history_sync.cli sync`.
ChatGPT remains source of truth; SQLite is an analysis index, history, and proposal
ledger. A complete snapshot reconciles missing conversations and Project moves;
an incomplete snapshot cannot tombstone anything.
