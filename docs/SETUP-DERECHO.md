# Workshop setup on Derecho / Casper

A handful of NCAR-system-specific gotchas you'll hit before things "just
work". Walk through these once before the workshop and you won't get
stuck in the room.

## 1. Clone the repo and install the package

```bash
cd ~                       # or wherever you keep code
git clone https://github.com/AnonNick/claude-workshop.git
cd claude-workshop

module load conda          # gets you Python 3.10 + xarray + netCDF4 + matplotlib
pip install -e .
pytest -m "not needs_data" # quick sanity — should show 3 passed
pytest                     # full run — 10 passed, 2 failed (intentional)
```

The two failing tests are the workshop exercises. Don't fix them yet.

## 2. Install Claude Code

```bash
curl -fsSL claude.ai/install.sh | bash
```

The installer drops a binary in `~/.claude/bin`. Add it to your PATH in
`~/.bashrc`:

```bash
echo 'export PATH="$HOME/.claude/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
claude --version           # should print a version
```

Run `claude` once, paste the API key you were given (option 2 in the
prompt), and you're done.

## 3. Install GitNexus — and the two Derecho gotchas

GitNexus is a Node CLI that ships a native `lbugjs.node` add-on. The
generic "one-liner" install from the README does not work on Derecho.
Two reasons:

### Gotcha A — `npx -y` is broken on Derecho's node

The default install instructions tell you to register the MCP server as

```
claude mcp add gitnexus -- npx -y gitnexus@latest mcp
```

`npx -y` re-resolves the package on every launch and hits this npm bug:

```
TypeError: Cannot destructure property 'package' of 'node.target' as it is null.
```

**Workaround:** install GitNexus globally once, then point the MCP at the
installed binary instead of letting `npx` re-resolve it each time.

```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

npm install -g gitnexus
which gitnexus             # should print ~/.npm-global/bin/gitnexus
```

### Gotcha B — `GLIBCXX_3.4.32` not found

Derecho's `node` binary has a baked-in `RPATH` pointing at GCC 12.5.0's
`libstdc++.so.6`. GitNexus's native add-on needs a newer one:

```
Error: ... libstdc++.so.6: version `GLIBCXX_3.4.32' not found
       (required by .../@ladybugdb/core/lbugjs.node)
```

`RPATH` takes precedence over `LD_LIBRARY_PATH`, so the only fix that
works is `LD_PRELOAD` of a newer `libstdc++.so.6`. The system-wide
miniforge env on Derecho has one available to every user:

```
/glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6
```

Sanity check (should print `2`):

```bash
strings /glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6 \
  | grep -c GLIBCXX_3.4.32
```

## 4. Index the repo with GitNexus

```bash
cd ~/claude-workshop

LD_PRELOAD=/glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6 \
  gitnexus analyze
```

You should see a "Walked N files / Parsed N symbols / Wrote .gitnexus/"
summary at the end. If you previously indexed with `--embeddings`, pass
that again — re-running without it deletes embedded vectors. Check with:

```bash
jq '.stats.embeddings' .gitnexus/meta.json   # null if unembedded
```

## 5. Register the MCP server with Claude Code

The MCP-add command needs the `LD_PRELOAD` baked into the server
definition (so Claude's MCP supervisor sets it on every server launch):

```bash
claude mcp remove gitnexus -s user 2>/dev/null    # idempotent — ignore "not found"
claude mcp add gitnexus -s user \
  -e LD_PRELOAD=/glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6 \
  -- ~/.npm-global/bin/gitnexus mcp
```

Verify:

```bash
claude mcp list
```

You should see `gitnexus: … - ✓ Connected`. If it says `✗ Failed to
connect`, re-check the libstdc++ path and that `which gitnexus` resolves
to `~/.npm-global/bin/gitnexus`.

**Restart Claude Code** after this step — MCP servers and their tools
are loaded at session startup, not live, so an already-open session
won't see the new tools.

## 6. Smoke-test from inside Claude

```bash
cd ~/claude-workshop
claude
```

```
> /mcp
```

You should see `gitnexus` listed with ~7 tools. Then:

```
> What does this repo do?
```

Claude should read the README, CLAUDE.md, and call `gitnexus_*` tools
(rather than plain Bash grep) for any structural questions. Watch the
tool-call list for `mcp__gitnexus__*` calls — that's the signal that
the MCP is wired up correctly.

## Quick reference

| Path | What it is |
|---|---|
| `~/.npm-global/bin/gitnexus` | the GitNexus CLI (installed globally) |
| `/glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6` | the newer libstdc++ to LD_PRELOAD |
| `~/.claude/bin/claude` | Claude Code CLI |
| `~/.gitnexus/meta.json` (per-project) | GitNexus index metadata |
| `/glade/campaign/hao/itmodel/joemci/archive/f.e22.FXSD.f19_f19_mg17.001/atm/hist/2020/` | the WACCM-X file the tests read |
