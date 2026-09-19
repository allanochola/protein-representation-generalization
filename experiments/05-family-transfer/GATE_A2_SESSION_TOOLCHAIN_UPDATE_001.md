# Gate A2 session-toolchain update 001

A Kaggle reset removed the previous session manifest and tool binaries. This update records a rebuilt environment while A2-SS remains disabled.

Previous session manifest SHA-256: `957aef98a65d5dc646cdc33a02fd352bf8b7d8d0afd9d6c4500013acd8873d2e`.

New session manifest SHA-256: `46f16cddd0b823f6a2f37ae60508bb7576f6724362141c27cf55dafc812ed25a`.

The companion JSON records source identities, exact build commands, compiler versions, Pfam file identities, pressed database identities and session binary hashes. The source commit and pinned Pfam bytes are durable identities; rebuilt binaries are session identities. Same version output alone does not establish identical build flags.

Pfam 37.0, 21,979 models, `--cut_ga`, the MMseqs2 source commit and scientific parameters, the two-run replay rule, and the frozen joint input hashes are unchanged. No scan or geometry computation was performed to choose this environment.

The runner pin is adopted in a subsequent disabled commit. Audits must pass before a separate authorization commit and one execution.
