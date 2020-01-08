# Skyline Extraction Training

#### Requirements
* TensorFlow Core 1.11.


#### Models
* **PeakLens_original:** Original model for skyline extraction with 428,732 parameters.
* **PeakLens_optimized:** Optimized model for skyline extraction with 20,578 parameters.


#### Folders
* **checkpoint:** Checkpoints for the best performing training epoch for both models.
* **graphs:** Files to visualize the graphs' quantitative training metrics with TensorBoard.
* **protobufs:** Trained models exported as protobuf.


#### Notebooks
* **peaklens-original-training.ipynb:** Notebook to train PeakLens_original model.
* **peaklens-optimized-training.ipynb:** Notebook to train PeakLens_optimized model.

#### To run on the SODALITE testbed
* Download the tensorflow 1.11 GPU container 
`/usr/local/bin/singularity pull docker://tensorflow/tensorflow:1.15.0-gpu `
* Submit the pbs job 
`qsub training_job.pbs (or training_test.pbs) `
