#!/bin/bash
# Run python3 inside the research container. Used by VS Code as the # Python interpreter, so stdout must carry ONLY Python's output: VS Code # parses it during interpreter discovery.
# Runs outside a login shell, so set what the module system needs.

export USER=${USER:-$(id -un)}
export PROJECT=<YOUR_PROJECT_ID>

export APPTAINER_PYTHON_IMAGE=/scratch/${PROJECT}/${USER}/containers/<YOUR_APPTAINER_IMAGE>.sif

export MODULEPATH=/etc/scl/modulefiles:/opt/Modules/modulefiles:/opt/Modules/v4.3.0/modulefiles:/apps/Modules/modulefiles
export MODULES_PAGER=""   # no pager: it would hang waiting for RETURN

source /etc/profile.d/modules.sh

# Loads apptainer (plus squashfuse for fast image mounts). The site's
# `module` sends messages to stdout, so silence both streams.
module load apptainer


# -q hides apptainer INFO lines; -Xfrozen_modules=off lets debugpy hit
# breakpoints in the standard library.
exec apptainer -q exec --cleanenv --env "MPLCONFIGDIR=/tmp/mplcache-$(id -u)" "$APPTAINER_PYTHON_IMAGE" python3 -Xfrozen_modules=off "$@"
