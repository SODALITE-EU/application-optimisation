import json
import os
from tuner import tuner

class jobfile_generator():

    def __init__(self, job_json_obj, batch_file:str, scheduler:str):
        # logging.info("Reading job data from file " + job_file)
        self.scheduler = scheduler
        self.batch_file = batch_file
        self.job_json_obj = job_json_obj
        self.job_data = job_json_obj['job']['job_options']
        self.app_data = job_json_obj['job']['application']
        self.opt_data = job_json_obj['job']['optimisation']
        print(self.job_data)

        if scheduler == 'torque':
            self.__generate_torque_header(batch_file)
        elif scheduler == 'slurm':
            self.__generate_slurm_header(batch_file)

    # Based on https://kb.northwestern.edu/page.php?id=89454
    def __generate_torque_header(self, filename:str):
        self.scheduler = 'torque'
        self.batch_file = filename
        DIRECTIVE = '#PBS'
        f = open(filename, 'w')
        f.write('#!/bin/bash')
        f.write('\n')
        f.write('## START OF HEADER ## ')
        f.write('\n')
        if "job_name" in self.job_data:
            f.write(DIRECTIVE + ' -N ' + self.job_data['job_name'])
            f.write('\n')
        if "account" in self.job_data:
            f.write(DIRECTIVE + ' -A ' + self.job_data['account'])
            f.write('\n')
        if "queue" in self.job_data:
            f.write(DIRECTIVE + ' -q ' + self.job_data['queue'])
            f.write('\n')
        if "wall_time_limit" in self.job_data:
            f.write(DIRECTIVE + ' -l walltime=' + self.job_data['wall_time_limit'])
            f.write('\n')
        if "node_count" in self.job_data:
            f.write(DIRECTIVE + ' -l nodes=' + str(self.job_data['node_count']))
            f.write('\n')
        if "core_count" in self.job_data:
            f.write(DIRECTIVE + ' -l procs=' + str(self.job_data['core_count']))
            f.write('\n')
        if "process_count_per_node" in self.job_data:
            f.write(DIRECTIVE + ' -l ppn=' + str(self.job_data['process_count_per_node']))
            f.write('\n')
        if "core_count_per_process" in self.job_data:
            pass
        if "memory_limit" in self.job_data:
            f.write(DIRECTIVE + ' -l mem=' + self.job_data['memory_limit'])
            f.write('\n')
        if "minimum_memory_per_processor" in self.job_data:
            f.write(DIRECTIVE + ' -l pmem=' + self.job_data['minimum_memory_per_processor'])
            f.write('\n')
        if "request_gpus" in self.job_data:
            f.write(DIRECTIVE + ' -l gpus=' + str(self.job_data['request_gpus']))
            f.write('\n')
        if "request_specific_nodes" in self.job_data:
            f.write(DIRECTIVE + ' -l nodes=' + self.job_data['request_specific_nodes'])
            f.write('\n')
        if "job_array" in self.job_data:
            f.write(DIRECTIVE + ' -t ' + self.job_data['job_array'])
            f.write('\n')
        if "standard_output_file" in self.job_data:
            f.write(DIRECTIVE + ' -o ' + self.job_data['standard_output_file'])
            f.write('\n')
        if "standard_error_file" in self.job_data:
            f.write(DIRECTIVE + ' -e ' + self.job_data['standard_error_file'])
            f.write('\n')
        if "combine_stdout_stderr" in self.job_data:
            f.write(DIRECTIVE + ' -j oe')
            f.write('\n')
        if "architecture_constraint" in self.job_data:
            f.write(DIRECTIVE + ' -l partition=' + self.job_data['architecture_constraint'])
            f.write('\n')
        if "copy_environment" in self.job_data:
            f.write(DIRECTIVE + ' -V ')
            f.write('\n')
        if "copy_environment_variable" in self.job_data:
            f.write(DIRECTIVE + ' -v ' + self.job_data['copy_environment_variable'])
            f.write('\n')
        if "job_dependency" in self.job_data:
            f.write(DIRECTIVE + ' -W ' + self.job_data['job_dependency'])
            f.write('\n')
        if "request_event_notification" in self.job_data:
            f.write(DIRECTIVE + ' -m ' + self.job_data['request_event_notification'])
            f.write('\n')
        if "email_address" in self.job_data:
            f.write(DIRECTIVE + ' M ' + self.job_data['email_address'])
            f.write('\n')
        if "defer_job" in self.job_data:
            f.write(DIRECTIVE + ' -a ' + self.job_data['defer_job'])
            f.write('\n')
        if "node_exclusive" in self.job_data:
            f.write(DIRECTIVE + ' -l naccesspolicy=singlejob')
            f.write('\n')

        f.write('## END OF HEADER ## ')
        f.write('\n')
        f.write('cd $PBS_O_WORKDIR')
        f.write('\n')
        f.close()

    def __generate_slurm_header(self, filename:str):
        self.scheduler = 'slurm'
        self.batch_file = filename
        DIRECTIVE = '#SBATCH'
        f = open(filename, 'w')
        f.write('#!/bin/bash')
        f.write('\n')
        f.write('## START OF HEADER ##')
        f.write('\n')
        if "job_name" in self.job_data:
            f.write(DIRECTIVE + ' -J ' + self.job_data['job_name'])
            f.write('\n')
        if "account" in self.job_data:
            f.write(DIRECTIVE + ' -A ' + self.job_data['account'])
            f.write('\n')
        if "queue" in self.job_data:
            f.write(DIRECTIVE + ' --partition=' + self.job_data['queue'])
            f.write('\n')
        if "wall_time_limit" in self.job_data:
            f.write(DIRECTIVE + ' --time=' + self.job_data['wall_time_limit'])
            f.write('\n')
        if "node_count" in self.job_data:
            f.write(DIRECTIVE + ' -N ' + str(self.job_data['node_count']))
            f.write('\n')
        if "core_count" in self.job_data:
            f.write(DIRECTIVE + ' -n ' + str(self.job_data['core_count']))
            f.write('\n')
        if "process_count_per_node" in self.job_data:
            f.write(DIRECTIVE + ' --ntasks-per-node=' + str(self.job_data['process_count_per_node']))
            f.write('\n')
        if "core_count_per_process" in self.job_data:
            f.write(DIRECTIVE + ' ----cpus-per-task=' + str(self.job_data['core_count_per_process']))
            f.write('\n')
        if "memory_limit" in self.job_data:
            f.write(DIRECTIVE + ' --mem=' + self.job_data['memory_limit'])
            f.write('\n')
        if "minimum_memory_per_processor" in self.job_data:
            f.write(DIRECTIVE + ' --mem-per-cpu=' + self.job_data['minimum_memory_per_processor'])
            f.write('\n')
        if "request_gpus" in self.job_data:
            f.write(DIRECTIVE + ' --gres=gpu:' + str(self.job_data['request_gpus']))
            f.write('\n')
        if "request_specific_nodes" in self.job_data:
            f.write(DIRECTIVE + ' --nodelist=' + self.job_data['request_specific_nodes'])
            f.write('\n')
        if "job_array" in self.job_data:
            f.write(DIRECTIVE + ' -a ' + self.job_data['job_array'])
            f.write('\n')
        if "standard_output_file" in self.job_data:
            f.write(DIRECTIVE + ' --output=' + self.job_data['standard_output_file'])
            f.write('\n')
        if "standard_error_file" in self.job_data:
            f.write(DIRECTIVE + ' -error=' + self.job_data['standard_error_file'])
            f.write('\n')
        if "combine_stdout_stderr" in self.job_data:
            pass
        if "architecture_constraint" in self.job_data:
            f.write(DIRECTIVE + ' -C ' + self.job_data['architecture_constraint'])
            f.write('\n')
        if "copy_environment" in self.job_data:
            f.write(DIRECTIVE + ' --export=ALL ')
            f.write('\n')
        if "copy_environment_variable" in self.job_data:
            f.write(DIRECTIVE + ' --export=' + self.job_data['copy_environment_variable'])
            f.write('\n')
        if "job_dependency" in self.job_data:
            f.write(DIRECTIVE + ' --dependency=' + self.job_data['job_dependency'])
            f.write('\n')
        if "request_event_notification" in self.job_data:
            f.write(DIRECTIVE + ' --mail-type=' + self.job_data['request_event_notification'])
            f.write('\n')
        if "email_address" in self.job_data:
            f.write(DIRECTIVE + ' --mail-user=' + self.job_data['email_address'])
            f.write('\n')
        if "defer_job" in self.job_data:
            f.write(DIRECTIVE + ' --begin=' + self.job_data['defer_job'])
            f.write('\n')
        if "node_exclusive" in self.job_data:
            f.write(DIRECTIVE + ' --exclusive')
            f.write('\n')

        f.write('## END OF HEADER ##')
        f.write('\n')
        f.write('cd $SLURM_SUBMIT_DIR')
        f.write('\n')

        f.close()

    def add_tuner(self):
        __tuner = tuner()
        __tuner.encode_tune(self.job_json_obj, self.batch_file)
        with open(self.batch_file, 'a') as f:
            f.seek(0, os.SEEK_END)
            f.write('\n')
            f.write('## START OF TUNER ##')
            f.write('\n')
            f.write('wget --no-check-certificate ' + __tuner.get_tune_link())
            f.write('\n')
            if "container_runtime" in self.app_data:
                cont = self.app_data['container_runtime']
                f.write('\nsingularity exec {} {}'.format(cont, __tuner.get_tune_filename()))
                f.write('\n')
            else:
                f.write(__tuner.get_tune_filename())
                f.write('\n')
            f.write('## END OF TUNER ##')
            f.write('\n')
            f.close()

    def add_optscript(self, scriptfile, scriptlink):
        with open(self.batch_file, 'a') as f:
            f.seek(0, os.SEEK_END)
            f.write('\n')
            f.write('wget --no-check-certificate ' + scriptlink)
            f.write('\n')
            f.write(scriptfile)
            f.write('\n')
            f.close()


    def add_apprun(self):
        with open(self.batch_file, 'a') as f:
            f.seek(0, os.SEEK_END)
            if "app_type" in self.app_data:
                app_type = self.app_data['app_type']
                exe = self.app_data['executable']
                arg = ''
                if "arguments" in self.app_data:
                    arg = self.app_data['arguments']
                if app_type == 'mpi':
                    mpi_ranks = 1
                    threads = 1
                    if "mpi_ranks" in self.app_data:
                        mpi_ranks = self.app_data['mpi_ranks']
                    if "threads" in self.app_data:
                        threads = self.app_data['threads']
                    f.write('\nexport OMP_NUM_THREADS={}\n'.format(threads))
                    if "container_runtime" in self.app_data:
                        cont = self.app_data['container_runtime']
                        f.write('\nsingularity exec {} '.format(cont))
                    else:
                        f.write('\n')
                    if self.scheduler == 'torque':
                        f.write('mpirun -np {} {} {}\n'.format(mpi_ranks, exe, arg))
                    elif self.scheduler == 'slurm':
                        f.write('srun -n {} {} {}\n'.format(mpi_ranks, exe, arg))
                elif app_type == 'python':
                    if "container_runtime" in self.app_data:
                        cont = self.app_data['container_runtime']
                        f.write('\nsingularity exec {} '.format(cont))
                    else:
                        f.write('\n')

                    f.write('python3 {} {}\n'.format(exe, arg))

            f.close()


def main():
    dsl_file = "../test/mpi_solver.json"
    with open(dsl_file) as json_file:
        obj = json.load(json_file)
        gen_t = jobfile_generator(obj, "../test/torque.pbs","torque")
        gen_s = jobfile_generator(obj, "../test/slurm.batch", "slurm")
        gen_t.add_apprun()
        gen_s.add_apprun()


if __name__ == '__main__':
    main()