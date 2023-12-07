import os
import socket
import subprocess
import multiprocessing
from shutil import copytree
from subprocess import Popen
from .validation_utils import micro_valid_int
from .file_utils import linux_path_converter

def find_char_indexes(string, target_char, invert = 0):
    matching_indexes = []
    for i, char in enumerate(string):
        if char == target_char and invert == 0:
            matching_indexes.append(i)
        elif char != target_char and invert == 1:
            matching_indexes.append(i)
    return matching_indexes

def clean_name(string,conversions = {"(":"", ")":"", "^":"pow", " ":"_"}):
    return_string = ""
    for char in string:
        if char in conversions:
            return_string += conversions[char]
        else:
            return_string += char
    return return_string


def job_script_maker(template_file_path,
                     save_path,
                     remote_job_path,
                     exec_name,
                     job_desc = "qsub_log",
                     job_path_line = 9,
                     exec_line = 15,
                     file_name = "job_submission_script.sh"):
    
    remote_job_path = linux_path_converter(remote_job_path)
    with open(template_file_path, "r") as file:
        template_lines = file.read().split("\n")
        
    template_lines[6] = f"#$ -N {job_desc}"
    template_lines[job_path_line-1] = f'job_dir="{remote_job_path}"'
    template_lines[exec_line - 1] = f"./{exec_name}"
    
    with open(os.path.join(save_path, file_name), "w+") as file:
        for line in template_lines:
            file.write(f"{line}\n")


def get_batch_IDs(string, lower, upper):
    if "-" in string:
        upper_lower = string.split("-")
        if len(upper_lower) == 2:
            if micro_valid_int(upper_lower[0], lower, upper) and micro_valid_int(upper_lower[1], lower, upper):
                return list(range(int(upper_lower[0]), int(upper_lower[1]) + 1))
    if "," in string:
        nums = string.split(",")
        if all([micro_valid_int(element, lower, upper) for element in nums]):
            return [int(element) for element in nums]
    else:
        if micro_valid_int(string, lower, upper):
            if int(string) == upper:
                return int(string)
            return [int(string)]
    return False

def get_seed(cwd, job_path, seeds_path, seed_size):
    seeds = [int(seed.name) for seed in os.scandir(seeds_path) if seed.is_dir()]
    new_seed_path = os.path.join(seeds_path, str(seed_size))
    if seed_size not in seeds:
        os.mkdir(new_seed_path)
        os.chdir(new_seed_path)
        Popen(["python",os.path.join(seeds_path, "make_poly_seed.py"),str(seed_size)]).wait()
        os.chdir(cwd)
    copytree(new_seed_path, os.path.join(job_path, "seed"))


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def background_process(command_array, silent = True):
    def child_process(command_array, silent = True):
        if silent:
            subprocess.Popen(command_array, start_new_session = True, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        else:
            subprocess.Popen(command_array, start_new_session = True)
    process = multiprocessing.Process(target = child_process, args = [command_array])
    process.daemon = True
    process.start()







