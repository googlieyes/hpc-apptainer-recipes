#!/bin/bash
# Open an interactive shell inside the research container (VS Code's terminal).

# Runs outside a login shell, so set up the module system by hand.
# USER is needed because the apptainer modulefile references it.
export USER=${USER:-$(id -un)}
export MODULES_PAGER=""   # no pager prompt
export TERM=${TERM:-xterm-256color}   # interactive shell needs a terminal type

# Init modules, then add Petrichor's modulefiles with `module use`
# (keeps the site's default MODULEPATH intact).
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
