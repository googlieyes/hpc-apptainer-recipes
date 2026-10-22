#!/bin/bash

# Open an interactive shell inside the research container. Used by VS Code # as the terminal shell.
# Runs outside a login shell, so set what the module system needs.

export USER=${USER:-$(id -un)}


export PROJECT=<YOUR_PROJECT_ID>
export APPTAINER_PYTHON_IMAGE=/scratch/${PROJECT}/${USER}/containers/<YOUR_APPTAINER_IMAGE>.sif

export MODULEPATH=/etc/scl/modulefiles:/opt/Modules/modulefiles:/opt/Modules/v4.3.0/modulefiles:/apps/Modules/modulefiles
export TERM=${TERM:-xterm-256color}

# interactive shells need a terminal type
export MODULES_PAGER="" # no pager: it would prompt for RETURN

source /etc/profile.d/modules.sh
# Loads apptainer (plus squashfuse for fast image mounts). The site's # `module` sends messages to stdout, so silence both streams.

module load apptainer >/dev/null 2>&1

# -q hides apptainer INFO lines; TERM is passed in because --cleanenv # may drop it.
exec apptainer -q shell --cleanenv \ --env "TERM=$TERM" \
--env "MPLCONFIGDIR=/tmp/mplcache-$(id -u)" \
"$APPTAINER_PYTHON_IMAGE"
