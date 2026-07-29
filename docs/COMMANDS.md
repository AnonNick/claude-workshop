# Handout — Part 2: Claude Code

Every command for the Claude Code half of the workshop, in the order you'll
run them. Part 1 (claude.ai) needs no repo and isn't covered here.

Two prompt flavours appear below:

| Prefix | What it means |
|---|---|
| `$` | shell command — run in your terminal |
| `>` | typed inside Claude Code (after running `claude`) |

Each section maps to a slide. Timings are the slide's, not a rule.

---

## Exercise 08 · Setup check · 5 min

```bash
$ claude --version          # should print a version
```

No Claude Code yet?

```bash
$ curl -fsSL claude.ai/install.sh | bash
$ echo 'export PATH="$HOME/.claude/bin:$PATH"' >> ~/.bashrc   # or ~/.zshrc
$ source ~/.bashrc
```

Then pick a codebase. **Either** works for everything that follows — your
own code is more interesting, the workshop repo is more predictable.

**Your own code:**

```bash
$ cd ~/path/to/any/project/you/brought
```

**Workshop repo:**

```bash
$ git clone https://github.com/AnonNick/claude-workshop.git
$ cd claude-workshop
$ python3 -m venv .venv && source .venv/bin/activate
$ pip install -e .[dev]
$ pytest                    # expect: 2 failed, 10 passed
```

The two failures are the exercises. Don't fix them yet.

Either way, finish by starting the agent:

```bash
$ claude
```

Helpers are circulating — flag anything broken.

---

## Three dials · model · effort · mode

Leave the defaults. Reach up when the problem earns it.

| Dial | How | Options |
|---|---|---|
| Model | `> /model` | Sonnet (default) · Opus (hardest reasoning) · Haiku (quick loops) |
| Effort | `> /effort` | low · medium · high (default) · xhigh |
| Mode | `Shift+Tab` cycles | Default · Accept Edits · Plan · Auto · Don't Ask · Bypass |

Two keywords worth knowing:

- **`ultrathink`** — max thinking for one turn. Just type it in your prompt.
- **`ultracode`** — session mode: xhigh plus parallel orchestration.
  Deliberate use only; it spends a lot.

Context and cost, any time:

```
> /context      # what's filling the window right now
> /cost         # tokens and spend this session
> /compact      # summarise history at a seam you pick
> /clear        # fresh start
> /doctor       # diagnose a broken install
```

---

## Your cockpit · `/statusline` · 5 min

Slide 30 sends you here for the full prompt. Paste this, adjusting to taste:

```
> /statusline write a bash script (type "command") that reads the Claude
  JSON on stdin and prints, joined by " | ": model name in cyan; a 10-char
  ░█ bar + % for context, green; git branch with the Powerline glyph in
  magenta; rate-limit fractions colored green<40 / yellow<80 / red≥80;
  cwd basename in blue. Use jq + raw ANSI; skip empty parts.
```

Claude writes the script into `~/.claude/settings.json`. Next turn, the new
line appears above your prompt:

```
~/wxpost   Opus 4.8 | ███████░░░ 68% |  main | 5h[3h]:42% | 7d:61% | wxpost
```

---

## INIT · `/init` and CLAUDE.md · 6 min

```
> /init
```

Claude reads the repo and writes a `CLAUDE.md`. **Note:** the workshop repo
already ships one, so `/init` will offer to extend it rather than start from
scratch — take the offer.

Then open the file and **edit one line you actually mean**. That is the
whole point: `CLAUDE.md` loads fresh every session, so in a shared repo it's
how the lab teaches Claude.

Quick-add, without leaving the chat — start a message with `#`:

```
> # Pressure is stored in Pa internally, even though WACCM-X files use hPa.
```

Claude asks where to save it:

- `[1] Project` → `./CLAUDE.md` — your team sees it
- `[2] User` → `~/.claude/CLAUDE.md` — just you, every project

Check what landed:

```bash
$ git diff CLAUDE.md
$ cat ~/.claude/CLAUDE.md
```

`/memory` opens both to edit. Auto-memory — the notes Claude takes on its
own — lives in `~/.claude/projects/…/memory/`; review it like a diff.

---

## EXPLORE · let it map the code first · 6 min

**Workshop repo:**

```
> explain what this codebase does and how it's organized
```

**Your repo:** same, then:

```
> what does @<some-file> actually do?
```

`@` tab-completes file paths, and reads images and notebooks too. Watch the
read list — that's your signal it actually looked instead of guessing.

Two more that make it work across the whole tree:

```
> what depends on the function `interp_1d` in @src/wxpost/interp/linear.py?
> draw me an architecture diagram of this package as a Mermaid graph
```

---

## PLAN · look, don't touch · 7 min

`Shift+Tab` to **Plan mode** first. Nothing changes until you approve.

**Workshop repo:**

```
> the test suite has two failures. investigate the interpolation one and
  propose a fix
```

That's `test_to_height_thermosphere_telec`. It returns ~255 K where it
expects ~1700 K. `to_pressure` works fine and only `to_height` fails — the
useful question is what those two share.

**Your repo:**

```
> here's something that's broken or has always bugged me: <describe>.
  investigate and propose a fix
```

or:

```
> propose the three most valuable improvements to this codebase
```

---

## CODE · approve, then read the diff · 8 min

Approve the plan and Claude edits. **Read the diff before accepting it** —
the permission prompt is the accountability moment. Never approve what you
don't understand.

Stuck? Escalate for one turn:

```
> ultrathink why is this still failing?
> /effort xhigh
```

Three layers of undo:

- **Diff approval** — accept, edit, or reject each change
- **`/undo`** — step back a turn; files revert
- **`git`** — commit before you start, and Claude's work is just a diff

---

## VERIFY · the durable output · 8 min

**Workshop repo:**

```
> write a test that would have caught this — show it failing before the fix
  and passing after. then run the whole suite
```

**Your repo:**

```
> verify the fix — run the tests if there are any; if not, write and run a
  quick check that proves it works
```

Read what the test asserts. A weakened test passes too — that's a known
failure mode, not a hypothetical one.

With both bugs fixed:

```bash
$ pytest                                        # 12 passed
$ python examples/plot_surface_temperature.py   # hemispheres correct now
```

---

## CREATE · it makes things and runs them · 8 min

The CLI's answer to Artifacts.

**Workshop repo:**

```
> write a script that plots zonal-mean temperature from data/sample.nc,
  then run it
```

or:

```
> build a single-file interactive HTML page visualizing the data, and open it
```

**Your repo:**

```
> make something this project is missing: a README, an architecture diagram,
  a plot of <your data>, an interactive page — then open it
```

---

## Worth knowing before you leave

**Session survival**

```bash
$ claude -c                      # resume last session
$ claude -r                      # pick from history
$ claude -p "question"           # headless, one shot
$ cat run.log | claude -p "what failed?"
```

**Skills** — reusable how-to folders (`SKILL.md`), loaded when the task
matches. Frontmatter can pin `model:` and `effort:`, so the skill carries
its own settings. Git-shareable, which makes them lab-wide conventions.

```
> write a skill for code review of changes to src/wxpost/. it should run
  pytest first, check that new public functions have docstrings, and flag
  added print() statements. save it as
  .claude/skills/review-wxpost/SKILL.md — make the description specific
  enough that you auto-invoke it when I say "review my changes"
```

**Subagents** — parallel workers with their own context window. Their
chatter stays in their window; you get the summary.

```
> review these three modules in parallel
```

**Background** — `Ctrl+B` sends a long task to the background.

**MCP** — plug Claude into live systems beyond files and shell.

```bash
$ claude mcp add <name> …
```

Project-wide via `.mcp.json`, managed with `/mcp`. An MCP server is code
with access — know what you installed, and treat a `.mcp.json` in a shared
repo as a decision for the group.

---

## Spending context and tokens well

**Context**

- One task, one session — `/clear` between; `-c` only to continue
- Point, don't dump — `@` the two files that matter; grep a log before piping it
- Compact at seams you pick
- Keep `CLAUDE.md` lean — it's a per-session tax
- Delegate exploration to subagents; keep the chatter in their window

**Tokens**

- Think expensive, execute cheap — Opus designs the plan or skill, Sonnet or
  Haiku runs it. Skill frontmatter makes that permanent
- Haiku for repetitive chores; Opus only after Sonnet has actually failed
- Effort down for trivial asks; `ultrathink` for one hard turn
- Orchestration keeps intermediate results out of your window — why it
  scales, and why it costs

Your meters are yours, but the bill is the lab's.

---

## Files worth remembering

| Path | What it is |
|---|---|
| `./CLAUDE.md` | project memory · team sees it |
| `~/.claude/CLAUDE.md` | user memory · just you, every project |
| `~/.claude/projects/…/memory/` | auto-memory · what Claude noticed |
| `./.claude/skills/*/SKILL.md` | project skills · committed |
| `~/.claude/skills/*/SKILL.md` | user skills · personal |
| `./.claude/commands/*.md` | custom slash commands |
| `./.mcp.json` | project-scope MCP servers |
| `~/.claude/settings.json` | user settings · status line, MCP servers |

## Getting help after today

- Book time: <https://calendar.app.google/S9MPoeG2Pe4bqfH79>
- Docs: <https://docs.claude.com>
- Day-to-day questions: the Slack / Teams channel
