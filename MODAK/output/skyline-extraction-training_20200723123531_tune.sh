#!/bin/bash

## START OF TUNER ##
wget --no-check-certificate https://www.dropbox.com/s/iaivd8wujhctpl5/cresta.tar.gz
tar -xvf cresta.tar.gz
export PATH=$PATH:$(pwd)/cresta
wget --no-check-certificate https://www.dropbox.com/s/m2j06vhtm7137u2/skyline-extraction-training_20200723123531.tune
tune skyline-extraction-training_20200723123531.tune
## END OF TUNER ##
