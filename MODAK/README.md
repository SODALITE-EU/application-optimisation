# MODAK Application Optimiser 
contains 4 components  
- Mapper  
- Scaler  
- Tuner  
- Enforcer  

To use MODAK, it requires a input json with
- job options
- application run data
- target data
- optimisation DSL

```
m = MODAK()
# dsl_file = "../test/input/tf_snow.json"  #tensorflow AI training example
dsl_file = "../test/input/mpi_solver.json" #MPI application example
with open(dsl_file) as json_file:
    m.optimise(json.load(json_file))
```

creates a job submission script that you can use to submit to a batch scheduler 
like slurm or torque




