# Private configuration and Git

Keep passwords, real device configurations, client/device keys, firmware flash
backups and provisioning logs in `.local/`. That entire directory is ignored.
The S2's private configuration stays on disk and on the board, not in Git.
Live `firmware/config.json`, other non-example firmware configurations, local
gateway plists, environment files, credential/key files, databases and editor
backups are also ignored. Commit only empty/placeholder example configurations.
CAD `config.json` files describe geometry and remain tracked.

The local pre-commit hook rejects staged files matching ignore rules (including
files added with `git add -f`), checks for known local Wi-Fi/device credentials,
and runs Gitleaks with fully redacted output. The exact-value check uses local
S2 provisioning files and the live firmware configuration; Gitleaks supplies
broader pattern detection. Neither check sends secrets to an external service.

Install Gitleaks and enable the hook in each checkout:

```sh
git config --local core.hooksPath .githooks
```

The hook is enabled in the current project checkout. Missing Gitleaks or a
failed credential check blocks the commit. Hooks are local safeguards, can be
bypassed, and are not automatically enabled in a fresh clone. Ignore rules do
not remove files already tracked or erase earlier commits. No automatic scan
can identify every possible piece of sensitive information: review staged
changes before committing, and keep new private artifacts under `.local/`.

## Audit on 2026-09-05

After fetching GitHub refs, the audit searched 298 historical Git blobs across
all available refs and reflogs, 18 ZIP members, and tracked working files for
the actual Wi-Fi password and both gateway keys (raw, JSON-escaped and Base64).
There were no matches. A fully redacted Gitleaks history scan also reported no
leaks. Private audit reports remain under `.local/s2/`. No history rewrite was
needed. This records the scope of the audit, not a guarantee about unknown
secrets or copies outside this repository.
