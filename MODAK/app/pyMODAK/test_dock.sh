docker exec -it app_modaksql_1  python3 -m unittest test_dsl_reader
docker exec -it app_modaksql_1  python3 -m unittest test_MODAK_driver
docker exec -it app_modaksql_1  python3 -m unittest test_mapper
docker exec -it app_modaksql_1  python3 -m unittest test_MODAK
docker exec -it app_modaksql_1  python3 MODAK.py -i /IO/tf_snow.json -o /IO/tf_snow_opt.json