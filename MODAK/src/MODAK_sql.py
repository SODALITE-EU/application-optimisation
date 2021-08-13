class MODAK_sql:

    CREATE_INFRA_TABLE = "create external table          \
            infrastructure(infra_id  int,                \
            name string,                                 \
            num_nodes int,                               \
            is_active boolean,                           \
            description string)                          \
            stored as PARQUET location                   \
            '{}/infrastructure'"

    CREATE_QUEUE_TABLE = "create external table          \
            queue(queue_id  int,                         \
            name string,                                 \
            num_nodes int,                               \
            is_active boolean,                           \
            node_spec string,                            \
            description string,                          \
            infra_id int)                                \
            stored as parquet location                   \
            '{}/queue'"

    CREATE_BENCH_TABLE = "create external table          \
            benchmark(run_id int,                        \
            queue_id  int,                               \
            num_cores int,                               \
            compute_flops double,                        \
            memory_bw double,                            \
            network_bw double,                           \
            io_bw double,                                \
            acc_compute_flops double,                    \
            acc_memory_bw double,                        \
            PCIe_bw double)                              \
            stored as parquet location                   \
            '{}/benchmark'"

    CREATE_MODEL_TABLE = "create external table          \
            model(model_id int,                          \
            queue_id  int,                               \
            compute_flops string,                     \
            memory_bw string,                            \
            network_bw string,                           \
            io_bw string,                                \
            acc_compute_flops string,                    \
            acc_memory_bw string,                        \
            PCIe_bw string)                              \
            stored as parquet location                   \
            '{}/model'"

    CREATE_APPMODEL_TABLE = "create external table       \
            appmodel(appmodel_id int,                       \
            queue_id  int,                               \
            app_id  int,                                 \
            compute_flops double,                        \
            memory_bw double,                            \
            network_bw double,                           \
            io_bw double,                                \
            acc_compute_flops double,                    \
            acc_memory_bw double,                        \
            PCIe_bw double,                              \
            acc_share double)                            \
            stored as parquet location                   \
            '{}/appmodel'"

    CREATE_APP_TABLE = "create external table            \
            application(app_id int,                      \
            name  string,                                \
            app_type string,                             \
            description string,                          \
            src string)                                  \
            stored as parquet location                   \
            '{}/application'"

    CREATE_AUDIT_TABLE = "create external table         \
            audit_log(file_line  bigint,               \
            start_time timestamp,                       \
            end_time timestamp,                         \
            run_time_sec bigint,                        \
            queue_id  int,                              \
            app_id  int,                                \
            aprun_id bigint,                            \
            job_id string,                              \
            num_nodes int,                              \
            run_stat int,                               \
            command string,                             \
            command_uniq string)                        \
            stored as parquet location                  \
            '{}/audit_log'"

    CREATE_OPT_TABLE = "create external table            \
            optimisation(opt_id int,                      \
            opt_dsl_code  string,                                \
            app_name  string,                                \
            target string,                                  \
            optimisation string)                                  \
            stored as parquet location                   \
            '{}/optimisation'"

    CREATE_MAPPER_TABLE = "create external table            \
            mapper(map_id int,                      \
            opt_dsl_code  string,                                \
            container_file string,                             \
            image_type string,                                  \
            image_hub string,                                  \
            src string)                                        \
            stored as parquet location                   \
            '{}/mapper'"

    table_create_stmt = {
        "infrastructure": CREATE_INFRA_TABLE,
        "queue": CREATE_QUEUE_TABLE,
        "benchmark": CREATE_BENCH_TABLE,
        "model": CREATE_MODEL_TABLE,
        "appmodel": CREATE_APPMODEL_TABLE,
        "application": CREATE_APP_TABLE,
        "audit_log": CREATE_AUDIT_TABLE,
        "optimisation": CREATE_OPT_TABLE,
        "mapper": CREATE_MAPPER_TABLE,
    }


def main():
    print("Test MODAK sql")
    print(MODAK_sql.CREATE_APP_TABLE.format("dir"))
    print(MODAK_sql.table_create_stmt["mapper"].format("dir"))


if __name__ == "__main__":
    main()
