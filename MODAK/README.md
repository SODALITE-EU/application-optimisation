# MODAK Application Optimiser

MODAK requires the following inputs

- Job submission options for batch schedulers such as SLURM and TORQUE
- Application configuration such as application name, run and build command
- Infrastructure configuration such as target name, type and scheduler type
- Optimisation DSL with specification of target hardware, software libraries and optimisations to encode. Also
  contains inputs for auto-tuning and auto-scaling.

MODAK produces a job script (for batch submission) and an optimised container that can be used for application
deployment. The image registry contains MODAK optimised containers while performance models, optimisation
rules and constraints are stored and retrieved from the Model repository. Singularity was chosen to provide a
portable and reproducible runtime for the application deployment, due to better performance and native support for
HPC.

MODAK has four main components, as described below: Mapper, Enforcer, Tuner and Scaler.


- Containers provide an optimised runtime for application deployment based on the target hardware and along
  with any software dependencies and libraries. MODAK builds and labels containers with appropriate optimisation.
  The Mapper maps application deployment to an optimised container runtime based on the required
  optimisation. Currently, MODAK supports TensorFlow, PyTorch, MXnet, mpich, openmpi, and mvapich2
  containers for x86 and NVIDIA GPUs. These containers are further labelled with version requirements and
  support for optimisations like graph compilers or BLAS/LAPACK.

- the Enforcer optimises the deployment based on optimisation rules defined by users and optimisation DSL
  inputs. Rules can be defined for targets, applications, libraries, and data. The Enforcer component generates
  an optimisation script that is then added to the deployment.

- Autotuning enables users to automatically search possible application deployments for the desired result.
  MODAK’s Tuner supports the CRESTA autotuning framework. The framework defines a DSL to expose
  the tuning choices as parameters, constrain and inject them into the application source, then build and run the
  application. The framework supports exhaustive search of the parameter space and can tune for any metric
  output, not just runtime.

- In MODAK, we can predict the efficiency and speedup of an application on N nodes based on the performance
  prediction model. This allows MODAK to automatically scale applications to certain numbers of nodes based
  on the model prediction. Using the parallel efficiency metric specified by the user in the optimisation DSL,
  the Scaler aims to predict the scale at which parallel efficiency is achieved and automatically increase the
  number of nodes of the deployment (Autoscale). The Scaler can also enable or disable accelerator, memory,
  and storage devices based on the model and availability in the target.

```
m = MODAK()
# dsl_file = "../test/input/tf_snow.json"  #tensorflow AI training example
dsl_file = "../test/input/mpi_solver.json" #MPI application example
with open(dsl_file) as json_file:
    m.optimise(json.load(json_file))
```

creates a job submission script that you can use to submit to a batch scheduler
like slurm or torque

[Examples](EXAMPLE.md)

[Install](INSTALL.md)
