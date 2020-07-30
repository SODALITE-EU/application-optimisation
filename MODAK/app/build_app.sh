#!/bin/bash
mysqldump --user=root --password=Abhinaya21 --databases iac_model test_iac_model > pyMODAK/modak_mysqldump.sql
tar -czvf modak.tar.gz -C ../../MODAK .
mv modak.tar.gz pyMODAK/.
docker-compose build --no-cache
docker-compose up
