#from prettytable import PrettyTable
import os, sys, re, itertools, subprocess, json
from subprocess import PIPE, run


gpu_logpath = "/home/taccuser/slurm-automation/out_gpu.log"
srun_command = "sudo srun -N 1 --gres=gpu:2 hostname"
autodetect_command = "salloc -N 1 --gres=gpu:2 --begin=now --time=10"
regex=r'^node-name:.*$'


num_gpus = 0
with open(gpu_logpath, "r") as file:
    for line in file:
        num_gpus += 1
print("Number of GPUs:")
print(num_gpus)

def cmdline(command):
    process = Popen(args=command, stdout=PIPE, shell=True)
    return process.communicate()[0]


def slurm_gpudetect():
    res = os.popen("%s" %srun_command).read()
    res_out = res.strip() #strip: removes spaces from output
    file1 = open("test-server.log","r")
    var = re.findall(r'node-name:(.*?)(?=\s*,\s*node-name:|$)', file1.read())    
    str1 = ''.join(var)
    if res_out == str1:
        print("Pass")
    else:               
        print("Fail")

def slurm_node_allocation():
    #res = os.popen("%s >/dev/tty" %autodetect_command).read()
    res = subprocess.run("%s 2>&1 | tee allocation.log >/dev/tty" %autodetect_command, timeout=10, shell=True)
    #res = subprocess.check_output("%s 2>&1 | tee allocation.log >/dev/tty" %autodetect_command, shell=True).read()
    #res = os.popen("exit()").read()
    print(res)

def slurm_load_conf(var):
    config = json.loads(open('/home/taccuser/slurm-automation/conf.json').read())
    return config["%s" %var]
    #print(config["%s" %var])

def slurm_automatic_allocation(n1hostname,n1autoallocation_command):
    n1host = slurm_load_conf(n1hostname)
    n1_autoallocation = slurm_load_conf(n1autoallocation_command)
    allocate  =  os.popen("%s" %n1_autoallocation).read()
    res = allocate.strip()
    #print(res)
    if n1host == res:
        print("Pass")
    else:
        print("Fail")

def slurm_autonode_allocation():
    slurm_automatic_allocation("N1hostname","N1_autoallocation")
    nodeexist = slurm_load_conf("N2hostname")
    if nodeexist != "None":
        print("Multi-Node exist!")
        slurm_automatic_allocation("N2hostname","N2_autoallocation")        
    else:
        print("Multi-Node not exist!")

#slurm_gpudetect()
slurm_node_allocation() 
#slurm_load_conf()
#slurm_autonode_allocation()
