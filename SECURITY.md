# Security Disclosure

## March 2026 code injection in `app.py`

| | |
|---|---|
| **Date introduced** | 2026-03-03 (commit `962a2cd`) |
| **Date discovered** | 2026-05-05 (home-page audit) |
| **Date remediated** | 2026-05-11 (this commit) |
| **Severity** | Critical |
| **Scope** | `app.py` only |

### What happened

Commit `962a2cd` — *"feat: implement global navigation ribbon"* — added an obfuscated `exec()` block at the end of `app.py`. The block was base64 + zlib + XOR encoded. Decoded, it is a multi-stage malware loader with the following behavior:

- Checks the host's locale and timezone, and exits silently if Russian indicators are present (anti-analysis pattern typical of Russian-speaking threat actors).
- Drops a persistence marker at `~/init.json`.
- Reads a command-and-control URL from transaction memos on Solana wallet `BjVeAjPrSKFiingBn4vZvghsGj9KCE8AJVtbc9S8o8SC` (public-blockchain dead-drop technique).
- Downloads Node.js v22.9.0 to the user's home directory.
- Fetches an encrypted JavaScript payload from the C2 URL and evaluates it via Node.js as a detached subprocess.

The technique stack (blockchain-memo C2, Russian-locale exclusion, Node.js stager for an encrypted JS stealer) is consistent with the *"Contagious Interview" / DEV#POPPER* campaign attributed by industry researchers to North Korean threat actors targeting developers via supply-chain compromise. Attribution is not confirmed.

The maintainer did not author this code. The introducing commit used the maintainer's name and email; provenance of the injection (stolen credential, compromised dev environment, etc.) is unconfirmed.

### Affected commits

The payload was reachable from:

- `962a2cd` — introducing commit
- `6b1da37` — descendant on `executive_overview`
- `ea4cb23` — merge of `executive_overview` into `main`

The five other files modified in `962a2cd` (`utils/nav.css`, `utils/navigation.py`, `views/home.py`, `test_app.py`, and the `rsconnect/shinyapps.io/.../gp-food-basket.dcf` deployment record) were audited and contain no additional payloads. The global navigation ribbon feature itself is legitimate work.

### Indicators of compromise

If you cloned this repository and ran `streamlit run app.py` between 2026-03-03 and 2026-05-11, check your home directory and project tree for:

- `~/init.json` — loader persistence marker
- `~/node-v22.9.0-darwin-arm64/`, `~/node-v22.9.0-darwin-x64/`, `~/node-v22.9.0-linux-x64/`, `~/node-v22.9.0-linux-arm64/`, or `~/node-v22.9.0-win-x64/`
- `i.js` anywhere inside the project directory

Presence of any of these means the loader executed in your environment and the downstream JavaScript payload ran as a background process.

### Status

- The malicious commit content remains visible in git history (`git show 962a2cd`) for forensic and disclosure purposes. History was not rewritten.
- The shinyapps.io deployment recorded in `rsconnect/shinyapps.io/conrad-linus-muhirwe/gp-food-basket.dcf` was taken offline separately and is no longer serving the affected build.

### Reporting

If you find additional artifacts or have information about how the injection was introduced, please open a GitHub issue on this repository.
