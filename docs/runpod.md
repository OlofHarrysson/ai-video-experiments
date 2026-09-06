# RunPod tools

RunPod skills and the Codex MCP connection are scoped to this Git repository. The `runpodctl` executable may be installed globally. No global RunPod skill, plugin marketplace, or MCP registration is needed.

## Installed files

- `.agents/skills/`: eight unmodified official skills and their references: `runpod`, `runpod-mcp`, `runpodctl`, `runpod-templates`, `runpod-usage`, `flash`, `companion-clis`, and `runpod-migrate`.
- `.agents/runpod-source.json`: upstream version, commit, and installation provenance.
- `.agents/RUNPOD-LICENSE`: upstream Apache 2.0 license.
- `.codex/config.toml`: the hosted MCP connection at `https://mcp.getrunpod.io/`.

The installed snapshot is RunPod plugin version 1.2.0, commit `4912d93e5ac4746acf6415ca395413eabf0564f4`. Only its skill directories are copied; plugin manifests, hooks, commands, and global registrations are not installed. Updates are deliberate replacements from a reviewed upstream commit, with provenance updated in the same change.

Codex discovers `.agents/skills/` from the working directory up to the Git root, so these skills also apply when working in `apps/deforum/`. Project MCP configuration loads for trusted projects. Restart/reload Codex if newly installed skills or the connection do not appear.

## Authentication

The MCP server is configured for OAuth. From the repository root, sign in with:

```bash
codex mcp login runpod
```

Complete the browser sign-in yourself. Codex stores OAuth credentials outside the repository in its credential store; repository scoping controls where the server is configured, not where credentials are stored. No token belongs in the checked-in TOML.

MCP OAuth does not authenticate `runpodctl`. For CLI operations, put a RunPod API key in ignored `apps/deforum/.env` using the example in that directory. Load it explicitly with `uv` when invoking the CLI:

```bash
cd apps/deforum
uv run --no-project --env-file .env runpodctl user
```

Use the same prefix for other `runpodctl` commands. This uses `uv` to supply the environment for the global executable; it does not install a Python SDK. Do not add the key to shell startup files or global Codex configuration for this experiment.

Use one working control interface for each operation. The MCP handles infrastructure management once connected; the CLI is useful for SSH and file transfer. No Flash SDK or companion CLI is installed merely because its skill is present.

## Verification and scope

Verified on 2026-09-06 with Codex CLI 0.153.4:

- All 138 installed skill/reference files match the pinned upstream snapshot byte for byte.
- The MCP configuration resolves from the repository root and `apps/deforum/`, and is absent from `/tmp` and the global Codex config.
- `codex mcp login runpod` completed successfully; `codex mcp list --json` reports OAuth authentication. No account Pod listing has been performed yet.
- `runpodctl` 2.12.0 (`51ca7f0`) is installed globally through the official Homebrew tap. `runpodctl user` reports `no_credentials`; it requires a separate API key.
- No global RunPod skills or plugin registration, Flash SDK, or paid GPU resource was installed/created by this setup.

From this repository, `codex mcp get runpod --json` must resolve the hosted connection. From an unrelated directory, the same command must report no RunPod server unless the user separately configures one there. Config resolution is not proof of authentication: after sign-in, list Pods with the MCP tools to verify account access.

Before creating paid resources, inspect existing Pods, current rates, and the live official ComfyUI template. The [Deforum app README](../apps/deforum/README.md) owns the experiment sequence and budget boundary.

## Sources

- [Codex MCP project configuration](https://developers.openai.com/codex/mcp/).
- [Codex repository skill discovery](https://developers.openai.com/codex/skills/).
- [RunPod onboarding guide](https://docs.runpod.io/agent-setup.md).
- [Official RunPod skill source](https://github.com/runpod/runpod-plugins-official/tree/4912d93e5ac4746acf6415ca395413eabf0564f4/plugins/runpod/skills).
