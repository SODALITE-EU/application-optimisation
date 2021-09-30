# SODALITE Application Optimizer (MODAK)

The MODAK (Model Optimized Deployment of Applications in Containers) package, a software-defined optimization framework for containerized MPI and AI applications, is the SODALITE component responsible for enabling the static optimization of applications before deployment. It aims to optimize the performance of application deployment to infrastructure in a software-defined way. Automation in application optimization is enabled using performance modeling and container technology. Containers provide an optimized runtime for application deployment based on the target hardware and along with any software dependencies and libraries.

## Directory structure

Contains all components for the Application Optimizer:

*   [AI](AI) - Experimentation with container optimizations for Artificial Intelligence Training and Inference
*   [Performance-Model](Performance-Model) - Infrastructure and Application Performance model
*   [MODAK](MODAK) - the main application optimizer
*   [use-cases](use-cases) - SODALITE Use case applications
*   [iac-model-repo](iac-model-repo) - Model repository
*   [containers](containers) - Containers definition files

## Setup

For development you need the `pre-commit` tools.
This registers the `pre-commit` hooks for the current git checkout such
that tools like `black` or `flake8` are run automatically on commit.

```console
$ pip install pre-commit
$ pre-commit install --install-hooks
```

To manually check that the current tree is clean:

```console
$ pre-commit run -a
```

## How to use MODAK
Please follow the instructions in the [MODAK](MODAK) directory.
