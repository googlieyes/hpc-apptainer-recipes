# Apptainer HPC Toolkit

This repository contains supporting material for the **"Using Apptainer Containers on HPC"** workshop presented as part of the Melbourne Research Computing Roadshow 2026.

The workshop introduces the basic concepts and practical use of Apptainer containers in High Performance Computing (HPC) environments. Participants gain hands-on experience using, building, and working with containers to create reproducible computational workflows.

## Workshop Learning Outcomes

By the end of the workshop, participants should be able to:

- Understand what containers are and why they can be useful for computational workflows.
- Understand why Apptainer is commonly used in HPC environments.
- Work with existing containers and execute applications within them.
- Understand the basic structure of an Apptainer definition file and when creating a custom container may be useful.
- Recognise when a container is an appropriate solution and when alternatives, such as existing HPC modules or Python/R environments, may be simpler.
- Apply basic good practices when selecting, creating, and using containers to support maintainable and reproducible computational workflows.

## Repository Contents

This repository contains:

- Example Apptainer definition files.
- Example HPC job submission scripts.
- Supporting scripts used during the workshop.
- Additional resources and references for further learning.

## Reproducible Research Environments

One of the workshop exercises demonstrates how to create a reproducible Python environment using Apptainer.

This approach provides a fixed set of software libraries and versions, defined once in a container image, that can be shared and reused across a research group. Participants can use the same containerised environment from Visual Studio Code running on their own laptops while executing workloads on HPC compute nodes.

Benefits include:

- Reproducible analyses and workflows.
- Consistent software environments across users and systems.
- Simplified dependency management.
- Improved collaboration and portability.

## Workshop Information

For workshop details, see the Melbourne Research Computing Roadshow 2026 event page:

[Melbourne Research Computing Roadshow 2026](https://events.humanitix.com/melbourne-research-computing-roadshow-2026)

## License

This repository is provided for educational, training, and research purposes.

Please refer to the LICENSE file for terms of use.

## Author

