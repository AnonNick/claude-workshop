# Workshop setup on Derecho / Casper

A handful of NCAR-system-specific gotchas you'll hit before things "just
work". Walk through these once before the workshop and you won't get
stuck in the room.

## 1. Clone the repo and install the package

`wxpost` goes into its **own** conda environment — not the base interpreter
the `conda` module hands you.

```bash
cd ~                       # or wherever you keep code
git clone https://github.com/AnonNick/claude-workshop.git
cd claude-workshop

module load conda                        # makes `conda` available
conda create -n wxpost python=3.12 -y    # one-time
conda activate wxpost
python --version                         # confirm: Python 3.12.x

pip install -e .[dev]      # pulls numpy, xarray, netCDF4, matplotlib
pytest -m "not needs_data" # quick sanity — should show 3 passed
pytest                     # full run — 10 passed, 2 failed (intentional)
```

Every new shell session needs the env back:

```bash
module load conda
conda activate wxpost
```

(Add those two lines to `~/.bashrc` if you don't want to type them every
time.)

> **Not on an NCAR system?** There's no `conda` module to load — use any
> isolated Python 3.10+ interpreter instead. See the
> ["Anywhere else"](../README.md#anywhere-else) section of the README.

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

## 3. Smoke-test from inside Claude

```bash
cd ~/claude-workshop
claude
```

```
> What does this repo do?
```

Claude should read `README.md`, `CLAUDE.md`, and a few source files before
answering. Watch the read list — that's your signal it actually looked
rather than guessed.

## Quick reference

| Path | What it is |
|---|---|
| `~/.claude/bin/claude` | Claude Code CLI |
| `/glade/campaign/hao/itmodel/joemci/archive/f.e22.FXSD.f19_f19_mg17.001/atm/hist/2020/` | the WACCM-X file the tests read |
