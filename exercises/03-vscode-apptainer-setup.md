# VS Code + Containerised Python on an HPC Cluster (Apptainer)

A companion to the "Create an interactive container" part of the workshop. It describes how to set up and use a reproducible Python
environment from VS Code, with Python running inside an Apptainer container on
HPC compute nodes.

Paths and module names below are for **Petrichor** (CSIRO); adapt the
cluster-specific bits (`/scratch3`, `/var/apps_petrichor/...`, host names) for
another system.

---

## The bigger picture

- **Apptainer** provides the software environment (a fixed Python stack in a container).
- **HPC** provides the compute resources (CPU/GPU, memory, storage).
- **VS Code** provides the interface for editing, running, and debugging your code in that environment.

The goal is a *reproducible, shared* Python environment — defined once in a
container — that the whole research group uses from VS Code on their own
laptops, while the code runs on HPC compute nodes.

## How it works

VS Code's own remote server runs directly on a compute node, exactly like a
normal Remote-SSH session. Only the **Python interpreter, debugger, and
integrated terminal** come from the container, via two small wrapper scripts you
point VS Code at. When VS Code needs to run Python, check a package, or launch
the debugger, it calls a wrapper, which starts the container and runs the command
inside it. Everything else — file browsing, git, extensions — behaves like any
Remote-SSH session.

### Why two wrappers?

- **`vscode-python-wrapper.sh`** is the **interpreter** — VS Code calls it to run a single Python command (running a `.py` file, the ▷ Run button, IntelliSense). It runs `apptainer exec … python3`, and its output must be clean because VS Code parses it to identify the interpreter.
- **`vscode-shell-wrapper.sh`** is the **terminal** — it opens an interactive shell inside the container (the `Apptainer>` prompt) via `apptainer shell`, so you can type `python`, `pip freeze`, `git` directly.

You need both because running one Python command and giving someone an
interactive shell are different jobs.

---

## Part 1 — Set up the environment (once)

Run these on the HPC login node.

### Step 1: Create a place for it

```bash
mkdir -p ~/bin
mkdir -p /scratch3/$USER/containers
cd /scratch3/$USER/containers
```

Small files (the wrapper scripts) go in `~/bin` (permanent, fixed path). The
container image goes on `/scratch3` (larger working storage). Note `/scratch3`
auto-flushes files that are unused for an extended period, so keep the pull
command (Step 2) handy to re-stage the image if needed.

### Step 2: Get a container image

```bash
module load apptainer
apptainer pull python-research.sif docker://jupyter/scipy-notebook:latest
```

This pulls a public scientific-Python image and converts it to a single
Apptainer `.sif` file. It includes Python, numpy, pandas, scipy, matplotlib,
debugpy and ipykernel. Any image you use must include **debugpy** and
**ipykernel** for the debugger and notebooks to work.

> A `.sif` file (Singularity Image Format) is one self-contained, read-only file
> holding the whole environment (OS userland, Python, every library). Because
> it's one immutable file, it behaves identically everywhere and is easy to
> share, lock, and version.

### Step 3: Lock the image (recommended)

```bash
chmod -R a-w /scratch3/$USER/containers
```

Read-only keeps the environment reproducible and protects the image from being
overwritten or deleted. To change it later: `chmod -R u+w /scratch3/$USER/containers`.

### Step 4: Create the interpreter wrapper

Save as `~/bin/vscode-python-wrapper.sh`:

```bash
#!/bin/bash
# Run python3 inside the research container (VS Code's Python interpreter).
# stdout must carry ONLY Python's output — VS Code parses it to discover the interpreter.

# Runs outside a login shell, so set up the module system by hand.
# USER is needed because the apptainer modulefile references it.
export USER=${USER:-$(id -un)}
export MODULES_PAGER=""   # no pager prompt

# Init modules, then add the site's modulefiles with `module use`
# (keeps the default MODULEPATH intact).
source /etc/profile.d/modules.sh
module use /var/apps_petrichor/modules/modulefiles

# Put apptainer (and squashfuse/fuse-overlayfs) on PATH; silence module output.
module load apptainer >/dev/null 2>&1

IMAGE=/scratch3/$USER/containers/python-research.sif

# -q hides INFO lines; -Xfrozen_modules=off lets debugpy hit stdlib breakpoints.
exec apptainer -q exec --cleanenv \
    --env "MPLCONFIGDIR=/tmp/mplcache-$(id -u)" \
    "$IMAGE" python3 -Xfrozen_modules=off "$@"
```

Make it executable: `chmod +x ~/bin/vscode-python-wrapper.sh`

Key points: all non-Python output is silenced (VS Code parses the interpreter's
output); `--cleanenv` stops host variables leaking in; `MPLCONFIGDIR` gives
matplotlib a writable cache; `exec` replaces the script with Python so VS Code
talks to Python directly.

### Step 5: Create the terminal wrapper

Save as `~/bin/vscode-shell-wrapper.sh`:

```bash
#!/bin/bash
# Open an interactive shell inside the research container (VS Code's terminal).

# Runs outside a login shell, so set up the module system by hand.
# USER is needed because the apptainer modulefile references it.
export USER=${USER:-$(id -un)}
export MODULES_PAGER=""   # no pager prompt
export TERM=${TERM:-xterm-256color}   # interactive shell needs a terminal type

# Init modules, then add the site's modulefiles with `module use`
# (keeps the default MODULEPATH intact).
source /etc/profile.d/modules.sh
module use /var/apps_petrichor/modules/modulefiles

# Put apptainer (and squashfuse/fuse-overlayfs) on PATH; silence module output.
module load apptainer >/dev/null 2>&1

IMAGE=/scratch3/$USER/containers/python-research.sif

# -q hides INFO lines; TERM is passed in because --cleanenv may drop it.
exec apptainer -q shell --cleanenv \
    --env "TERM=$TERM" \
    --env "MPLCONFIGDIR=/tmp/mplcache-$(id -u)" \
    "$IMAGE"
```

Make it executable: `chmod +x ~/bin/vscode-shell-wrapper.sh`

Same pattern as the interpreter wrapper; the extra `TERM` gives an interactive
shell the terminal type it needs for colours and line editing (`--cleanenv` may
drop it).

### Step 6: Verify it works (from the command line, before VS Code)

```bash
env -i HOME=$HOME ~/bin/vscode-python-wrapper.sh -c "import numpy; print(numpy.__version__)"
```

`env -i HOME=$HOME` strips the environment to mimic exactly how VS Code calls the
wrapper (no login shell). A fast numpy version number means the container starts
and its Python runs. If it takes ~10 s, squashfuse isn't resolving — check the
`module load apptainer` output (temporarily remove `>/dev/null 2>&1`).

Then confirm the debugger component:

```bash
~/bin/vscode-python-wrapper.sh -m debugpy --version
```

A version number means debugpy is present. `No module named debugpy` means the
image lacks it — use an image that has it.

---

## Part 2 — Connect your laptop (once)

Done on your laptop, not on HPC.

### Step 1: Set up an SSH key

An SSH key lets your laptop connect without a password (essential, since VS Code
makes many connections). Check for an existing key:

```bash
ls ~/.ssh/<SSH_KEY_NAME>
```

If missing, create and register one:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/<SSH_KEY_NAME> -C "<username>@<HPC_HOSTNAME>"
ssh-copy-id -i ~/.ssh/<SSH_KEY_NAME>.pub <username>@<HPC_HOSTNAME>
```

`ssh-copy-id` prompts for your HPC password once, then installs the key. (If
`ssh-copy-id` is unavailable, append `~/.ssh/<SSH_KEY_NAME>.pub` to
`~/.ssh/authorized_keys` on the host manually.)

### Step 2: Configure SSH

Add to `~/.ssh/config` on your laptop (replace `<...>` placeholders):

```
Host <HPC_ALIAS>
    HostName <HPC_HOSTNAME>
    User <username>
    IdentityFile ~/.ssh/<SSH_KEY_NAME>
    IdentitiesOnly yes

# Compute node names are 3 digits (c036, etc.); match only those.
Host c???
    User <username>
    IdentityFile ~/.ssh/<SSH_KEY_NAME>
    IdentitiesOnly yes
    ProxyJump <HPC_ALIAS>
    HostKeyAlias <HPC_HOSTNAME>
```

- The first block is a short alias for the login node: `ssh <HPC_ALIAS>`.
- The second covers compute nodes. `ProxyJump` routes through the login node (compute nodes aren't reachable directly). `HostKeyAlias` stops a host-key prompt for every new node (all nodes share the login node's host key). `IdentitiesOnly yes` offers only your key.

### Step 3: Auto-configure your project folder

Add `.vscode/settings.json` to your project's root. VS Code reads it over
Remote-SSH and sets up the interpreter and terminal automatically — no
per-session steps. Works for your own folder or a shared team folder.

```json
{
  "python.defaultInterpreterPath": "/home/<username>/bin/vscode-python-wrapper.sh",
  "terminal.integrated.profiles.linux": {
    "Container shell": {
      "path": "/home/<username>/bin/vscode-shell-wrapper.sh"
    }
  },
  "terminal.integrated.defaultProfile.linux": "Container shell"
}
```

**Replace `<username>` with your actual username** — JSON does no variable
expansion, so `$USER` or `<username>` won't work. The Container-shell default
profile is what makes every new terminal open *inside* the container.

---

## Part 3 — Every session

Reserve a node, connect VS Code, release the node when done. Files, scripts, and
the image persist between sessions; only the compute job is temporary.

### Step 1: Start a compute job

Log in to the HPC (`ssh <HPC_ALIAS>`), then allocate a node:

```bash
# SLURM
salloc --no-shell -A <project-code> -N1 -c4 --mem=16G -t 8:00:00
# PBS
qsub -I -P <project-code> -l ncpus=4,mem=16gb -l walltime=08:00:00
```

Find which node you were given:

```bash
# SLURM
squeue --me
# PBS
qstat -u $USER
```

Note the node name (e.g. `c036`) and the job ID.

### Step 2: Connect VS Code to your allocated node

On your laptop: Command Palette → **Remote-SSH: Connect to Host…** → enter the
node name (e.g. `c036`). A new VS Code window opens, connected to that node.

**Behind the scenes:** the SSH config routes through the login node, so you don't
log in twice. On first connection, VS Code downloads its remote server
(~230 MB) to the node and unpacks it into `~/.vscode-server` (~700 MB). Because
`~/.vscode-server` is in shared home, later connections from any node reuse it
and take seconds — the download only repeats when your laptop's VS Code updates
(set `"update.mode": "manual"` to control when).

### Step 3: Open your project and install the Python extension

1. **File → Open Folder…** → pick your project directory.
2. Open the **Extensions** view (icon in the activity bar, or View → Extensions).
3. Search for `python`.
4. On **Python** by **Microsoft**, click **Install in SSH: \<node\>** — this also installs Pylance and the Python Debugger.
5. It's ready when the entry shows an **Uninstall** / gear icon.

Install **Jupyter** the same way only if you use notebooks. Avoid the separate
**"Python Environments"** extension — install only the base **Python** extension.
The extension provides the editing experience (IntelliSense, highlighting,
linting); the interpreter is already set by `settings.json`.

### Step 4: Run your code through the container

With `settings.json` in place, every new terminal opens inside the container —
the prompt reads `Apptainer>`. Open one with **Terminal → New Terminal** and run
a script directly (no wrapper prefix):

```bash
python ~/projects/test_env.py
```

Expected output (the container's Python and packages):

```
Python version: 3.11.6
Executable: /opt/conda/bin/python3
numpy version: 1.24.4
Environment looks good.
```

The **Executable** line is the key check — it must point inside the container
(`/opt/conda/...`), not `/usr/bin/python3`. `pip freeze`, `git`, and the ▷ Run
button all work from this terminal too.

**Run from the GUI:** click a `.py` file in the Explorer to open it, click the
**▷ Run button** (top-right of the editor), and read the output in the Terminal
panel. The button works because it runs in the Container-shell terminal.

**A richer example** — `capability_demo.py` exercises numpy, scipy, pandas,
scikit-learn and matplotlib and renders a four-panel figure (signal smoothing,
linear regression, distribution fit, KMeans clustering), headless to a PNG:

```bash
python ~/projects/capability_demo.py
```

### Step 5: End the session

1. Close the VS Code window (on your laptop).
2. On the login node, release the job:

```bash
# SLURM
scancel <job-id>
# PBS
qdel <job-id>
```

Close VS Code first so its processes shut down cleanly, then `scancel` / `qdel`
frees the cores and memory. Nodes are shared, so the resources return to the
pool. (Find the job ID again with `squeue --me` / `qstat -u $USER`.)

---

## Updating the environment

Don't `pip install` into a running session — the `.sif` is read-only, and a
change inside one session wouldn't be shared with the group. Instead:

1. Update the image definition (the Dockerfile or `.def` recipe) and rebuild — or ask whoever maintains it.
2. Pull the new version under a new filename, e.g. `python-research-v2.sif`.
3. Update `IMAGE=` in both wrapper scripts to point at the new file.
4. Re-run the Part 1, Step 6 verification.

This keeps everyone on the same known set of package versions.

---

## Notes and limitations

- **F5 debugging is not covered.** VS Code's debugger expects a directly-runnable interpreter; the container wrapper is a shell script, so F5 won't start. Run and verify code from the terminal or the ▷ Run button.
- **Read-only image, writable data.** The `.sif` is immutable, but `/home`, `/scratch3`, `/tmp` etc. are host directories bind-mounted into the container at runtime, so your files stay writable.
- **Backup run (no Container shell).** From a plain `bash` terminal, run through the container with the full wrapper path: `/home/<username>/bin/vscode-python-wrapper.sh ~/projects/test_env.py`.
