from prettytable import PrettyTable
import os, sys, re, itertools, subprocess, json
from subprocess import PIPE, run


gpu_logpath = "/home/taccuser/slurm-automation/out_gpu.log"
srun_command = "srun -N 1 --gres=gpu:2 hostname"
autodetect_singlenode_command = "salloc -N 1 --gres=gpu:2 --begin=now --time=10"
autodetect_multinode_command = "salloc -N 2 --gres=gpu:2 --begin=now --time=10"
sinfo_command = "sinfo -Nl"
regex=r'^node-name:.*$'
nodepath = "/home/taccuser/slurm-automation/totalnodes.log"
alloc_regex=r'^salloc:.*$'

num_gpus = 0
with open(gpu_logpath, "r") as file:
    for line in file:
        num_gpus += 1
print("Number of GPUs:")
print(num_gpus)


x = PrettyTable()
x.field_names = ["Slurm Test Scenarious","Result"]

def cmdline(command):
    process = Popen(args=command, stdout=PIPE, shell=True)
    return process.communicate()[0]

def slurm_group_gpudetection():
    #print(os.popen("%s | tee totalnodes.log" %sinfo_command).read())
    #file1 = open("totalnodes.log","r")
    #var = re.findall(r'debug*(.*?)(?=\s*,\s*debug*|$)', file1.read())
    #print(var)
    with open(nodepath, "r") as file:
        for line in file:
            if "debug*" in line:
               print('Found keyword')
               print(line)
               str = line.split(" ")
               print(str[0])
        

def slurm_gpudetect():
    res = os.popen("%s" %srun_command).read()
    res_out = res.strip() #strip: removes spaces from output
    file1 = open("test-server.log","r")
    var = re.findall(r'node-name:(.*?)(?=\s*,\s*node-name:|$)', file1.read())    
    str1 = ''.join(var)
    if res_out == str1:
        #print("Pass")
        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Pass"])
        #print(x)
    else:               
        #print("Fail")
        x.add_row(["Total No.of Gpu vs Slurm No.of Gpu detecting", "Fail"])
        #print(x)

def validate_output():
    print("you have entered")
    with open("/home/taccuser/slurm-automation/allocation.log", "r") as file:
        if "error" in file.read():
            #print('Found keyword')
            x.add_row(["GPU autodetect single-node allocation", "Fail"])
            #print(x)
        else:
            x.add_row(["GPU autodetect single-node allocation", "Pass"])
            #print(x)
                

def slurm_node_allocation(autodetect_command):
    try:
        #res = os.popen("%s >/dev/tty" %autodetect_command).read()
        res = subprocess.run("%s 2>&1 | tee allocation.log >/dev/tty" %autodetect_command, timeout=2, shell=True)
        #res = run(autodetect_command, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        #res = subprocess.check_output(srun_command, shell=True).read()
        print(res)
        validate_output()
    except:
        pass        
        print("Pass")
        validate_output()


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
        x.add_row(["Auto node allocation", "Pass"])
        #print(x)
    else:
        print("Fail")
        x.add_row(["Auto node allocation", "Fail"])
        #print(x)

def slurm_autonode_allocation():
    try:
        slurm_automatic_allocation("N1hostname","N1_autoallocation")
        nodeexist = slurm_load_conf("N2hostname")
        print(nodeexist)
    except:
        pass
        #print("N2 has error")
    #if nodeexist != "None":
    #    print("Multi-Node exist!")
    #    slurm_automatic_allocation("N2hostname","N2_autoallocation")        
    #else:
    #    print("Multi-Node not exist!")

slurm_gpudetect()
slurm_node_allocation(autodetect_singlenode_command)
#slurm_node_allocation(autodetect_multinode_command)
#slurm_gpu_autodetect() 
#slurm_load_conf()
slurm_autonode_allocation()
print(x)
#slurm_group_gpudetection()
