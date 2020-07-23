#!/bin/bash

## START OF TUNER ##
wget --no-check-certificate https://www.dropbox.com/s/iaivd8wujhctpl5/cresta.tar.gz
tar -xvf cresta.tar.gz
export PATH=$PATH:$(pwd)/cresta
wget --no-check-certificate https://www.dropbox.com/s/d02sr1qdt4uke75/solver_20200723123411.tune
tune solver_20200723123411.tune
## END OF TUNER ##
