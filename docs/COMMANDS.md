# Workshop commands — full walkthrough on Derecho

Every command you'll run during the workshop, in the order you'll run
them. All of these assume you've just SSH'd into Derecho (or Casper —
either works).

Three command flavours appear here:

| Prompt prefix | What it means |
|---|---|
| `$` | shell command — run in your terminal |
| `>` | run inside Claude Code (i.e., after typing `claude` and getting the agent prompt) |
| `# in chat` | chat input that starts with `#` (a quick-add memory trigger) |

---

## Phase 0 · One-time setup (do this **before** the workshop) · *slides W03, W04*

Skip the whole phase if `claude --version` and `which gitnexus` already
both print something on this host.

### 0.1 · Get on Derecho with a fresh conda env

```bash
$ ssh derecho.hpc.ucar.edu
$ module load conda                              # makes `conda` available
$ conda create -n claude_test python=3.12 -y     # one-time
$ conda activate claude_test
$ python --version                               # confirm: Python 3.12.x
```

In every new shell session you'll need:

```bash
$ module load conda
$ conda activate claude_test
```

(Add those two lines to `~/.bashrc` if you don't want to type them
every time.)

### 0.2 · Clone the workshop repo

```bash
$ cd ~                        # or wherever you keep code
$ git clone https://github.com/AnonNick/claude-workshop.git
$ cd claude-workshop
$ pip install -e .            # pulls numpy, xarray, netCDF4, matplotlib
$ pytest -m "not needs_data"  # quick sanity — 3 passed
$ pytest                      # full run — 10 passed, 2 failed (intentional)
```

The two failing tests **are the exercises**. Don't fix them yet.

The full-run pytest reads a WACCM-X NetCDF off `/glade/campaign`. The
exact path:

```
/glade/campaign/hao/itmodel/joemci/archive/\
  f.e22.FXSD.f19_f19_mg17.001/atm/hist/2020/\
  f.e22.FXSD.f19_f19_mg17.001.cam.h0.2020-01.nc
```

A WACCM-X FXSD monthly-mean h0 file for January 2020 on the f19 grid
(96 × 144, 145 levels, ~1.8 GB). Tests that need it are marked
`needs_data` and skip automatically if you can't see the path. Quick
inspection — try any of:

```bash
$ ls -lh /glade/campaign/hao/itmodel/joemci/archive/\
    f.e22.FXSD.f19_f19_mg17.001/atm/hist/2020/ | head
$ ncdump -h /glade/campaign/hao/itmodel/joemci/archive/\
    f.e22.FXSD.f19_f19_mg17.001/atm/hist/2020/\
    f.e22.FXSD.f19_f19_mg17.001.cam.h0.2020-01.nc | head -30
```

The path is also hard-coded into `tests/conftest.py` (fixture
`waccmx_path`) and the example plot script — no env var needed.

### 0.3 · Install Claude Code

```bash
$ curl -fsSL claude.ai/install.sh | bash
$ echo 'export PATH="$HOME/.claude/bin:$PATH"' >> ~/.bashrc
$ source ~/.bashrc
$ claude --version            # should print a version
```

Auth once with the API key you were given:

```bash
$ claude                       # choose option 2, paste the key
> /exit                        # leave Claude for now
```

### 0.4 · Install Node + GitNexus globally

Derecho ships Node already, but the default install path won't work
because `npx -y` re-resolves on each launch and triggers an npm bug.
Install once, globally:

```bash
$ mkdir -p ~/.npm-global
$ npm config set prefix ~/.npm-global
$ echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
$ source ~/.bashrc

$ npm install -g gitnexus
$ which gitnexus               # → ~/.npm-global/bin/gitnexus
$ gitnexus --version           # → 1.5.3 or higher
```

### 0.5 · Verify the libstdc++ override

GitNexus's native add-on needs `GLIBCXX_3.4.32`, which Derecho's `node`
binary can't find on its own. We point at the system miniforge env:

```bash
$ strings /glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6 \
    | grep -c GLIBCXX_3.4.32
2
```

If you get `0`, see [SETUP-DERECHO.md](SETUP-DERECHO.md) for fallback
paths.

---

## Phase 1 · Workshop · Warm-up (Exercise 0) · *slides W05, W05a, W06*

### 1.1 · The four-part prompt · *slide W05a*

Before you type anything into Claude, get used to the shape of a good
prompt. Every non-trivial request has four parts:

| Part | What it is | Example |
|---|---|---|
| **GOAL** | what outcome you want | "Fix the failing T_elec test." |
| **FILES** | where to look | `@src/wxpost/interp/linear.py` |
| **CONSTRAINTS** | what not to change | "Keep the public API. No new deps." |
| **VERIFICATION** | how we'll know it worked | "pytest must pass. Add a regression test." |

Stitched into one prompt:

```
> Fix test_to_height_thermosphere_telec. The bug is in
  @src/wxpost/interp/linear.py. Don't change the public API; no new
  dependencies. Make pytest pass and add a regression test.
```

Every prompt you type later in the workshop should hit at least three
of the four.

### 1.2 · Land in the repo and start Claude · *slide W05*

```bash
$ cd ~/claude-workshop
$ claude
```

You should see the Claude banner, the cwd, and a `>` prompt.

### 1.3 · Ask Claude to orient itself · *slide W06*

```
> what does this repo do?
```

Watch the read list — Claude will open `README.md`, `pyproject.toml`,
maybe a few source files. That's your signal it actually looked.

```
> where would I add a new vertical coordinate?
```

Useful to see how Claude maps the question to the file layout. The
answer should mention `src/wxpost/coords/`.

```
> /exit
```

---

## Phase 2 · Fundamentals — the slash menu · *slides W08, W09, W10, W11, W11b, W11c*

Inside Claude (`$ claude` if you exited):

| Inside Claude | Why |
|---|---|
| `> /help` | see all slash commands available |
| `> /context` | see exactly what's in the context window right now |
| `> /model` | switch tier mid-session (Haiku · Sonnet · Opus) |
| `> /cost` | tokens used and dollars spent in this session |
| `> /compact` | summarize history so far; keeps insights, drops chatter |
| `> /clear` | wipe context, start fresh |
| `> /effort high` | crank up thinking depth for the next prompt |
| `> /review` | have Claude critique its own last response or diff |
| `> /memory` | open project + user CLAUDE.md side-by-side to edit |
| `> /init` | generate a starter CLAUDE.md for the current repo |
| `> /mcp` | list connected MCP servers and the tools each one exposes |
| `> /agents` | inspect & configure subagents |
| `> /hooks` | configure pre/post tool hooks (power-user) |
| `> /statusline` | configure the line printed above your prompt each turn |

### Pick one to actually customise — `/statusline` · *slide W11c*

```
> /statusline write a bash script (type "command") that reads the Claude
  JSON on stdin and prints, joined by " | ": model name in cyan; a 10-char
  ░█ bar + % for context, green; git branch with the Powerline glyph in
  magenta; rate-limit fractions colored green<40 / yellow<80 / red≥80;
  cwd basename in blue. Use jq + raw ANSI; skip empty parts.
```

Claude writes the script into `~/.claude/settings.json` for you. Next
turn, the new line appears above your prompt.

---

## Phase 3 · Memory (Exercise 1) · *slides W08–W13 (memory section)*

### 3.1 · Bootstrap CLAUDE.md for this repo · *slide W09 (project memory)*

```
> /init
```

Claude scans the repo and writes a draft `CLAUDE.md`. **Note**: this
repo already ships a `CLAUDE.md`. `/init` will offer to add to it or
overwrite — pick "add to it."

```
> /exit
$ git diff CLAUDE.md           # see what /init proposed
$ git checkout CLAUDE.md       # roll back if you want the original
```

### 3.2 · Quick-add memories with `#` · *slide W11 (quick-add)*

Inside Claude, type `#` as the first character of your message. Claude
treats the rest as a memory candidate and asks where to save it.

```
# in chat:
# I prefer short explanations and minimal diffs.
```

Pick `[2] User` — this lives in `~/.claude/CLAUDE.md`, every project
sees it.

```
# in chat:
# Tropospheric T tests in this repo target 1e4, 1e3, 1e2 Pa (100, 10, 1 hPa).
```

Pick `[1] Project` — this lives in `./CLAUDE.md`, your team sees it.

### 3.3 · Verify what got saved

```
> /exit
$ cat ~/.claude/CLAUDE.md
$ cat ./CLAUDE.md
```

---

## Phase 4 · MCP + GitNexus (Exercise 2) · *slides W14–W22*

### 4.1 · Index this repo with GitNexus · *slides W18, W20*

```bash
$ cd ~/claude-workshop
$ LD_PRELOAD=/glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6 \
    /glade/u/apps/opt/miniforge/envs/npl-2026a/bin/node \
    $HOME/.npm-global/bin/gitnexus analyze
```

You should see "Walked N files / Parsed N symbols / Wrote .gitnexus/"
followed by `.claude/skills/` being installed and `CLAUDE.md` being
updated. The index lives in `./.gitnexus/`.

### 4.2 · Register the GitNexus MCP server · *slides W17 (scopes), W20*

```bash
$ claude mcp remove gitnexus -s user 2>/dev/null    # idempotent
$ claude mcp add gitnexus -s user \
    -e LD_PRELOAD=/glade/u/apps/opt/miniforge/envs/npl-2026a/lib/libstdc++.so.6 \
    -- ~/.npm-global/bin/gitnexus mcp

$ claude mcp list
```

Expect `gitnexus: … - ✓ Connected`. If you see `✗ Failed to connect`,
re-check paths in step 0.4 and 0.5.

### 4.3 · Restart Claude so it picks up the new MCP

MCP tools are loaded at session startup, not live. Always restart after
adding a server.

```bash
$ claude
> /mcp                         # gitnexus should appear with ~7 tools
```

### 4.4 · Try a GitNexus-powered question · *slide W21 (Ex 2)*

```
> What depends on the function `interp_1d` in src/wxpost/interp/linear.py?
```

Watch the tool-call list — you should see `mcp__gitnexus__impact` (or
`mcp__gitnexus__query`) rather than plain `Bash grep`. That's the
signal the MCP is working.

```
> Draw me an architecture diagram of this package as a Mermaid graph.
```

The Mermaid diagram renders in VS Code (install the Mermaid preview
extension if you haven't).

---

## Phase 5 · Skills, slash commands, permission modes · *slides W23–W27a*

### 5.1 · Write a project skill · *slides W24, W25, W26 (Ex 3)*

```
> Write a skill for code review of changes to src/wxpost/. It should:
  1. Run pytest first and report failures.
  2. Check that any new public function has a docstring.
  3. Verify no print() statements were added.
  4. Output a markdown review.
  Save it as .claude/skills/review-wxpost/SKILL.md. Make the
  description specific enough that you'll auto-invoke it when I ask
  "review this PR" or "review my changes."
```

```
> /exit
$ cat .claude/skills/review-wxpost/SKILL.md
$ git status                   # the new skill should appear here
```

### 5.2 · Write a custom slash command · *slide W27*

```bash
$ mkdir -p .claude/commands
$ cat > .claude/commands/pr-summary.md <<'EOF'
Generate a PR description for the current branch.

1. Run `git log main..HEAD --oneline` to see what's new.
2. Group commits by type (feat / fix / docs / chore).
3. Open the most touched files and skim them.
4. Write a 3-section markdown PR body:
     ## What
     ## Why
     ## Test plan
5. Print it to the chat. Do NOT open a PR yet.

Tone: terse, factual, no emojis.
EOF
```

Use it:

```bash
$ claude
> /pr-summary
```

### 5.3 · Permission modes — the `Shift+Tab` cycle · *slide W26b*

How aggressive Claude is allowed to be. Cycle through the four modes
by tapping `Shift+Tab` from inside Claude:

| # of taps | Mode | Edits | Bash | Use when |
|---|---|---|---|---|
| 0 | **NORMAL** (default) | ASK | ASK | Learning the agent, sensitive paths. |
| 1 | **ACCEPT EDITS ON** | AUTO | ASK | You trust the diffs. Still gate command exec. |
| 2 | **PLAN** | BLOCKED | BLOCKED | Large refactors. Unfamiliar code. Read-only thinking. |
| 3 | **AUTO MODE ON** | AUTO | AUTO | Sandboxed env / scripted CI only. Not daily use. |

Cycling wraps — a fourth tap returns you to NORMAL. The current mode
shows in the status bar above your prompt.

### 5.4 · Plan mode and the safety net · *slide W27a*

Before you turn Claude loose on the bug exercise, get familiar with
plan mode (Shift+Tab × 2). Try this:

```bash
$ claude
```

Tap `Shift+Tab` twice. You should see something like
`> [plan mode]` in the status line. Then:

```
> pytest fails on tests/test_io.py::test_lat_orientation. Read the
  test and the code it tests. Tell me what the bug probably is, but
  do NOT change any files.
```

Claude can read, grep, run searches, and reason — but **cannot** edit
files or run commands until you approve the plan. Tap `Shift+Tab`
twice more to leave plan mode when you're done thinking.

Plus the three layers of undo:

- **Diff approval** — every edit shown as +/−. Accept, edit, or reject one-by-one.
- **`/undo`** — step back one turn; files revert.
- **`git`, always** — commit before a big task. Claude's work becomes a diff you can squash or drop.

---

## Phase 6 · Main exercise — fix the bugs · *slides W28, W29, W30*

### 6.1 · See the failures · *slide W29 (both bug cards)*

```bash
$ cd ~/claude-workshop
$ pytest
```

Two failures:
- `tests/test_io.py::test_lat_orientation` — the warm-up bug
- `tests/test_ops.py::test_to_height_thermosphere_telec` — the main bug

### 6.2 · See the warm-up bug visually · *slide W29 card 1*

```bash
$ python examples/plot_surface_temperature.py
```

It prints something like:

```
60°N (label):  +1.8°C    expected ~ -10°C  (NH winter)
60°S (label): -10.2°C    expected ~  +2°C  (SH summer)
⚠ The plot shows 60°N WARMER than 60°S in January. That's impossible.
```

The image is at `examples/surface_temperature.png` — open it in VS Code
or `eog`/`feh` if you have an X session.

### 6.3 · Fix Bug 1 with Claude · *slide W30 (workflow)*

```bash
$ claude
```

Tap `Shift+Tab` × 2 to enter plan mode. Then:

```
> The test tests/test_io.py::test_lat_orientation fails. Plan how to
  fix it; do not touch files yet. The examples plot also shows the
  hemispheres flipped — both symptoms are the same bug.
```

Read the plan. Approve it (Shift+Tab again or accept on the prompt).
Let Claude make the edit. Then:

```
> /exit
$ pytest tests/test_io.py
$ python examples/plot_surface_temperature.py    # plot should look right now
```

### 6.4 · Fix Bug 2 with the GitNexus workflow · *slide W30 (workflow)*

```bash
$ claude
```

Tap `Shift+Tab` × 2 to enter plan mode. Then:

```
> tests/test_ops.py::test_to_height_thermosphere_telec returns 280 K
  when it expects ~1600 K. to_pressure works fine; only to_height
  fails. Use GitNexus to find what's shared between the two ops and
  the most likely location of the bug. Don't change any files yet.
```

When Claude proposes a plan that touches `src/wxpost/interp/linear.py`,
let it edit. Then:

```
> /exit
$ pytest                       # 12 passed
```

### 6.5 · Have Claude review its own changes

```bash
$ claude
> review my changes
```

Your `review-wxpost` skill from Phase 5 should auto-invoke. If it
doesn't, name it explicitly: `> use the review-wxpost skill on my
changes`.

### 6.6 · Commit

```
> Commit my changes in two commits — one per bug. Write the commit
  messages yourself. Don't push.
```

```
> /exit
$ git log --oneline -5
```

---

## Phase 7 · Wrap-up reference · *slide W31 (cheat sheet)*

### Run anywhere

```bash
$ claude --version
$ claude mcp list
$ pytest                       # confirms everything still works
$ python examples/plot_surface_temperature.py
```

### Inside Claude — the budget five

```
> /context        # what's loaded
> /model          # switch tier
> /cost           # tokens + dollars
> /compact        # trim history
> /clear          # wipe
```

### Files worth remembering

| Path | What it is |
|---|---|
| `./CLAUDE.md` | project memory · team sees it |
| `~/.claude/CLAUDE.md` | user memory · just you, every project |
| `./.claude/skills/*/SKILL.md` | project skills · committed |
| `~/.claude/skills/*/SKILL.md` | user skills · personal |
| `./.claude/commands/*.md` | custom slash commands |
| `./.mcp.json` | project-scope MCP server registrations |
| `~/.claude/settings.json` | user-scope MCP servers + status line script |
| `./.gitnexus/` | GitNexus knowledge graph for this repo |
