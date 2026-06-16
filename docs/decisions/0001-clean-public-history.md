# 0001 Clean Public History

## Decision

Use a clean public branch (`public-main`) and preserve the raw workspace on `archive-raw-rop299`.

## Reason

The original repository contained coursework, literature PDFs, generated outputs, large embeddings, bytecode, and model checkpoints. Removing those files in a normal commit would leave them recoverable from public Git history.

## Consequence

The clean public branch starts with a new root commit. The archived branch remains available locally for recovery and provenance.
