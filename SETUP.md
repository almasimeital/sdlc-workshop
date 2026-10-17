# Before the workshop: setup

Please do this before the workshop, at your own desk. It takes about 15 minutes, most of it
downloading. Hit a problem? Send the error message to the facilitator before the day, not
during it.

You need four tools:

| Tool | Why |
|---|---|
| **Git** | Gets the exercises, and records your work as commits. On Windows it also brings Git Bash, which Claude Code uses to run commands. |
| **uv** | Runs Python for you. It downloads the right Python version itself, so you don't need to install Python. |
| **Claude Code** | The agent you'll work with. |
| **GitHub CLI (`gh`)** | Makes your own copy of the exercises on GitHub, a fork, so you can open a real pull request at the end. |

You also need a GitHub account for `gh`. No GitHub account, or GitHub blocked on your network?
You can still do the whole workshop: see [No GitHub?](#no-github). You don't need an editor
or anything else.

On a company laptop or network? Read
[Company laptops and corporate networks](#company-laptops-and-corporate-networks) first.

## Windows

Use **PowerShell**: open the Start menu and type `PowerShell`. After each install, **close
PowerShell and open it again**, so it finds the new command.

**1. Git for Windows.** Download and run the installer from
[git-scm.com/downloads/win](https://git-scm.com/downloads/win); the default options are
fine. Or, in PowerShell:

```powershell
winget install --id Git.Git -e
```

No administrator rights? Use the portable Git. On the same download page, get **Git for
Windows/x64 Portable** and run it. When it asks where to install, enter
`C:\Users\<you>\PortableGit`, with your Windows user name. Then put Git on your PATH and
tell Claude Code where Git Bash is:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$HOME\PortableGit\cmd", "User")
setx CLAUDE_CODE_GIT_BASH_PATH "$HOME\PortableGit\bin\bash.exe"
```

Check it: `git --version` prints a version number.

**2. uv.**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

If your laptop blocks that script, use WinGet instead:

```powershell
winget install --id=astral-sh.uv -e
```

Check it: `uv --version` prints a version number.

**3. Claude Code.**

```powershell
irm https://claude.ai/install.ps1 | iex
```

If your laptop blocks that script, use WinGet instead:

```powershell
winget install Anthropic.ClaudeCode
```

A WinGet install doesn't update itself, so run `winget upgrade Anthropic.ClaudeCode` now
and then.

Check it: `claude --version` prints a version number.

**4. GitHub CLI.**

```powershell
winget install --id GitHub.cli -e
```

Check it: `gh --version` prints a version number.

## macOS

Open **Terminal**.

**1. Git.** Run `git --version`. If Git isn't installed, macOS offers to install the command
line developer tools: accept, and wait for it to finish.

**2. uv.**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**3. Claude Code.**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**4. GitHub CLI.**

```bash
brew install gh
```

No Homebrew? Download the installer from [cli.github.com](https://cli.github.com/).

Close Terminal, open it again, and check: `uv --version`, `claude --version` and
`gh --version`.

## Both: tell Git who you are, and sign in to GitHub

Git won't save a commit until it has a name and an email. Any name and email will do: they
only label your own commits on your own computer.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Then sign in to GitHub once. Choose GitHub.com, and log in with your browser:

```bash
gh auth login
```

## Check that everything works

These commands work the same in PowerShell and in Terminal. Run them one at a time.

```bash
gh repo fork haco29/sdlc-workshop --clone
cd sdlc-workshop/exercises/01-agent-basics
uv run pytest -q
```

The first line makes your own copy of the repo on GitHub and downloads it. Already cloned
the original? Run `gh repo fork --remote` inside it instead: it keeps your folder and points
it at your fork.

The first `uv run` downloads Python and the test tools, so give it a minute. It should end
with **11 passed**. Then get exercise 2 ready too, so nothing big downloads during the
workshop:

```bash
cd ../02-sdlc-loop
uv run pytest -q
```

It should end with **17 passed**.

Now check that Claude Code can reach its model. You need the login details for Claude,
which you get separately. Go back to the top of the repo, so Claude Code doesn't start
inside an exercise, and start it:

```bash
cd ../..
claude
```

The first time, it asks you to log in. Then type a one-line prompt, such as
`Say hello in one sentence`, and press Enter. Any answer means it works. Type `/exit` to
quit.

Last, check that you can reach GitHub, where the SDLC kit comes from:

```bash
git ls-remote https://github.com/haco29/agentic-sdlc.git
```

It should print a few lines, each a long code and a name such as `HEAD`. If it fails,
GitHub may be blocked on your network: see "GitHub is blocked" under
[Company laptops and corporate networks](#company-laptops-and-corporate-networks).

That's it. Don't start Claude Code in the exercise folders yet, and don't install anything
else: the workshop takes you through the rest.

## If something goes wrong

| You see | What to do |
|---|---|
| `'git'`, `'uv'` or `'claude'` is not recognized | Close the terminal and open a new one. Still failing? The install directory isn't on your PATH: see [Fix your PATH](https://code.claude.com/docs/en/troubleshoot-install). |
| `The token '&&' is not a valid statement separator` | You're in an older PowerShell. Run the commands one at a time, as written above. |
| `python3` opens the Microsoft Store | You don't need it. Use `uv run …` as shown, and uv brings its own Python. |
| An installer asks for administrator rights you don't have | Claude Code and uv install without admin rights. For Git, use the portable Git from step 1, or ask IT before the workshop. |
| A download fails or times out, or an error mentions a certificate | You may be behind a company proxy or firewall: see [Company laptops and corporate networks](#company-laptops-and-corporate-networks). |
| `Please tell me who you are` when committing | Run the two `git config` lines above. |

## Company laptops and corporate networks

Company networks often inspect, proxy or block traffic. Find what you see below. Anything
"from IT" only your IT team can give you, so ask them before the workshop.

To set an environment variable for good, run `setx NAME "value"` in PowerShell, then close
PowerShell and open it again. On macOS, add `export NAME="value"` to `~/.zshrc` and open a
new Terminal.

**Errors about a certificate, SSL or TLS.** Your network inspects encrypted traffic with
its own certificate. Tell each tool to trust it:

- uv: set `UV_SYSTEM_CERTS` to `true`. uv then uses your system's certificate store.
- Git, on Windows: run `git config --global http.sslBackend schannel`. Git then uses the
  Windows certificate store.
- Claude Code uses your system's certificate store already. If it still shows certificate
  errors, set `NODE_EXTRA_CA_CERTS` to the path of the company CA certificate file, from IT.

**Downloads hang or time out: a proxy.** Set `HTTPS_PROXY` and `HTTP_PROXY` to the proxy
address from IT, for example `http://proxy.example.com:8080`. Git, uv and Claude Code all
use them.

**uv can't download packages: PyPI is blocked.** Set `UV_DEFAULT_INDEX` to your company's
PyPI mirror, with the URL from IT. uv then changes `uv.lock` to point at the mirror. That's
expected: leave that change out of your commits.

**`gh repo fork` or `git clone` fails: GitHub is blocked.** Ask the facilitator for the two repos as zip
files, and unzip them into the same folder. Install the SDLC kit from its folder, as in
step 2 of [WORKSHOP.md](exercises/02-sdlc-loop/WORKSHOP.md). The Git for Windows download
comes from GitHub too: if it fails, ask IT to install Git.

**Claude Code is already set up by IT**, for example through Amazon Bedrock. Skip the
Claude Code install and the login. Just check that it answers a prompt, as in
[Check that everything works](#check-that-everything-works).

**OneDrive.** On many company laptops, OneDrive syncs Documents and Desktop. Clone the
exercises somewhere it doesn't sync, such as `C:\dev`, before you run the checks:

```powershell
mkdir C:\dev
cd C:\dev
```

## No GitHub?

You can do the whole workshop without a GitHub account: skip `gh`, and get the exercises with
a plain clone instead of the fork:

```bash
git clone https://github.com/haco29/sdlc-workshop.git
```

Your work stays as commits on your computer, and at the end `/sdlc:pr` writes the pull
request description to a file, `pr.md`, instead of opening a pull request.
