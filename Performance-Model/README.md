# Performance model for application scaling

Results of the application scaling (for the ClinicalUC) are stored in the results directory.
The performance model can be extracted by running:

```
cd analysis
singularity pull docker://rootproject/root
./root_latest.sif root analysis_amdahl.cpp # .q to exit root
```

It will plots two windows for MPICH and OpenMPI, as reported in 
[D3.4](https://www.sodalite.eu/reports/d34-full-release-application-and-infrastructure-performance-models).