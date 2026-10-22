#!/bin/bash
# Run python3 inside the research container (VS Code's Python interpreter).
# stdout must carry ONLY Python's output — VS Code parses it to discover the interpreter.

# Runs outside a login shell, so set up the module system by hand.
# USER is needed because the apptainer modulefile references it.
export USER=${USER:-$(id -un)}
export MODULES_PAGER=""   # no pager prompt

# Init modules, then add Petrichor's modulefiles with `module use`
# (keeps the site's default MODULEPATH intact).
source /etc/profile.d/modules.sh
module use /var/apps_petrichor/modules/modulefiles

# Put apptainer (and squashfuse/fuse-overlayfs) on PATH; silence module output.
module load apptainer >/dev/null 2>&1

IMAGE=/scratch3/$USER/containers/python-research.sif

# -q hides INFO lines; -Xfrozen_modules=off lets debugpy hit stdlib breakpoints.
exec apptainer -q exec --cleanenv \
    --env "MPLCONFIGDIR=/tmp/mplcache-$(id -u)" \
    "$IMAGE" python3 -Xfrozen_modules=off "$@"
