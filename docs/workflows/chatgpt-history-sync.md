# ChatGPT Organizer History Synchronization

The ChatGPT history sidecar is repository-owned support infrastructure for the
conversation organizer. It obtains one explicit authenticated endpoint contract,
writes immutable raw snapshots, and imports them into local SQLite WAL. It is not a
control plane and must not apply titles or Project membership changes.

The adapter may use a fresh successful snapshot for large read-only analysis. Use
ChatGPT web pages for all mutation and read-back verification. Reauthenticate
explicitly on auth expiry; endpoint drift, timeout, incomplete export, malformed
manifest, and checksum mismatch are hard failures.
