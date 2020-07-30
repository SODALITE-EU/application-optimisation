#!/bin/bash

## START OF TUNER ##
wget --no-check-certificate https://www.dropbox.com/s/iaivd8wujhctpl5/cresta.tar.gz
tar -xvf cresta.tar.gz
export PATH=$PATH:$(pwd)/cresta
wget --no-check-certificate https://storage.googleapis.com/modak//modak/skyline-extraction-training_20200723224211.tune
tune skyline-extraction-training_20200723224211.tune
## END OF TUNER ##
