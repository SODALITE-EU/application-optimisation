#!/bin/bash
mysqldump --user=root --password=Abhinaya21 --databases iac_model test_iac_model > modak_mysqldump.sql
tar -czvf modak.tar.gz -C ../../MODAK .
docker build --no-cache . --tag modak
docker stop modak-test
docker rm modak-test
docker rm $(docker ps -a -q)
docker run --name modak-test --mount type=bind,source="$(pwd)"/IO,target=/IO -e MYSQL_ROOT_PASSWORD=my-secret-pw -d modak:latest
docker run --name modak-flask-test -d -p 80:5000 --mount type=bind,source="$(pwd)"/IO,target=/IO -e MYSQL_ROOT_PASSWORD=my-secret-pw -d modak:latest
#docker exec -it modak-test  python3 MODAK.py -i /IO/tf_snow.json -o /IO/tf_snow_opt.json
